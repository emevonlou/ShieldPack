from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from app.security import sha1_hash, split_hash_prefix_suffix
from app.config import settings

router = APIRouter(tags=["Passwords"])


class PasswordCheckRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=256)


class PasswordCheckResponse(BaseModel):
    pwned: bool
    count: int
    message: str
    risk_level: str
    recommendation: str


def calculate_risk(count: int) -> tuple[str, str]:
    if count == 0:
        return (
            "low",
            "Boa notícia: esta senha não foi encontrada na base consultada. Ainda assim, use senhas longas e exclusivas."
        )
    if count < 1000:
        return (
            "medium",
            "Esta senha já apareceu em vazamentos. Troque-a e não a reutilize em outras contas."
        )
    return (
        "high",
        "Risco alto: esta senha é amplamente conhecida em vazamentos. Troque imediatamente e ative autenticação em dois fatores."
    )


@router.post("/check-password", response_model=PasswordCheckResponse)
async def check_password(data: PasswordCheckRequest):
    try:
        password_hash = sha1_hash(data.password)
        prefix, suffix = split_hash_prefix_suffix(password_hash)

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(url, headers={"Add-Padding": "true"})

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Falha ao consultar o serviço de senhas vazadas."
            )

        matches = response.text.splitlines()

        for line in matches:
            parts = line.split(":")
            if len(parts) != 2:
                continue

            returned_suffix, count = parts[0].strip(), parts[1].strip()

            if returned_suffix.upper() == suffix:
                total = int(count)
                risk_level, recommendation = calculate_risk(total)
                return PasswordCheckResponse(
                    pwned=True,
                    count=total,
                    message=f"Esta senha já apareceu {total} vez(es) em vazamentos e não deve ser usada.",
                    risk_level=risk_level,
                    recommendation=recommendation,
                )

        risk_level, recommendation = calculate_risk(0)
        return PasswordCheckResponse(
            pwned=False,
            count=0,
            message="Nenhum vazamento encontrado para esta senha na base consultada.",
            risk_level=risk_level,
            recommendation=recommendation,
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao verificar a senha: {str(exc)}"
        )

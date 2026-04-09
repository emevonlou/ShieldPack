from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

from app.security import sha1_hash, split_hash_prefix_suffix

router = APIRouter(tags=["Passwords"])


class PasswordCheckRequest(BaseModel):
    password: str = Field(..., min_length=1, max_length=256)


class PasswordCheckResponse(BaseModel):
    pwned: bool
    count: int
    message: str


@router.post("/check-password", response_model=PasswordCheckResponse)
async def check_password(data: PasswordCheckRequest):
    try:
        password_hash = sha1_hash(data.password)
        prefix, suffix = split_hash_prefix_suffix(password_hash)

        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        async with httpx.AsyncClient(timeout=15.0) as client:
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
                return PasswordCheckResponse(
                    pwned=True,
                    count=total,
                    message=f"Esta senha já apareceu {total} vez(es) em vazamentos e não deve ser usada."
                )

        return PasswordCheckResponse(
            pwned=False,
            count=0,
            message="Nenhum vazamento encontrado para esta senha na base consultada."
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao verificar a senha: {str(exc)}"
        )

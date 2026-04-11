from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx

from app.config import settings

router = APIRouter(tags=["Email"])


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailCheckResponse(BaseModel):
    found: bool
    breaches: list[str]
    message: str


@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email(data: EmailCheckRequest):
    if not settings.enable_email_check:
        return EmailCheckResponse(
            found=False,
            breaches=[],
            message="Verificação de e-mail ainda não está ativada."
        )

    if not settings.hibp_api_key:
        raise HTTPException(
            status_code=500,
            detail="API key do HIBP não configurada."
        )

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{data.email}"

    headers = {
        "hibp-api-key": settings.hibp_api_key,
        "user-agent": "ShieldPack"
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 404:
            return EmailCheckResponse(
                found=False,
                breaches=[],
                message="Nenhum vazamento encontrado para este e-mail."
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Erro ao consultar serviço de vazamentos."
            )

        data_json = response.json()
        breaches = [item["Name"] for item in data_json]

        return EmailCheckResponse(
            found=True,
            breaches=breaches,
            message=f"E-mail encontrado em {len(breaches)} vazamento(s)."
        )

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(exc)}"
        )

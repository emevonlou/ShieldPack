from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import httpx

from app.config import settings

router = APIRouter(tags=["Email"])


class EmailCheckRequest(BaseModel):
    email: EmailStr


class EmailBreach(BaseModel):
    name: str
    domain: str
    exposed_data: list[str]


class EmailCheckResponse(BaseModel):
    found: bool
    demo_mode: bool
    breaches: list[EmailBreach]
    count: int
    risk_level: str
    message: str
    recommendation: str


DEMO_BREACHES = {
    "demo@shieldpack.dev": [
        {
            "name": "DemoMarket",
            "domain": "demomarket.test",
            "exposed_data": ["email", "password hash", "username"]
        },
        {
            "name": "ExampleCloud",
            "domain": "examplecloud.test",
            "exposed_data": ["email", "phone", "ip address"]
        },
    ],
    "risk@shieldpack.dev": [
        {
            "name": "OldForum",
            "domain": "oldforum.test",
            "exposed_data": ["email", "password hash", "username", "birth date"]
        },
        {
            "name": "ShopExample",
            "domain": "shopexample.test",
            "exposed_data": ["email", "address", "phone"]
        },
        {
            "name": "SocialDemo",
            "domain": "socialdemo.test",
            "exposed_data": ["email", "username", "private messages metadata"]
        },
    ],
}


def calculate_email_risk(count: int) -> tuple[str, str]:
    if count == 0:
        return (
            "low",
            "Nenhuma exposição foi encontrada para este e-mail na fonte consultada."
        )

    if count <= 2:
        return (
            "medium",
            "Este e-mail apareceu em vazamentos. Revise senhas reutilizadas e ative autenticação em dois fatores."
        )

    return (
        "high",
        "Este e-mail apareceu em múltiplos vazamentos. Priorize troca de senhas, revisão de contas críticas e autenticação em dois fatores."
    )


def build_email_response(email: str, breaches: list[dict], demo_mode: bool) -> EmailCheckResponse:
    breach_items = [EmailBreach(**item) for item in breaches]
    count = len(breach_items)
    risk_level, recommendation = calculate_email_risk(count)

    if count == 0:
        message = "Nenhum vazamento encontrado para este e-mail."
    else:
        message = f"E-mail encontrado em {count} vazamento(s)."

    return EmailCheckResponse(
        found=count > 0,
        demo_mode=demo_mode,
        breaches=breach_items,
        count=count,
        risk_level=risk_level,
        message=message,
        recommendation=recommendation,
    )


@router.post("/check-email", response_model=EmailCheckResponse)
async def check_email(data: EmailCheckRequest):
    normalized_email = data.email.lower().strip()

    if not settings.enable_email_check:
        return build_email_response(normalized_email, [], demo_mode=False)

    if settings.enable_email_demo_mode and not settings.hibp_api_key:
        demo_breaches = DEMO_BREACHES.get(normalized_email, [])
        return build_email_response(normalized_email, demo_breaches, demo_mode=True)

    if not settings.hibp_api_key:
        raise HTTPException(
            status_code=500,
            detail="API key do HIBP não configurada."
        )

    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{normalized_email}"

    headers = {
        "hibp-api-key": settings.hibp_api_key,
        "user-agent": "ShieldPack"
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 404:
            return build_email_response(normalized_email, [], demo_mode=False)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Erro ao consultar serviço de vazamentos."
            )

        data_json = response.json()

        breaches = [
            {
                "name": item.get("Name", "Unknown"),
                "domain": item.get("Domain", "unknown"),
                "exposed_data": item.get("DataClasses", []),
            }
            for item in data_json
        ]

        return build_email_response(normalized_email, breaches, demo_mode=False)

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(exc)}"
        )

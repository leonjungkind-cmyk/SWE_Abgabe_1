"""KundeRouter."""

from fastapi import APIRouter

kunde_router = APIRouter(
    prefix="/kunde",
    tags=["Kunde"],
)


@kunde_router.get("/hello")
def hello() -> dict[str, str]:
    """Einfacher Test-Endpunkt für einen schnellen Router-Check."""
    return {"message": "Hello World"}

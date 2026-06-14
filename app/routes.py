from fastapi import APIRouter

from .models import SolarData
from .services import cache, get_solar_data

router = APIRouter(prefix="/api")


@router.get("/solar-data", response_model=SolarData)
async def solar_data() -> SolarData:
    """Return the latest solar data"""
    return await get_solar_data()


@router.get("/health")
async def health() -> dict:
    """Simple health check"""
    return {
        "status": "healthy",
        "cache_valid": cache.get() is not None,
    }

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SunspotRegion(BaseModel):
    id: int
    noaa_number: int
    lat: float
    lon: float
    area: float
    intensity: float
    location: str
    mag_type: str


class SolarData(BaseModel):
    timestamp: datetime
    regions: List[SunspotRegion] = []
    solar_flux: Optional[float] = None
    xray_class: Optional[str] = None
    xray_flux: Optional[float] = None
    solar_wind_speed: Optional[float] = None
    solar_wind_density: Optional[float] = None
    kp_index: Optional[int] = None
    active_region_count: int = 0
    total_sunspot_area: float = 0
    carrington_rotation: Optional[float] = None

import asyncio
from datetime import datetime
from typing import Dict, List, Optional

import httpx

from .models import SolarData, SunspotRegion

NOAA_BASE_URL = "https://services.swpc.noaa.gov"
API_ENDPOINTS = {
    "regions": f"{NOAA_BASE_URL}/json/solar_regions.json",
    "xray": f"{NOAA_BASE_URL}/json/goes/primary/xrays-6-hour.json",
    "solar_wind": f"{NOAA_BASE_URL}/json/rtsw/rtsw_wind_1h.json",
    "plasma": f"{NOAA_BASE_URL}/json/rtsw/rtsw_plasma_1h.json",
    "kp": f"{NOAA_BASE_URL}/json/planetary_k_index_1m.json",
    "flux": f"{NOAA_BASE_URL}/json/f107_cm_flux.json",
}


class DataCache:
    """Simple time-based cache for solar data."""

    def __init__(self, ttl: int = 300) -> None:
        self.ttl = ttl
        self.data: Optional[SolarData] = None
        self.last_update: Optional[datetime] = None

    def get(self) -> Optional[SolarData]:
        if self.data and self.last_update:
            age = (datetime.utcnow() - self.last_update).total_seconds()
            if age < self.ttl:
                return self.data
        return None

    def set(self, data: SolarData) -> None:
        self.data = data
        self.last_update = datetime.utcnow()


cache = DataCache(ttl=300)


async def fetch_endpoint(client: httpx.AsyncClient, url: str) -> Optional[Dict]:
    try:
        resp = await client.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        return None
    return None


async def fetch_all_noaa_data() -> Dict[str, Optional[Dict]]:
    async with httpx.AsyncClient() as client:
        tasks = {key: fetch_endpoint(client, url) for key, url in API_ENDPOINTS.items()}
        return {key: await task for key, task in tasks.items()}


def parse_regions(regions_data: List[Dict]) -> List[SunspotRegion]:
    regions: List[SunspotRegion] = []
    for r in regions_data:
        try:
            regions.append(
                SunspotRegion(
                    id=int(r.get("region", 0)),
                    noaa_number=int(r.get("region", 0)),
                    lat=float(r.get("latitude", 0) or 0),
                    lon=float(r.get("longitude", 0) or 0),
                    area=float(r.get("area", 0) or 0),
                    intensity=float(r.get("intensity", 0) or 0),
                    location=r.get("location", ""),
                    mag_type=r.get("magType", ""),
                )
            )
        except Exception:
            continue
    return regions


def process_solar_data(raw: Dict[str, Optional[Dict]]) -> SolarData:
    regions_data = raw.get("regions") or []
    regions = parse_regions(regions_data)

    latest = lambda key: (raw.get(key) or [{}])[-1]

    return SolarData(
        timestamp=datetime.utcnow(),
        regions=regions,
        solar_flux=latest("flux").get("flux"),
        xray_class=latest("xray").get("class_type"),
        xray_flux=latest("xray").get("flux"),
        solar_wind_speed=latest("solar_wind").get("speed"),
        solar_wind_density=latest("plasma").get("density"),
        kp_index=latest("kp").get("kp_index"),
        active_region_count=len(regions),
        total_sunspot_area=sum(r.area for r in regions),
    )


def generate_demo_data() -> SolarData:
    demo_regions = [
        SunspotRegion(
            id=1,
            noaa_number=1000,
            lat=10,
            lon=20,
            area=100,
            intensity=0.5,
            location="N10E20",
            mag_type="Alpha",
        )
    ]
    return SolarData(
        timestamp=datetime.utcnow(),
        regions=demo_regions,
        solar_flux=123.4,
        xray_class="B1.0",
        xray_flux=1e-6,
        solar_wind_speed=350,
        solar_wind_density=5,
        kp_index=2,
        active_region_count=len(demo_regions),
        total_sunspot_area=sum(r.area for r in demo_regions),
        carrington_rotation=2290.5,
    )


async def get_solar_data() -> SolarData:
    cached = cache.get()
    if cached:
        return cached
    raw = await fetch_all_noaa_data()
    if any(raw.values()):
        data = process_solar_data(raw)
    else:
        data = generate_demo_data()
    cache.set(data)
    return data

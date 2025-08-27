# === HTML Content (would normally be in templates/) ===

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SOLAR MONITOR</title>
    <style>
        @font-face {
            font-family: 'Bitmap';
            src: local('Courier New'), local('Courier'), local('monospace');
        }
        
        :root {
            --bg: #000;
            --fg: #fff;
            --grid: #333;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Bitmap', 'Courier New', monospace;
            background: var(--bg);
            color: var(--fg);
            min-height: 100vh;
            overflow-x: hidden;
            image-rendering: pixelated;
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            border-bottom: 2px solid var(--fg);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }
        
        h1 {
            font-size: 32px;
            letter-spacing: 8px;
            font-weight: normal;
        }
        
        .status {
            display: flex;
            gap: 30px;
            font-size: 12px;
            letter-spacing: 2px;
        }
        
        .status-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .status-value {
            font-size: 18px;
            margin-top: 5px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }
        
        .sun-container {
            position: relative;
            aspect-ratio: 1;
            max-width: 600px;
            margin: 0 auto;
        }
        
        #sunCanvas {
            width: 100%;
            height: 100%;
            border: 2px solid var(--fg);
            cursor: crosshair;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 30px;
        }
        
        .control-group {
            border: 1px solid var(--fg);
            padding: 20px;
        }
        
        .control-title {
            font-size: 14px;
            letter-spacing: 4px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--grid);
        }
        
        .toggle-group {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .toggle {
            flex: 1;
            padding: 10px;
            background: var(--bg);
            color: var(--fg);
            border: 1px solid var(--fg);
            cursor: pointer;
            font-family: inherit;
            font-size: 11px;
            letter-spacing: 2px;
            transition: all 0.1s;
        }
        
        .toggle.active {
            background: var(--fg);
            color: var(--bg);
        }
        
        .toggle:hover:not(.active) {
            background: #222;
        }
        
        .slider-container {
            margin-bottom: 15px;
        }
        
        .slider-label {
            font-size: 10px;
            letter-spacing: 1px;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }
        
        input[type="range"] {
            width: 100%;
            height: 2px;
            background: var(--fg);
            outline: none;
            -webkit-appearance: none;
        }
        
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 12px;
            height: 12px;
            background: var(--fg);
            cursor: pointer;
        }
        
        input[type="range"]::-moz-range-thumb {
            width: 12px;
            height: 12px;
            background: var(--fg);
            cursor: pointer;
            border: none;
        }
        
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
            padding-top: 40px;
            border-top: 2px solid var(--fg);
        }
        
        .data-card {
            border: 1px solid var(--grid);
            padding: 15px;
        }
        
        .data-title {
            font-size: 10px;
            letter-spacing: 2px;
            margin-bottom: 10px;
            opacity: 0.7;
        }
        
        .data-value {
            font-size: 24px;
            letter-spacing: 1px;
        }
        
        .data-unit {
            font-size: 10px;
            opacity: 0.5;
            margin-left: 5px;
        }
        
        .region-list {
            max-height: 200px;
            overflow-y: auto;
            border: 1px solid var(--grid);
            padding: 10px;
            font-size: 10px;
            letter-spacing: 1px;
        }
        
        .region-item {
            padding: 5px 0;
            border-bottom: 1px solid #222;
            display: flex;
            justify-content: space-between;
        }
        
        .region-item:last-child {
            border-bottom: none;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @media (max-width: 768px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 24px;
                letter-spacing: 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <h1>SOLAR MONITOR</h1>
                <div class="status">
                    <div class="status-item">
                        <span>UTC</span>
                        <span class="status-value" id="utc-time">00:00:00</span>
                    </div>
                    <div class="status-item">
                        <span>REGIONS</span>
                        <span class="status-value" id="region-count">0</span>
                    </div>
                    <div class="status-item">
                        <span>STATUS</span>
                        <span class="status-value pulse" id="status">ACTIVE</span>
                    </div>
                </div>
            </div>
        </header>

        <div class="main-grid">
            <div class="sun-container">
                <canvas id="sunCanvas"></canvas>
            </div>

            <div class="controls">
                <div class="control-group">
                    <div class="control-title">VISUALIZATION</div>
                    <div class="toggle-group">
                        <button class="toggle active" data-mode="bit">BIT</button>
                        <button class="toggle" data-mode="linear">LINEAR</button>
                        <button class="toggle" data-mode="contour">CONTOUR</button>
                    </div>
                    <div class="slider-container">
                        <div class="slider-label">
                            <span>GRID RESOLUTION</span>
                            <span id="grid-value">16</span>
                        </div>
                        <input type="range" id="grid-slider" min="8" max="32" value="16" step="8">
                    </div>
                </div>

                <div class="control-group">
                    <div class="control-title">TIME CONTROL</div>
                    <div class="toggle-group">
                        <button class="toggle active" data-time="live">LIVE</button>
                        <button class="toggle" data-time="pause">PAUSE</button>
                    </div>
                    <div class="slider-container">
                        <div class="slider-label">
                            <span>TIME OFFSET</span>
                            <span id="time-value">0h</span>
                        </div>
                        <input type="range" id="time-slider" min="-168" max="0" value="0">
                    </div>
                </div>

                <div class="control-group">
                    <div class="control-title">ACTIVE REGIONS</div>
                    <div class="region-list" id="region-list">
                        <!-- Regions will be populated here -->
                    </div>
                </div>
            </div>
        </div>

        <div class="data-grid">
            <div class="data-card">
                <div class="data-title">SOLAR FLUX</div>
                <div class="data-value">
                    <span id="solar-flux">---</span>
                    <span class="data-unit">SFU</span>
                </div>
            </div>
            <div class="data-card">
                <div class="data-title">X-RAY FLUX</div>
                <div class="data-value">
                    <span id="xray-flux">---</span>
                    <span class="data-unit"></span>
                </div>
            </div>
            <div class="data-card">
                <div class="data-title">SOLAR WIND</div>
                <div class="data-value">
                    <span id="solar-wind">---</span>
                    <span class="data-unit">KM/S</span>
                </div>
            </div>
            <div class="data-card">
                <div class="data-title">KP INDEX</div>
                <div class="data-value">
                    <span id="kp-index">-</span>
                    <span class="data-unit"></span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Canvas setup
        const canvas = document.getElementById('sunCanvas');
        const ctx = canvas.getContext('2d');
        let gridSize = 16;
        let visualMode = 'bit';
        let isLive = true;
        let timeOffset = 0;
        let animationFrame;
        let solarData = null;

        // Carrington rotation parameters
        const OMEGA = 360 / 27.2753; // degrees per day
        let baseTime = Date.now();
        let currentRotation = 0;

        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            canvas.style.width = rect.width + 'px';
            canvas.style.height = rect.height + 'px';
        }

        function drawSun() {
            const width = canvas.width / window.devicePixelRatio;
            const height = canvas.height / window.devicePixelRatio;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) / 2 - 10;
            
            // Clear canvas
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, width, height);
            
            // Create grid
            const cellSize = (radius * 2) / gridSize;
            
            // Clip to circle
            ctx.save();
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.clip();
            
            // Draw grid cells
            for (let row = 0; row < gridSize; row++) {
                for (let col = 0; col < gridSize; col++) {
                    const x = centerX - radius + col * cellSize;
                    const y = centerY - radius + row * cellSize;
                    
                    // Convert to solar coordinates
                    const solarX = (col - gridSize/2) / (gridSize/2);
                    const solarY = (row - gridSize/2) / (gridSize/2);
                    const dist = Math.sqrt(solarX * solarX + solarY * solarY);
                    
                    if (dist <= 1 && solarData && solarData.regions) {
                        // Check if any sunspot is in this cell
                        let intensity = 0;
                        
                        for (let spot of solarData.regions) {
                            const spotLon = (spot.lon + currentRotation) % 360;
                            const lonRad = (spotLon - 180) * Math.PI / 180;
                            const latRad = spot.lat * Math.PI / 180;
                            
                            // Only visible on front hemisphere
                            if (Math.abs(spotLon - 180) < 90) {
                                const spotX = Math.sin(lonRad) * Math.cos(latRad);
                                const spotY = Math.sin(latRad);
                                
                                const cellDist = Math.sqrt(
                                    Math.pow(spotX - solarX, 2) + 
                                    Math.pow(spotY - solarY, 2)
                                );
                                
                                if (cellDist < 0.15) {
                                    if (visualMode === 'bit') {
                                        intensity = 1;
                                    } else if (visualMode === 'linear') {
                                        intensity = Math.max(intensity, spot.intensity);
                                    } else if (visualMode === 'contour') {
                                        intensity = Math.max(intensity, spot.intensity * (1 - cellDist / 0.15));
                                    }
                                }
                            }
                        }
                        
                        if (intensity > 0) {
                            if (visualMode === 'bit') {
                                ctx.fillStyle = '#fff';
                            } else {
                                const alpha = intensity;
                                ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                            }
                            ctx.fillRect(x, y, cellSize - 1, cellSize - 1);
                        }
                    }
                }
            }
            
            ctx.restore();
            
            // Draw sun outline
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.stroke();
        }

        function updateTime() {
            const now = new Date();
            document.getElementById('utc-time').textContent = 
                now.toUTCString().split(' ')[4];
        }

        function updateDisplay() {
            if (!solarData) return;
            
            // Update region list
            const list = document.getElementById('region-list');
            list.innerHTML = '';
            
            if (solarData.regions && solarData.regions.length > 0) {
                solarData.regions.forEach(spot => {
                    const item = document.createElement('div');
                    item.className = 'region-item';
                    item.innerHTML = `
                        <span>AR${spot.id}</span>
                        <span>${spot.area} MSH</span>
                    `;
                    list.appendChild(item);
                });
            } else {
                list.innerHTML = '<div style="opacity: 0.5">No active regions</div>';
            }
            
            document.getElementById('region-count').textContent = 
                solarData.active_region_count || 0;
            
            // Update data cards
            document.getElementById('solar-flux').textContent = 
                solarData.solar_flux ? solarData.solar_flux.toFixed(1) : '---';
            document.getElementById('xray-flux').textContent = 
                solarData.xray_class || '---';
            document.getElementById('solar-wind').textContent = 
                solarData.solar_wind_speed ? Math.floor(solarData.solar_wind_speed) : '---';
            document.getElementById('kp-index').textContent = 
                solarData.kp_index !== undefined ? solarData.kp_index : '-';#!/usr/bin/env python3
"""
#Solar Monitor - A minimalist solar activity visualization application
#Displays real-time sunspot data from NOAA in a stark bit-mapped aesthetic
#"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import httpx
import numpy as np
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create app instance
app = FastAPI(
    title="Solar Monitor",
    description="Real-time solar activity monitoring with bit-mapped visualization",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Data Models ===

class SunspotRegion(BaseModel):
    id: int
    noaa_number: Optional[int] = None
    lat: float  # Heliographic latitude
    lon: float  # Carrington longitude
    area: int   # Millionths of solar hemisphere (MSH)
    intensity: float  # Normalized 0-1
    location: str  # e.g., "N12E45"
    mag_type: Optional[str] = None  # Magnetic classification
    spot_count: Optional[int] = None

class SolarData(BaseModel):
    timestamp: datetime
    regions: List[SunspotRegion]
    solar_flux: float  # 10.7cm radio flux in SFU
    xray_class: str    # e.g., "C2.1"
    xray_flux: float   # W/m^2
    solar_wind_speed: float  # km/s
    solar_wind_density: float  # p/cm^3
    kp_index: float
    active_region_count: int
    total_sunspot_area: int  # Total area in MSH
    carrington_rotation: float  # Current rotation number

# === NOAA API Configuration ===

NOAA_BASE_URL = "https://services.swpc.noaa.gov"
API_ENDPOINTS = {
    "regions": f"{NOAA_BASE_URL}/json/solar_regions.json",
    "xray": f"{NOAA_BASE_URL}/json/goes/primary/xrays-6-hour.json",
    "solar_wind": f"{NOAA_BASE_URL}/json/rtsw/rtsw_wind_1h.json",
    "plasma": f"{NOAA_BASE_URL}/json/rtsw/rtsw_plasma_1h.json",
    "kp": f"{NOAA_BASE_URL}/json/planetary_k_index_1m.json",
    "flux": f"{NOAA_BASE_URL}/json/f107_cm_flux.json"
}

# === Cache Management ===

class DataCache:
    def __init__(self, ttl: int = 300):
        self.data = None
        self.last_update = None
        self.ttl = ttl  # Time to live in seconds
    
    def is_valid(self) -> bool:
        if not self.data or not self.last_update:
            return False
        return (datetime.utcnow() - self.last_update).total_seconds() < self.ttl
    
    def update(self, data):
        self.data = data
        self.last_update = datetime.utcnow()
    
    def get(self):
        return self.data if self.is_valid() else None

cache = DataCache(ttl=300)  # 5 minute cache

# === NOAA Data Fetching ===

async def fetch_noaa_endpoint(client: httpx.AsyncClient, endpoint: str) -> Optional[Dict]:
    """Fetch data from a NOAA SWPC endpoint"""
    try:
        response = await client.get(API_ENDPOINTS[endpoint], timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
    return None

async def fetch_all_noaa_data() -> Dict:
    """Fetch all relevant NOAA data concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = {
            endpoint: fetch_noaa_endpoint(client, endpoint)
            for endpoint in API_ENDPOINTS.keys()
        }
        results = {}
        for endpoint, task in tasks.items():
            results[endpoint] = await task
    return results

def parse_regions(regions_data: List[Dict]) -> List[SunspotRegion]:
    """Parse NOAA region data into our format"""
    regions = []
    
    for region in regions_data:
        try:
            # Get region number safely
            region_num = region.get("region")
            if region_num is None:
                continue
            region_id = int(region_num) if region_num else 0
            
            # Convert location string (e.g., "N12E45") to lat/lon
            location = region.get("location", "")
            lat = 0.0
            lon = 0.0
            
            if location and len(location) >= 4:
                # Parse location string
                ns = location[0]
                lat_str = ""
                ew = ""
                lon_str = ""
                
                for i, char in enumerate(location[1:], 1):
                    if char in "EW":
                        lat_str = location[1:i]
                        ew = char
                        lon_str = location[i+1:]
                        break
                
                try:
                    lat = float(lat_str) * (1 if ns == "N" else -1)
                    lon = float(lon_str) * (1 if ew == "E" else -1)
                except ValueError:
                    pass
            
            # Get area safely - handle None, empty string, etc.
            area_val = region.get("area")
            if area_val is None or area_val == "":
                area = 0
            else:
                try:
                    area = int(float(area_val))  # Convert through float in case of decimal
                except (ValueError, TypeError):
                    area = 0
            
            # Calculate intensity
            intensity = min(1.0, float(area) / 500) if area > 0 else 0.1
            
            # Get spot count safely
            spot_count_val = region.get("spot_count")
            spot_count = None
            if spot_count_val is not None and spot_count_val != "":
                try:
                    spot_count = int(float(spot_count_val))
                except (ValueError, TypeError):
                    pass
            
            # Create region object
            regions.append(SunspotRegion(
                id=region_id,
                noaa_number=region_id,
                lat=lat,
                lon=lon,
                area=area,
                intensity=intensity,
                location=location,
                mag_type=region.get("mag_type", "") or "",
                spot_count=spot_count
            ))
        except Exception as e:
            print(f"Error parsing region {region}: {e}")
            continue
    
    return regions

def process_solar_data(raw_data: Dict) -> SolarData:
    """Process raw NOAA data into SolarData object"""
    
    # Parse regions
    regions = []
    if raw_data.get("regions") and raw_data["regions"] is not None:
        regions = parse_regions(raw_data["regions"])
    
    # Parse X-ray data
    xray_class = "A1.0"
    xray_flux = 1e-8
    if raw_data.get("xray") and raw_data["xray"]:
        try:
            # Filter out None entries and get latest
            valid_xray = [x for x in raw_data["xray"] if x and x.get("flux") is not None]
            if valid_xray:
                latest = max(valid_xray, key=lambda x: x.get("time_tag", ""))
                xray_flux = float(latest.get("flux", 1e-8))
                
                # Convert flux to class
                if xray_flux >= 1e-4:
                    xray_class = f"X{xray_flux/1e-4:.1f}"
                elif xray_flux >= 1e-5:
                    xray_class = f"M{xray_flux/1e-5:.1f}"
                elif xray_flux >= 1e-6:
                    xray_class = f"C{xray_flux/1e-6:.1f}"
                elif xray_flux >= 1e-7:
                    xray_class = f"B{xray_flux/1e-7:.1f}"
                else:
                    xray_class = f"A{xray_flux/1e-8:.1f}"
        except Exception as e:
            print(f"Error parsing X-ray data: {e}")
    
    # Parse solar wind
    wind_speed = 400.0
    wind_density = 5.0
    if raw_data.get("solar_wind") and raw_data["solar_wind"]:
        try:
            valid_wind = [w for w in raw_data["solar_wind"] if w and w.get("speed") is not None]
            if valid_wind:
                latest = valid_wind[-1]
                speed_val = latest.get("speed")
                if speed_val is not None and speed_val != "":
                    wind_speed = float(speed_val)
        except Exception as e:
            print(f"Error parsing solar wind: {e}")
    
    if raw_data.get("plasma") and raw_data["plasma"]:
        try:
            valid_plasma = [p for p in raw_data["plasma"] if p and p.get("density") is not None]
            if valid_plasma:
                latest = valid_plasma[-1]
                density_val = latest.get("density")
                if density_val is not None and density_val != "":
                    wind_density = float(density_val)
        except Exception as e:
            print(f"Error parsing plasma data: {e}")
    
    # Parse Kp index
    kp_index = 2.0
    if raw_data.get("kp") and raw_data["kp"]:
        try:
            valid_kp = [k for k in raw_data["kp"] if k and k.get("kp") is not None]
            if valid_kp:
                latest = max(valid_kp, key=lambda x: x.get("time_tag", ""))
                kp_val = latest.get("kp")
                if kp_val is not None and kp_val != "":
                    kp_index = float(kp_val)
        except Exception as e:
            print(f"Error parsing Kp data: {e}")
    
    # Parse solar flux
    solar_flux = 100.0
    if raw_data.get("flux") and raw_data["flux"]:
        try:
            valid_flux = [f for f in raw_data["flux"] if f and f.get("flux") is not None]
            if valid_flux:
                latest = valid_flux[-1]
                flux_val = latest.get("flux")
                if flux_val is not None and flux_val != "":
                    solar_flux = float(flux_val)
        except Exception as e:
            print(f"Error parsing flux data: {e}")
    
    # Calculate totals
    total_area = sum(r.area for r in regions)
    
    # Calculate current Carrington rotation
    # Rotation 1 started November 9, 1853
    ref_date = datetime(1853, 11, 9)
    days_since = (datetime.utcnow() - ref_date).total_seconds() / 86400
    carrington_rotation = 1 + days_since / 27.2753
    
    return SolarData(
        timestamp=datetime.utcnow(),
        regions=regions,
        solar_flux=solar_flux,
        xray_class=xray_class,
        xray_flux=xray_flux,
        solar_wind_speed=wind_speed,
        solar_wind_density=wind_density,
        kp_index=kp_index,
        active_region_count=len(regions),
        total_sunspot_area=total_area,
        carrington_rotation=carrington_rotation
    )

def generate_demo_data() -> SolarData:
    """Generate demonstration data when NOAA is unavailable"""
    demo_regions = [
        SunspotRegion(
            id=13901, noaa_number=13901, lat=12, lon=45, area=200,
            intensity=0.8, location="N12E45", mag_type="Beta"
        ),
        SunspotRegion(
            id=13902, noaa_number=13902, lat=-18, lon=120, area=150,
            intensity=0.6, location="S18E30", mag_type="Beta-Gamma"
        ),
        SunspotRegion(
            id=13903, noaa_number=13903, lat=25, lon=200, area=100,
            intensity=0.9, location="N25W20", mag_type="Alpha"
        ),
        SunspotRegion(
            id=13904, noaa_number=13904, lat=-8, lon=280, area=180,
            intensity=0.7, location="S08W80", mag_type="Beta"
        ),
    ]
    
    return SolarData(
        timestamp=datetime.utcnow(),
        regions=demo_regions,
        solar_flux=142.3,
        xray_class="C2.1",
        xray_flux=2.1e-6,
        solar_wind_speed=385,
        solar_wind_density=4.8,
        kp_index=3,
        active_region_count=len(demo_regions),
        total_sunspot_area=sum(r.area for r in demo_regions),
        carrington_rotation=2290.5
    )

# === API Routes ===

@app.get("/api/solar-data")
async def get_solar_data():
    """Get current solar data from NOAA or cache"""
    # Check cache first
    cached_data = cache.get()
    if cached_data:
        return cached_data
    
    # Fetch new data
    raw_data = await fetch_all_noaa_data()
    
    # Process data or use demo if fetch failed
    if any(raw_data.values()):
        solar_data = process_solar_data(raw_data)
    else:
        print("Using demo data - NOAA unavailable")
        solar_data = generate_demo_data()
    
    # Update cache
    cache.update(solar_data)
    
    return solar_data

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_valid": cache.is_valid()
    }

# === WebSocket for real-time updates ===

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send updates every 30 seconds
            solar_data = await get_solar_data()
            await websocket.send_json(solar_data.dict())
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# === Serve HTML ===

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application"""
    return HTML_CONTENT

# === Background Tasks ===

async def update_cache_task():
    """Periodically update the cache"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            raw_data = await fetch_all_noaa_data()
            if any(raw_data.values()):
                solar_data = process_solar_data(raw_data)
                cache.update(solar_data)
                await manager.broadcast(solar_data.dict())
        except Exception as e:
            print(f"Cache update error: {e}")

@app.on_event("startup")
async def startup():
    """Initialize application"""
    # Start background task
    asyncio.create_task(update_cache_task())
    # Initial data fetch
    await get_solar_data()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
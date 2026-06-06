# Demo: parse NOAA SWPC-style solar region data and plot a "ball of squares" grid
# Notes:
# - Internet access is disabled here, so this notebook uses a tiny built-in sample.
# - The same code path will work with the live JSON if you set OFFLINE_DEMO=False.
#
# What it does:
# 1) Parses region latitude/longitude (heliographic), and optionally central meridian distance (CMD) if present.
# 2) Uses an orthographic projection to place each visible region on a unit solar disk.
# 3) Buckets points into an N x N square grid drawn over the disk and annotates each square with NOAA region IDs.
#
# How to use with live data locally:
#   - Set OFFLINE_DEMO = False
#   - Ensure 'requests' is installed (pip install requests)
#   - Run this cell; it will fetch:
#       https://services.swpc.noaa.gov/json/solar_regions.json
#     Optionally, it can also fetch L0 (Carrington longitude of central meridian) from an ephemeris, but we default to CMD if available.
#
# IMPORTANT plotting rule for this environment:
#   - We use matplotlib (no seaborn), a single plot, and don't set explicit colors.

import math
import json
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# -------- Configuration --------
OFFLINE_DEMO = False   # set to False when you want to fetch the live JSON locally
GRID_SIZE = 20        # number of squares along each axis; try 20–40
SAVE_PATH = Path("solar_regions_grid.png")

# -------- Helper functions --------
def wrap180(angle_deg: float) -> float:
    """Wrap an angle in degrees to [-180, 180)."""
    a = (angle_deg + 180.0) % 360.0 - 180.0
    # Put 180 exactly at -180 for consistency (matplotlib aesthetics)
    if a == 180.0:
        a = -180.0
    return a

def parse_location_str(loc: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse strings like 'N11E29' or 'S17W66' into (lat, cmd) in degrees.
    lat: +N / -S
    cmd: West positive, East negative (convention used by many SRS tables)
    Returns (lat_deg, cmd_deg). Either can be None if parsing fails.
    """
    if not isinstance(loc, str):
        return (None, None)
    loc = loc.strip().upper()
    # Expect formats like N11E29, S09W10, etc.
    try:
        # Split at the latitude part (N/S) then longitude E/W
        if ("N" in loc or "S" in loc) and ("E" in loc or "W" in loc):
            # Find letter indices
            n_idx = loc.find("N")
            s_idx = loc.find("S")
            if n_idx == -1 and s_idx == -1:
                return (None, None)
            lat_sign = 1 if n_idx != -1 else -1
            lat_idx = n_idx if n_idx != -1 else s_idx
            # Remaining part after N## or S##
            i = lat_idx + 1
            # Consume digits for latitude
            j = i
            while j < len(loc) and loc[j].isdigit():
                j += 1
            lat_val = float(loc[i:j]) if i < j else None
            if lat_val is None:
                return (None, None)
            lat = lat_sign * lat_val

            # Next must be E or W
            if j >= len(loc):
                return (lat, None)
            ew = loc[j]
            if ew not in ("E", "W"):
                return (lat, None)
            j += 1
            # digits for CMD
            k = j
            while k < len(loc) and loc[k].isdigit():
                k += 1
            cmd_val = float(loc[j:k]) if j < k else None
            if cmd_val is None:
                return (lat, None)
            # West positive, East negative
            cmd = cmd_val if ew == "W" else -cmd_val
            return (lat, cmd)
    except Exception:
        pass
    return (None, None)

def extract_lat_lon_cmd(rec: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Try to extract heliographic latitude, Carrington longitude, and/or CMD (central meridian distance) from a record.
    Returns (lat_deg, lon_carr_deg, cmd_deg)
    """
    lat = None
    lon = None
    cmd = None

    # Many datasets use keys like 'latitude'/'longitude' (numeric)
    for key in ["latitude", "lat", "Latitude"]:
        if key in rec:
            try:
                lat = float(rec[key])
                break
            except Exception:
                pass

    for key in ["longitude", "lon", "Longitude", "carrington_longitude", "carr_lon"]:
        if key in rec:
            try:
                lon = float(rec[key])
                break
            except Exception:
                pass

    # Some datasets provide CMD (central meridian distance) explicitly (degrees; W positive)
    for key in ["cmd", "CMD", "central_meridian_distance"]:
        if key in rec:
            try:
                cmd = float(rec[key])
                break
            except Exception:
                pass

    # Some provide a "location" like "N11E29"
    if ("location" in rec) and (lat is None or cmd is None):
        lat2, cmd2 = parse_location_str(rec["location"])
        if lat is None:
            lat = lat2
        if cmd is None:
            cmd = cmd2

    return (lat, lon, cmd)

def orthographic_xy(lat_deg: float, dlon_deg: float) -> Tuple[float, float, bool]:
    """
    Project (lat, delta_lon_to_cmeridian) onto a unit disk using an orthographic projection centered on the Earth-facing meridian.
    Returns (x, y, visible_flag)
    """
    lat = math.radians(lat_deg)
    dlon = math.radians(dlon_deg)
    # Visible hemisphere if |dlon| <= 90 degrees
    visible = abs(dlon_deg) <= 90.0
    # Orthographic projection (phi0 = 0 for equatorial view)
    x = math.cos(lat) * math.sin(dlon)
    y = math.sin(lat)
    return x, y, visible

def region_id_from_record(rec: Dict[str, Any]) -> str:
    # Common keys: 'region', 'regionnum', 'region_number', 'noaa_number', 'num'
    for key in ["region", "regionnum", "region_number", "noaa_number", "num", "Number", "Region"]:
        if key in rec:
            try:
                return str(int(rec[key]))
            except Exception:
                return str(rec[key])
    # Fallback to 'id' if present
    if "id" in rec:
        return str(rec["id"])
    return "?"

def to_grid_index(x: float, y: float, n: int) -> Optional[Tuple[int, int]]:
    # Only accept points inside the unit disk
    if x*x + y*y > 1.0:
        return None
    # Map [-1,1] to [0, n)
    gx = int((x + 1.0) / 2.0 * n)
    gy = int((y + 1.0) / 2.0 * n)
    # Clamp to [0, n-1]
    gx = max(0, min(n - 1, gx))
    gy = max(0, min(n - 1, gy))
    return (gx, gy)

def fetch_live_json(url: str) -> List[Dict[str, Any]]:
    import requests
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    data = r.json()
    # Some SWPC endpoints wrap data differently; ensure we return a list of dicts
    if isinstance(data, dict):
        # Try typical container keys
        for k in ["regions", "data", "items"]:
            if k in data and isinstance(data[k], list):
                return data[k]
        # Otherwise make a single-element list
        return [data]
    if isinstance(data, list):
        return data
    return []

# -------- Sample minimal data (for offline demo) --------
sample_regions = [
    # Mimic SRS: 4191 at N11E29, Carrington ~172 (values illustrative)
    {"region": 4191, "location": "N11E29", "longitude": 172},
    {"region": 4193, "location": "S27W16", "longitude": 217},
    {"region": 4194, "location": "N02E13", "longitude": 188},
    {"region": 4195, "location": "S17E54", "longitude": 147},
    {"region": 4196, "location": "S11E64", "longitude": 137},
    {"region": 4188, "location": "S09W10", "longitude": 211},
]

# -------- Main data load --------
if OFFLINE_DEMO:
    records = sample_regions
    L0 = None  # central meridian Carrington longitude; not needed if CMD is available
else:
    # Live data path
    SOLAR_REGIONS_URL = "https://services.swpc.noaa.gov/json/solar_regions.json"
    try:
        records = fetch_live_json(SOLAR_REGIONS_URL)
    except Exception as e:
        print(f"Live fetch failed: {e}")
        print("Falling back to built-in sample...")
        records = sample_regions

    # OPTIONAL: fetch an ephemeris that includes L0 (Carrington longitude of central meridian)
    # If not available, the code will use CMD if present; otherwise regions will be drawn on central meridian.
    L0 = None
    try:
        # One place you might find L0 is an ephemeris feed; this path is illustrative and may change.
        EPHEMERIS_URL = "https://services.swpc.noaa.gov/products/solar-wind/ephemerides.json"
        eph_list = fetch_live_json(EPHEMERIS_URL)
        # Try to take the last entry that has 'l0' or 'carrington_lon'
        for rec in reversed(eph_list):
            for k in ["l0", "L0", "carrington_lon", "carrington_longitude"]:
                if k in rec:
                    try:
                        L0 = float(rec[k])
                        break
                    except Exception:
                        pass
            if L0 is not None:
                break
    except Exception as e:
        # It's okay; we'll fall back to CMD or center
        pass

# -------- Transform to projected points and grid-bucket --------
rows = []
grid_map: Dict[Tuple[int, int], List[str]] = {}
kept = 0
for rec in records:
    lat, lon_carr, cmd = extract_lat_lon_cmd(rec)
    rid = region_id_from_record(rec)

    # If CMD is not provided but both lon and L0 are known, compute CMD = wrap(lon - L0).
    dlon = None
    if cmd is not None:
        dlon = cmd
    elif (lon_carr is not None) and (L0 is not None):
        dlon = wrap180(lon_carr - L0)
    else:
        # Without CMD or L0 we can't determine visibility cleanly; place on central meridian.
        dlon = 0.0

    if lat is None or dlon is None:
        continue

    x, y, visible = orthographic_xy(lat, dlon)
    if not visible:
        # Skip far-side regions for the "ball of squares" view
        continue

    idx = to_grid_index(x, y, GRID_SIZE)
    if idx is None:
        continue
    grid_map.setdefault(idx, []).append(rid)
    kept += 1
    rows.append({"region_id": rid, "lat_deg": lat, "dlon_cmd_deg": dlon, "x": x, "y": y, "tile_x": idx[0], "tile_y": idx[1]})

df = pd.DataFrame(rows)
# Show table interactively (handy when running locally); comment out if noisy
try:
    from caas_jupyter_tools import display_dataframe_to_user
    display_dataframe_to_user("Solar regions projected to grid (visible hemisphere)", df)
except Exception:
    pass

# -------- Plot --------
fig, ax = plt.subplots(figsize=(6, 6))

# Draw the solar disk
circle = plt.Circle((0, 0), 1.0, fill=False, linewidth=1.5)
ax.add_artist(circle)

# Draw the equator and central meridian for reference
ax.axhline(0, linewidth=1, linestyle="--", alpha=0.6)  # solar equator
ax.axvline(0, linewidth=1, linestyle="--", alpha=0.6)  # central meridian

# Draw grid lines
grid_vals = np.linspace(-1, 1, GRID_SIZE + 1)
for g in grid_vals:
    ax.plot([g, g], [-1, 1], linewidth=0.5, alpha=0.4)
    ax.plot([-1, 1], [g, g], linewidth=0.5, alpha=0.4)

# Annotate squares that contain one or more regions
for (gx, gy), ids in grid_map.items():
    # Compute the square center
    x0 = -1 + (gx + 0.5) * (2.0 / GRID_SIZE)
    y0 = -1 + (gy + 0.5) * (2.0 / GRID_SIZE)
    label = ids[0] if len(ids) == 1 else f"{ids[0]}+{len(ids)-1}"
    ax.text(x0, y0, label, ha="center", va="center", fontsize=8)

ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-1.05, 1.05)
ax.set_xticks([])
ax.set_yticks([])
ax.set_title(f"Solar active regions on a {GRID_SIZE}×{GRID_SIZE} grid (visible hemisphere)")

fig.tight_layout()
fig.savefig(SAVE_PATH, dpi=150)

print(f"Saved figure to: {SAVE_PATH}")

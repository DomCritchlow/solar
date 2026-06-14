# Mollweide (long oval) map of NOAA/SWPC solar regions
# - Each 1°×1° heliographic lat/lon cell is a "square" in the grid,
#   filled with the number of spots (numspot) in that cell.
# - Live mode fetches https://services.swpc.noaa.gov/json/solar_regions.json
#   and tries to be robust to slightly different key names.
#
# IMPORTANT (for you to run locally):
#   - In this environment, internet is disabled. Set OFFLINE_DEMO=False
#     on your own machine to fetch the live JSON.
#   - pip install requests numpy matplotlib pandas
#
# Plotting rules (per your environment constraints):
#   - matplotlib only (no seaborn)
#   - single plot (no subplots)
#   - no explicit color choices

import json
import math
from typing import Dict, Any, Tuple, Optional, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ----------------- Config -----------------
OFFLINE_DEMO = False   # set to False when you run this locally
SAVE_PATH = Path("solar_regions_mollweide.png")

# ----------------- Helpers -----------------
def wrap180(lon_deg: float) -> float:
    """Wrap angle to [-180, 180)."""
    a = (lon_deg + 180.0) % 360.0 - 180.0
    return -180.0 if a == 180.0 else a

def parse_location_str(loc: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Parse 'N11E29' or 'S17W66' -> (lat_deg, CMD_deg).
    CMD: West positive, East negative (common SRS convention).
    """
    if not isinstance(loc, str):
        return (None, None)
    s = loc.strip().upper()
    try:
        # Find N/S
        n_idx, s_idx = s.find("N"), s.find("S")
        if n_idx == -1 and s_idx == -1:
            return (None, None)
        lat_sign = 1 if n_idx != -1 else -1
        i = n_idx if n_idx != -1 else s_idx
        # digits after N/S
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        lat = float(s[i+1:j]) * lat_sign if j > i+1 else None
        if j >= len(s):
            return (lat, None)
        ew = s[j]
        if ew not in ("E", "W"):
            return (lat, None)
        k = j + 1
        while k < len(s) and s[k].isdigit():
            k += 1
        cmd = float(s[j+1:k]) if k > j+1 else None
        if cmd is None:
            return (lat, None)
        cmd = cmd if ew == "W" else -cmd
        return (lat, cmd)
    except Exception:
        return (None, None)

def fetch_solar_regions() -> List[Dict[str, Any]]:
    if OFFLINE_DEMO:
        # A tiny sample that mirrors the SRS style.
        return [
            {"region": 4191, "location": "N12W13", "longitude": 174, "area": 400, "extent": 12, "class": "EHI", "numspot": 13, "magclass": "B"},
            {"region": 4197, "location": "S17E30", "longitude": 131, "area": 720, "extent": 13, "class": "EKI", "numspot": 29, "magclass": "BG"},
            {"region": 4200, "location": "S08W14", "longitude": 175, "area": 40,  "extent": 5,  "class": "DAI", "numspot": 11, "magclass": "B"},
            {"region": 4199, "location": "N04E45", "longitude": 116, "area": 170, "extent": 5,  "class": "CAO", "numspot": 9,  "magclass": "B"},
            {"region": 4201, "location": "S21E44", "longitude": 117, "area": 100, "extent": 9,  "class": "DSI", "numspot": 7,  "magclass": "B"},
            {"region": 4188, "location": "S09W50", "longitude": 211, "area": 30,  "extent": 1,  "class": "HSX", "numspot": 1,  "magclass": "A"},
        ]
    else:
        import requests
        url = "https://services.swpc.noaa.gov/json/solar_regions.json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            # Sometimes wrapped
            for k in ("regions", "data", "items"):
                if k in data and isinstance(data[k], list):
                    return data[k]
            return [data]
        return data if isinstance(data, list) else []

def get_val(d: Dict[str, Any], keys: List[str], default=None):
    for k in keys:
        if k in d:
            return d[k]
    return default

def coerce_float(x) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def coerce_int(x) -> Optional[int]:
    try:
        return int(x)
    except Exception:
        try:
            f = float(x)
            return int(round(f))
        except Exception:
            return None

def extract_fields(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Return a normalized dict with keys:
       region_id, lat, carr_lon, cmd, numspot, mcintosh, mwilson"""
    out = {}

    # region id
    rid = get_val(rec, ["region", "regionnum", "region_number", "noaa_number", "num", "Number", "Region", "id"])
    out["region_id"] = str(rid) if rid is not None else "?"

    # latitude
    lat = None
    for key in ["latitude", "lat", "Latitude"]:
        lat = coerce_float(rec.get(key))
        if lat is not None:
            break

    # carrington longitude
    carr_lon = None
    for key in ["longitude", "lon", "Longitude", "carrington_longitude", "carr_lon", "Long", "long"]:
        carr_lon = coerce_float(rec.get(key))
        if carr_lon is not None:
            break

    # CMD (West positive)
    cmd = None
    for key in ["cmd", "CMD", "central_meridian_distance"]:
        cmd = coerce_float(rec.get(key))
        if cmd is not None:
            break

    # Parse 'location' like N11E29 to fill in lat/CMD if missing
    if ("location" in rec) and (lat is None or cmd is None):
        plat, pcmd = parse_location_str(str(rec["location"]))
        if lat is None:
            lat = plat
        if cmd is None:
            cmd = pcmd

    # number of spots
    numspot = None
    for key in ["numspot", "numspots", "spot_count", "spots", "spotnum", "spot_count_total"]:
        numspot = coerce_int(rec.get(key))
        if numspot is not None:
            break
    if numspot is None:
        numspot = 1  # sensible default

    # McIntosh 3-letter class (e.g., EKI, HSX)
    mcintosh = get_val(rec, ["class", "mcintosh", "mcintosh_class", "sunspot_class"], default=None)
    if isinstance(mcintosh, (list, tuple)):
        mcintosh = mcintosh[0] if mcintosh else None

    # Mount Wilson magnetic class (e.g., A, B, BG, BGD, BD, etc.)
    mwilson = get_val(rec, ["magclass", "mag_class", "magnetic_class", "mw_class"], default=None)

    out.update(dict(lat=lat, carr_lon=carr_lon, cmd=cmd, numspot=numspot, mcintosh=mcintosh, mwilson=mwilson))
    return out

# ----------------- Load data -----------------
records = fetch_solar_regions()
norm = [extract_fields(r) for r in records]
df = pd.DataFrame(records)
df.to_csv("parsed_solar_regions.csv")
df = pd.DataFrame(norm)

# Heuristic: prefer Carrington longitude when present; otherwise try to estimate from CMD by centering on 0°
# (For a full 360° map, Carrington longitude is ideal. Most SWPC region feeds include it.)
def estimate_carr_lon(row) -> Optional[float]:
    if not np.isnan(row.get("carr_lon", np.nan)):
        return row["carr_lon"]
    # As a last resort, put CMD on central meridian (0°) which collapses all to 0-based longitudes;
    # this is only a placeholder if Carrington longitude is really missing.
    cmd = row.get("cmd", None)
    if cmd is None or np.isnan(cmd):
        return None
    # map CMD [-90, 90] to around 0; keep it wrapped
    return wrap180(cmd)

df["carr_lon_est"] = df.apply(estimate_carr_lon, axis=1)
# drop rows without lat or carr_lon_est
df = df.dropna(subset=["lat", "carr_lon_est"]).copy()
# Wrap Carrington longitude to [-180, 180)
df["lon_wrap"] = df["carr_lon_est"].map(wrap180)

# ----------------- Build a 1° grid and aggregate numspot -----------------
lon_edges = np.arange(-180.5, 180.5 + 1e-9, 1.0)  # 361 edges => 360 cells
lat_edges = np.arange(-90.5,  90.5  + 1e-9, 1.0)  # 181 edges => 180 cells

# bins counts
grid = np.zeros((len(lat_edges) - 1, len(lon_edges) - 1), dtype=float)

# For optional text overlay (IDs and numspots per cell)
cell_ids: Dict[Tuple[int, int], List[str]] = {}

for _, r in df.iterrows():
    lat = float(r["lat"])
    lon = float(r["lon_wrap"])
    ns  = int(r["numspot"]) if not np.isnan(r["numspot"]) else 0
    # nearest integer degree
    lat_bin_center = int(round(lat))
    lon_bin_center = int(round(lon))
    # convert to index
    lat_idx = lat_bin_center + 90     # [-90..+90] -> [0..180]
    lon_idx = lon_bin_center + 180    # [-180..+180] -> [0..360]
    # clamp to grid
    lat_idx = max(0, min(grid.shape[0]-1, lat_idx))
    lon_idx = max(0, min(grid.shape[1]-1, lon_idx))
    grid[lat_idx, lon_idx] += ns
    cell_ids.setdefault((lat_idx, lon_idx), []).append(str(r["region_id"]))

# ----------------- Mollweide plot -----------------
fig = plt.figure(figsize=(9, 5))
ax = fig.add_subplot(111, projection="mollweide")

# pcolormesh expects radians
LON, LAT = np.meshgrid(np.radians(lon_edges[:-1] + 0.5), np.radians(lat_edges[:-1] + 0.5))
# Use nearest shading so each cell looks "blocky"
pm = ax.pcolormesh(LON, LAT, grid, shading="nearest")

# Add a colorbar (default colormap)
cbar = fig.colorbar(pm, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label("Numspot per 1°×1° cell")

# Grid lines & labels
ax.grid(True)
ax.set_title("NOAA/SWPC Solar Regions — 1°×1° Mollweide Grid\n(cell value = sunspot count per cell)")

# Optional: draw numeric labels for non-zero cells (kept conservative to avoid clutter)
# You can comment this block out if it gets too busy.
for (lat_i, lon_i), ids in list(cell_ids.items()):
    val = int(grid[lat_i, lon_i])
    if val <= 0:
        continue
    # Only label if the array is small enough to be readable. Tune threshold if needed.
    if len(cell_ids) <= 250:
        # center of that bin (degrees -> radians)
        lon_center = np.radians(lon_i - 180 + 0.0)
        lat_center = np.radians(lat_i - 90 + 0.0)
        ax.text(lon_center, lat_center, str(val), ha="center", va="center", fontsize=6)

fig.tight_layout()
fig.savefig(SAVE_PATH, dpi=150)

print(f"Saved Mollweide grid to: {SAVE_PATH}")
print("A preview DataFrame of parsed fields:")
print(df[["region_id","lat","carr_lon_est","numspot","mcintosh","mwilson"]].head(12))

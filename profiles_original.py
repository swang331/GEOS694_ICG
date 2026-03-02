#!/usr/bin/env python3
"""
G2S JSON -> profiles (T, U, V, density, pressure) + effective sound speed
Y-axis now in meters

Outputs next to the JSON:
  - <stem>_profiles.csv (includes z in km and m, plus c0 and cEff)
  - <stem>_T_profile.png, _U_profile.png, _V_profile.png, _rho_profile.png, _P_profile.png
  - <stem>_cEff_alpha<deg>profile.png
"""

# User config
JSON_PATH  = r"/Users/serinawang/Desktop/g2s_2023-10-18.json"
ALPHA_DEG  = 0.0   # 0=E, 90=N, 180=W, 270=S
GAMMA      = 1.4    # Common air value
R_DRY      = 287.0  # Specific dry air constant J/kg K

import json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import cos, sin, radians

def load_g2s_json(path: Path):
    with open(path, "r") as f:
        raw = json.load(f)
    data_map = {e.get("parameter"): {"units": e.get("units"), "values": e.get("values")}
                for e in raw.get("data", []) if e.get("parameter")}
    return {"meta": raw.get("metadata", {}), "data": data_map}

def extract_df(g2s: dict):
    d = g2s["data"]

    Z0_km = float(d["Z0"]["values"][0])                  # km
<<<<<<< HEAD
    Z_km  = np.asarray(d["Z"]["values"], dtype=float)    # km AGL

    df = pd.DataFrame({
        "z_agl_km": Z_km,
        "z_msl_km": Z_km + Z0_km,
=======
    Z_km  = np.asarray(d["Z"]["values"], dtype=float)    # km above ground level (AGL)

    df = pd.DataFrame({
        "z_agl_km": Z_km,
        "z_msl_km": Z_km + Z0_km,   # MSL = mean sea level
>>>>>>> 5cc2330 (fixde variable names to be more intuitive)
        "T_K":       np.asarray(d["T"]["values"], dtype=float),
        "U_ms":      np.asarray(d["U"]["values"], dtype=float),
        "V_ms":      np.asarray(d["V"]["values"], dtype=float),
        "rho_g_cm3": np.asarray(d["R"]["values"], dtype=float),
        "P_mbar":    np.asarray(d["P"]["values"], dtype=float),
    })

    df["z_agl_m"] = df["z_agl_km"] * 1000.0
    df["z_msl_m"] = df["z_msl_km"] * 1000.0

    df["rho_kg_m3"] = df["rho_g_cm3"] * 1000.0   # 1 g/cm^3 = 1000 kg/m^3
    df["P_Pa"]      = df["P_mbar"]    * 100.0    # 1 mbar = 100 Pa
    return df

def compute_sound_speeds(df: pd.DataFrame, alpha_deg: float) -> pd.DataFrame:
    df["c0_ms"]   = np.sqrt(GAMMA * R_DRY * df["T_K"].to_numpy())
    a             = radians(alpha_deg)
    df["cEff_ms"] = df["c0_ms"] + (df["U_ms"] * sin(a) + df["V_ms"] * cos(a))
    return df

def save_csv(df: pd.DataFrame, out_csv: Path):
    cols = [
        "z_agl_km","z_msl_km","z_agl_m","z_msl_m",
        "T_K","U_ms","V_ms",
        "rho_g_cm3","rho_kg_m3",
        "P_mbar","P_Pa",
        "c0_ms","cEff_ms",
    ]
    df.to_csv(out_csv, index=False, float_format="%.8g", columns=cols)

def plot_profile(x, z_m, xlabel, out_png):
    plt.figure(figsize=(4, 6))
    plt.plot(x, z_m)
    plt.xlabel(xlabel)
    plt.ylabel("Height (m)")
    plt.grid(True, linestyle=":", linewidth=0.6)
    plt.tight_layout()
    plt.ylim(0, 10000)
    plt.savefig(out_png, dpi=200)
    plt.show()

def main():
    in_path = Path(JSON_PATH).expanduser().resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    g2s = load_g2s_json(in_path)
    df  = extract_df(g2s)
    df  = compute_sound_speeds(df, ALPHA_DEG)

    stem   = in_path.with_suffix("")
    outdir = stem.parent
    out_csv = outdir / f"{stem.name}_profiles.csv"
    save_csv(df, out_csv)

    # Plots (y in meters)
    plot_profile(df["T_K"].values,       df["z_agl_m"].values, "Temperature (K)",      outdir / f"{stem.name}_T_profile.png")
    plot_profile(df["U_ms"].values,      df["z_agl_m"].values, "Zonal wind U (m/s)",   outdir / f"{stem.name}_U_profile.png")
    plot_profile(df["V_ms"].values,      df["z_agl_m"].values, "Meridional wind V (m/s)", outdir / f"{stem.name}_V_profile.png")
    plot_profile(df["rho_kg_m3"].values, df["z_agl_m"].values, "Density (kg/m³)",      outdir / f"{stem.name}_rho_profile.png")
    plot_profile(df["P_Pa"].values,      df["z_agl_m"].values, "Pressure (Pa)",        outdir / f"{stem.name}_P_profile.png")

    adeg_str = str(int(round(ALPHA_DEG))) if abs(ALPHA_DEG - round(ALPHA_DEG)) < 1e-6 else f"{ALPHA_DEG:g}"
    plot_profile(df["cEff_ms"].values,   df["z_agl_m"].values, f"c_eff (m/s) @ α={adeg_str}°", outdir / f"{stem.name}_cEff_alpha{adeg_str}deg_profile.png")

    meta = g2s.get("meta", {})
    tstr = meta.get("time", {}).get("datetime", "unknown time")
    loc  = meta.get("location", {})
    print(f"Wrote {out_csv}")
    print(f"Time: {tstr}  Location: lat {loc.get('latitude')}, lon {loc.get('longitude')}")
    print(df[["z_agl_m","c0_ms","cEff_ms"]].describe())

if __name__ == "__main__":
    main()
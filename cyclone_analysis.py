"""
Cyclone Return Period Analysis

Author: Jagannath Ghosh
Description:
This script computes cyclone intensity return periods using ERA5 ensemble
and IMD observations with spatial filtering via haversine distance.

Key Features:
- Ensemble uncertainty estimation
- Observed vs modeled comparison
- Extreme value statistics
Acknowledgement: Dr. Jonathan Lin (Cornell University)
"""

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# 📍 LOCATION
clat = 22.13
clon = 86.33

#  HAVERSINE

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return 6371 * c

# ================== MODEL ==========================

folder_path = r"data\era5 Jonathan"
fn_list = glob.glob(os.path.join(folder_path, "*.nc"))

ds = xr.open_mfdataset(fn_list, concat_dim='ensemble', combine='nested')

# Distance filter
dists = haversine(clon, clat, ds['lon_trks'], ds['lat_trks']).load()
vmax_at_poi = ds['vmax_trks'].where(dists <= 100).max(dim='time').load()

# Bins
vmax_bins = np.arange(10, 81, 5)
vmax_bins_knots = vmax_bins * 1.94384

total_years_model = len(ds['year']) * len(ds['ensemble'])

vmax_flat = vmax_at_poi.data.flatten()
vmax_flat = vmax_flat[~np.isnan(vmax_flat)]

exceedance = []
for v in vmax_bins:
    exceedance.append(np.sum(vmax_flat >= v))

exceedance = np.array(exceedance, dtype=float)
exceedance[exceedance == 0] = np.nan

rp_model = total_years_model / exceedance

all_curves = []

for e in range(len(ds['ensemble'])):
    vmax_e = vmax_at_poi.isel(ensemble=e).values.flatten()
    vmax_e = vmax_e[~np.isnan(vmax_e)]

    exc = []
    for v in vmax_bins:
        exc.append(np.sum(vmax_e >= v))

    exc = np.array(exc, dtype=float)
    exc[exc == 0] = np.nan

    rp_e = len(ds['year']) / exc
    all_curves.append(rp_e)

all_curves = np.array(all_curves)

# Percentiles
rp_5 = np.nanpercentile(all_curves, 5, axis=0)
rp_95 = np.nanpercentile(all_curves, 95, axis=0)

# ================== OBSERVED (IMD Excel) ==================

excel_file = r"data\cyclone IMD.xlsx"
xls = pd.ExcelFile(excel_file)

all_obs_max = []

for sheet in xls.sheet_names:

    df = pd.read_excel(excel_file, sheet_name=sheet, header=None)

    # Basin filter
    df[1] = df[1].astype(str).str.strip().str.upper()
    df = df[df[1] == 'BOB']

    # Numeric conversion
    df[5] = pd.to_numeric(df[5], errors='coerce')   # lat
    df[6] = pd.to_numeric(df[6], errors='coerce')   # lon
    df[9] = pd.to_numeric(df[9], errors='coerce')   # wind

    df = df.dropna(subset=[5,6,9])

    # Distance filter
    d = haversine(clon, clat, df[6], df[5])
    df = df[d <= 300]

    # Max per storm
    storm_max = df.groupby(0)[9].max()
    all_obs_max.extend(storm_max.values)

all_obs_max = np.array(all_obs_max)
all_obs_max = all_obs_max[~np.isnan(all_obs_max)]

# ================================
# CORRECT ANNUAL NORMALIZATION
# ================================
total_years_obs = len(xls.sheet_names)
total_storms_obs = len(all_obs_max)

lambda_rate = total_storms_obs / total_years_obs  # storms/year
vmax_bins_obs = vmax_bins_knots
exceedance_obs = []
for v in vmax_bins_obs:
    exceedance_obs.append(np.sum(all_obs_max >= v))
exceedance_obs = np.array(exceedance_obs, dtype=float)
exceedance_obs[exceedance_obs == 0] = np.nan
rp_obs = total_years_obs / (exceedance_obs / lambda_rate)


plt.figure(figsize=(7,5))

for e in range(len(all_curves)):
    plt.plot(vmax_bins_knots, np.log(all_curves[e]),
             color='gray', alpha=0.3)
plt.plot(vmax_bins_knots, np.log(rp_5),
         color='green', linewidth=3, label='5th Percentile')
plt.plot(vmax_bins_knots, np.log(rp_95),
         color='red', linewidth=3, label='95th Percentile')

plt.plot(vmax_bins_knots, np.log(rp_model),
         color='black', linewidth=3, label='Modeled Risk')

plt.plot(vmax_bins_knots, np.log(rp_obs),
         'k--', linewidth=3, label='Observed (Corrected)')

plt.yticks(np.log([2,5,10,20,30,50,100]),
           [2,5,10,20,30,50,100])

plt.xlabel('Intensity (knots)')
plt.ylabel('Return Period (years)')
plt.title('Cyclone Return Period: Model vs Observed (BOB)')

plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()

plt.ylim(np.log(2), np.log(100))
plt.xlim(40, 150)

plt.show()

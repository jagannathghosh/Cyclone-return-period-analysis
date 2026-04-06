# Cyclone-return-period-analysis
Cyclone return period analysis using ERA5 ensemble data and IMD observations

This project estimates cyclone intensity return periods using ERA5 ensemble cyclone track data and IMD observed cyclone data over the Bay of Bengal region.

Study Location

Latitude: 22.13
Longitude: 86.33

Objectives
Estimate cyclone intensity return periods
Compare modeled vs observed cyclone risk
Quantify uncertainty using ensemble simulations
Apply spatial filtering using haversine distance
Methodology
Used haversine distance to filter cyclones near the location
Extracted maximum wind speed (Vmax) per cyclone
Computed exceedance counts for different intensity bins
Estimated return period using total years and exceedance
Applied ensemble-based uncertainty (5th and 95th percentile)
Corrected observed data using annual storm rate
Output
Return period curves (log scale)
Model vs observed comparison
Ensemble uncertainty range
Project Structure

cyclone-return-period-analysis/
│── cyclone_analysis.py
│── README.md


Requirements

Install dependencies using:
pip install -r requirements.txt

Libraries used:
xarray
pandas
numpy
matplotlib
netCDF4
openpyxl

How to Run
Update file paths in the script:
folder_path = "data/era5/"
excel_file = "data/cyclone_IMD.xlsx"
Run the script:
python cyclone_analysis.py
Data

ERA5 cyclone track data (NetCDF)
IMD cyclone dataset (Excel)

Note: Data is not included due to size limitations

Applications
Climate risk analysis
Disaster management
Extreme weather assessment
Infrastructure planning
Author

Jagannath Ghosh
BSMS, IISER Berhampur

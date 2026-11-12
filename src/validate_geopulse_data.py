
import pandas as pd
from pathlib import Path

project_path = Path(__file__).resolve().parent.parent

gps_file = project_path / "data" / "raw_gps_pings.csv"
store_file = project_path / "data" / "store_locations.csv"

gps_df = pd.read_csv(gps_file)
store_df = pd.read_csv(store_file)

print("GEOPULSE DATA VALIDATION")
print("=" * 40)

print("\nGPS DATA")
print("Total GPS Records:", len(gps_df))
print("Unique Devices:", gps_df["DeviceID"].nunique())
print("Missing Values:", gps_df.isnull().sum().sum())
print("Duplicate Rows:", gps_df.duplicated().sum())

print("\nSTORE DATA")
print("Total Stores:", len(store_df))
print("Missing Values:", store_df.isnull().sum().sum())
print("Duplicate Rows:", store_df.duplicated().sum())

valid_gps = (
    gps_df["Latitude"].between(-90, 90)
    & gps_df["Longitude"].between(-180, 180)
)

valid_stores = (
    store_df["Latitude"].between(-90, 90)
    & store_df["Longitude"].between(-180, 180)
)

print("\nLOCATION VALIDATION")
print("Valid GPS Coordinates:", valid_gps.sum())
print("Invalid GPS Coordinates:", (~valid_gps).sum())
print("Valid Store Coordinates:", valid_stores.sum())
print("Invalid Store Coordinates:", (~valid_stores).sum())

print("\nDATA PREVIEW")
print(gps_df.head())
print("\n")
print(store_df.head())

print("\nValidation completed!")

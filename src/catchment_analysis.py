
import pandas as pd
import numpy as np
from pathlib import Path

project_path = Path(__file__).resolve().parent.parent

gps_df = pd.read_csv(project_path / "data" / "raw_gps_pings.csv")
store_df = pd.read_csv(project_path / "data" / "store_locations.csv")

EARTH_RADIUS = 6371000
CATCHMENT_RADIUS = 500

gps_lat = np.radians(gps_df["Latitude"].to_numpy())
gps_lon = np.radians(gps_df["Longitude"].to_numpy())

store_lat = np.radians(store_df["Latitude"].to_numpy())
store_lon = np.radians(store_df["Longitude"].to_numpy())

lat_diff = gps_lat[:, None] - store_lat[None, :]
lon_diff = gps_lon[:, None] - store_lon[None, :]

a = (
    np.sin(lat_diff / 2) ** 2
    + np.cos(gps_lat[:, None])
    * np.cos(store_lat[None, :])
    * np.sin(lon_diff / 2) ** 2
)

distances = 2 * EARTH_RADIUS * np.arcsin(np.sqrt(a))

nearest_indices = np.argmin(distances, axis=1)
nearest_distances = distances[
    np.arange(len(gps_df)), nearest_indices
]

gps_df["Nearest_Store_ID"] = (
    store_df.iloc[nearest_indices]["StoreID"].to_numpy()
)

gps_df["Nearest_Store_Distance_M"] = np.round(
    nearest_distances, 2
)

gps_df["Within_500m"] = nearest_distances <= CATCHMENT_RADIUS

gps_df["Catchment_Store_ID"] = np.where(
    gps_df["Within_500m"],
    gps_df["Nearest_Store_ID"],
    "Outside"
)

summary = []

for _, store in store_df.iterrows():
    store_pings = gps_df[
        (gps_df["Catchment_Store_ID"] == store["StoreID"])
    ]

    summary.append({
        "StoreID": store["StoreID"],
        "StoreName": store["StoreName"],
        "GPS_Pings_Within_500m": len(store_pings),
        "Unique_Devices_Within_500m":
            store_pings["DeviceID"].nunique()
    })

summary_df = pd.DataFrame(summary)

output_folder = project_path / "data"
output_folder.mkdir(exist_ok=True)

gps_df.to_csv(
    output_folder / "gps_store_distances.csv",
    index=False
)

summary_df.to_csv(
    output_folder / "store_catchment_summary.csv",
    index=False
)

print("GEOPULSE CATCHMENT ANALYSIS")
print("=" * 45)

print("Total GPS Records:", len(gps_df))
print("Total Stores:", len(store_df))
print("Catchment Radius:", CATCHMENT_RADIUS, "meters")
print("GPS Pings Within 500m:", gps_df["Within_500m"].sum())
print(
    "GPS Pings Outside 500m:",
    (~gps_df["Within_500m"]).sum()
)

print("\nSTORE CATCHMENT SUMMARY")
print(summary_df.to_string(index=False))

print("\nFiles generated successfully!")

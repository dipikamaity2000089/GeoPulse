
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

STORES_FILE = RAW_DIR / "store_metadata.csv"
COMPETITORS_FILE = RAW_DIR / "competitor_locations.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

stores = pd.read_csv(STORES_FILE)
competitors = pd.read_csv(COMPETITORS_FILE)

def find_column(df, candidates):
    for name in candidates:
        if name in df.columns:
            return name
    raise ValueError(
        f"Could not find any of {candidates}. "
        f"Available columns: {list(df.columns)}"
    )

store_id_col = find_column(stores, ["Store_ID", "store_id"])
competitor_id_col = find_column(
    competitors, ["Competitor_ID", "competitor_id"]
)

store_lat_col = find_column(stores, ["Latitude", "latitude", "Lat", "lat"])
store_lon_col = find_column(stores, ["Longitude", "longitude", "Lon", "lon"])

competitor_lat_col = find_column(
    competitors, ["Latitude", "latitude", "Lat", "lat"]
)
competitor_lon_col = find_column(
    competitors, ["Longitude", "longitude", "Lon", "lon"]
)

def haversine(lat1, lon1, lat2, lon2):
    earth_radius = 6371.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return earth_radius * c

print("=" * 60)
print("GEOPULSE SPATIAL ANALYSIS")
print("=" * 60)

print(f"Stores loaded: {len(stores)}")
print(f"Competitors loaded: {len(competitors)}")

# 1. COMPETITOR PROXIMITY ANALYSIS

competitor_results = []

for _, store in stores.iterrows():
    distances = haversine(
        store[store_lat_col],
        store[store_lon_col],
        competitors[competitor_lat_col].to_numpy(),
        competitors[competitor_lon_col].to_numpy()
    )

    nearest_index = np.argmin(distances)

    competitor_results.append({
        "Store_ID": store[store_id_col],
        "Nearest_Competitor_ID": competitors.iloc[nearest_index][competitor_id_col],
        "Nearest_Competitor_Distance_KM": round(float(distances[nearest_index]), 3),
        "Competitors_Within_1_KM": int(np.sum(distances <= 1)),
        "Competitors_Within_3_KM": int(np.sum(distances <= 3)),
        "Competitors_Within_5_KM": int(np.sum(distances <= 5))
    })

competitor_proximity = pd.DataFrame(competitor_results)

competitor_proximity = competitor_proximity.sort_values(
    "Nearest_Competitor_Distance_KM"
)

competitor_proximity.to_csv(
    PROCESSED_DIR / "competitor_proximity_analysis.csv",
    index=False
)

# 2. STORE-TO-STORE PROXIMITY ANALYSIS

store_results = []

for i in range(len(stores)):
    store_a = stores.iloc[i]

    for j in range(i + 1, len(stores)):
        store_b = stores.iloc[j]

        distance = haversine(
            store_a[store_lat_col],
            store_a[store_lon_col],
            store_b[store_lat_col],
            store_b[store_lon_col]
        )

        store_results.append({
            "Store_A": store_a[store_id_col],
            "Store_B": store_b[store_id_col],
            "Distance_KM": round(float(distance), 3)
        })

store_distances = pd.DataFrame(store_results)

store_distances = store_distances.sort_values("Distance_KM")

store_distances.to_csv(
    PROCESSED_DIR / "store_spatial_distances.csv",
    index=False
)

# 3. STORE DENSITY ANALYSIS

density_results = []

for _, store in stores.iterrows():
    distances = haversine(
        store[store_lat_col],
        store[store_lon_col],
        stores[store_lat_col].to_numpy(),
        stores[store_lon_col].to_numpy()
    )

    other_stores = stores[store_id_col] != store[store_id_col]

    density_results.append({
        "Store_ID": store[store_id_col],
        "Stores_Within_1_KM": int(np.sum((distances <= 1) & other_stores)),
        "Stores_Within_3_KM": int(np.sum((distances <= 3) & other_stores)),
        "Stores_Within_5_KM": int(np.sum((distances <= 5) & other_stores))
    })

store_density = pd.DataFrame(density_results)

store_density = store_density.sort_values(
    "Stores_Within_3_KM", ascending=False
)

store_density.to_csv(
    PROCESSED_DIR / "store_density_analysis.csv",
    index=False
)

# SUMMARY

print("\nCLOSEST STORE-COMPETITOR PAIRS")
print(competitor_proximity.head(10).to_string(index=False))

print("\nSTORES WITH HIGHEST COMPETITOR CONCENTRATION")
print(
    competitor_proximity.sort_values(
        "Competitors_Within_3_KM", ascending=False
    ).head(10).to_string(index=False)
)

print("\nCLOSEST STORE-TO-STORE PAIRS")
print(store_distances.head(10).to_string(index=False))

print("\nHIGHEST STORE DENSITY")
print(store_density.head(10).to_string(index=False))

print("\nOUTPUT FILES CREATED")
print("1. competitor_proximity_analysis.csv")
print("2. store_spatial_distances.csv")
print("3. store_density_analysis.csv")

print("\nSPATIAL ANALYSIS COMPLETED")

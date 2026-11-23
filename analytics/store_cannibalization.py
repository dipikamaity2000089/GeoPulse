import pandas as pd
import numpy as np
from pathlib import Path
from itertools import combinations

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

visits = pd.read_csv(RAW_DIR / "store_visits.csv")
stores = pd.read_csv(RAW_DIR / "store_metadata.csv")

print("=" * 65)
print("GEOPULSE — STORE CANNIBALIZATION ANALYSIS")
print("=" * 65)

# 1. Prepare store visitor profiles

store_visitors = (
    visits.groupby("Store_ID")["Device_ID"]
    .apply(set)
    .to_dict()
)

store_visit_counts = (
    visits.groupby("Store_ID")
    .size()
    .to_dict()
)

store_info = stores.set_index("Store_ID").to_dict("index")

# 2. Distance calculation using the Haversine formula

def calculate_distance_km(lat1, lon1, lat2, lon2):
    earth_radius = 6371.0

    lat1, lon1, lat2, lon2 = np.radians(
        [lat1, lon1, lat2, lon2]
    )

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2)
        * np.sin(delta_lon / 2) ** 2
    )

    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return earth_radius * c

# 3. Compare pairs of stores

results = []

store_ids = list(store_visitors.keys())

MAX_DISTANCE_KM = 3.0

for store_a, store_b in combinations(store_ids, 2):

    info_a = store_info[store_a]
    info_b = store_info[store_b]

    distance = calculate_distance_km(
        info_a["Latitude"],
        info_a["Longitude"],
        info_b["Latitude"],
        info_b["Longitude"]
    )

    if distance > MAX_DISTANCE_KM:
        continue

    visitors_a = store_visitors[store_a]
    visitors_b = store_visitors[store_b]

    shared_visitors = visitors_a.intersection(visitors_b)
    union_visitors = visitors_a.union(visitors_b)

    shared_count = len(shared_visitors)
    visitors_a_count = len(visitors_a)
    visitors_b_count = len(visitors_b)

    jaccard_overlap = (
        shared_count / len(union_visitors)
        if union_visitors else 0
    )

    overlap_a = (
        shared_count / visitors_a_count * 100
        if visitors_a_count else 0
    )

    overlap_b = (
        shared_count / visitors_b_count * 100
        if visitors_b_count else 0
    )

    results.append({
        "Store_A": store_a,
        "Store_A_Name": info_a["Store_Name"],
        "Store_A_Category": info_a["Store_Category"],
        "Store_B": store_b,
        "Store_B_Name": info_b["Store_Name"],
        "Store_B_Category": info_b["Store_Category"],
        "Distance_KM": round(distance, 3),
        "Store_A_Visitors": visitors_a_count,
        "Store_B_Visitors": visitors_b_count,
        "Shared_Visitors": shared_count,
        "Jaccard_Overlap_Percent": round(jaccard_overlap * 100, 2),
        "Store_A_Shared_Visitor_Percent": round(overlap_a, 2),
        "Store_B_Shared_Visitor_Percent": round(overlap_b, 2),
        "Store_A_Total_Visits": store_visit_counts.get(store_a, 0),
        "Store_B_Total_Visits": store_visit_counts.get(store_b, 0)
    })

# 4. Build results table

cannibalization_df = pd.DataFrame(results)

if not cannibalization_df.empty:

    cannibalization_df = cannibalization_df.sort_values(
        ["Jaccard_Overlap_Percent", "Shared_Visitors"],
        ascending=False
    )

    cannibalization_df["Overlap_Classification"] = pd.cut(
        cannibalization_df["Jaccard_Overlap_Percent"],
        bins=[-0.01, 10, 25, 50, 100],
        labels=[
            "Low Overlap",
            "Moderate Overlap",
            "High Overlap",
            "Very High Overlap"
        ]
    )

# 5. Save output

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

output_path = PROCESSED_DIR / "store_cannibalization_analysis.csv"

cannibalization_df.to_csv(output_path, index=False)

# 6. Display summary

print(f"\nDistance threshold: {MAX_DISTANCE_KM} km")
print(f"Stores analyzed: {len(store_ids)}")
print(f"Nearby store pairs found: {len(cannibalization_df)}")

if not cannibalization_df.empty:

    print("\nTOP 10 STORE PAIRS BY VISITOR OVERLAP")
    print("-" * 65)

    columns_to_display = [
        "Store_A",
        "Store_B",
        "Distance_KM",
        "Shared_Visitors",
        "Jaccard_Overlap_Percent",
        "Overlap_Classification"
    ]

    print(
        cannibalization_df[columns_to_display]
        .head(10)
        .to_string(index=False)
    )

    print("\nOVERLAP CLASSIFICATION SUMMARY")
    print("-" * 65)

    print(
        cannibalization_df["Overlap_Classification"]
        .value_counts()
        .to_string()
    )

else:
    print("\nNo store pairs found within the selected distance threshold.")

print(f"\nOutput saved: {output_path}")
print("\nCANNIBALIZATION ANALYSIS COMPLETED")
print("=" * 65)

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

WEIGHTS = {
    "Footfall_Score": 0.35,
    "Competitor_Score": 0.25,
    "Density_Score": 0.15,
    "Mobility_Score": 0.15,
    "Accessibility_Score": 0.10
}

stores = pd.read_csv(RAW_DIR / "store_metadata.csv")
visits = pd.read_csv(RAW_DIR / "store_visits.csv")
competitors = pd.read_csv(PROCESSED_DIR / "competitor_proximity_analysis.csv")
density = pd.read_csv(PROCESSED_DIR / "store_density_analysis.csv")
mobility = pd.read_csv(PROCESSED_DIR / "store_transition_analysis.csv")

def percentile_score(series, higher_is_better=True):
    series = pd.to_numeric(series, errors="coerce")
    scores = series.rank(pct=True) * 100

    if not higher_is_better:
        scores = 100 - scores

    return scores.fillna(50).round(2)

def find_column(df, candidates):
    for column in candidates:
        if column in df.columns:
            return column
    return None

store_id = find_column(stores, ["Store_ID", "store_id"])

if store_id is None:
    raise ValueError("Store_ID column not found in store metadata.")

# 1. FOOTFALL SCORE

footfall = visits.groupby("Store_ID").agg(
    Total_Visits=("Visit_ID", "count"),
    Unique_Visitors=("Device_ID", "nunique")
).reset_index()

footfall["Footfall_Score"] = percentile_score(
    footfall["Total_Visits"]
)

# 2. COMPETITOR SCORE

competitors["Competitor_Score"] = percentile_score(
    competitors["Competitors_Within_3_KM"],
    higher_is_better=False
)

# 3. STORE DENSITY SCORE

density["Density_Score"] = percentile_score(
    density["Stores_Within_3_KM"],
    higher_is_better=False
)

# 4. MOBILITY SCORE

mobility_score = mobility.groupby("Store_A").agg(
    Outgoing_Transitions=("Transition_Count", "sum"),
    Mobility_Destinations=("Store_B", "nunique")
).reset_index()

mobility_score = mobility_score.rename(
    columns={"Store_A": "Store_ID"}
)

mobility_score["Mobility_Score"] = percentile_score(
    mobility_score["Outgoing_Transitions"]
)


# 5. ACCESSIBILITY SCORE

transit_col = find_column(
    stores,
    ["Nearby_Transit_Access", "Transit_Access", "Transit_Accessibility"]
)

parking_col = find_column(
    stores,
    ["Parking_Available", "Parking_Availability", "Parking_Access"]
)

accessibility_parts = []

if transit_col:
    accessibility_parts.append(
        stores[transit_col].map({True: 100, False: 0})
    )

if parking_col:
    accessibility_parts.append(
        stores[parking_col].map({True: 100, False: 0})
    )

if accessibility_parts:
    stores["Accessibility_Score"] = pd.concat(
        accessibility_parts, axis=1
    ).mean(axis=1)
else:
    stores["Accessibility_Score"] = 50.0

stores["Accessibility_Score"] = stores[
    "Accessibility_Score"
].fillna(50).round(2)

# 6. MERGE ALL SCORES

recommendations = stores[["Store_ID"]].copy()

recommendations = recommendations.merge(
    footfall[["Store_ID", "Total_Visits", "Unique_Visitors", "Footfall_Score"]],
    on="Store_ID", how="left"
)

recommendations = recommendations.merge(
    competitors[["Store_ID", "Nearest_Competitor_Distance_KM",
                "Competitors_Within_3_KM", "Competitor_Score"]],
    on="Store_ID", how="left"
)

recommendations = recommendations.merge(
    density[["Store_ID", "Stores_Within_3_KM", "Density_Score"]],
    on="Store_ID", how="left"
)

recommendations = recommendations.merge(
    mobility_score[["Store_ID", "Outgoing_Transitions",
                   "Mobility_Destinations", "Mobility_Score"]],
    on="Store_ID", how="left"
)

recommendations["Accessibility_Score"] = stores["Accessibility_Score"].values

score_columns = list(WEIGHTS.keys())

recommendations[score_columns] = recommendations[score_columns].fillna(50)

# 7. WEIGHTED SCORE

recommendations["Weighted_Score"] = sum(
    recommendations[column] * weight
    for column, weight in WEIGHTS.items()
)

recommendations["Weighted_Score"] = recommendations[
    "Weighted_Score"
].round(2)

recommendations = recommendations.sort_values(
    "Weighted_Score", ascending=False
).reset_index(drop=True)

recommendations["Location_Rank"] = range(1, len(recommendations) + 1)

recommendations["Recommendation_Category"] = pd.cut(
    recommendations["Weighted_Score"],
    bins=[-1, 40, 60, 75, 100],
    labels=["Low Potential", "Moderate Potential",
            "Good Potential", "High Potential"]
)

# 8. SAVE RESULTS

recommendations.to_csv(
    PROCESSED_DIR / "store_location_recommendations.csv",
    index=False
)

# 9. DISPLAY RESULTS

print("=" * 65)
print("GEOPULSE STORE LOCATION RECOMMENDATION ENGINE")
print("=" * 65)

print(f"Stores evaluated: {len(recommendations)}")

print("\nSCORING WEIGHTS")
for factor, weight in WEIGHTS.items():
    print(f"{factor:<25} {weight * 100:.0f}%")

print("\nTOP 10 RECOMMENDED STORES")

display_columns = [
    "Location_Rank",
    "Store_ID",
    "Weighted_Score",
    "Recommendation_Category",
    "Footfall_Score",
    "Competitor_Score",
    "Density_Score",
    "Mobility_Score",
    "Accessibility_Score"
]

print(recommendations[display_columns].head(10).to_string(index=False))

print("\nBOTTOM 5 RANKED STORES")

print(recommendations[display_columns].tail(5).to_string(index=False))

print("\nOUTPUT CREATED")
print("store_location_recommendations.csv")

print("\nLOCATION RECOMMENDATION ANALYSIS COMPLETED")

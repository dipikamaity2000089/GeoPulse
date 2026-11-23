import pandas as pd
import numpy as np
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Input files
STORE_FILE = BASE_DIR / "data" / "processed" / "store_locations.csv"
CANDIDATE_FILE = BASE_DIR / "data" / "processed" / "candidate_locations.csv"

# Output directory
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Output file
OUTPUT_FILE = OUTPUT_DIR / "cannibalization_analysis.csv"
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate geographical distance using the Haversine formula.
    Returns distance in kilometres.
    """
    earth_radius_km = 6371.0

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

    return earth_radius_km * c
def calculate_overlap_area(distance, radius1, radius2):
    """
    Calculate the intersection area of two circular catchment zones.
    Returns overlap area in square kilometres.
    """

    # No overlap when circles are separate
    if distance >= radius1 + radius2:
        return 0.0

    # One circle is completely inside the other
    if distance <= abs(radius1 - radius2):
        return np.pi * min(radius1, radius2) ** 2

    # Partial overlap
    part1 = radius1 ** 2 * np.arccos(
        (distance ** 2 + radius1 ** 2 - radius2 ** 2)
        / (2 * distance * radius1)
    )

    part2 = radius2 ** 2 * np.arccos(
        (distance ** 2 + radius2 ** 2 - radius1 ** 2)
        / (2 * distance * radius2)
    )

    part3 = 0.5 * np.sqrt(
        (-distance + radius1 + radius2)
        * (distance + radius1 - radius2)
        * (distance - radius1 + radius2)
        * (distance + radius1 + radius2)
    )

    return part1 + part2 - part3
def load_data():
    print("Loading existing store and candidate datasets...")

    stores = pd.read_csv(STORE_FILE)
    candidates = pd.read_csv(CANDIDATE_FILE)

    # Clean city and category values
    for df in [stores, candidates]:
        df["city"] = df["city"].astype(str).str.strip()

    stores["store_category"] = (
        stores["store_category"].astype(str).str.strip()
    )

    candidates["proposed_store_category"] = (
        candidates["proposed_store_category"].astype(str).str.strip()
    )

    # Validate numeric columns
    store_columns = [
        "latitude", "longitude", "catchment_radius_km"
    ]

    candidate_columns = [
        "latitude", "longitude", "target_catchment_radius_km"
    ]

    for column in store_columns:
        stores[column] = pd.to_numeric(
            stores[column], errors="coerce"
        )

    for column in candidate_columns:
        candidates[column] = pd.to_numeric(
            candidates[column], errors="coerce"
        )

    # Check for missing or invalid values
    if stores[store_columns].isna().any().any():
        raise ValueError("Invalid existing store data found.")

    if candidates[candidate_columns].isna().any().any():
        raise ValueError("Invalid candidate data found.")

    if (stores["catchment_radius_km"] <= 0).any():
        raise ValueError("Invalid existing store catchment radius.")

    if (candidates["target_catchment_radius_km"] <= 0).any():
        raise ValueError("Invalid candidate catchment radius.")

    print(f"Existing stores loaded: {len(stores)}")
    print(f"Candidate locations loaded: {len(candidates)}")

    return stores, candidates
def analyze_cannibalization(stores, candidates):
    print("\nCalculating catchment area overlap...")

    results = []

    for _, candidate in candidates.iterrows():

        # Select existing stores in the same city and category
        matching_stores = stores[
            (stores["city"] == candidate["city"])
            & (
                stores["store_category"].str.lower()
                == candidate["proposed_store_category"].lower()
            )
        ].copy()

        total_overlap_area = 0.0
        overlapping_stores = []

        candidate_radius = float(
            candidate["target_catchment_radius_km"]
        )

        candidate_area = np.pi * candidate_radius ** 2

        for _, store in matching_stores.iterrows():

            distance = calculate_distance(
                candidate["latitude"],
                candidate["longitude"],
                store["latitude"],
                store["longitude"]
            )

            store_radius = float(store["catchment_radius_km"])

            overlap_area = calculate_overlap_area(
                distance,
                candidate_radius,
                store_radius
            )

            if overlap_area > 0:
                overlapping_stores.append({
                    "store_id": store["store_id"],
                    "store_name": store["store_name"],
                    "distance_km": round(distance, 3),
                    "overlap_area_km2": round(overlap_area, 3)
                })

                total_overlap_area += overlap_area

        # Calculate overlap percentage
        overlap_percentage = min(
            (total_overlap_area / candidate_area) * 100,
            100.0
        )

        # Classify potential cannibalization risk
        if overlap_percentage == 0:
            risk = "Low"
        elif overlap_percentage < 25:
            risk = "Moderate"
        elif overlap_percentage < 50:
            risk = "High"
        else:
            risk = "Very High"

        results.append({
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "city": candidate["city"],
            "store_category": candidate["proposed_store_category"],
            "candidate_catchment_radius_km": candidate_radius,
            "existing_same_category_stores": len(matching_stores),
            "overlapping_store_count": len(overlapping_stores),
            "overlap_area_km2": round(total_overlap_area, 3),
            "overlap_percentage": round(overlap_percentage, 2),
            "cannibalization_risk": risk,
            "overlapping_stores": (
                "; ".join(
                    store["store_id"] for store in overlapping_stores
                ) or "No overlapping stores"
            )
        })

    return pd.DataFrame(results)
def main():
    print("=" * 60)
    print("GEOPULSE - STORE CANNIBALIZATION ANALYSIS")
    print("=" * 60)

    stores, candidates = load_data()

    results = analyze_cannibalization(stores, candidates)

    if results.empty:
        raise ValueError("No cannibalization results were generated.")

    # Sort by potential overlap percentage
    results = results.sort_values(
        by="overlap_percentage",
        ascending=False
    )

    # Save analysis results
    results.to_csv(OUTPUT_FILE, index=False)

    print("\nANALYSIS SUMMARY")
    print("-" * 60)
    print(f"Existing stores analysed: {len(stores)}")
    print(f"Candidate locations analysed: {len(results)}")
    print(f"Cities analysed: {results['city'].nunique()}")
    print(
        "Candidates with overlapping stores: "
        f"{(results['overlapping_store_count'] > 0).sum()}"
    )

    print("\nRISK DISTRIBUTION")
    print("-" * 60)
    print(results["cannibalization_risk"].value_counts().to_string())

    print("\nCANNIBALIZATION RESULTS")
    print("-" * 60)

    print(
        results[
            [
                "candidate_id",
                "city",
                "overlapping_store_count",
                "overlap_percentage",
                "cannibalization_risk"
            ]
        ].to_string(index=False)
    )

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
    
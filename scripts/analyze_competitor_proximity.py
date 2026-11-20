import pandas as pd
import numpy as np
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Input files
CANDIDATE_FILE = BASE_DIR / "data" / "processed" / "candidate_locations.csv"
COMPETITOR_FILE = BASE_DIR / "data" / "processed" / "competitor_locations.csv"

# Output directory
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Output file
OUTPUT_FILE = OUTPUT_DIR / "competitor_proximity_analysis.csv"
def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate geographical distance between two coordinates
    using the Haversine formula.
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
def load_data():
    print("Loading candidate and competitor datasets...")

    candidates = pd.read_csv(CANDIDATE_FILE)
    competitors = pd.read_csv(COMPETITOR_FILE)

    # Convert coordinates to numeric values
    coordinate_columns = ["latitude", "longitude"]

    for column in coordinate_columns:
        candidates[column] = pd.to_numeric(
            candidates[column], errors="coerce"
        )
        competitors[column] = pd.to_numeric(
            competitors[column], errors="coerce"
        )

    # Clean city and category names
    candidates["city"] = candidates["city"].astype(str).str.strip()
    competitors["city"] = competitors["city"].astype(str).str.strip()

    candidates["proposed_store_category"] = (
        candidates["proposed_store_category"].astype(str).str.strip()
    )

    competitors["competitor_category"] = (
        competitors["competitor_category"].astype(str).str.strip()
    )

    # Validate coordinates
    if candidates[coordinate_columns].isna().any().any():
        raise ValueError("Invalid candidate coordinates found.")

    if competitors[coordinate_columns].isna().any().any():
        raise ValueError("Invalid competitor coordinates found.")

    print(f"Candidates loaded: {len(candidates)}")
    print(f"Competitors loaded: {len(competitors)}")

    return candidates, competitors
def analyze_proximity(candidates, competitors):
    print("\nCalculating competitor proximity...")

    results = []

    for _, candidate in candidates.iterrows():

        # Select competitors from the same city
        city_competitors = competitors[
            competitors["city"] == candidate["city"]
        ].copy()

        if city_competitors.empty:
            continue

        # Calculate distance from candidate to each competitor
        city_competitors["distance_km"] = city_competitors.apply(
            lambda competitor: calculate_distance(
                candidate["latitude"],
                candidate["longitude"],
                competitor["latitude"],
                competitor["longitude"]
            ),
            axis=1
        )

        # Find the nearest competitor
        nearest = city_competitors.loc[
            city_competitors["distance_km"].idxmin()
        ]

        # Get candidate's catchment radius
        radius = float(candidate["target_catchment_radius_km"])

        # Find competitors within the catchment radius
        nearby = city_competitors[
            city_competitors["distance_km"] <= radius
        ]

        # Count competitors belonging to the same category
        same_category = nearby[
            nearby["competitor_category"].str.lower()
            == candidate["proposed_store_category"].lower()
        ]

        results.append({
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["candidate_name"],
            "city": candidate["city"],
            "proposed_store_category": candidate["proposed_store_category"],
            "catchment_radius_km": radius,
            "nearest_competitor": nearest["competitor_name"],
            "nearest_competitor_category": nearest["competitor_category"],
            "nearest_competitor_distance_km": round(
                nearest["distance_km"], 3
            ),
            "competitors_within_catchment": len(nearby),
            "same_category_competitors": len(same_category),
            "total_competitors_in_city": len(city_competitors)
        })

    return pd.DataFrame(results)
def main():
    print("=" * 60)
    print("GEOPULSE - COMPETITOR PROXIMITY ANALYSIS")
    print("=" * 60)

    candidates, competitors = load_data()

    results = analyze_proximity(candidates, competitors)

    if results.empty:
        raise ValueError("No proximity results were generated.")

    # Sort candidates by nearest competitor distance
    results = results.sort_values(
        by="nearest_competitor_distance_km"
    )

    # Save analysis results
    results.to_csv(OUTPUT_FILE, index=False)

    print("\nANALYSIS SUMMARY")
    print("-" * 60)
    print(f"Candidates analysed: {len(results)}")
    print(f"Competitors available: {len(competitors)}")
    print(f"Cities analysed: {results['city'].nunique()}")
    print(
        "Average nearest competitor distance: "
        f"{results['nearest_competitor_distance_km'].mean():.3f} km"
    )

    print("\nPROXIMITY RESULTS")
    print("-" * 60)

    print(
        results[
            [
                "candidate_id",
                "city",
                "nearest_competitor_distance_km",
                "competitors_within_catchment",
                "same_category_competitors"
            ]
        ].to_string(index=False)
    )

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
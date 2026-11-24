import pandas as pd
import numpy as np
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Input files
CANDIDATE_FILE = BASE_DIR / "data" / "processed" / "candidate_locations.csv"
COMPETITOR_FILE = BASE_DIR / "data" / "processed" / "competitor_proximity_analysis.csv"
CANNIBALIZATION_FILE = BASE_DIR / "data" / "processed" / "cannibalization_analysis.csv"
FOOTFALL_FILE = BASE_DIR / "data" / "processed" / "hourly_footfall_summary.csv"

# Output directory
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Output file
OUTPUT_FILE = OUTPUT_DIR / "store_location_recommendations.csv"
def load_data():
    print("Loading candidate, competitor, cannibalization and footfall datasets...")

    candidates = pd.read_csv(CANDIDATE_FILE)
    competitors = pd.read_csv(COMPETITOR_FILE)
    cannibalization = pd.read_csv(CANNIBALIZATION_FILE)
    footfall = pd.read_csv(FOOTFALL_FILE)

    # Validate dataset record counts
    if len(candidates) != 25:
        raise ValueError("Unexpected candidate dataset size.")

    if candidates["candidate_id"].duplicated().any():
        raise ValueError("Duplicate candidate IDs found.")

    # Validate required columns
    required_columns = {
        "candidates": [
            "candidate_id", "candidate_name", "city",
            "proposed_store_category", "estimated_rent_index"
        ],
        "competitors": [
            "candidate_id", "nearest_competitor_distance_km",
            "competitors_within_catchment",
            "same_category_competitors"
        ],
        "cannibalization": [
            "candidate_id", "overlap_percentage"
        ],
        "footfall": [
            "city", "date", "total_visitors"
        ]
    }

    datasets = {
        "candidates": candidates,
        "competitors": competitors,
        "cannibalization": cannibalization,
        "footfall": footfall
    }

    for name, columns in required_columns.items():
        missing = set(columns) - set(datasets[name].columns)

        if missing:
            raise ValueError(
                f"Missing columns in {name}: {missing}"
            )

    # Check that all candidate IDs match across datasets
    candidate_ids = set(candidates["candidate_id"])

    if set(competitors["candidate_id"]) != candidate_ids:
        raise ValueError("Competitor candidate IDs do not match.")

    if set(cannibalization["candidate_id"]) != candidate_ids:
        raise ValueError("Cannibalization candidate IDs do not match.")

    # Validate numeric values
    numeric_columns = [
        (candidates, "estimated_rent_index"),
        (competitors, "nearest_competitor_distance_km"),
        (competitors, "competitors_within_catchment"),
        (competitors, "same_category_competitors"),
        (cannibalization, "overlap_percentage"),
        (footfall, "total_visitors")
    ]

    for df, column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

        if df[column].isna().any():
            raise ValueError(
                f"Invalid numeric values in {column}."
            )

    if (candidates["estimated_rent_index"] <= 0).any():
        raise ValueError("Rent index must be positive.")

    if (competitors["nearest_competitor_distance_km"] < 0).any():
        raise ValueError("Invalid competitor distance.")

    if (cannibalization["overlap_percentage"] < 0).any() or (
        cannibalization["overlap_percentage"] > 100
    ).any():
        raise ValueError("Invalid cannibalization percentage.")

    if (footfall["total_visitors"] < 0).any():
        raise ValueError("Invalid footfall values.")

    print(f"Candidate locations loaded: {len(candidates)}")
    print(f"Competitor records loaded: {len(competitors)}")
    print(f"Cannibalization records loaded: {len(cannibalization)}")
    print(f"Footfall records loaded: {len(footfall)}")

    return candidates, competitors, cannibalization, footfall
def normalize_score(values, higher_is_better=True):
    """
    Normalize values to a score between 0 and 100.
    """

    minimum = values.min()
    maximum = values.max()

    if maximum == minimum:
        return pd.Series(100.0, index=values.index)

    normalized = (values - minimum) / (maximum - minimum)

    if not higher_is_better:
        normalized = 1 - normalized

    return normalized * 100


def calculate_recommendation_scores(
    candidates, competitors, cannibalization, footfall
):
    print("\nCalculating store location recommendation scores...")

    # Calculate total visitor activity for each city
    city_footfall = (
        footfall.groupby("city", as_index=False)
        .agg(total_city_visitors=("total_visitors", "sum"))
    )

    # Merge all datasets using candidate IDs
    results = candidates.merge(
        competitors,
        on="candidate_id",
        suffixes=("", "_competitor"),
        validate="one_to_one"
    )

    results = results.merge(
        cannibalization[
            ["candidate_id", "overlap_percentage",
             "cannibalization_risk"]
        ],
        on="candidate_id",
        validate="one_to_one"
    )

    results = results.merge(
        city_footfall,
        on="city",
        validate="many_to_one"
    )

    if len(results) != len(candidates):
        raise ValueError("Candidate records were lost during merging.")

    # 1. Footfall demand score (35%)
    results["footfall_score"] = normalize_score(
        results["total_city_visitors"]
    )

    # 2. Competitor opportunity score (25%)
    distance_score = normalize_score(
        results["nearest_competitor_distance_km"]
    )

    competitor_density_score = normalize_score(
        results["competitors_within_catchment"],
        higher_is_better=False
    )

    same_category_score = normalize_score(
        results["same_category_competitors"],
        higher_is_better=False
    )

    results["competitor_opportunity_score"] = (
        distance_score * 0.50
        + competitor_density_score * 0.25
        + same_category_score * 0.25
    )

    # 3. Cannibalization suitability score (25%)
    results["cannibalization_score"] = (
        100 - results["overlap_percentage"]
    )

    # 4. Rent affordability score (15%)
    results["rent_affordability_score"] = normalize_score(
        results["estimated_rent_index"],
        higher_is_better=False
    )

    # Calculate weighted recommendation score
    results["recommendation_score"] = (
        results["footfall_score"] * 0.35
        + results["competitor_opportunity_score"] * 0.25
        + results["cannibalization_score"] * 0.25
        + results["rent_affordability_score"] * 0.15
    )

    # Classify recommendation
    def classify_recommendation(score):
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Moderate"
        else:
            return "Low"

    results["recommendation_category"] = (
        results["recommendation_score"]
        .apply(classify_recommendation)
    )

    # Rank candidates from highest to lowest score
    results = results.sort_values(
        by="recommendation_score",
        ascending=False
    ).reset_index(drop=True)

    results["recommendation_rank"] = (
        results["recommendation_score"]
        .rank(method="first", ascending=False)
        .astype(int)
    )

    return results
def main():
    print("=" * 65)
    print("GEOPULSE - SMART STORE LOCATION RECOMMENDATION")
    print("=" * 65)

    candidates, competitors, cannibalization, footfall = load_data()

    results = calculate_recommendation_scores(
        candidates,
        competitors,
        cannibalization,
        footfall
    )

    if results.empty:
        raise ValueError("No recommendation results generated.")

    # Select important output columns
    output_columns = [
        "recommendation_rank",
        "candidate_id",
        "candidate_name",
        "city",
        "proposed_store_category",
        "total_city_visitors",
        "footfall_score",
        "competitor_opportunity_score",
        "cannibalization_score",
        "rent_affordability_score",
        "recommendation_score",
        "recommendation_category"
    ]

    output = results[output_columns].copy()

    # Round score columns
    score_columns = [
        "footfall_score",
        "competitor_opportunity_score",
        "cannibalization_score",
        "rent_affordability_score",
        "recommendation_score"
    ]

    output[score_columns] = output[score_columns].round(2)

    # Save recommendations
    output.to_csv(OUTPUT_FILE, index=False)

    print("\nRECOMMENDATION SUMMARY")
    print("-" * 65)

    print(f"Candidates evaluated: {len(output)}")
    print(f"Cities analysed: {output['city'].nunique()}")

    print("\nRECOMMENDATION DISTRIBUTION")
    print("-" * 65)

    print(
        output["recommendation_category"]
        .value_counts()
        .to_string()
    )

    print("\nTOP 10 RECOMMENDED LOCATIONS")
    print("-" * 65)

    print(
        output[
            [
                "recommendation_rank",
                "candidate_id",
                "city",
                "recommendation_score",
                "recommendation_category"
            ]
        ].head(10).to_string(index=False)
    )

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
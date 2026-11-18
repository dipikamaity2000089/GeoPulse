from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

FOOTFALL_FILE = PROCESSED_DIR / "footfall_observations.csv"
STORE_FILE = PROCESSED_DIR / "store_locations.csv"

OUTPUT_FILE = PROCESSED_DIR / "store_footfall_by_hour.csv"


def main():
    print("=" * 55)
    print("GEOPULSE GEOGRAPHIC FOOTFALL DATA PREPARATION")
    print("=" * 55)

    # Load datasets
    footfall = pd.read_csv(FOOTFALL_FILE)
    stores = pd.read_csv(STORE_FILE)

    # Aggregate visitor counts by store and hour
    footfall["timestamp"] = pd.to_datetime(footfall["timestamp"])
    footfall["hour"] = footfall["timestamp"].dt.hour
    footfall["date"] = footfall["timestamp"].dt.date

    summary = (
        footfall.groupby(["store_id", "hour"])
        .agg(
            total_visitors=("visitor_count", "sum"),
            average_visitors=("visitor_count", "mean"),
            observation_days=("date", "nunique")
        )
        .reset_index()
    )

    # Attach geographic and store information
    store_details = stores[
        [
            "store_id",
            "city",
            "country",
            "store_category",
            "latitude",
            "longitude"
        ]
    ]

    geographic_data = summary.merge(
        store_details,
        on="store_id",
        how="left",
        validate="many_to_one"
    )

    # Round average visitor counts
    geographic_data["average_visitors"] = (
        geographic_data["average_visitors"].round(2)
    )

    # Validate geographic data
    validation_passed = (
        geographic_data["city"].notna().all()
        and geographic_data["latitude"].notna().all()
        and geographic_data["longitude"].notna().all()
        and len(geographic_data) == 700
        and (geographic_data["observation_days"] == 14).all()
    )

    print("\nGEOGRAPHIC FOOTFALL VALIDATION")
    print("Output records:", len(geographic_data))
    print("Missing locations:", geographic_data["latitude"].isna().sum())
    print("Stores represented:", geographic_data["store_id"].nunique())
    print("Hours represented:", geographic_data["hour"].nunique())
    print("Observation days:", geographic_data["observation_days"].unique())

    print(
        "\nVALIDATION:",
        "PASSED" if validation_passed else "FAILED"
    )

    if not validation_passed:
        raise ValueError("Geographic footfall validation failed.")

    # Save output
    geographic_data.to_csv(OUTPUT_FILE, index=False)

    print("\nFIRST 10 RECORDS:")
    print(geographic_data.head(10).to_string(index=False))

    print(f"\n[OK] Saved: {OUTPUT_FILE.name}")
    print("=" * 55)


if __name__ == "__main__":
    main()

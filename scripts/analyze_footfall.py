from pathlib import Path

import pandas as pd


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "footfall_observations.csv"

OUTPUT_FILE = PROCESSED_DIR / "hourly_footfall_summary.csv"


def main():
    print("=" * 55)
    print("GEOPULSE HOURLY FOOTFALL ANALYSIS")
    print("=" * 55)

    # Load footfall data
    df = pd.read_csv(INPUT_FILE)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Extract date and hour
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    # Aggregate hourly footfall
    hourly_summary = (
        df.groupby(["city", "date", "hour"])
        .agg(
            total_visitors=("visitor_count", "sum"),
            average_visitors=("visitor_count", "mean"),
            store_count=("store_id", "nunique")
        )
        .reset_index()
    )

    # Round average visitor count
    hourly_summary["average_visitors"] = (
        hourly_summary["average_visitors"].round(2)
    )

    # Save analytical output
    hourly_summary.to_csv(OUTPUT_FILE, index=False)

    print(f"\nInput observations: {len(df)}")
    print(f"Hourly summary records: {len(hourly_summary)}")

    print("\nFIRST 10 RECORDS:")
    print(hourly_summary.head(10).to_string(index=False))

    print(f"\n[OK] Saved: {OUTPUT_FILE.name}")

    print("\n" + "=" * 55)
    print("HOURLY FOOTFALL ANALYSIS COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()

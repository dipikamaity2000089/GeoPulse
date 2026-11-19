from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

INPUT_FILE = PROCESSED_DIR / "hourly_footfall_summary.csv"

HOURLY_OUTPUT = PROCESSED_DIR / "hourly_footfall_analysis.csv"
DAY_OUTPUT = PROCESSED_DIR / "day_of_week_footfall_analysis.csv"
DAY_TYPE_OUTPUT = PROCESSED_DIR / "weekday_weekend_footfall_analysis.csv"


def main():
    print("=" * 60)
    print("GEOPULSE TIME-BASED MOBILITY ANALYSIS")
    print("=" * 60)

    # Load hourly footfall summary
    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "city",
        "date",
        "hour",
        "total_visitors",
        "average_visitors",
        "store_count"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Convert columns into appropriate data types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
    df["total_visitors"] = pd.to_numeric(
        df["total_visitors"], errors="coerce"
    )
    df["average_visitors"] = pd.to_numeric(
        df["average_visitors"], errors="coerce"
    )

    if df[required_columns].isna().any().any():
        raise ValueError("Missing or invalid values found in input data.")

    # Identify day names and weekdays/weekends
    df["day_name"] = df["date"].dt.day_name()

    df["day_type"] = df["date"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

    print("\nINPUT DATA INFORMATION")
    print("Total records:", len(df))
    print("Cities:", sorted(df["city"].unique().tolist()))
    print("Observation dates:", df["date"].nunique())
    print(
        "Date range:",
        df["date"].min().date(),
        "to",
        df["date"].max().date()
    )

    # 1. HOURLY FOOTFALL ANALYSIS
    hourly_summary = (
        df.groupby(["city", "hour"], as_index=False)
        .agg(
            average_total_visitors=("total_visitors", "mean"),
            average_visitors_per_store=("average_visitors", "mean"),
            minimum_hourly_visitors=("total_visitors", "min"),
            maximum_hourly_visitors=("total_visitors", "max"),
            observation_days=("date", "nunique")
        )
    )

    # Round average values
    average_columns = [
        "average_total_visitors",
        "average_visitors_per_store"
    ]

    hourly_summary[average_columns] = (
        hourly_summary[average_columns].round(2)
    )

    # 2. PREPARE DAILY FOOTFALL TOTALS
    daily_summary = (
        df.groupby(
            ["city", "date", "day_name", "day_type"],
            as_index=False
        )
        .agg(
            daily_total_visitors=("total_visitors", "sum"),
            daily_average_hourly_visitors=("total_visitors", "mean")
        )
    )

    # 3. DAY-OF-WEEK ANALYSIS
    daily_summary["day_number"] = (
        daily_summary["date"].dt.dayofweek
    )

    day_summary = (
        daily_summary.groupby(
            ["city", "day_number", "day_name"],
            as_index=False
        )
        .agg(
            average_daily_visitors=("daily_total_visitors", "mean"),
            average_hourly_visitors=(
                "daily_average_hourly_visitors", "mean"
            ),
            observed_days=("date", "nunique")
        )
        .sort_values(["city", "day_number"])
        .drop(columns="day_number")
    )

    day_summary[
        ["average_daily_visitors", "average_hourly_visitors"]
    ] = day_summary[
        ["average_daily_visitors", "average_hourly_visitors"]
    ].round(2)

    # 4. WEEKDAY VS WEEKEND ANALYSIS
    day_type_summary = (
        daily_summary.groupby(
            ["city", "day_type"],
            as_index=False
        )
        .agg(
            average_daily_visitors=("daily_total_visitors", "mean"),
            average_hourly_visitors=(
                "daily_average_hourly_visitors", "mean"
            ),
            observed_days=("date", "nunique")
        )
    )

    day_type_summary[
        ["average_daily_visitors", "average_hourly_visitors"]
    ] = day_type_summary[
        ["average_daily_visitors", "average_hourly_visitors"]
    ].round(2)

    # 5. IDENTIFY PEAK AND QUIET HOURS
    peak_hours = hourly_summary.loc[
        hourly_summary.groupby("city")[
            "average_total_visitors"
        ].idxmax()
    ].sort_values("city")

    quiet_hours = hourly_summary.loc[
        hourly_summary.groupby("city")[
            "average_total_visitors"
        ].idxmin()
    ].sort_values("city")

    # Save analytical outputs
    hourly_summary.to_csv(HOURLY_OUTPUT, index=False)
    day_summary.to_csv(DAY_OUTPUT, index=False)
    day_type_summary.to_csv(DAY_TYPE_OUTPUT, index=False)

    # Display results
    print("\nPEAK FOOTFALL HOURS")
    print(
        peak_hours[
            ["city", "hour", "average_total_visitors"]
        ].to_string(index=False)
    )

    print("\nQUIETEST FOOTFALL HOURS")
    print(
        quiet_hours[
            ["city", "hour", "average_total_visitors"]
        ].to_string(index=False)
    )

    print("\nWEEKDAY VS WEEKEND COMPARISON")
    print(day_type_summary.to_string(index=False))

    print("\nGENERATED OUTPUT FILES")
    print(HOURLY_OUTPUT.name)
    print(DAY_OUTPUT.name)
    print(DAY_TYPE_OUTPUT.name)

    print("\n" + "=" * 60)
    print("TIME-BASED MOBILITY ANALYSIS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()

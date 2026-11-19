from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_DIR = PROCESSED_DIR / "visualizations"

HOURLY_FILE = PROCESSED_DIR / "hourly_footfall_analysis.csv"
DAY_FILE = PROCESSED_DIR / "day_of_week_footfall_analysis.csv"
DAY_TYPE_FILE = PROCESSED_DIR / "weekday_weekend_footfall_analysis.csv"


def main():
    print("=" * 60)
    print("GEOPULSE TIME-BASED MOBILITY VISUALIZATION")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load analysis results
    hourly = pd.read_csv(HOURLY_FILE)
    day = pd.read_csv(DAY_FILE)
    day_type = pd.read_csv(DAY_TYPE_FILE)

    # 1. HOURLY FOOTFALL TREND
    plt.figure(figsize=(11, 6))

    for city in sorted(hourly["city"].unique()):
        city_data = hourly[hourly["city"] == city].sort_values("hour")

        plt.plot(
            city_data["hour"],
            city_data["average_total_visitors"],
            marker="o",
            label=city
        )

    plt.title("Hourly Footfall Trends Across Cities")
    plt.xlabel("Hour of the Day")
    plt.ylabel("Average Total Visitors")
    plt.xticks(range(8, 22))
    plt.grid(True, alpha=0.3)
    plt.legend(title="City")
    plt.tight_layout()

    hourly_output = OUTPUT_DIR / "hourly_footfall_trend.png"
    plt.savefig(hourly_output, dpi=150)
    plt.close()

    # 2. DAY-OF-WEEK FOOTFALL
    day_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    day["day_name"] = pd.Categorical(
        day["day_name"],
        categories=day_order,
        ordered=True
    )

    plt.figure(figsize=(11, 6))

    for city in sorted(day["city"].unique()):
        city_data = (
            day[day["city"] == city]
            .sort_values("day_name")
        )

        plt.plot(
            city_data["day_name"].astype(str),
            city_data["average_daily_visitors"],
            marker="o",
            label=city
        )

    plt.title("Average Daily Footfall by Day of the Week")
    plt.xlabel("Day of the Week")
    plt.ylabel("Average Daily Visitors")
    plt.grid(True, alpha=0.3)
    plt.legend(title="City")
    plt.tight_layout()

    day_output = OUTPUT_DIR / "day_of_week_footfall.png"
    plt.savefig(day_output, dpi=150)
    plt.close()

    # 3. WEEKDAY VS WEEKEND COMPARISON
    comparison = day_type.pivot(
        index="city",
        columns="day_type",
        values="average_daily_visitors"
    )

    comparison = comparison.reindex(
        columns=["Weekday", "Weekend"]
    )

    ax = comparison.plot(
        kind="bar",
        figsize=(11, 6),
        width=0.75
    )

    ax.set_title("Weekday vs Weekend Average Daily Footfall")
    ax.set_xlabel("City")
    ax.set_ylabel("Average Daily Visitors")
    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(title="Day Type")

    plt.tight_layout()

    comparison_output = (
        OUTPUT_DIR / "weekday_weekend_comparison.png"
    )

    plt.savefig(comparison_output, dpi=150)
    plt.close()

    # Display generated files
    print("\nVISUALIZATION FILES GENERATED")

    for file_path in [
        hourly_output,
        day_output,
        comparison_output
    ]:
        print(f"[OK] {file_path}")

    print("\n" + "=" * 60)
    print("TIME-BASED VISUALIZATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()

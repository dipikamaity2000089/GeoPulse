
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

visits_path = RAW_DIR / "store_visits.csv"
stores_path = RAW_DIR / "store_metadata.csv"

visits = pd.read_csv(visits_path)
stores = pd.read_csv(stores_path)

print("=" * 60)
print("GEOPULSE — STORE FOOTFALL ANALYTICS")
print("=" * 60)

required_columns = ["Store_ID", "Arrival_Time", "Dwell_Time_Minutes"]

missing_columns = [
    column for column in required_columns
    if column not in visits.columns
]

if missing_columns:
    raise ValueError(f"Missing columns in visits dataset: {missing_columns}")

visits["Arrival_Time"] = pd.to_datetime(
    visits["Arrival_Time"], errors="coerce"
)

visits["Dwell_Time_Minutes"] = pd.to_numeric(
    visits["Dwell_Time_Minutes"], errors="coerce"
)

visits = visits.dropna(subset=["Store_ID", "Arrival_Time"])

visits["Hour"] = visits["Arrival_Time"].dt.hour
visits["Day_Name"] = visits["Arrival_Time"].dt.day_name()
visits["Day_Type"] = visits["Arrival_Time"].dt.dayofweek.map(
    lambda day: "Weekend" if day >= 5 else "Weekday"
)

# 1. Store-level footfall analysis

store_footfall = (
    visits.groupby("Store_ID")
    .agg(
        Total_Visits=("Visit_ID", "count"),
        Unique_Devices=("Device_ID", "nunique"),
        Average_Dwell_Minutes=("Dwell_Time_Minutes", "mean"),
        Total_Dwell_Minutes=("Dwell_Time_Minutes", "sum")
    )
    .reset_index()
)

store_footfall["Average_Dwell_Minutes"] = (
    store_footfall["Average_Dwell_Minutes"].round(2)
)

store_footfall = store_footfall.merge(
    stores,
    on="Store_ID",
    how="left"
)

store_footfall = store_footfall.sort_values(
    "Total_Visits", ascending=False
)

# 2. Hourly footfall analysis

hourly_footfall = (
    visits.groupby("Hour")
    .agg(
        Total_Visits=("Visit_ID", "count"),
        Average_Dwell_Minutes=("Dwell_Time_Minutes", "mean")
    )
    .reset_index()
)

hourly_footfall["Average_Dwell_Minutes"] = (
    hourly_footfall["Average_Dwell_Minutes"].round(2)
)

hourly_footfall = hourly_footfall.sort_values("Hour")

# 3. Weekday vs weekend analysis

day_type_analysis = (
    visits.groupby("Day_Type")
    .agg(
        Total_Visits=("Visit_ID", "count"),
        Unique_Devices=("Device_ID", "nunique"),
        Average_Dwell_Minutes=("Dwell_Time_Minutes", "mean")
    )
    .reset_index()
)

day_type_analysis["Average_Dwell_Minutes"] = (
    day_type_analysis["Average_Dwell_Minutes"].round(2)
)

# 4. Day-of-week analysis

daily_footfall = (
    visits.groupby("Day_Name")
    .agg(
        Total_Visits=("Visit_ID", "count"),
        Average_Dwell_Minutes=("Dwell_Time_Minutes", "mean")
    )
    .reset_index()
)

daily_footfall["Average_Dwell_Minutes"] = (
    daily_footfall["Average_Dwell_Minutes"].round(2)
)

# 5. Save analytics outputs

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

store_footfall.to_csv(
    PROCESSED_DIR / "store_footfall_analysis.csv",
    index=False
)

hourly_footfall.to_csv(
    PROCESSED_DIR / "hourly_footfall_analysis.csv",
    index=False
)

day_type_analysis.to_csv(
    PROCESSED_DIR / "weekday_weekend_analysis.csv",
    index=False
)

daily_footfall.to_csv(
    PROCESSED_DIR / "daily_footfall_analysis.csv",
    index=False
)

# 6. Display insights

print("\nTOP 10 STORES BY FOOTFALL")
print("-" * 60)

print(
    store_footfall[
        ["Store_ID", "Total_Visits", "Average_Dwell_Minutes"]
    ].head(10).to_string(index=False)
)

print("\nHOURLY FOOTFALL")
print("-" * 60)
print(hourly_footfall.to_string(index=False))

print("\nWEEKDAY VS WEEKEND")
print("-" * 60)
print(day_type_analysis.to_string(index=False))

print("\nBUSIEST HOUR")
print("-" * 60)

peak_hour = hourly_footfall.loc[
    hourly_footfall["Total_Visits"].idxmax()
]

print(
    f"Hour: {int(peak_hour['Hour']):02d}:00 | "
    f"Visits: {int(peak_hour['Total_Visits'])}"
)

print("\nANALYTICS OUTPUTS SAVED")
print("-" * 60)
print("store_footfall_analysis.csv")
print("hourly_footfall_analysis.csv")
print("weekday_weekend_analysis.csv")
print("daily_footfall_analysis.csv")

print("\nSTORE FOOTFALL ANALYTICS COMPLETED")
print("=" * 60)

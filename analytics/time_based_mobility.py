
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

VISITS_FILE = RAW_DIR / "store_visits.csv"
STORES_FILE = RAW_DIR / "store_metadata.csv"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

visits = pd.read_csv(VISITS_FILE)
stores = pd.read_csv(STORES_FILE)

required_columns = [
    "Device_ID",
    "Store_ID",
    "Arrival_Time",
    "Departure_Time",
    "Visit_ID"
]

missing_columns = [col for col in required_columns if col not in visits.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

visits["Arrival_Time"] = pd.to_datetime(visits["Arrival_Time"], errors="coerce")
visits["Departure_Time"] = pd.to_datetime(visits["Departure_Time"], errors="coerce")

visits = visits.dropna(subset=["Device_ID", "Store_ID", "Arrival_Time"])
visits = visits.sort_values(["Device_ID", "Arrival_Time"]).reset_index(drop=True)

print("=" * 60)
print("GEOPULSE TIME-BASED MOBILITY ANALYSIS")
print("=" * 60)

print(f"Total visits analyzed: {len(visits):,}")
print(f"Unique devices: {visits['Device_ID'].nunique():,}")
print(f"Unique stores visited: {visits['Store_ID'].nunique():,}")

visits["Arrival_Hour"] = visits["Arrival_Time"].dt.hour
visits["Day_Name"] = visits["Arrival_Time"].dt.day_name()
visits["Date"] = visits["Arrival_Time"].dt.date

visits["Next_Store"] = visits.groupby("Device_ID")["Store_ID"].shift(-1)
visits["Next_Visit_Time"] = visits.groupby("Device_ID")["Arrival_Time"].shift(-1)

visits["Hours_Between_Visits"] = (
    visits["Next_Visit_Time"] - visits["Arrival_Time"]
).dt.total_seconds() / 3600

visits["Next_Visit_Date"] = visits["Next_Visit_Time"].dt.date

visits["Transition_Gap_Hours"] = visits["Hours_Between_Visits"]

transitions = visits[
    visits["Next_Store"].notna()
    & (visits["Store_ID"] != visits["Next_Store"])
    & (visits["Transition_Gap_Hours"] >= 0)
    & (visits["Transition_Gap_Hours"] <= 6)
].copy()

transition_analysis = transitions.groupby(
    ["Store_ID", "Next_Store"]
).agg(
    Transition_Count=("Visit_ID", "count"),
    Unique_Devices=("Device_ID", "nunique"),
    Average_Gap_Hours=("Hours_Between_Visits", "mean")
).reset_index()

transition_analysis = transition_analysis.rename(
    columns={
        "Store_ID": "Store_A",
        "Next_Store": "Store_B"
    }
)

transition_analysis["Average_Gap_Hours"] = transition_analysis[
    "Average_Gap_Hours"
].round(2)

transition_analysis = transition_analysis.sort_values(
    "Transition_Count", ascending=False
)

transition_analysis.to_csv(
    PROCESSED_DIR / "store_transition_analysis.csv", index=False
)

first_visits = visits.groupby("Device_ID", as_index=False).first()

first_store_analysis = first_visits.groupby("Store_ID").agg(
    First_Visit_Count=("Device_ID", "count")
).reset_index()

first_store_analysis = first_store_analysis.sort_values(
    "First_Visit_Count", ascending=False
)

first_store_analysis.to_csv(
    PROCESSED_DIR / "first_store_analysis.csv", index=False
)

hourly_mobility = visits.groupby("Arrival_Hour").agg(
    Total_Visits=("Visit_ID", "count"),
    Unique_Devices=("Device_ID", "nunique"),
    Average_Dwell_Minutes=("Dwell_Time_Minutes", "mean")
).reset_index()

hourly_mobility["Average_Dwell_Minutes"] = hourly_mobility[
    "Average_Dwell_Minutes"
].round(2)

hourly_mobility.to_csv(
    PROCESSED_DIR / "hourly_mobility_analysis.csv", index=False
)

journeys = visits.groupby("Device_ID").agg(
    Total_Visits=("Visit_ID", "count"),
    Unique_Stores_Visited=("Store_ID", "nunique"),
    First_Visit=("Arrival_Time", "min"),
    Last_Visit=("Arrival_Time", "max"),
    Store_Journey=("Store_ID", lambda x: " -> ".join(x.astype(str)))
).reset_index()

journeys = journeys.sort_values("Total_Visits", ascending=False)

journeys.to_csv(
    PROCESSED_DIR / "device_journey_sequences.csv", index=False
)

repeat_visits = visits.groupby("Store_ID").agg(
    Total_Visits=("Visit_ID", "count"),
    Unique_Visitors=("Device_ID", "nunique")
).reset_index()

repeat_visits["Repeat_Visitors"] = (
    visits.groupby("Store_ID")["Device_ID"]
    .apply(lambda x: (x.value_counts() > 1).sum())
    .values
)

repeat_visits["Repeat_Visitor_Percent"] = (
    repeat_visits["Repeat_Visitors"] / repeat_visits["Unique_Visitors"] * 100
).round(2)

repeat_visits = repeat_visits.sort_values(
    "Repeat_Visitor_Percent", ascending=False
)

repeat_visits.to_csv(
    PROCESSED_DIR / "repeat_visit_analysis.csv", index=False
)

print("\nTOP STORE-TO-STORE TRANSITIONS")
print(transition_analysis.head(10).to_string(index=False))

print("\nTOP FIRST-VISITED STORES")
print(first_store_analysis.head(10).to_string(index=False))

print("\nHOURLY VISITOR MOVEMENT")
print(hourly_mobility.to_string(index=False))

print("\nTOP REPEAT-VISIT STORES")
print(repeat_visits.head(10).to_string(index=False))

print("\nTOP VISITOR JOURNEYS")
print(journeys.head(5).to_string(index=False))

print("\nOUTPUT FILES CREATED")
print("1. store_transition_analysis.csv")
print("2. first_store_analysis.csv")
print("3. hourly_mobility_analysis.csv")
print("4. device_journey_sequences.csv")
print("5. repeat_visit_analysis.csv")

print("\nTIME-BASED MOBILITY ANALYSIS COMPLETED")

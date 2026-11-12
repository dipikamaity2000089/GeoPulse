
import pandas as pd
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent
input_file = base_path / "data" / "gps_store_distances.csv"

df = pd.read_csv(input_file)

df["Timestamp"] = pd.to_datetime(df["Timestamp"])

nearby_df = df[df["Within_500m"] == True].copy()

nearby_df["Hour"] = nearby_df["Timestamp"].dt.hour

hourly_summary = nearby_df.groupby(
    ["Nearest_Store_ID", "Hour"]
).agg(
    Total_GPS_Pings=("DeviceID", "count"),
    Unique_Visitors=("DeviceID", "nunique")
).reset_index()

output_file = base_path / "data" / "hourly_footfall.csv"

hourly_summary.to_csv(output_file, index=False)

print("HOURLY FOOT TRAFFIC ANALYSIS")
print("--------------------------------")
print("Total Stores:", hourly_summary["Nearest_Store_ID"].nunique())
print("Total Hours:", hourly_summary["Hour"].nunique())
print("\nHourly Footfall Summary:")
print(hourly_summary.head(15))

print("\nHourly footfall analysis completed!")

import pandas as pd
import matplotlib.pyplot as plt
gps = pd.read_csv("data/gps_data.csv")
gps["Timestamp"] = pd.to_datetime(gps["Timestamp"])
gps["Hour"] = gps["Timestamp"].dt.hour
hourly_analysis = gps.groupby("Hour").agg(
    Total_GPS_Points=("DeviceID", "count"),
    Unique_Devices=("DeviceID", "nunique")
).reindex(range(24), fill_value=0).reset_index()
hourly_analysis.to_csv(
    "data/hourly_mobility_analysis.csv",
    index=False
)
print("24-Hour Footfall Analysis:")
print(hourly_analysis.to_string(index=False))
plt.figure(figsize=(14, 6))
plt.bar(
    hourly_analysis["Hour"],
    hourly_analysis["Total_GPS_Points"]
)
plt.xticks(range(24))
plt.xlabel("Hour of Day (0-23)")
plt.ylabel("Total GPS Points")
plt.title("GeoPulse: 24-Hour GPS Footfall Analysis")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("data/24_hour_footfall_chart.png", dpi=300)
plt.show()
print("24-Hour Analysis Completed Successfully!")
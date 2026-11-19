import pandas as pd
df = pd.read_csv("data/hourly_mobility_analysis.csv")
peak_hour = df.loc[df["Total_GPS_Points"].idxmax()]
lowest_hour = df.loc[df["Total_GPS_Points"].idxmin()]
device_peak = df.loc[df["Unique_Devices"].idxmax()]
print("===== GeoPulse Peak Footfall Analysis =====")
print("\nPeak Footfall Hour:")
print("Hour:", peak_hour["Hour"])
print("GPS Points:", peak_hour["Total_GPS_Points"])
print("\nLowest Footfall Hour:")
print("Hour:", lowest_hour["Hour"])
print("GPS Points:", lowest_hour["Total_GPS_Points"])
print("\nHighest Unique Device Hour:")
print("Hour:", device_peak["Hour"])
print("Unique Devices:", device_peak["Unique_Devices"])
print("\nPeak Footfall Analysis Completed!")
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.bar(
    df["Hour"],
    df["Total_GPS_Points"]
)
plt.xlabel("Hour of Day (0-23)")
plt.ylabel("Total GPS Points")
plt.title("GeoPulse: Peak Footfall Analysis (24 Hours)")
plt.xticks(range(24))
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig("data/peak_footfall_chart.png", dpi=300)
plt.show()
print("Peak Footfall Chart Created Successfully!")

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

base_path = Path(__file__).resolve().parent.parent
input_file = base_path / "data" / "hourly_footfall.csv"
output_folder = base_path / "dashboard"
output_folder.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)

df["Hour"] = pd.to_numeric(df["Hour"])

hourly_data = df.groupby(
    ["Hour", "Nearest_Store_ID"]
)["Total_GPS_Pings"].sum().reset_index()

plt.figure(figsize=(12, 6))

for store in hourly_data["Nearest_Store_ID"].unique():
    store_data = hourly_data[
        hourly_data["Nearest_Store_ID"] == store
    ]
    plt.plot(
        store_data["Hour"],
        store_data["Total_GPS_Pings"],
        marker="o",
        label=store
    )

plt.title("Hourly Footfall Trend by Store")
plt.xlabel("Hour of the Day")
plt.ylabel("Total GPS Pings")
plt.xticks(range(6, 19))
plt.legend(title="Store ID")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_folder / "hourly_footfall_trend.png")
plt.show()

store_data = df.groupby(
    "Nearest_Store_ID"
)["Total_GPS_Pings"].sum().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
store_data.plot(kind="bar")

plt.title("Store-wise Footfall Comparison")
plt.xlabel("Store ID")
plt.ylabel("Total GPS Pings")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(output_folder / "store_footfall_comparison.png")
plt.show()

print("Footfall visualizations created successfully!")
print("Charts saved in the dashboard folder.")


import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
np.random.seed(42)

locations = [
    (13.0418, 80.2341),
    (13.0850, 80.2101),
    (12.9750, 80.2212),
    (12.9352, 80.2300)
]

records = []

start_time = datetime(2026, 11, 1, 6, 0)

for device in range(1, 1001):
    device_id = f"D{device:04d}"
    current_location = random.choice(locations)

    number_of_pings = random.randint(5, 10)

    for ping in range(number_of_pings):
        latitude = current_location[0] + np.random.normal(0, 0.002)
        longitude = current_location[1] + np.random.normal(0, 0.002)

        timestamp = start_time + timedelta(
            minutes=random.randint(0, 720)
        )

        records.append({
            "DeviceID": device_id,
            "Latitude": round(latitude, 6),
            "Longitude": round(longitude, 6),
            "Timestamp": timestamp
        })

df = pd.DataFrame(records)

df = df.sort_values(
    by=["DeviceID", "Timestamp"]
)

output_path = Path(__file__).resolve().parent.parent / "data"
output_path.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path / "raw_gps_pings.csv", index=False)

print("GEOPULSE GPS DATA GENERATION")
print("--------------------------------")
print("Total GPS Records:", len(df))
print("Unique Devices:", df["DeviceID"].nunique())
print("Missing Values:", df.isnull().sum().sum())
print("Duplicate Rows:", df.duplicated().sum())
print("\nDataset Preview:")
print(df.head())
print("\nGPS dataset generated successfully!")

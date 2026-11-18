import pandas as pd
import random
from datetime import datetime, timedelta
random.seed(42)
stores = [
    (22.5726, 88.3639),
    (22.5740, 88.3650),
    (22.5760, 88.3670)
]
records = []
start_time = datetime(2026, 11, 12, 0, 0)
for hour in range(24):
    timestamp = start_time + timedelta(hours=hour)
    for i in range(8):
        device_id = f"D{random.randint(1, 20):03d}"
        lat, lon = random.choice(stores)
        latitude = lat + random.uniform(-0.001, 0.001)
        longitude = lon + random.uniform(-0.001, 0.001)
        records.append({
            "DeviceID": device_id,
            "Lat": round(latitude, 6),
            "Long": round(longitude, 6),
            "Timestamp": timestamp
        })
gps_df = pd.DataFrame(records)
gps_df.to_csv("data/gps_data.csv", index=False)
print("24-Hour GPS Dataset Created Successfully!")
print("Total GPS Records:", len(gps_df))
print("Unique Devices:", gps_df["DeviceID"].nunique())
print("Time Range:")
print(gps_df["Timestamp"].min())
print(gps_df["Timestamp"].max())
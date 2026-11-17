import pandas as pd
from math import radians, sin, cos, sqrt, atan2
gps = pd.read_csv("data/gps_data.csv")
stores = pd.read_csv("data/stores.csv")
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
device_store = []
for _, point in gps.iterrows():
    for _, store in stores.iterrows():
        distance = calculate_distance(
            point["Lat"], point["Long"],
            store["StoreLat"], store["StoreLong"]
        )
        if distance <= 500:
            device_store.append({
                "DeviceID": point["DeviceID"],
                "StoreID": store["StoreID"]
            })
df = pd.DataFrame(device_store)
device_summary = (
    df.groupby("DeviceID")["StoreID"]
    .nunique()
    .reset_index(name="Stores_Within_500m")
)
device_summary["Cannibalization_Risk"] = (
    device_summary["Stores_Within_500m"] > 1
)
device_summary.to_csv(
    "data/device_store_overlap.csv", index=False
)
print(device_summary)
print(
    "\nDevices in Multiple Store Catchments:",
    device_summary["Cannibalization_Risk"].sum()
)
print("\nCannibalization Analysis Completed!")
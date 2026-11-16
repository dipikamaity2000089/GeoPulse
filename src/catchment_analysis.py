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
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c
results = []
for _, store in stores.iterrows():
    count = 0
    devices = set()
    for _, point in gps.iterrows():
        distance = calculate_distance(
            store["StoreLat"],
            store["StoreLong"],
            point["Lat"],
            point["Long"]
        )
        if distance <= 500:
            count += 1
            devices.add(point["DeviceID"])
    results.append({
        "StoreID": store["StoreID"],
        "Total_GPS_Points": count,
        "Unique_Devices": len(devices)
    })
result_df = pd.DataFrame(results)
result_df.to_csv("data/catchment_analysis.csv", index=False)
print(result_df)
print("\n500-Meter Catchment Analysis Completed!")
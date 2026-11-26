import pandas as pd
import numpy as np
gps = pd.read_csv("data/gps_data.csv")
stores = pd.read_csv("data/stores.csv")
results = []
for _, point in gps.iterrows():
    distances = np.sqrt(
        (stores["StoreLat"] - point["Lat"]) ** 2
        + (stores["StoreLong"] - point["Long"]) ** 2
    )
    nearest_distance = distances.min()
    if nearest_distance > 0.005:
        results.append({
            "Lat": point["Lat"],
            "Long": point["Long"],
            "DeviceID": point["DeviceID"],
            "NearestStoreDistance": nearest_distance
        })
zones = pd.DataFrame(results)
if not zones.empty:
    zones["Zone"] = (
        zones["Lat"].round(3).astype(str)
        + "_"
        + zones["Long"].round(3).astype(str)
    )
    zone_analysis = zones.groupby("Zone").agg(
        GPS_Activity=("DeviceID", "count"),
        UniqueDevices=("DeviceID", "nunique"),
        AvgDistance=("NearestStoreDistance", "mean"),
        Lat=("Lat", "mean"),
        Long=("Long", "mean")
    ).reset_index()
    zone_analysis["Opportunity"] = zone_analysis["GPS_Activity"].apply(
        lambda x: "High" if x >= 5
        else "Medium" if x >= 2
        else "Low"
    )
    zone_analysis = zone_analysis.sort_values(
        "GPS_Activity", ascending=False
    )
    zone_analysis.to_csv(
        "data/underserved_zones.csv",
        index=False
    )
    print("Underserved Zone Detection completed!")
    print(zone_analysis.head(10))
else:
    print("No underserved zones detected.")
import pandas as pd
import math
gps = pd.read_csv("GeoPulse-Dipika/data/gps_data.csv")
stores = pd.read_csv("GeoPulse-Dipika/data/stores.csv")
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
results = []
for _, store in stores.iterrows():
    store_id = store["StoreID"]
    store_name = store["StoreName"]
    store_lat = store["StoreLat"]
    store_long = store["StoreLong"]
    nearby_devices = set()
    for _, point in gps.iterrows():
        distance = calculate_distance(
            store_lat,
            store_long,
            point["Lat"],
            point["Long"]
        )
        if distance <= 500:
            nearby_devices.add(point["DeviceID"])
    footfall = len(nearby_devices)
    competitors = 0
    for _, other_store in stores.iterrows():
        if other_store["StoreID"] == store_id:
            continue
        distance = calculate_distance(
            store_lat,
            store_long,
            other_store["StoreLat"],
            other_store["StoreLong"]
        )
        if distance <= 1000:
            competitors += 1
    shared_devices = 0
    for _, other_store in stores.iterrows():
        if other_store["StoreID"] == store_id:
            continue
        other_devices = set()
        for _, point in gps.iterrows():
            distance = calculate_distance(
                other_store["StoreLat"],
                other_store["StoreLong"],
                point["Lat"],
                point["Long"]
            )
            if distance <= 500:
                other_devices.add(point["DeviceID"])
        shared_devices += len(nearby_devices.intersection(other_devices))
    if footfall > 0:
        cannibalization_risk = min(
            100,
            (shared_devices / footfall) * 100
        )
    else:
        cannibalization_risk = 0
    results.append({
        "StoreID": store_id,
        "StoreName": store_name,
        "Footfall": footfall,
        "Nearby_Competitors": competitors,
        "Cannibalization_Risk": round(cannibalization_risk, 2)
    })
result_df = pd.DataFrame(results)
max_footfall = result_df["Footfall"].max()
if max_footfall > 0:
    result_df["Footfall_Score"] = (
        result_df["Footfall"] / max_footfall
    ) * 100
else:
    result_df["Footfall_Score"] = 0
result_df["Competition_Score"] = (
    100 / (1 + result_df["Nearby_Competitors"])
)
result_df["Cannibalization_Score"] = (
    100 - result_df["Cannibalization_Risk"]
)
result_df["Opportunity_Score"] = (
    result_df["Footfall_Score"] * 0.50
    + result_df["Competition_Score"] * 0.30
    + result_df["Cannibalization_Score"] * 0.20
)
def classify_opportunity(score):
    if score >= 70:
        return "High Opportunity"
    elif score >= 40:
        return "Medium Opportunity"
    else:
        return "Low Opportunity"
result_df["Opportunity_Level"] = (
    result_df["Opportunity_Score"]
    .apply(classify_opportunity)
)
result_df = result_df.sort_values(
    by="Opportunity_Score",
    ascending=False
)
result_df.to_csv(
    "GeoPulse-Dipika/data/location_opportunity_analysis.csv",
    index=False
)
print("\n===== GEO PULSE LOCATION OPPORTUNITY ANALYSIS =====\n")
print(result_df.to_string(index=False))
print("\nBest Location Opportunity:")
best_location = result_df.iloc[0]
print(best_location["StoreName"])
print("Opportunity Score:", round(best_location["Opportunity_Score"], 2))
print("Opportunity Level:", best_location["Opportunity_Level"])
print("\nAnalysis completed successfully!")
import pandas as pd
df = pd.read_csv("data/stores.csv")
print("===== GEOPULSE STORE LOCATION ANALYSIS =====")
print("\nStore Dataset:")
print(df)
print("\nColumn Names:")
print(df.columns.tolist())
print("\nDataset Information:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())
print("\nTotal Number of Stores:", len(df))
print("\nStore data loaded successfully!")
from math import radians, sin, cos, sqrt, atan2
from itertools import combinations
def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371  # Kilometers
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return earth_radius * c
results = []
for store1, store2 in combinations(df.to_dict("records"), 2):
    distance = calculate_distance(
        store1["StoreLat"],
        store1["StoreLong"],
        store2["StoreLat"],
        store2["StoreLong"]
    )
    results.append({
        "Store_1": store1["StoreName"],
        "Store_2": store2["StoreName"],
        "Distance_KM": round(distance, 3),
        "Distance_Meters": round(distance * 1000, 2)
    })
distance_df = pd.DataFrame(results)
print("\n===== STORE DISTANCE ANALYSIS =====")
print(distance_df)
distance_df.to_csv("data/store_distances.csv", index=False)
print("\nStore distance analysis completed!")
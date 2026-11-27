import pandas as pd
import numpy as np
gps = pd.read_csv("data/gps_data.csv")
stores = pd.read_csv("data/stores.csv")
candidate_locations = [
    (22.577, 88.367),
    (22.576, 88.368),
    (22.576, 88.367),
    (22.577, 88.368)
]
results = []
for i, (lat, lon) in enumerate(candidate_locations, start=1):
    distance = np.sqrt(
        (gps["Lat"] - lat) ** 2 +
        (gps["Long"] - lon) ** 2
    )
    gps_activity = (distance < 0.005).sum()
    store_distance = np.sqrt(
        (stores["StoreLat"] - lat) ** 2 +
        (stores["StoreLong"] - lon) ** 2
    )
    nearest_store_distance = store_distance.min()
    if nearest_store_distance < 0.005:
        risk = "High"
    elif nearest_store_distance < 0.01:
        risk = "Medium"
    else:
        risk = "Low"
    opportunity_score = (
        gps_activity * 0.7 +
        nearest_store_distance * 1000 * 0.3
    )
    results.append({
        "Candidate_Zone": f"Zone {i}",
        "Latitude": lat,
        "Longitude": lon,
        "GPS_Activity": gps_activity,
        "Nearest_Store_Distance": nearest_store_distance,
        "Cannibalization_Risk": risk,
        "Opportunity_Score": opportunity_score
    })
df = pd.DataFrame(results)
df["Rank"] = df["Opportunity_Score"].rank(
    ascending=False,
    method="dense"
).astype(int)
df["Recommendation"] = df["Rank"].apply(
    lambda x: "Best Expansion Location"
    if x == 1
    else "Potential Location"
    if x <= 2
    else "Low Priority"
)
df = df.sort_values("Rank")
df.to_csv(
    "data/what_if_expansion_simulation.csv",
    index=False
)
print("\nWHAT-IF STORE EXPANSION SIMULATION\n")
print(df[[
    "Candidate_Zone",
    "GPS_Activity",
    "Cannibalization_Risk",
    "Opportunity_Score",
    "Rank",
    "Recommendation"
]])
print("\nSimulation completed successfully!")
print("Results saved to data/what_if_expansion_simulation.csv")
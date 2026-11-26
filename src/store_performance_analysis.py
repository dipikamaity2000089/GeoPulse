import pandas as pd
gps = pd.read_csv("data/gps_data.csv")
stores = pd.read_csv("data/stores.csv")
results = []
for _, store in stores.iterrows():
    distance = (
        (gps["Lat"] - store["StoreLat"]) ** 2
        + (gps["Long"] - store["StoreLong"]) ** 2
    ) ** 0.5
    nearby = gps[distance < 0.005]
    results.append({
        "StoreName": store["StoreName"],
        "Footfall": len(nearby),
        "UniqueDevices": nearby["DeviceID"].nunique()
    })
df = pd.DataFrame(results)
df["Rank"] = df["Footfall"].rank(
    ascending=False, method="dense"
).astype(int)
df["PerformanceCategory"] = df["Footfall"].apply(
    lambda x: "High" if x >= df["Footfall"].mean()
    else "Low"
)
df = df.sort_values("Rank")
df.to_csv("data/store_performance_analysis.csv", index=False)
print("Store Performance Analysis completed!")
print(df)
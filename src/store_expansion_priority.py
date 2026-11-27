import pandas as pd
df = pd.read_csv("data/underserved_zones.csv")
df["ExpansionScore"] = (
    df["GPS_Activity"] * 0.5
    + df["UniqueDevices"] * 0.3
    + df["AvgDistance"] * 1000 * 0.2
)
df["PriorityRank"] = df["ExpansionScore"].rank(
    ascending=False,
    method="dense"
).astype(int)
df["Priority"] = df["PriorityRank"].apply(
    lambda x: "High Priority" if x == 1
    else "Medium Priority" if x <= 3
    else "Low Priority"
)
df = df.sort_values("PriorityRank")
df.to_csv("data/store_expansion_priority.csv", index=False)
print("\nStore Expansion Priority Ranking\n")
print(df[[
    "Zone",
    "GPS_Activity",
    "UniqueDevices",
    "AvgDistance",
    "ExpansionScore",
    "PriorityRank",
    "Priority"
]])
print("\nExpansion Priority Analysis completed successfully!")
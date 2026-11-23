import pandas as pd
from pathlib import Path
project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data"
df = pd.read_csv(data_folder / "location_opportunity_analysis.csv")
def generate_recommendation(row):
    footfall = row["Footfall"]
    competition = row["Nearby_Competitors"]
    risk = row["Cannibalization_Risk"]
    score = row["Opportunity_Score"]
    if score >= 70 and footfall > 0 and competition <= 1:
        return (
            "High potential location. "
            "Consider opening a new retail store."
        )
    elif score >= 70 and competition > 1:
        return (
            "High footfall but strong competition. "
            "Evaluate competitor strategy before expansion."
        )
    elif score >= 40 and risk >= 50:
        return (
            "Moderate opportunity with high cannibalization risk. "
            "Avoid placing a store too close to existing stores."
        )
    elif score >= 40:
        return (
            "Moderate opportunity. "
            "Collect more customer movement data before making a decision."
        )
    else:
        return (
            "Low opportunity. "
            "Consider avoiding this location for new store expansion."
        )
df["Smart_Recommendation"] = df.apply(
    generate_recommendation,
    axis=1
)
output_file = data_folder / "smart_recommendations.csv"
df.to_csv(output_file, index=False)
print("\n===== GEO PULSE SMART RECOMMENDATION SYSTEM =====\n")
for _, row in df.iterrows():
    print("----------------------------------------")
    print("Store:", row["StoreName"])
    print("Opportunity Score:", round(row["Opportunity_Score"], 2))
    print("Opportunity Level:", row["Opportunity_Level"])
    print("Footfall:", row["Footfall"])
    print("Nearby Competitors:", row["Nearby_Competitors"])
    print("Cannibalization Risk:", row["Cannibalization_Risk"], "%")
    print("\nRecommendation:")
    print(row["Smart_Recommendation"])
print("\n----------------------------------------")
print("Smart Recommendation Analysis Completed!")
print("Results saved to:", output_file)
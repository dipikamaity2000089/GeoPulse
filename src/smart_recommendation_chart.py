import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
project_folder = Path(__file__).resolve().parent.parent
data_folder = project_folder / "data"
df = pd.read_csv(data_folder / "smart_recommendations.csv")
df = df.sort_values(
    by="Opportunity_Score",
    ascending=False
)
plt.figure(figsize=(10, 6))
bars = plt.bar(
    df["StoreName"],
    df["Opportunity_Score"]
)
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.1f}",
        ha="center",
        va="bottom"
    )
plt.title("GeoPulse: Retail Location Opportunity Score")
plt.xlabel("Store Location")
plt.ylabel("Opportunity Score (0-100)")
plt.ylim(0, 110)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
output_file = data_folder / "smart_recommendation_chart.png"
plt.savefig(output_file, dpi=300)
plt.show()
print("Chart created successfully!")
print("Chart saved to:", output_file)
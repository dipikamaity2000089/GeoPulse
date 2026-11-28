import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("data/expansion_roi_prediction.csv")
plt.figure(figsize=(12, 7))
plt.bar(
    df["Candidate_Zone"],
    df["Monthly_Net_Profit"]
)
plt.axhline(
    y=0,
    linestyle="--",
    label="Break-Even Line"
)
plt.title("GeoPulse: Expansion ROI Comparison")
plt.xlabel("Candidate Zone")
plt.ylabel("Monthly Net Profit (₹)")
plt.legend()
plt.tight_layout()
plt.savefig(
    "data/expansion_roi_comparison_chart.png",
    dpi=300
)
plt.show()
print("ROI Comparison Chart created successfully!")
print("Chart saved to data/expansion_roi_comparison_chart.png")
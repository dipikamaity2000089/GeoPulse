import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("data/expansion_roi_prediction.csv")
break_even = pd.read_csv("data/expansion_break_even_analysis.csv")
df = df.merge(
    break_even[["Candidate_Zone", "Break_Even_Status"]],
    on="Candidate_Zone",
    how="left"
)
df = df.sort_values(
    by="Monthly_Net_Profit",
    ascending=False
)
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
axes[0, 0].bar(
    df["Candidate_Zone"],
    df["Monthly_Revenue"]
)
axes[0, 0].set_title("Monthly Revenue")
axes[0, 0].set_ylabel("Revenue (₹)")
axes[0, 1].bar(
    df["Candidate_Zone"],
    df["Monthly_Net_Profit"]
)
axes[0, 1].axhline(y=0, linestyle="--")
axes[0, 1].set_title("Monthly Net Profit / Loss")
axes[0, 1].set_ylabel("Profit (₹)")
axes[1, 0].bar(
    df["Candidate_Zone"],
    df["Monthly_ROI_Percent"]
)
axes[1, 0].axhline(y=0, linestyle="--")
axes[1, 0].set_title("Monthly ROI (%)")
axes[1, 0].set_ylabel("ROI (%)")
axes[1, 1].bar(
    df["Candidate_Zone"],
    df["Estimated_Customers"],
    label="Estimated Customers"
)
axes[1, 1].axhline(
    y=571.43,
    linestyle="--",
    label="Break-Even Customers"
)
axes[1, 1].set_title("Customer vs Break-Even")
axes[1, 1].set_ylabel("Customers")
axes[1, 1].legend()
fig.suptitle(
    "GeoPulse - Expansion Financial Dashboard",
    fontsize=16
)
plt.tight_layout()
plt.savefig(
    "data/expansion_financial_dashboard.png",
    dpi=300
)
plt.show()
print("Financial Dashboard created successfully!")
print("Saved to data/expansion_financial_dashboard.png")
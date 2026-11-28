import pandas as pd
df = pd.read_csv("data/expansion_roi_prediction.csv")
MONTHLY_OPERATIONAL_COST = 60000
AVERAGE_CUSTOMER_SPEND = 300
GROSS_MARGIN = 0.35
CONVERSION_RATE = 0.15
MONTHLY_ACTIVITY_FACTOR = 10
df["Break_Even_Revenue"] = (
    MONTHLY_OPERATIONAL_COST / GROSS_MARGIN
)
df["Break_Even_Customers"] = (
    MONTHLY_OPERATIONAL_COST
    / (AVERAGE_CUSTOMER_SPEND * GROSS_MARGIN)
)
df["Required_Visitors"] = (
    df["Break_Even_Customers"] / CONVERSION_RATE
)
df["Estimated_Monthly_Visitors"] = (
    df["GPS_Activity"] * MONTHLY_ACTIVITY_FACTOR
)
df["Estimated_Customers"] = (
    df["Estimated_Monthly_Visitors"] * CONVERSION_RATE
)
df["Break_Even_Status"] = df["Monthly_Net_Profit"].apply(
    lambda profit: "Above Break-Even"
    if profit >= 0
    else "Below Break-Even"
)
df.to_csv(
    "data/expansion_break_even_analysis.csv",
    index=False
)
print("\nGeoPulse: Expansion Break-Even Analysis\n")
print(
    df[[
        "Candidate_Zone",
        "Estimated_Customers",
        "Break_Even_Customers",
        "Break_Even_Revenue",
        "Required_Visitors",
        "Break_Even_Status"
    ]].round(2)
)
print("\nBreak-Even Analysis completed successfully!")
print("Results saved to data/expansion_break_even_analysis.csv")
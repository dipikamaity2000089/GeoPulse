import pandas as pd
df = pd.read_csv("data/what_if_expansion_simulation.csv")
INITIAL_INVESTMENT = 500000      
MONTHLY_OPERATIONAL_COST = 60000  
CONVERSION_RATE = 0.15            
AVERAGE_CUSTOMER_SPEND = 300       
GROSS_MARGIN = 0.35               
MONTHLY_ACTIVITY_FACTOR = 10       
df["Estimated_Monthly_Visitors"] = (
    df["GPS_Activity"] * MONTHLY_ACTIVITY_FACTOR
)
df["Estimated_Customers"] = (
    df["Estimated_Monthly_Visitors"] * CONVERSION_RATE
)
df["Monthly_Revenue"] = (
    df["Estimated_Customers"] * AVERAGE_CUSTOMER_SPEND
)
df["Gross_Profit"] = (
    df["Monthly_Revenue"] * GROSS_MARGIN
)
df["Monthly_Net_Profit"] = (
    df["Gross_Profit"] - MONTHLY_OPERATIONAL_COST
)
df["Monthly_ROI_Percent"] = (
    df["Monthly_Net_Profit"] / INITIAL_INVESTMENT
) * 100
df["Payback_Period_Months"] = (
    INITIAL_INVESTMENT / df["Monthly_Net_Profit"]
)
df.loc[
    df["Monthly_Net_Profit"] <= 0,
    "Payback_Period_Months"
] = float("inf")
df["Financial_Recommendation"] = df["Monthly_Net_Profit"].apply(
    lambda profit:
    "Recommended" if profit >= 50000
    else "Consider Carefully" if profit > 0
    else "Not Recommended"
)
df = df.sort_values(
    by="Monthly_Net_Profit",
    ascending=False
)
df.to_csv(
    "data/expansion_roi_prediction.csv",
    index=False
)
print("\nGeoPulse: Expansion ROI Prediction\n")
print(
    df[[
        "Candidate_Zone",
        "GPS_Activity",
        "Monthly_Revenue",
        "Monthly_Net_Profit",
        "Monthly_ROI_Percent",
        "Payback_Period_Months",
        "Financial_Recommendation"
    ]].round(2)
)
print("\nROI Prediction completed successfully!")
print("Results saved to data/expansion_roi_prediction.csv")
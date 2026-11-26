import pandas as pd
df = pd.read_csv("data/store_performance_analysis.csv")
total_footfall = df["Footfall"].sum()
average_footfall = df["Footfall"].mean()
best_store = df.loc[df["Footfall"].idxmax()]
lowest_store = df.loc[df["Footfall"].idxmin()]
insights = []
insights.append(
    f"Total store footfall is {total_footfall} GPS observations."
)
insights.append(
    f"Average footfall per store is {average_footfall:.2f}."
)
insights.append(
    f"{best_store['StoreName']} is the best-performing store "
    f"with {best_store['Footfall']} observations."
)
insights.append(
    f"{lowest_store['StoreName']} has the lowest footfall "
    f"with {lowest_store['Footfall']} observations."
)
for _, store in df.iterrows():
    if store["Footfall"] > average_footfall:
        insights.append(
            f"{store['StoreName']} is performing above average."
        )
    elif store["Footfall"] < average_footfall:
        insights.append(
            f"{store['StoreName']} is performing below average."
        )
    else:
        insights.append(
            f"{store['StoreName']} is performing at average level."
        )
print("\nGeoPulse: Store Performance Insights\n")
for i, insight in enumerate(insights, 1):
    print(f"{i}. {insight}")

insights_df = pd.DataFrame({"Insights": insights})
insights_df.to_csv(
    "data/store_performance_insights.csv",
    index=False
)
print("\nInsights generated and saved successfully!")
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("data/store_performance_analysis.csv")
plt.figure(figsize=(8, 5))
plt.bar(df["StoreName"], df["Footfall"])
plt.title("GeoPulse: Store-wise Footfall Performance")
plt.xlabel("Store Name")
plt.ylabel("Footfall")
plt.tight_layout()
plt.savefig("data/store_performance_chart.png", dpi=300)
plt.show()
print("Store Performance Chart created successfully!")
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv("data/store_expansion_priority.csv")
plt.figure(figsize=(10, 6))
plt.bar(
    df["Zone"],
    df["ExpansionScore"]
)
plt.title("GeoPulse: Store Expansion Priority")
plt.xlabel("Underserved Zones")
plt.ylabel("Expansion Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(
    "data/store_expansion_priority_chart.png",
    dpi=300
)
plt.show()
print("Store Expansion Priority Chart created successfully!")

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "store_location_recommendations.csv"

recommendations = pd.read_csv(OUTPUT_FILE)

print("=" * 65)
print("GEOPULSE RECOMMENDATION VALIDATION")
print("=" * 65)

checks = {}

checks["Total stores evaluated"] = len(recommendations) == 100
checks["Duplicate Store IDs"] = recommendations["Store_ID"].is_unique
checks["Duplicate ranks"] = recommendations["Location_Rank"].is_unique
checks["Ranks cover 1 to 100"] = sorted(recommendations["Location_Rank"].tolist()) == list(range(1, 101))
checks["Scores within 0-100"] = recommendations["Weighted_Score"].between(0, 100).all()
checks["No missing scores"] = recommendations["Weighted_Score"].notna().all()
checks["Ranking sorted correctly"] = recommendations.sort_values("Location_Rank")["Weighted_Score"].is_monotonic_decreasing

score_columns = [
    "Footfall_Score",
    "Competitor_Score",
    "Density_Score",
    "Mobility_Score",
    "Accessibility_Score"
]

checks["All scoring factors present"] = all(
    column in recommendations.columns for column in score_columns
)

for check, result in checks.items():
    status = "PASS" if result else "FAIL"
    print(f"{status:<8} | {check}")

print("-" * 65)
print(f"Checks Passed: {sum(checks.values())}/{len(checks)}")

if all(checks.values()):
    print("VALIDATION SUCCESSFUL")
else:
    print("VALIDATION FAILED - REVIEW REQUIRED")

expected_score = (
    recommendations["Footfall_Score"] * 0.35
    + recommendations["Competitor_Score"] * 0.25
    + recommendations["Density_Score"] * 0.15
    + recommendations["Mobility_Score"] * 0.15
    + recommendations["Accessibility_Score"] * 0.10
)

score_difference = (
    recommendations["Weighted_Score"] - expected_score
).abs()

checks["Weighted formula accuracy"] = score_difference.max() <= 0.011

print(f"Maximum formula difference: {score_difference.max():.6f}")

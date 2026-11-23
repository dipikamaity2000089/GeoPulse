import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

files = {
    "stores": RAW_DIR / "store_metadata.csv",
    "competitors": RAW_DIR / "competitor_locations.csv",
    "visits": RAW_DIR / "store_visits.csv",
    "pings": RAW_DIR / "gps_pings.csv"
}

stores = pd.read_csv(files["stores"])
competitors = pd.read_csv(files["competitors"])
visits = pd.read_csv(files["visits"])
pings = pd.read_csv(files["pings"])

report = []

def add_check(dataset, check, status, details):
    report.append({
        "Dataset": dataset,
        "Check": check,
        "Status": status,
        "Details": str(details)
    })

def check_required_columns(df, dataset, required):
    missing = [col for col in required if col not in df.columns]

    if missing:
        add_check(dataset, "Required columns", "FAIL", f"Missing columns: {missing}")
        return False

    add_check(dataset, "Required columns", "PASS", "All required columns present")
    return True

def check_missing_values(df, dataset, expected_null_columns=None, expected_null_mask=None):
    expected_null_columns = expected_null_columns or []
    expected_null_mask = expected_null_mask if expected_null_mask is not None else pd.Series(False, index=df.index)

    total_missing = int(df.isna().sum().sum())
    expected_missing = 0

    for column in expected_null_columns:
        if column in df.columns:
            expected_missing += int(df.loc[expected_null_mask, column].isna().sum())

    unexpected_missing = total_missing - expected_missing

    if unexpected_missing == 0 and expected_missing > 0:
        status = "INFO"
    elif unexpected_missing > 0:
        status = "FAIL"
    else:
        status = "PASS"

    add_check(
        dataset,
        "Missing values",
        status,
        f"Total missing: {total_missing} | Expected: {expected_missing} | Unexpected: {unexpected_missing}"
    )

def check_duplicate_ids(df, dataset, column):
    if column not in df.columns:
        add_check(dataset, f"Duplicate {column}", "SKIP", "Column not found")
        return

    duplicates = int(df[column].duplicated().sum())
    status = "PASS" if duplicates == 0 else "FAIL"

    add_check(dataset, f"Duplicate {column}", status, f"Duplicate count: {duplicates}")

def check_coordinates(df, dataset):
    if not {"Latitude", "Longitude"}.issubset(df.columns):
        add_check(dataset, "Coordinate validity", "SKIP", "Coordinate columns missing")
        return

    invalid = (
        ~df["Latitude"].between(-90, 90)
        | ~df["Longitude"].between(-180, 180)
        | df["Latitude"].isna()
        | df["Longitude"].isna()
    ).sum()

    status = "PASS" if invalid == 0 else "FAIL"

    add_check(dataset, "Coordinate validity", status, f"Invalid coordinates: {int(invalid)}")

def check_foreign_keys(child_df, column, parent_df, parent_column, label):
    if column not in child_df.columns or parent_column not in parent_df.columns:
        add_check("Relationships", label, "SKIP", "Required columns missing")
        return

    invalid = int((~child_df[column].isin(parent_df[parent_column])).sum())
    status = "PASS" if invalid == 0 else "FAIL"

    add_check("Relationships", label, status, f"Unmatched records: {invalid}")

print("=" * 65)
print("GEOPULSE — DATA QUALITY VALIDATION")
print("=" * 65)

required_columns = {
    "stores": [
        "Store_ID", "Store_Name", "Store_Category",
        "District", "Latitude", "Longitude"
    ],
    "competitors": [
        "Competitor_ID", "Competitor_Name",
        "Competitor_Category", "Latitude", "Longitude"
    ],
    "visits": [
        "Visit_ID", "Device_ID", "Store_ID",
        "Arrival_Time", "Departure_Time", "Dwell_Time_Minutes"
    ],
    "pings": [
        "Ping_ID", "Device_ID", "Visit_ID", "Store_ID",
        "Timestamp", "Latitude", "Longitude"
    ]
}

dataframes = {
    "stores": stores,
    "competitors": competitors,
    "visits": visits,
    "pings": pings
}

for dataset, df in dataframes.items():
    check_required_columns(df, dataset, required_columns[dataset])

# Expected missing values: previous-visit information for a device's first visit
expected_null_columns = [
    "Previous_Store_ID",
    "Previous_Visit_Time",
    "Hours_Since_Previous_Visit"
]

first_visit_mask = pd.Series(False, index=visits.index)

if {"Device_ID", "Arrival_Time"}.issubset(visits.columns):
    sorted_visits = visits.copy()
    sorted_visits["Arrival_Time"] = pd.to_datetime(
        sorted_visits["Arrival_Time"], errors="coerce"
    )
    first_visit_indices = sorted_visits.sort_values("Arrival_Time").groupby(
        "Device_ID"
    ).head(1).index
    first_visit_mask.loc[first_visit_indices] = True

for dataset, df in dataframes.items():
    if dataset == "visits":
        check_missing_values(
            df,
            dataset,
            expected_null_columns,
            first_visit_mask
        )
    else:
        check_missing_values(df, dataset)

# Duplicate ID checks
check_duplicate_ids(stores, "stores", "Store_ID")
check_duplicate_ids(competitors, "competitors", "Competitor_ID")
check_duplicate_ids(visits, "visits", "Visit_ID")
check_duplicate_ids(pings, "pings", "Ping_ID")

# Coordinate checks
check_coordinates(stores, "stores")
check_coordinates(competitors, "competitors")
check_coordinates(pings, "pings")

# Foreign key checks
check_foreign_keys(visits, "Store_ID", stores, "Store_ID", "Visits → Stores")
check_foreign_keys(pings, "Store_ID", stores, "Store_ID", "GPS Pings → Stores")
check_foreign_keys(pings, "Visit_ID", visits, "Visit_ID", "GPS Pings → Visits")

# Visit duration validation
if {"Arrival_Time", "Departure_Time"}.issubset(visits.columns):
    arrival = pd.to_datetime(visits["Arrival_Time"], errors="coerce")
    departure = pd.to_datetime(visits["Departure_Time"], errors="coerce")

    invalid_order = int((departure < arrival).sum())
    invalid_dates = int(arrival.isna().sum() + departure.isna().sum())

    add_check(
        "visits",
        "Arrival / Departure order",
        "PASS" if invalid_order == 0 else "FAIL",
        f"Departure before arrival: {invalid_order}"
    )

    add_check(
        "visits",
        "Timestamp validity",
        "PASS" if invalid_dates == 0 else "FAIL",
        f"Invalid timestamps: {invalid_dates}"
    )

    calculated_duration = (departure - arrival).dt.total_seconds() / 60

    if "Dwell_Time_Minutes" in visits.columns:
        stored_duration = pd.to_numeric(visits["Dwell_Time_Minutes"], errors="coerce")
        mismatch = int(
            (~calculated_duration.round(2).eq(stored_duration.round(2))).sum()
        )

        add_check(
            "visits",
            "Dwell time consistency",
            "PASS" if mismatch == 0 else "FAIL",
            f"Duration mismatches: {mismatch}"
        )

# GPS timestamp validation
if "Timestamp" in pings.columns:
    timestamps = pd.to_datetime(pings["Timestamp"], errors="coerce")
    invalid_timestamps = int(timestamps.isna().sum())

    add_check(
        "pings",
        "Timestamp validity",
        "PASS" if invalid_timestamps == 0 else "FAIL",
        f"Invalid timestamps: {invalid_timestamps}"
    )

# Device coverage
if "Device_ID" in visits.columns and "Device_ID" in pings.columns:
    visit_devices = visits["Device_ID"].nunique()
    ping_devices = pings["Device_ID"].nunique()

    add_check(
        "Coverage",
        "Unique devices",
        "PASS" if visit_devices == ping_devices else "FAIL",
        f"Devices in visits: {visit_devices}, devices in pings: {ping_devices}"
    )

# Store coverage
visited_stores = visits["Store_ID"].nunique()
total_stores = stores["Store_ID"].nunique()

unvisited_stores = int(
    (~stores["Store_ID"].isin(visits["Store_ID"])).sum()
)

add_check(
    "Coverage",
    "Store visit coverage",
    "PASS" if unvisited_stores == 0 else "INFO",
    f"Visited stores: {visited_stores}/{total_stores}, stores without visits: {unvisited_stores}"
)

# Save report
report_df = pd.DataFrame(report)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

report_path = PROCESSED_DIR / "data_quality_report.csv"
report_df.to_csv(report_path, index=False)

# Display report
print("\nVALIDATION RESULTS")
print("-" * 65)

for _, row in report_df.iterrows():
    print(f"[{row['Status']}] {row['Dataset']} | {row['Check']}")
    print(f"       {row['Details']}")

print("-" * 65)

passed = (report_df["Status"] == "PASS").sum()
failed = (report_df["Status"] == "FAIL").sum()
info = (report_df["Status"] == "INFO").sum()
skipped = (report_df["Status"] == "SKIP").sum()

print(f"Total Checks : {len(report_df)}")
print(f"Passed      : {passed}")
print(f"Info        : {info}")
print(f"Failed      : {failed}")
print(f"Skipped     : {skipped}")
print(f"Report Saved: {report_path}")

print("=" * 65)
print("VALIDATION COMPLETED")
print("=" * 65)
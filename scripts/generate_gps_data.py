import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

START_DATE = datetime(2026, 8, 1)
TOTAL_DAYS = 90
TOTAL_DEVICES = 5000
TOTAL_STORES = 100
TOTAL_COMPETITORS = 60

categories = [
    "Supermarket",
    "Fashion",
    "Electronics",
    "Grocery",
    "Shopping Mall",
    "Home & Living",
    "Convenience Store",
    "Discount Retail",
    "Pharmacy",
    "Sports & Lifestyle"
]

districts = [
    "Central", "North", "South", "East", "West",
    "Urban Core", "Suburban North", "Suburban South",
    "Commercial District", "Residential Zone", "Transit Zone"
]

device_types = ["Android", "iOS"]

# Synthetic study area
LAT_MIN, LAT_MAX = 13.0200, 13.1100
LON_MIN, LON_MAX = 80.2200, 80.3000

store_records = []
competitor_records = []
visit_records = []
ping_records = []

stores = {}

# ------------------------------------------
# 1. GENERATE 100 STORE LOCATIONS
# ------------------------------------------

for i in range(1, TOTAL_STORES + 1):

    store_id = f"ST{i:03d}"
    category = random.choice(categories)
    district = random.choice(districts)

    latitude = random.uniform(LAT_MIN, LAT_MAX)
    longitude = random.uniform(LON_MIN, LON_MAX)

    area_sqft = random.randint(1500, 50000)
    capacity = int(area_sqft / random.uniform(25, 60))

    popularity = random.uniform(0.5, 2.5)

    opening_hour = random.choice([8, 9, 10])
    closing_hour = random.choice([20, 21, 22, 23])

    stores[store_id] = {
        "Store_Name": f"{category.replace(' ', '')}_{i:03d}",
        "Store_Category": category,
        "District": district,
        "Latitude": latitude,
        "Longitude": longitude,
        "Popularity": popularity
    }

    store_records.append({
        "Store_ID": store_id,
        "Store_Name": stores[store_id]["Store_Name"],
        "Store_Category": category,
        "District": district,
        "Latitude": round(latitude, 6),
        "Longitude": round(longitude, 6),
        "Store_Area_SqFt": area_sqft,
        "Estimated_Capacity": capacity,
        "Opening_Hour": f"{opening_hour:02d}:00",
        "Closing_Hour": f"{closing_hour:02d}:00",
        "Parking_Available": random.choice([True, False]),
        "Nearby_Transit_Access": random.choice([True, False]),
        "Popularity_Score": round(popularity, 2),
        "Store_Status": "Active"
    })

store_df = pd.DataFrame(store_records)

# ------------------------------------------
# 2. GENERATE 60 COMPETITOR LOCATIONS
# ------------------------------------------

competitor_types = [
    "Supermarket",
    "Fashion",
    "Electronics",
    "Grocery",
    "Shopping Mall",
    "Home & Living",
    "Convenience Store",
    "Discount Retail"
]

for i in range(1, TOTAL_COMPETITORS + 1):

    competitor_records.append({
        "Competitor_ID": f"COMP{i:03d}",
        "Competitor_Name": f"Competitor_{i:03d}",
        "Competitor_Category": random.choice(competitor_types),
        "District": random.choice(districts),
        "Latitude": round(random.uniform(LAT_MIN, LAT_MAX), 6),
        "Longitude": round(random.uniform(LON_MIN, LON_MAX), 6),
        "Estimated_Size_SqFt": random.randint(1000, 40000),
        "Price_Segment": random.choice(["Budget", "Mid-Range", "Premium"]),
        "Parking_Available": random.choice([True, False])
    })

competitor_df = pd.DataFrame(competitor_records)

# ------------------------------------------
# 3. GENERATE SYNTHETIC DEVICE PROFILES
# ------------------------------------------

device_profiles = {}

store_ids = list(stores.keys())
store_weights = [stores[s]["Popularity"] for s in store_ids]

for i in range(1, TOTAL_DEVICES + 1):

    device_id = f"DEV{i:06d}"

    preferred_store = random.choices(
        store_ids,
        weights=store_weights,
        k=1
    )[0]

    device_profiles[device_id] = {
        "Device_Type": random.choice(device_types),
        "Preferred_Store": preferred_store
    }

# ------------------------------------------
# 4. GENERATE 90 DAYS OF VISITS & GPS PINGS
# ------------------------------------------

for device_id, profile in device_profiles.items():

    preferred_store = profile["Preferred_Store"]

    for day in range(TOTAL_DAYS):

        current_date = START_DATE + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5

        visit_probability = 0.17 if is_weekend else 0.12

        if random.random() > visit_probability:
            continue

        visits_per_day = random.choices(
            [1, 2, 3],
            weights=[80, 18, 2],
            k=1
        )[0]

        for visit_number in range(visits_per_day):

            if random.random() < 0.35:
                store_id = preferred_store
            else:
                store_id = random.choices(
                    store_ids,
                    weights=store_weights,
                    k=1
                )[0]

            store = stores[store_id]

            # Visit time
            arrival_hour = random.choices(
                [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                weights=[3, 5, 8, 10, 8, 7, 8, 10, 12, 13, 10, 6],
                k=1
            )[0]

            arrival_time = current_date + timedelta(
                hours=arrival_hour,
                minutes=random.randint(0, 59)
            )

            dwell_minutes = random.randint(10, 180)
            departure_time = arrival_time + timedelta(minutes=dwell_minutes)

            visit_id = f"VIS{len(visit_records) + 1:09d}"

            ping_interval = random.choice([5, 10, 15])
            ping_count = max(2, dwell_minutes // ping_interval)

            visit_records.append({
                "Visit_ID": visit_id,
                "Device_ID": device_id,
                "Store_ID": store_id,
                "Store_Category": store["Store_Category"],
                "District": store["District"],
                "Arrival_Time": arrival_time,
                "Departure_Time": departure_time,
                "Dwell_Time_Minutes": dwell_minutes,
                "Visit_Date": current_date.date(),
                "Day_Of_Week": current_date.strftime("%A"),
                "Day_Type": "Weekend" if is_weekend else "Weekday",
                "Arrival_Hour": arrival_hour,
                "Time_Slot": (
                    "Morning" if arrival_hour < 12
                    else "Afternoon" if arrival_hour < 17
                    else "Evening"
                ),
                "Visit_Sequence": 0,
                "Repeat_Visit": False,
                "Visit_Duration_Category": (
                    "Short" if dwell_minutes <= 30
                    else "Medium" if dwell_minutes <= 60
                    else "Long" if dwell_minutes <= 120
                    else "Extended"
                ),
                "Ping_Interval_Minutes": ping_interval
            })

            # GPS pings during the simulated visit
            for ping_num in range(ping_count):

                ping_time = arrival_time + timedelta(
                    minutes=ping_num * ping_interval
                )

                if ping_time > departure_time:
                    break

                latitude = store["Latitude"] + random.uniform(-0.0012, 0.0012)
                longitude = store["Longitude"] + random.uniform(-0.0012, 0.0012)

                ping_records.append({
                    "Ping_ID": f"PING{len(ping_records) + 1:010d}",
                    "Device_ID": device_id,
                    "Visit_ID": visit_id,
                    "Store_ID": store_id,
                    "Timestamp": ping_time,
                    "Latitude": round(latitude, 6),
                    "Longitude": round(longitude, 6),
                    "Location_Accuracy_Meters": random.randint(5, 50),
                    "Signal_Strength": random.randint(1, 5),
                    "Device_Type": profile["Device_Type"],
                    "Ping_Interval_Minutes": ping_interval,
                    "Day_Type": "Weekend" if is_weekend else "Weekday",
                    "Time_Slot": (
                        "Morning" if arrival_hour < 12
                        else "Afternoon" if arrival_hour < 17
                        else "Evening"
                    )
                })

# ------------------------------------------
# 5. PROCESS VISIT SEQUENCES
# ------------------------------------------

visit_df = pd.DataFrame(visit_records)

if not visit_df.empty:

    visit_df = visit_df.sort_values(
        ["Device_ID", "Arrival_Time"]
    ).reset_index(drop=True)

    visit_df["Visit_Sequence"] = (
        visit_df.groupby("Device_ID").cumcount() + 1
    )

    visit_df["Repeat_Visit"] = (
        visit_df.groupby(["Device_ID", "Store_ID"]).cumcount() > 0
    )

    visit_df["Previous_Store_ID"] = (
        visit_df.groupby("Device_ID")["Store_ID"].shift(1)
    )

    visit_df["Previous_Visit_Time"] = (
        visit_df.groupby("Device_ID")["Arrival_Time"].shift(1)
    )

    visit_df["Hours_Since_Previous_Visit"] = (
        (
            visit_df["Arrival_Time"]
            - visit_df["Previous_Visit_Time"]
        ).dt.total_seconds() / 3600
    ).round(2)

# ------------------------------------------
# 6. SORT GPS PINGS
# ------------------------------------------

ping_df = pd.DataFrame(ping_records)

if not ping_df.empty:
    ping_df = ping_df.sort_values(
        ["Timestamp", "Device_ID"]
    ).reset_index(drop=True)

# ------------------------------------------
# 7. SAVE DATASETS
# ------------------------------------------

RAW_DIR.mkdir(parents=True, exist_ok=True)

store_df.to_csv(RAW_DIR / "store_metadata.csv", index=False)
competitor_df.to_csv(RAW_DIR / "competitor_locations.csv", index=False)
visit_df.to_csv(RAW_DIR / "store_visits.csv", index=False)
ping_df.to_csv(RAW_DIR / "gps_pings.csv", index=False)

# ------------------------------------------
# 8. GENERATION SUMMARY
# ------------------------------------------

print("=" * 60)
print("GEOPULSE — DATA GENERATION REPORT")
print("=" * 60)

print(f"Simulation Start       : {START_DATE.date()}")
print(f"Simulation End        : {(START_DATE + timedelta(days=TOTAL_DAYS-1)).date()}")
print(f"Simulation Days       : {TOTAL_DAYS}")
print(f"Synthetic Devices     : {TOTAL_DEVICES:,}")
print(f"Retail Stores        : {len(store_df):,}")
print(f"Competitor Locations : {len(competitor_df):,}")
print(f"Total Store Visits  : {len(visit_df):,}")
print(f"Total GPS Pings     : {len(ping_df):,}")

print("-" * 60)
print("DATASET FILES")
print("-" * 60)

for filename in [
    "store_metadata.csv",
    "competitor_locations.csv",
    "store_visits.csv",
    "gps_pings.csv"
]:
    print(f"data/raw/{filename}")

print("=" * 60)
print("DATA GENERATION COMPLETED")
print("=" * 60)
import csv
import json
from pathlib import Path
import pandas as pd


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Raw dataset directory
DATA_DIR = PROJECT_ROOT / "data" / "raw" / "geopulse_synthetic_dataset"


# Required columns for each dataset
REQUIRED_COLUMNS = {
    "store_locations.csv": [
        "store_id", "store_name", "city", "country",
        "store_category", "latitude", "longitude",
        "catchment_radius_km", "data_type"
    ],
    "competitor_locations.csv": [
        "competitor_id", "competitor_name", "city",
        "competitor_category", "latitude", "longitude",
        "data_type"
    ],
    "candidate_locations.csv": [
        "candidate_id", "candidate_name", "city",
        "proposed_store_category", "latitude", "longitude",
        "estimated_rent_index", "target_catchment_radius_km",
        "data_type"
    ],
    "footfall_observations.csv": [
        "store_id", "city", "timestamp", "visitor_count",
        "latitude", "longitude", "data_type"
    ],
    "mobility_flows.csv": [
        "date", "city", "origin_zone_id",
        "origin_latitude", "origin_longitude",
        "destination_store_id", "destination_latitude",
        "destination_longitude", "estimated_trips",
        "distance_km", "data_type"
    ],
    "mobility_zones.csv": [
        "zone_id", "zone_name", "city",
        "centroid_latitude", "centroid_longitude",
        "data_type"
    ]
}


def load_csv(filename, required_columns):
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {filename}")

    df = pd.read_csv(file_path)

    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{filename} is missing columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    return df

def load_metadata():
    """Load the dataset metadata JSON file."""

    metadata_path = DATA_DIR / "dataset_metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError("Missing file: dataset_metadata.json")

    with metadata_path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)

def convert_data_types(datasets):
    numeric_columns = {
        "store_locations.csv": [
            "latitude", "longitude", "catchment_radius_km"
        ],
        "competitor_locations.csv": [
            "latitude", "longitude"
        ],
        "candidate_locations.csv": [
            "latitude", "longitude",
            "estimated_rent_index", "target_catchment_radius_km"
        ],
        "footfall_observations.csv": [
            "visitor_count", "latitude", "longitude"
        ],
        "mobility_flows.csv": [
            "origin_latitude", "origin_longitude",
            "destination_latitude", "destination_longitude",
            "estimated_trips", "distance_km"
        ],
        "mobility_zones.csv": [
            "centroid_latitude", "centroid_longitude"
        ]
    }

    for filename, columns in numeric_columns.items():
        for column in columns:
            datasets[filename][column] = pd.to_numeric(
                datasets[filename][column],
                errors="raise"
            )

    datasets["footfall_observations.csv"]["timestamp"] = pd.to_datetime(
        datasets["footfall_observations.csv"]["timestamp"],
        errors="raise"
    )

    datasets["mobility_flows.csv"]["date"] = pd.to_datetime(
        datasets["mobility_flows.csv"]["date"],
        errors="raise"
    )

    print("[OK] Numeric and date columns converted successfully")

    return datasets


def clean_text_data(datasets):
    text_columns = {
        "store_locations.csv": [
            "store_id", "store_name", "city",
            "country", "store_category", "data_type"
        ],
        "competitor_locations.csv": [
            "competitor_id", "competitor_name",
            "city", "competitor_category", "data_type"
        ],
        "candidate_locations.csv": [
            "candidate_id", "candidate_name",
            "city", "proposed_store_category", "data_type"
        ],
        "footfall_observations.csv": [
            "store_id", "city", "data_type"
        ],
        "mobility_flows.csv": [
            "city", "origin_zone_id",
            "destination_store_id", "data_type"
        ],
        "mobility_zones.csv": [
            "zone_id", "zone_name", "city", "data_type"
        ]
    }

    print("\n" + "=" * 55)
    print("GEOPULSE TEXT CLEANING")
    print("=" * 55)

    for filename, columns in text_columns.items():
        df = datasets[filename]

        for column in columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
            )

        print(f"[OK] Cleaned text columns: {filename}")

    print("Text cleaning completed successfully.")
    print("=" * 55)

    return datasets


def validate_data(datasets):
    print("\n" + "=" * 55)
    print("GEOPULSE DATA VALIDATION")
    print("=" * 55)

    validation_passed = True

    coordinate_columns = {
        "store_locations.csv": ["latitude", "longitude"],
        "competitor_locations.csv": ["latitude", "longitude"],
        "candidate_locations.csv": ["latitude", "longitude"],
        "footfall_observations.csv": ["latitude", "longitude"],
        "mobility_flows.csv": [
            "origin_latitude", "origin_longitude",
            "destination_latitude", "destination_longitude"
        ],
        "mobility_zones.csv": [
            "centroid_latitude", "centroid_longitude"
        ]
    }

    unique_keys = {
        "store_locations.csv": ["store_id"],
        "competitor_locations.csv": ["competitor_id"],
        "candidate_locations.csv": ["candidate_id"],
        "mobility_zones.csv": ["zone_id"],
        "footfall_observations.csv": ["store_id", "timestamp"],
        "mobility_flows.csv": [
            "date", "origin_zone_id", "destination_store_id"
        ]
    }

    non_negative_columns = {
        "store_locations.csv": ["catchment_radius_km"],
        "candidate_locations.csv": [
            "estimated_rent_index", "target_catchment_radius_km"
        ],
        "footfall_observations.csv": ["visitor_count"],
        "mobility_flows.csv": ["distance_km", "estimated_trips"]
    }

    for filename, df in datasets.items():
        print(f"\n{filename}")

        missing = int(df.isnull().sum().sum())
        print(f"Missing values: {missing}")

        if missing > 0:
            validation_passed = False

        invalid_coordinates = 0

        for column in coordinate_columns[filename]:
            if "latitude" in column:
                invalid_coordinates += int(
                    ((df[column] < -90) | (df[column] > 90)).sum()
                )
            else:
                invalid_coordinates += int(
                    ((df[column] < -180) | (df[column] > 180)).sum()
                )

        print(f"Invalid coordinates: {invalid_coordinates}")

        if invalid_coordinates > 0:
            validation_passed = False

        duplicate_count = int(
            df.duplicated(subset=unique_keys[filename]).sum()
        )

        print(f"Duplicate records: {duplicate_count}")

        if duplicate_count > 0:
            validation_passed = False

        for column in non_negative_columns.get(filename, []):
            negative_count = int((df[column] < 0).sum())

            print(f"Negative {column}: {negative_count}")

            if negative_count > 0:
                validation_passed = False

    print("\n" + "=" * 55)
    print("REFERENTIAL INTEGRITY VALIDATION")
    print("=" * 55)

    stores = datasets["store_locations.csv"]
    zones = datasets["mobility_zones.csv"]
    footfall = datasets["footfall_observations.csv"]
    flows = datasets["mobility_flows.csv"]

    store_ids = set(stores["store_id"])
    zone_ids = set(zones["zone_id"])

    # Check 1: Footfall records reference existing stores
    invalid_footfall_stores = int(
        (~footfall["store_id"].isin(store_ids)).sum()
    )

    print(
        f"Unmatched footfall store IDs: "
        f"{invalid_footfall_stores}"
    )

    # Check 2: Mobility flows reference existing stores
    invalid_flow_stores = int(
        (~flows["destination_store_id"].isin(store_ids)).sum()
    )

    print(
        f"Unmatched mobility destination store IDs: "
        f"{invalid_flow_stores}"
    )

    # Check 3: Mobility flows reference existing zones
    invalid_flow_zones = int(
        (~flows["origin_zone_id"].isin(zone_ids)).sum()
    )

    print(
        f"Unmatched mobility origin zone IDs: "
        f"{invalid_flow_zones}"
    )

    # Check 4: Destination store city matches flow city
    store_city_map = stores.set_index("store_id")["city"]

    destination_cities = flows["destination_store_id"].map(
        store_city_map
    )

    destination_city_mismatches = int(
        (flows["city"] != destination_cities).sum()
    )

    print(
        f"Destination store city mismatches: "
        f"{destination_city_mismatches}"
    )

    # Check 5: Origin zone city matches flow city
    zone_city_map = zones.set_index("zone_id")["city"]

    origin_cities = flows["origin_zone_id"].map(zone_city_map)

    origin_city_mismatches = int(
        (flows["city"] != origin_cities).sum()
    )

    print(
        f"Origin zone city mismatches: "
        f"{origin_city_mismatches}"
    )

    relationship_errors = (
        invalid_footfall_stores
        + invalid_flow_stores
        + invalid_flow_zones
        + destination_city_mismatches
        + origin_city_mismatches
    )

    if relationship_errors > 0:
        validation_passed = False

    print(
        "Referential integrity:",
        "PASSED" if relationship_errors == 0 else "FAILED"
    )
    print("=" * 55)

    print("\nOverall validation:",
          "PASSED" if validation_passed else "FAILED")
    print("=" * 55)

    return validation_passed

def save_processed_data(datasets):
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 55)
    print("SAVING PROCESSED DATA")
    print("=" * 55)

    for filename, df in datasets.items():
        output_path = PROCESSED_DIR / filename
        df.to_csv(output_path, index=False)

        print(f"[OK] Saved {filename}: {len(df):,} records")

    print("All processed datasets saved successfully.")
    print("=" * 55)

def main():
    print("=" * 55)
    print("GEOPULSE DATA LOADING")
    print("=" * 55)

    total_records = 0
    datasets = {}

    for filename, columns in REQUIRED_COLUMNS.items():
        try:
            records = load_csv(filename, columns)
            datasets[filename] = records
            total_records += len(records)

            print(f"[OK] {filename}: {len(records):,} records")

        except (OSError, ValueError, csv.Error) as error:
            print(f"[ERROR] {error}")
            return

    try:
        metadata = load_metadata()
        print("[OK] dataset_metadata.json loaded successfully")

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"[ERROR] Metadata loading failed: {error}")
        return

    try:
        datasets = convert_data_types(datasets)
        datasets = clean_text_data(datasets)

    except (ValueError, TypeError) as error:
        print(f"[ERROR] Data preparation failed: {error}")
        return

    if not validate_data(datasets):
        print("[ERROR] Data validation failed. Processed files were not saved.")
        return

    save_processed_data(datasets)

    print("-" * 55)
    print(f"Total CSV records loaded: {total_records:,}")
    print(f"Datasets loaded: {len(datasets)}")
    print("Metadata type:", type(metadata).__name__)
    print("Data loading completed successfully.")
    print("=" * 55)


if __name__ == "__main__":
    main()

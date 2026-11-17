from pathlib import Path

import pandas as pd
import geopandas as gpd


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
GEOSPATIAL_DIR = PROCESSED_DIR / "geospatial"

# Geographic coordinate reference system
SOURCE_CRS = "EPSG:4326"


def create_geospatial_data(filename):
    file_path = PROCESSED_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Missing processed file: {filename}")

    df = pd.read_csv(file_path)

    required_columns = {"latitude", "longitude"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"{filename} is missing columns: "
            f"{', '.join(sorted(missing_columns))}"
        )

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(
            df["longitude"],
            df["latitude"]
        ),
        crs=SOURCE_CRS
    )

    print(f"[OK] {filename}: {len(gdf)} geographic points created")

    return gdf

def validate_geospatial_data(gdf, filename):
    invalid_geometry_count = int((~gdf.geometry.is_valid).sum())
    empty_geometry_count = int(gdf.geometry.is_empty.sum())

    missing_geometry_count = int(gdf.geometry.isna().sum())

    crs_valid = gdf.crs == SOURCE_CRS

    print(f"\nGeospatial validation: {filename}")
    print(f"Invalid geometries: {invalid_geometry_count}")
    print(f"Empty geometries: {empty_geometry_count}")
    print(f"Missing geometries: {missing_geometry_count}")
    print(f"CRS validation: {'PASSED' if crs_valid else 'FAILED'}")

    validation_passed = (
        invalid_geometry_count == 0
        and empty_geometry_count == 0
        and missing_geometry_count == 0
        and crs_valid
    )

    print(
        "Geospatial validation:",
        "PASSED" if validation_passed else "FAILED"
    )

    return validation_passed


def main():
    print("=" * 55)
    print("GEOPULSE GEOSPATIAL DATA PREPARATION")
    print("=" * 55)

    GEOSPATIAL_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Source directory: {PROCESSED_DIR}")
    print(f"Output directory: {GEOSPATIAL_DIR}")
    print(f"Source CRS: {SOURCE_CRS}")

    location_files = [
        "store_locations.csv",
        "competitor_locations.csv",
        "candidate_locations.csv"
    ]

    geospatial_datasets = {}

    overall_validation_passed = True

    for filename in location_files:
        gdf = create_geospatial_data(filename)

        validation_passed = validate_geospatial_data(
            gdf, filename
        )

        if not validation_passed:
            overall_validation_passed = False

        geospatial_datasets[filename] = gdf

    print("\n" + "=" * 55)
    print(
        "OVERALL GEOSPATIAL VALIDATION:",
        "PASSED" if overall_validation_passed else "FAILED"
    )
    print("=" * 55)

    if not overall_validation_passed:
        print("[ERROR] Geospatial validation failed.")
        return

    print("\nSAVING GEOSPATIAL DATA")

    output_names = {
        "store_locations.csv": "stores.geojson",
        "competitor_locations.csv": "competitors.geojson",
        "candidate_locations.csv": "candidates.geojson"
    }

    for filename, gdf in geospatial_datasets.items():
        output_file = GEOSPATIAL_DIR / output_names[filename]

        gdf.to_file(output_file, driver="GeoJSON")

        print(f"[OK] Saved {output_file.name}: {len(gdf)} points")

    print("\nGeospatial dataset preparation completed.")
    print("=" * 55)


if __name__ == "__main__":
    main()

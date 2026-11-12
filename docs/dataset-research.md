# GeoPulse Dataset Research

**Project:** GeoPulse – Hyper-Local Retail Mobility Analytics
**Research status:** Initial research completed; synthetic development dataset selected for prototype development. Final production dataset is pending mentor/team confirmation.
**Geographic scope:** City-independent. The system should support data from different cities rather than being hardcoded to one location.

## 1. Research Objective

Identify suitable datasets for the six proposed GeoPulse features:

1. Smart Footfall Heatmap
2. Store Cannibalization Detection
3. Time-Based Mobility Analysis
4. Transparent Smart Store Recommendation
5. Competitor Proximity Analysis
6. What-If Location Simulator

No official dataset has been provided by the mentor or team. Therefore, an assistant-generated synthetic dataset has been prepared for initial development and testing. External sources remain candidates for future evaluation and real-world data integration.

## 2. Data Requirements

| Data requirement | Useful information | Supported features |
|---|---|---|
| Retail locations | Store name, category, latitude, longitude | Competitor proximity, recommendations |
| Mobility data | Movement records, timestamps, spatial locations | Heatmaps, time-based analysis |
| Footfall data | Visitor counts, timestamps, sensor/location details | Heatmaps, mobility analysis |
| Geographic boundaries | City boundaries, area polygons | Catchment and spatial analysis |
| Candidate locations | Candidate ID, coordinates, store category | Recommendations, simulator |

**Important:** Store locations are not footfall data. Mobility trajectories are not automatically retail visits. These data types must be distinguished in the project.

## 3. Candidate Data Sources

### 3.1 WorldMove

- Coverage: More than 1,600 cities across 179 countries.
- Data type: Synthetic human mobility trajectories, city boundaries, regional divisions, POI distributions and commuting matrices.
- Potential use: Multi-city mobility experiments and prototype testing.
- Limitation: Mobility trajectories are synthetic, not actual measured retail footfall.
- Status: Potential supplementary source for prototype testing.

Links:
- Research paper: https://www.nature.com/articles/s41597-026-06555-2
- GitHub: https://github.com/tsinghua-fib-lab/WorldMove
- Data portal: https://fi.ee.tsinghua.edu.cn/worldmove/

### 3.2 OpenStreetMap

- Coverage: Geographic data across many countries and regions.
- Data type: Shops, amenities, roads and other geographic points of interest.
- Potential use: Store locations, competitor identification and proximity analysis.
- Limitation: Does not provide visitor counts or actual retail footfall. Data completeness can vary by location.
- Licence: Open Database Licence (ODbL); attribution and other licence obligations must be followed.
- Status: Candidate for geographic store and competitor data.

Links:
- Website: https://www.openstreetmap.org/
- Licence: https://www.openstreetmap.org/copyright

### 3.3 Google Places Insights

- Coverage: Supported city and country listings.
- Data type: Aggregated business counts, POI density, categories and other place attributes.
- Potential use: Competitor density and location comparison.
- Limitation: Requires product access and Google Cloud/BigQuery setup. Full datasets require a subscription. It does not provide direct human footfall measurements.
- Status: Optional candidate, subject to access and cost approval.

Links:
- Overview: https://developers.google.com/maps/documentation/placesinsights/overview
- Data coverage: https://developers.google.com/maps/documentation/placesinsights/about-data
- Setup: https://developers.google.com/maps/documentation/placesinsights/cloud-setup

### 3.4 Johannesburg Shopping Mall Visits Dataset

- Coverage: Three major shopping malls in Johannesburg, South Africa, during 2022–2023.
- Data type: Consumer visit observations collected through smartphone signal tracking.
- Potential use: Real-world retail mobility case study and visit-pattern analysis.
- Limitation: Limited to three malls in one city; not suitable as a global dataset.
- Licence: CC BY 4.0, according to the dataset record.
- Status: Candidate supplementary real-world dataset.

Links:
- Dataset: https://data.mendeley.com/datasets/pzpnbk5xz2/5
- Research article: https://www.sciencedirect.com/science/article/pii/S2352340926002015

### 3.5 UK SmartStreetSensor Footfall Data

- Coverage: 1,151 sensor locations across 107 cities in Great Britain.
- Period: 2015–2020.
- Data type: Five-minute aggregated footfall estimates derived from passive Wi-Fi sensor observations.
- Potential use: Time-based footfall analysis and heatmap methodology.
- Limitation: UK-only, historical data. The data service lists its licence as "Other (Not Open)"; access and reuse permission must be checked.
- Status: Research reference until permission is confirmed.

Link:
https://data.geods.ac.uk/dataset/local-data-company-smartstreetsensor-footfall-data

## 4. Preliminary Comparison

| Source | Geographic coverage | Actual retail footfall? | Main purpose |
|---|---|---|---|
| WorldMove | 1,600+ cities | No – synthetic mobility | Mobility prototype |
| OpenStreetMap | Broad geographic coverage | No | Store and competitor locations |
| Google Places Insights | Supported locations | No | POI density |
| Johannesburg dataset | Three malls | Reported visit observations | Real-world case study |
| UK SmartStreetSensor | Great Britain | Footfall estimates | Historical footfall analysis |
| GeoPulse synthetic dataset | Five example cities | No – simulated counts and flows | Initial development and testing |

## 5. Selected Development Dataset

### 5.1 Dataset Overview

For initial development, a synthetic dataset was generated specifically for GeoPulse.

The dataset includes five example cities:

- Chennai
- Mumbai
- Bengaluru
- London
- Singapore

The system is designed to be city-independent. These cities are sample data locations and do not restrict future use in other supported cities.

**Dataset type:** Synthetic
**Purpose:** Prototype development, testing and demonstration
**Observation period:** 1 October 2026 to 14 October 2026
**Total CSV records:** 14,165
**Status:** Downloaded, extracted, inspected and initially validated.

### 5.2 Dataset Files

| File | Records | Description |
|---|---:|---|
| store_locations.csv | 50 | Synthetic retail store locations |
| competitor_locations.csv | 60 | Synthetic competitor locations |
| candidate_locations.csv | 25 | Proposed candidate store locations |
| footfall_observations.csv | 9,800 | Hourly simulated visitor counts |
| mobility_flows.csv | 4,200 | Simulated origin-zone-to-store trip aggregates |
| mobility_zones.csv | 30 | Synthetic mobility-zone centroids |
| **Total** | **14,165** | **Six CSV files** |

The dataset also contains:
- `README.md` – dataset description, structure and limitations.
- `dataset_metadata.json` – dataset metadata.

### 5.3 Feature Mapping

| Dataset file | Intended GeoPulse features |
|---|---|
| store_locations.csv | Store analysis, catchment and recommendations |
| competitor_locations.csv | Competitor proximity and cannibalization |
| candidate_locations.csv | Store recommendations and what-if simulation |
| footfall_observations.csv | Footfall heatmap and time-based analysis |
| mobility_flows.csv | Mobility analysis and catchment estimation |
| mobility_zones.csv | Geographic analysis and mobility visualization |

### 5.4 Important Relationships

The following relationships are used to connect the CSV files:

1. `footfall_observations.store_id` → `store_locations.store_id`
2. `mobility_flows.destination_store_id` → `store_locations.store_id`
3. `mobility_flows.origin_zone_id` → `mobility_zones.zone_id`

These relationships allow store-level footfall and mobility information to be combined with location data.

## 6. Initial Dataset Validation

Initial structural and consistency checks were performed using Windows PowerShell.

### 6.1 Validation Results

| Validation check | Result |
|---|---|
| CSV record count | 14,165 records inspected |
| Missing values | 0 found |
| Duplicate rows | 0 duplicate groups |
| Invalid coordinate ranges | 0 found |
| Unmatched footfall store IDs | 0 |
| Unmatched mobility destination store IDs | 0 |
| Unmatched mobility origin-zone IDs | 0 |
| Mobility flow city mismatches | 0 |
| Duplicate store IDs | 0 |
| Duplicate competitor IDs | 0 |
| Duplicate candidate IDs | 0 |
| Duplicate mobility-zone IDs | 0 |

**Validation outcome:** All initial checks performed so far passed.

These checks establish structural consistency and valid coordinate ranges. They do not prove that the simulated data represents actual retail activity or that all business assumptions are accurate.

### 6.2 Dataset Limitations

- All individual store, competitor, candidate and mobility-zone coordinates are simulated.
- Visitor counts and mobility flows are synthetic, not actual customer observations.
- Catchment radii and estimated rent indices are illustrative.
- The dataset does not contain individual human trajectories or customer identities.
- The five example cities do not represent complete geographic coverage of those cities.
- Mobility flow distances use a simplified local planar approximation.
- Synthetic values have not been calibrated against real retail measurements.

**This dataset is intended only for prototype development, testing and demonstration. It must not be used to make real commercial location decisions.**

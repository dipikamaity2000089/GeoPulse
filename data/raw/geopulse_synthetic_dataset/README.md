# GeoPulse Synthetic Dataset

## Important data disclosure
Every record in this package is synthetic and generated for GeoPulse development,
testing, demonstrations, and analytics prototyping. It is NOT actual customer
tracking, real store information, or measured real-world footfall.

City names and approximate city-centre anchors are used only to create a
multi-city demonstration. Individual store, competitor, candidate, zone
coordinates and all counts/flows are simulated.

## Geographic scope
Five example cities: Chennai, Mumbai, Bengaluru, London, and Singapore.
The data model is city-independent; these examples do not imply global coverage.

## Files
- `store_locations.csv`: 50 synthetic stores, categories, coordinates, catchment radii.
- `competitor_locations.csv`: 60 synthetic competitor points of interest.
- `candidate_locations.csv`: 25 synthetic candidate store sites and rent indices.
- `footfall_observations.csv`: 9,800 hourly synthetic visitor-count observations over 14 days.
- `mobility_flows.csv`: 4,200 synthetic origin-zone-to-store trip aggregates over 14 days.
- `mobility_zones.csv`: 30 synthetic mobility-zone centroids.

## Feature mapping
1. Smart Footfall Heatmap: `footfall_observations.csv` joined with store coordinates.
2. Store Cannibalization Detection: store locations, catchment radii, candidate sites and mobility flows.
3. Time-Based Mobility Analysis: timestamps and visitor counts in `footfall_observations.csv`.
4. Transparent Smart Store Recommendation: candidate sites, store categories, footfall, competitors and catchments.
5. Competitor Proximity Analysis: `competitor_locations.csv` and `candidate_locations.csv` / `store_locations.csv`.
6. What-If Location Simulator: candidate sites plus store, competitor, footfall and mobility data.

## Suggested joins
- `footfall_observations.store_id` -> `store_locations.store_id`
- `mobility_flows.destination_store_id` -> `store_locations.store_id`
- `mobility_flows.origin_zone_id` -> `mobility_zones.zone_id`

## Time range
2026-10-01 through 2026-10-14 inclusive, hourly observations from 08:00 to 21:00.

## Limitations
- Synthetic counts and flows are not calibrated to real footfall.
- Catchment radius and rent index are illustrative assumptions.
- Mobility flow distances use a simple local planar approximation.
- Do not use these records to make real commercial investment decisions.
- Before production use, replace or supplement with properly licensed real data and validate all models.

## Reproducibility
Generated with a fixed random seed (20261112), so the values are reproducible
if the same generation logic and library behavior are retained.

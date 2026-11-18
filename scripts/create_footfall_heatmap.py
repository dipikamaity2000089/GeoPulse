
from pathlib import Path

import pandas as pd
import folium
import xyzservices.providers as xyz
from folium.plugins import HeatMap


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MAP_DIR = PROCESSED_DIR / "maps"

INPUT_FILE = PROCESSED_DIR / "store_footfall_by_hour.csv"
OUTPUT_FILE = MAP_DIR / "footfall_heatmap.html"


# Classify stores based on average hourly footfall
def classify_footfall(visitors):
    if visitors >= 60:
        return "red"
    elif visitors >= 30:
        return "orange"
    else:
        return "green"


def main():
    print("=" * 55)
    print("GEOPULSE SMART FOOTFALL HEATMAP")
    print("=" * 55)

    # Load geographic footfall data
    df = pd.read_csv(INPUT_FILE)

    print("\nAVAILABLE CITIES")

    cities = sorted(df["city"].unique())

    for index, city in enumerate(cities, start=1):
        print(f"{index}. {city}")

    selected_number = int(input("\nSelect a city (enter number): "))

    if selected_number < 1 or selected_number > len(cities):
        raise ValueError("Invalid city selection.")

    selected_city = cities[selected_number - 1]

    city_data = df[df["city"] == selected_city].copy()

    print(f"\nSelected city: {selected_city}")
    print("Store-hour records:", len(city_data))

    # Display available hours
    print("\nAVAILABLE HOURS")

    hours = sorted(city_data["hour"].unique())

    for hour in hours:
        print(f"{hour:02d}:00")

    selected_hour = int(input("\nSelect an hour (8-21): "))

    if selected_hour not in hours:
        raise ValueError("Invalid hour selection.")

    city_data = city_data[
        city_data["hour"] == selected_hour
    ].copy()

    print(f"\nSelected hour: {selected_hour:02d}:00")
    print("Records for selected hour:", len(city_data))

    # Calculate average footfall intensity for each store
    store_locations = (
        city_data.groupby(
            ["store_id", "latitude", "longitude"]
        )["average_visitors"]
        .mean()
        .reset_index()
    )

    # Create map centered on the selected city
    center_lat = city_data["latitude"].mean()
    center_lon = city_data["longitude"].mean()

    footfall_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=xyz.Esri.WorldGrayCanvas
    )

    # Prepare heatmap coordinates and intensity
    heat_data = store_locations[
        ["latitude", "longitude", "average_visitors"]
    ].values.tolist()

    # Generate the footfall heatmap
    HeatMap(
        heat_data,
        radius=25,
        blur=15,
        min_opacity=0.4,
        max_val=100,
        gradient={
            0.2: "blue",
            0.4: "lime",
            0.6: "yellow",
            0.8: "orange",
            1.0: "red"
        }
    ).add_to(footfall_map)

    # Add interactive store markers
    for _, store in city_data.iterrows():

        popup_text = f"""
        <b>Store ID:</b> {store['store_id']}<br>
        <b>City:</b> {selected_city}<br>
        <b>Hour:</b> {selected_hour:02d}:00<br>
        <b>Average Visitors:</b> {store['average_visitors']}<br>
        <b>Total Visitors (14 days):</b> {store['total_visitors']}
        """

        folium.Marker(
            location=[
                store["latitude"],
                store["longitude"]
            ],
            popup=folium.Popup(
                popup_text,
                max_width=250
            ),
            tooltip=store["store_id"],
            icon=folium.Icon(
                color=classify_footfall(
                    store["average_visitors"]
                ),
                icon="shopping-cart"
            )
        ).add_to(footfall_map)

    # Save the interactive map after adding all markers
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    # Add a footfall colour legend to the map
    legend_html = """
    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;
        width: 190px;
        background-color: white;
        border: 2px solid grey;
        border-radius: 8px;
        padding: 12px;
        z-index: 9999;
        font-size: 14px;
    ">
        <b>Footfall Intensity</b><br><br>
        <span style="color:red;">●</span>
        High: 60 or more<br>
        <span style="color:orange;">●</span>
        Medium: 30–59<br>
        <span style="color:green;">●</span>
        Low: below 30
    </div>
    """

    footfall_map.get_root().html.add_child(
        folium.Element(legend_html)
    )
    footfall_map.save(OUTPUT_FILE)

    print(f"\n[OK] Heatmap saved: {OUTPUT_FILE}")

    print("\nDATASET INFORMATION")
    print("Total records:", len(df))
    print("Available cities:", df["city"].unique().tolist())
    print("Available hours:", sorted(df["hour"].unique().tolist()))

    print("\nFootfall data loaded successfully.")

    print("\nMARKER COLOUR GUIDE")
    print("Red: High footfall (60 or more)")
    print("Orange: Medium footfall (30 to 59)")
    print("Green: Low footfall (below 30)")

    print("\n" + "=" * 55)
    print("GEOPULSE SMART FOOTFALL HEATMAP COMPLETED")
    print("=" * 55)


if __name__ == "__main__":
    main()

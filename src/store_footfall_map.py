import pandas as pd
import folium
import math
from folium.plugins import HeatMap
from pathlib import Path
project_folder = Path(__file__).resolve().parents[1]
data_folder = project_folder / "data"
gps = pd.read_csv(data_folder / "gps_data.csv")
stores = pd.read_csv(data_folder / "stores.csv")
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
results = []
for _, store in stores.iterrows():
    store_lat = store["StoreLat"]
    store_lon = store["StoreLong"]
    footfall = 0
    for _, point in gps.iterrows():
        distance = calculate_distance(
            store_lat,
            store_lon,
            point["Lat"],
            point["Long"]
        )
        if distance <= 500:
            footfall += 1
    results.append({
        "StoreID": store["StoreID"],
        "StoreName": store["StoreName"],
        "Footfall_Within_500m": footfall
    })
footfall_df = pd.DataFrame(results)
output_csv = data_folder / "store_footfall_analysis.csv"
footfall_df.to_csv(output_csv, index=False)
center_lat = stores["StoreLat"].mean()
center_lon = stores["StoreLong"].mean()
geo_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14
)
heat_data = gps[["Lat", "Long"]].values.tolist()
HeatMap(
    heat_data,
    radius=15,
    blur=20
).add_to(geo_map)
for _, store in stores.iterrows():
    store_name = store["StoreName"]
    store_lat = store["StoreLat"]
    store_lon = store["StoreLong"]
    footfall = footfall_df.loc[
        footfall_df["StoreName"] == store_name,
        "Footfall_Within_500m"
    ].values[0]
    folium.Marker(
        location=[store_lat, store_lon],
        popup=f"""
        <b>{store_name}</b><br>
        GPS Footfall within 500m: {footfall}
        """,
        tooltip=store_name,
        icon=folium.Icon(color="blue", icon="shopping-cart")
    ).add_to(geo_map)
    folium.Circle(
        location=[store_lat, store_lon],
        radius=500,
        color="blue",
        fill=True,
        fill_opacity=0.08,
        popup=f"{store_name} - 500m Catchment"
    ).add_to(geo_map)
output_map = data_folder / "store_footfall_map.html"
geo_map.save(output_map)
print("Store Footfall Analysis Completed!")
print(footfall_df)
print("\nCSV saved to:", output_csv)
print("Map saved to:", output_map)
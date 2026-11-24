import pandas as pd
import folium
from folium.plugins import HeatMap
gps = pd.read_csv("data/gps_data.csv")
stores = pd.read_csv("data/stores.csv")
center_lat = gps["Lat"].mean()
center_lon = gps["Long"].mean()
geo_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14,
    tiles="OpenStreetMap"
)
heat_data = gps[["Lat", "Long"]].values.tolist()
HeatMap(
    heat_data,
    radius=18,
    blur=15,
    min_opacity=0.4
).add_to(geo_map)
for _, store in stores.iterrows():
    lat = store["StoreLat"]
    lon = store["StoreLong"]
    folium.Marker(
        location=[lat, lon],
        popup=f"Store: {store['StoreName']}",
        tooltip=store["StoreName"],
        icon=folium.Icon(color="blue", icon="shopping-cart")
    ).add_to(geo_map)
    folium.Circle(
        location=[lat, lon],
        radius=500,
        color="blue",
        fill=True,
        fill_opacity=0.08,
        popup="500m Catchment Area"
    ).add_to(geo_map)
for _, point in gps.iterrows():
    folium.CircleMarker(
        location=[point["Lat"], point["Long"]],
        radius=2,
        color="red",
        fill=True,
        fill_opacity=0.5
    ).add_to(geo_map)
output_file = "data/store_mobility_map.html"
geo_map.save(output_file)
print("GeoPulse Mobility Map created successfully!")
print("Map saved to:", output_file)
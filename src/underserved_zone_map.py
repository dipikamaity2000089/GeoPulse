import pandas as pd
import folium
zones = pd.read_csv("data/underserved_zones.csv")
stores = pd.read_csv("data/stores.csv")
center_lat = zones["Lat"].mean()
center_lon = zones["Long"].mean()
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=14,
    tiles="https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    attr="© OpenStreetMap contributors"
)
colors = {
    "High": "red",
    "Medium": "orange",
    "Low": "blue"
}
for _, zone in zones.iterrows():
    color = colors.get(zone["Opportunity"], "blue")
    popup_text = f"""
    <b>Opportunity Zone</b><br>
    GPS Activity: {zone['GPS_Activity']}<br>
    Unique Devices: {zone['UniqueDevices']}<br>
    Opportunity: {zone['Opportunity']}<br>
    Average Distance: {zone['AvgDistance']:.5f}
    """
    folium.CircleMarker(
        location=[zone["Lat"], zone["Long"]],
        radius=8 + zone["GPS_Activity"],
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=popup_text,
        tooltip=f"{zone['Opportunity']} Opportunity Zone"
    ).add_to(m)
for _, store in stores.iterrows():
    folium.Marker(
        location=[store["StoreLat"], store["StoreLong"]],
        popup=store["StoreName"],
        tooltip=store["StoreName"],
        icon=folium.Icon(color="green", icon="shopping-cart")
    ).add_to(m)
legend_html = """
<div style="
position: fixed;
bottom: 30px;
left: 30px;
width: 170px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
padding: 10px;
font-size: 14px;
">
<b>Opportunity Legend</b><br>
<span style="color:red;">●</span> High Opportunity<br>
<span style="color:orange;">●</span> Medium Opportunity<br>
<span style="color:blue;">●</span> Low Opportunity<br>
<span style="color:green;">●</span> Existing Stores
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
m.save("data/underserved_zone_map.html")
print("Underserved Zone Map created successfully!")
import pandas as pd
import folium
df = pd.read_csv("data/what_if_expansion_simulation.csv")
center_lat = df["Latitude"].mean()
center_lon = df["Longitude"].mean()
m = folium.Map(
    location=[df["Latitude"].mean(), df["Longitude"].mean()],
    zoom_start=14,
    tiles=None
)

folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Esri World Street Map",
    overlay=False,
    control=True
).add_to(m)
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles © Esri — Sources: Esri, OpenStreetMap contributors",
    name="Esri Street Map",
    overlay=False,
    control=True
).add_to(m)
for _, row in df.iterrows():
    if row["Rank"] == 1:
        color = "green"
    elif row["Rank"] == 2:
        color = "orange"
    else:
        color = "red"
    popup_text = f"""
    <b>{row['Candidate_Zone']}</b><br>
    GPS Activity: {row['GPS_Activity']}<br>
    Opportunity Score: {row['Opportunity_Score']:.2f}<br>
    Cannibalization Risk: {row['Cannibalization_Risk']}<br>
    Rank: {row['Rank']}<br>
    Recommendation: {row['Recommendation']}
    """
    folium.Marker(
        location=[row["Latitude"], row["Longitude"]],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=row["Candidate_Zone"],
        icon=folium.Icon(
            color=color,
            icon="info-sign"
        )
    ).add_to(m)
legend_html = """
<div style="
position: fixed;
bottom: 40px;
left: 40px;
width: 190px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
padding: 10px;
font-size: 14px;
">
<b>Expansion Priority</b><br>
<span style="color:green;">●</span>
Best Location (Rank 1)<br>
<span style="color:orange;">●</span>
Second Priority (Rank 2)<br>
<span style="color:red;">●</span>
Lower Priority (Rank 3 & 4)
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))
folium.LayerControl().add_to(m)
locations = df[["Latitude", "Longitude"]].values.tolist()
m.fit_bounds(locations)
m.save("data/what_if_expansion_map.html")
print("Interactive Expansion Map created successfully!")
print("Map saved to: data/what_if_expansion_map.html")
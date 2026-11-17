
import { useEffect, useState } from "react";
import Papa from "papaparse";
import { heatLayer } from "@linkurious/leaflet-heat";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import "./HeatmapPage.css";

function HeatLayer({ points }) {
  const map = useMap();

  useEffect(() => {
    let heat = null;
    let cancelled = false;

    if (!points.length) return;

    const heatPoints = points.map((point) => [
      Number(point.Latitude),
      Number(point.Longitude),
      0.7
    ]);

    import("leaflet.heat").then(() => {
      if (cancelled || typeof L.heatLayer !== "function") {
        console.error("Leaflet heat plugin was not loaded correctly");
        return;
      }

      heat = L.heatLayer(heatPoints, {
        radius: 25,
        blur: 20,
        maxZoom: 17,
        max: 1,
        gradient: {
          0.2: "#36B37E",
          0.5: "#FFD166",
          0.8: "#FF8C42",
          1: "#E63946"
        }
      }).addTo(map);
    }).catch((error) => {
      console.error("Heatmap loading error:", error);
    });

    return () => {
      cancelled = true;
      if (heat) {
        map.removeLayer(heat);
      }
    };
  }, [map, points]);

  return null;
}

function HeatmapPage() {
  const [gpsData, setGpsData] = useState([]);
  const [storeData, setStoreData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeFilter, setTimeFilter] = useState("All");

  useEffect(() => {
    Promise.all([
      fetch("/data/raw_gps_pings.csv").then((res) => {
        if (!res.ok) throw new Error("GPS dataset not found");
        return res.text();
      }),
      fetch("/data/store_locations.csv").then((res) => {
        if (!res.ok) throw new Error("Store dataset not found");
        return res.text();
      })
    ])
      .then(([gpsCsv, storeCsv]) => {
        const gps = Papa.parse(gpsCsv, {
          header: true,
          skipEmptyLines: true,
          dynamicTyping: true
        }).data;

        const stores = Papa.parse(storeCsv, {
          header: true,
          skipEmptyLines: true,
          dynamicTyping: true
        }).data;

        setGpsData(
          gps.filter(
            (item) =>
              Number.isFinite(Number(item.Latitude)) &&
              Number.isFinite(Number(item.Longitude))
          )
        );

        setStoreData(
          stores.filter(
            (item) =>
              Number.isFinite(Number(item.Latitude)) &&
              Number.isFinite(Number(item.Longitude))
          )
        );

        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filteredData = gpsData.filter((point) => {
    if (timeFilter === "All") return true;

    const hour = new Date(
      point.Timestamp.replace(" ", "T")
    ).getHours();

    if (timeFilter === "Morning") return hour >= 6 && hour < 12;
    if (timeFilter === "Afternoon") return hour >= 12 && hour < 17;
    if (timeFilter === "Evening") return hour >= 17 && hour < 21;
    if (timeFilter === "Night") return hour >= 21 || hour < 6;

    return true;
  });

  if (loading) {
    return <div className="heat-message">Loading footfall map...</div>;
  }

  if (error) {
    return <div className="heat-message">Error: {error}</div>;
  }

  return (
    <div className="heatmap-page">
      <div className="heat-header">
        <div>
          <p className="heat-eyebrow">GEOLOCATION INTELLIGENCE</p>
          <h1>Smart Footfall Heatmap</h1>
          <p>Explore GPS activity and existing retail store locations.</p>
        </div>

        <select
          value={timeFilter}
          onChange={(e) => setTimeFilter(e.target.value)}
          className="heat-filter"
        >
          <option value="All">All Day</option>
          <option value="Morning">Morning</option>
          <option value="Afternoon">Afternoon</option>
          <option value="Evening">Evening</option>
          <option value="Night">Night</option>
        </select>
      </div>

      <div className="heat-stats">
        <div className="heat-stat">
          <span>GPS Records</span>
          <h2>{filteredData.length.toLocaleString()}</h2>
        </div>

        <div className="heat-stat">
          <span>Stores Displayed</span>
          <h2>{storeData.length}</h2>
        </div>

        <div className="heat-stat">
          <span>Time Period</span>
          <h2>{timeFilter}</h2>
        </div>
      </div>

      <div className="heat-map-container">
        <MapContainer
          center={[13.04, 80.23]}
          zoom={12}
          scrollWheelZoom={true}
          className="heat-map"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <HeatLayer points={filteredData} />

          {storeData.map((store) => (
            <CircleMarker
              key={store.StoreID}
              center={[
                Number(store.Latitude),
                Number(store.Longitude)
              ]}
              radius={8}
              pathOptions={{
                color: "#ffffff",
                weight: 2,
                fillColor: "#2563EB",
                fillOpacity: 1
              }}
            >
              <Popup>
                <strong>{store.StoreName}</strong>
                <br />
                Store ID: {store.StoreID}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="heat-legend">
        <span><i className="legend-dot green"></i> Low activity</span>
        <span><i className="legend-dot yellow"></i> Moderate activity</span>
        <span><i className="legend-dot orange"></i> High activity</span>
        <span><i className="legend-dot red"></i> Very high activity</span>
        <span><i className="legend-dot blue"></i> Existing stores</span>
      </div>

      <p className="heat-note">
        Note: Heat intensity represents synthetic GPS ping density,
        not verified customer counts.
      </p>
    </div>
  );
}

export default HeatmapPage;

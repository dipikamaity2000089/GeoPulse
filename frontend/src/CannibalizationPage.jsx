
import { useEffect, useState } from "react";
import Papa from "papaparse";

import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  Popup
} from "react-leaflet";

import "leaflet/dist/leaflet.css";
import "./CannibalizationPage.css";

const RADIUS = 500;

function calculateDistance(lat1, lon1, lat2, lon2) {
  const toRadians = (value) => (value * Math.PI) / 180;

  const earthRadius = 6371000;

  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) ** 2;

  return (
    earthRadius *
    2 *
    Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  );
}

function getRisk(distance) {
  if (distance <= 500) return "High";
  if (distance <= 1000) return "Medium";
  return "Low";
}

function CannibalizationPage() {
  const [stores, setStores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/data/store_locations.csv")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Store dataset not found");
        }

        return response.text();
      })
      .then((csv) => {
        const result = Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          dynamicTyping: true
        });

        const validStores = result.data.filter(
          (store) =>
            Number.isFinite(Number(store.Latitude)) &&
            Number.isFinite(Number(store.Longitude))
        );

        setStores(validStores);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Calculate distances between every pair of stores
  const allStorePairs = [];

  for (let i = 0; i < stores.length; i++) {
    for (let j = i + 1; j < stores.length; j++) {
      const first = stores[i];
      const second = stores[j];

      const distance = calculateDistance(
        Number(first.Latitude),
        Number(first.Longitude),
        Number(second.Latitude),
        Number(second.Longitude)
      );

      allStorePairs.push({
        firstStore: first,
        secondStore: second,
        distance,
        overlapDistance: Math.max(0, 1000 - distance),
        overlap: distance < 1000,
        risk: getRisk(distance)
      });
    }
  }

  // Find all geographically overlapping pairs
  const overlappingPairs = allStorePairs.filter(
    (pair) => pair.overlap
  );

  // Select the 10 closest store pairs
  const nearestPairs = [...allStorePairs]
    .sort((a, b) => a.distance - b.distance)
    .slice(0, 10);

  const affectedStores = new Set();

  overlappingPairs.forEach((pair) => {
    affectedStores.add(pair.firstStore.StoreID);
    affectedStores.add(pair.secondStore.StoreID);
  });

  const highRiskCount = nearestPairs.filter(
    (pair) => pair.risk === "High"
  ).length;

  const mediumRiskCount = nearestPairs.filter(
    (pair) => pair.risk === "Medium"
  ).length;

  if (loading) {
    return (
      <div className="cann-message">
        Loading store locations...
      </div>
    );
  }

  if (error) {
    return (
      <div className="cann-message">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="cann-page">

      <div className="cann-heading">
        <div>
          <p className="cann-eyebrow">
            RETAIL NETWORK INTELLIGENCE
          </p>

          <h2>Store Cannibalization Detection</h2>

          <p>
            Identify nearby stores and analyze potentially
            overlapping 500-metre catchment areas.
          </p>
        </div>
      </div>

      <div className="cann-stats">

        <div className="cann-card">
          <span>Total Stores</span>
          <h2>{stores.length}</h2>
        </div>

        <div className="cann-card">
          <span>Overlapping Store Pairs</span>
          <h2>{overlappingPairs.length}</h2>
        </div>

        <div className="cann-card">
          <span>Potentially Affected Stores</span>
          <h2>{affectedStores.size}</h2>
        </div>

        <div className="cann-card">
          <span>High-Risk Pairs in Top 10</span>
          <h2>{highRiskCount}</h2>
        </div>

      </div>

      <div className="cann-map-panel">

        <div className="cann-section-heading">
          <div>
            <h3>Store Catchment Map</h3>
            <p>
              Each circle represents a 500-metre radius
              around a store.
            </p>
          </div>
        </div>

        <div className="cann-map">

          <MapContainer
            center={[13.04, 80.23]}
            zoom={12}
            scrollWheelZoom={true}
            className="cann-leaflet-map"
          >

            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {stores.map((store, index) => (
              <Circle
                key={`circle-${store.StoreID || index}`}
                center={[
                  Number(store.Latitude),
                  Number(store.Longitude)
                ]}
                radius={RADIUS}
                pathOptions={{
                  color: "#2563EB",
                  weight: 2,
                  fillColor: "#60A5FA",
                  fillOpacity: 0.13
                }}
              />
            ))}

            {stores.map((store, index) => (
              <CircleMarker
                key={`marker-${store.StoreID || index}`}
                center={[
                  Number(store.Latitude),
                  Number(store.Longitude)
                ]}
                radius={7}
                pathOptions={{
                  color: "#ffffff",
                  weight: 2,
                  fillColor: "#1D4ED8",
                  fillOpacity: 1
                }}
              >
                <Popup>
                  <strong>{store.StoreName}</strong>
                  <br />
                  Store ID: {store.StoreID}
                  <br />
                  Catchment Radius: 500 metres
                </Popup>
              </CircleMarker>
            ))}

          </MapContainer>

        </div>

        <div className="cann-legend">
          <span>
            <i className="cann-legend-dot"></i>
            Store location
          </span>

          <span>
            <i className="cann-legend-circle"></i>
            500 m catchment area
          </span>
        </div>

      </div>

      <div className="cann-table-panel">

        <div className="cann-section-heading">
          <div>
            <h3>Nearest 10 Store Pairs</h3>
            <p>
              Stores ranked by distance between their locations.
            </p>
          </div>
        </div>

        <div className="cann-risk-summary">
          <span>High Risk: {highRiskCount}</span>
          <span>Medium Risk: {mediumRiskCount}</span>
          <span>
            Low Risk: {nearestPairs.length -
              highRiskCount - mediumRiskCount}
          </span>
        </div>

        {nearestPairs.length === 0 ? (
          <p className="cann-empty">
            No store pairs available.
          </p>
        ) : (

          <div className="cann-table-wrap">

            <table>
              <thead>
                <tr>
                  <th>Store 1</th>
                  <th>Store 2</th>
                  <th>Distance</th>
                  <th>Overlap</th>
                  <th>Risk Level</th>
                </tr>
              </thead>

              <tbody>
                {nearestPairs.map((pair, index) => (
                  <tr key={index}>

                    <td>
                      {pair.firstStore.StoreName ||
                        pair.firstStore.StoreID}
                    </td>

                    <td>
                      {pair.secondStore.StoreName ||
                        pair.secondStore.StoreID}
                    </td>

                    <td>
                      {Math.round(pair.distance)} m
                    </td>

                    <td>
                      {pair.overlap ? "Yes" : "No"}
                    </td>

                    <td>
                      <span
                        className={`cann-risk ${pair.risk.toLowerCase()}`}
                      >
                        {pair.risk}
                      </span>
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>

          </div>
        )}

      </div>

      <p className="cann-note">
        Note: Risk levels are based on geographic proximity.
        Catchment overlap does not establish actual customer
        loss or business cannibalization.
      </p>

    </div>
  );
}

export default CannibalizationPage;

import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from "react-leaflet";
import { loadCSV } from "./csvLoader";

const panelStyle = {
  background: "#111827",
  border: "1px solid #253247",
  borderRadius: "12px",
  padding: "18px",
};

const textMuted = "#94A3B8";

function getColor(visits, maxVisits) {
  const ratio = maxVisits ? visits / maxVisits : 0;

  if (ratio >= 0.75) return "#F43F5E";
  if (ratio >= 0.5) return "#F59E0B";
  if (ratio >= 0.25) return "#22D3EE";
  return "#64748B";
}

function MapBounds({ stores }) {
  const map = useMap();

  useEffect(() => {
    if (!stores.length) return;

    const bounds = stores
      .filter((store) => store.Latitude && store.Longitude)
      .map((store) => [Number(store.Latitude), Number(store.Longitude)]);

    if (bounds.length) {
      map.fitBounds(bounds, { padding: [35, 35], maxZoom: 13 });
    }
  }, [stores, map]);

  return null;
}

export default function FootfallHeatmap() {
  const [stores, setStores] = useState([]);
  const [district, setDistrict] = useState("All Districts");
  const [category, setCategory] = useState("All Categories");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCSV("store_footfall_analysis.csv")
      .then((data) => {
        const validStores = data.filter(
          (store) =>
            Number.isFinite(Number(store.Latitude)) &&
            Number.isFinite(Number(store.Longitude))
        );
        setStores(validStores);
      })
      .catch(() => setError("Unable to load store footfall data."))
      .finally(() => setLoading(false));
  }, []);

  const districts = useMemo(
    () => [...new Set(stores.map((s) => s.District).filter(Boolean))].sort(),
    [stores]
  );

  const categories = useMemo(
    () =>
      [...new Set(stores.map((s) => s.Store_Category).filter(Boolean))].sort(),
    [stores]
  );

  const filteredStores = useMemo(
    () =>
      stores.filter(
        (store) =>
          (district === "All Districts" || store.District === district) &&
          (category === "All Categories" || store.Store_Category === category)
      ),
    [stores, district, category]
  );

  const totalVisits = filteredStores.reduce(
    (sum, store) => sum + Number(store.Total_Visits || 0),
    0
  );

  const busiestStore = filteredStores.reduce(
    (top, store) =>
      Number(store.Total_Visits) > Number(top?.Total_Visits || 0) ? store : top,
    null
  );

  const maxVisits = Math.max(
    ...filteredStores.map((store) => Number(store.Total_Visits || 0)),
    1
  );

  const averageVisits = filteredStores.length
    ? Math.round(totalVisits / filteredStores.length)
    : 0;

  const selectStyle = {
    background: "#1E293B",
    border: "1px solid #334155",
    color: "#E2E8F0",
    padding: "10px 12px",
    borderRadius: "8px",
    outline: "none",
    minWidth: "170px",
  };

  if (loading) {
    return (
      <div style={{ color: "#E2E8F0", padding: "30px" }}>
        Loading footfall data...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ color: "#F87171", padding: "30px" }}>
        {error}
      </div>
    );
  }

  return (
    <div style={{ color: "#E2E8F0", display: "grid", gap: "20px" }}>
      <div>
        <h1 style={{ fontSize: "25px", margin: "0 0 8px" }}>
          Footfall Heatmap
        </h1>
        <p style={{ color: textMuted, margin: 0 }}>
          Geographic store performance and visitor intensity
        </p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
        <select
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          style={selectStyle}
        >
          <option>All Districts</option>
          {districts.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          style={selectStyle}
        >
          <option>All Categories</option>
          {categories.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))",
          gap: "14px",
        }}
      >
        {[
          ["Stores on Map", filteredStores.length],
          ["Total Visits", totalVisits.toLocaleString("en-IN")],
          ["Avg Visits / Store", averageVisits.toLocaleString("en-IN")],
          ["Busiest Store", busiestStore?.Store_ID || "—"],
        ].map(([label, value]) => (
          <div key={label} style={panelStyle}>
            <div style={{ color: textMuted, fontSize: "13px" }}>{label}</div>
            <div style={{ fontSize: "24px", fontWeight: 700, marginTop: "10px" }}>
              {value}
            </div>
            {label === "Busiest Store" && busiestStore && (
              <div style={{ color: textMuted, fontSize: "12px", marginTop: "5px" }}>
                {Number(busiestStore.Total_Visits).toLocaleString("en-IN")} visits
              </div>
            )}
          </div>
        ))}
      </div>

      <div
        style={{
          ...panelStyle,
          padding: "8px",
          overflow: "hidden",
        }}
      >
        <div style={{ height: "520px", width: "100%", borderRadius: "9px", overflow: "hidden" }}>
          <MapContainer
            center={[13.08, 80.27]}
            zoom={11}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            <MapBounds stores={filteredStores} />

            {filteredStores.map((store) => {
              const visits = Number(store.Total_Visits || 0);
              const radius = 5 + (visits / maxVisits) * 12;

              return (
                <CircleMarker
                  key={store.Store_ID}
                  center={[Number(store.Latitude), Number(store.Longitude)]}
                  radius={radius}
                  pathOptions={{
                    color: getColor(visits, maxVisits),
                    fillColor: getColor(visits, maxVisits),
                    fillOpacity: 0.72,
                    weight: 1.5,
                  }}
                >
                  <Popup>
                    <div style={{ minWidth: "165px" }}>
                      <strong>{store.Store_Name || store.Store_ID}</strong>
                      <br />
                      Store ID: {store.Store_ID}
                      <br />
                      Visits: {visits.toLocaleString("en-IN")}
                      <br />
                      Category: {store.Store_Category}
                      <br />
                      District: {store.District}
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>

        <div
          style={{
            display: "flex",
            gap: "18px",
            flexWrap: "wrap",
            padding: "14px 10px 8px",
            alignItems: "center",
          }}
        >
          <span style={{ fontSize: "12px", color: textMuted }}>Footfall Intensity</span>
          {[
            ["#64748B", "Low"],
            ["#22D3EE", "Moderate"],
            ["#F59E0B", "High"],
            ["#F43F5E", "Very High"],
          ].map(([color, label]) => (
            <div
              key={label}
              style={{ display: "flex", gap: "6px", alignItems: "center", fontSize: "12px" }}
            >
              <span
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  background: color,
                  display: "inline-block",
                }}
              />
              {label}
            </div>
          ))}
        </div>
      </div>

      <div style={panelStyle}>
        <h3 style={{ marginTop: 0, marginBottom: "14px" }}>Top Stores by Footfall</h3>
        {filteredStores
          .slice()
          .sort((a, b) => Number(b.Total_Visits) - Number(a.Total_Visits))
          .slice(0, 10)
          .map((store, index) => (
            <div
              key={store.Store_ID}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "11px 0",
                borderBottom: index !== 9 ? "1px solid #253247" : "none",
              }}
            >
              <span style={{ color: textMuted, width: "22px" }}>{index + 1}</span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: "14px", fontWeight: 600 }}>
                  {store.Store_Name || store.Store_ID}
                </div>
                <div style={{ color: textMuted, fontSize: "12px", marginTop: "3px" }}>
                  {store.District} · {store.Store_Category}
                </div>
              </div>
              <div style={{ fontWeight: 600, whiteSpace: "nowrap" }}>
                {Number(store.Total_Visits).toLocaleString("en-IN")}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
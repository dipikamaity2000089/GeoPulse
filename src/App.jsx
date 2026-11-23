
import { useState, useEffect } from "react";
import "./App.css";
import { loadCSV } from "./csvLoader";
import FootfallHeatmap from "./FootfallHeatmap";
import StoreAnalysis from "./StoreAnalysis";
import MobilityPatterns from "./MobilityPatterns";
function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCSV("hourly_footfall_analysis.csv")
      .then((data) => setEvents(data))
      .catch((error) => console.error("Dashboard data error:", error))
      .finally(() => setLoading(false));
  }, []);

  const menuItems = [
    { name: "Overview", icon: "◫" },
    { name: "Footfall Heatmap", icon: "⌖" },
    { name: "Store Analysis", icon: "▤" },
    { name: "Mobility Patterns", icon: "⇄" },
    { name: "Cannibalization", icon: "◎" },
    { name: "Competitor Analysis", icon: "⌂" },
    { name: "Store Recommendations", icon: "✧" },
    { name: "Location Simulator", icon: "⌘" },
  ];

  const totalVisits = events.reduce(
    (sum, item) => sum + Number(item.Total_Visits || item.Visits || 0),
    0
  );

  const totalDevices = 5000;
  const totalStores = 100;

  const averageDailyVisits = Math.round(totalVisits / 90);

  const cardStyle = {
    background: "#111827",
    border: "1px solid #253247",
    borderRadius: "12px",
    padding: "20px",
  };

  const muted = "#94A3B8";

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        background: "#0B1120",
        color: "#E2E8F0",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      {sidebarOpen && (
        <aside
          style={{
            width: "245px",
            background: "#0F172A",
            borderRight: "1px solid #253247",
            padding: "22px 14px",
            flexShrink: 0,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              marginBottom: "35px",
              padding: "0 10px",
            }}
          >
            <div
              style={{
                width: "38px",
                height: "38px",
                borderRadius: "11px",
                background: "linear-gradient(135deg, #22D3EE, #6366F1)",
                display: "grid",
                placeItems: "center",
                fontWeight: 800,
                color: "#FFFFFF",
                fontSize: "18px",
              }}
            >
              G
            </div>

            <div>
              <div style={{ fontSize: "19px", fontWeight: 750 }}>GeoPulse</div>
              <div style={{ color: muted, fontSize: "11px", marginTop: "3px" }}>
                LOCATION INTELLIGENCE
              </div>
            </div>
          </div>

          <div
            style={{
              fontSize: "11px",
              color: muted,
              padding: "0 10px",
              marginBottom: "12px",
              letterSpacing: "1px",
            }}
          >
            WORKSPACE
          </div>

          <nav style={{ display: "grid", gap: "5px" }}>
            {menuItems.map((item) => {
              const active = activePage === item.name;

              return (
                <button
                  key={item.name}
                  onClick={() => setActivePage(item.name)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "12px",
                    width: "100%",
                    textAlign: "left",
                    padding: "12px",
                    border: "none",
                    borderRadius: "9px",
                    cursor: "pointer",
                    background: active ? "#1E293B" : "transparent",
                    color: active ? "#22D3EE" : "#CBD5E1",
                    fontSize: "13px",
                    fontWeight: active ? 650 : 450,
                  }}
                >
                  <span style={{ fontSize: "17px", width: "22px" }}>
                    {item.icon}
                  </span>
                  {item.name}
                </button>
              );
            })}
          </nav>

          <div
            style={{
              marginTop: "35px",
              borderTop: "1px solid #253247",
              padding: "18px 10px",
              color: muted,
              fontSize: "12px",
              lineHeight: 1.7,
            }}
          >
            <div style={{ color: "#CBD5E1", fontWeight: 600 }}>
              GeoPulse Analytics
            </div>
            <div>Retail location intelligence platform</div>
            <div style={{ marginTop: "8px" }}>Dataset · 90 Days</div>
          </div>
        </aside>
      )}

      <main style={{ flex: 1, minWidth: 0 }}>
        <header
          style={{
            height: "68px",
            borderBottom: "1px solid #253247",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 25px",
            background: "#0F172A",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{
                background: "transparent",
                border: "1px solid #334155",
                color: "#E2E8F0",
                borderRadius: "8px",
                padding: "8px 11px",
                cursor: "pointer",
              }}
            >
              ☰
            </button>

            <span style={{ fontSize: "14px", fontWeight: 600 }}>
              {activePage}
            </span>
          </div>

          <div style={{ color: muted, fontSize: "12px" }}>
            RETAIL INTELLIGENCE
          </div>
        </header>

     <section style={{ padding: "25px", maxWidth: "1600px", margin: "auto" }}>
  {activePage === "Footfall Heatmap" ? (
    <FootfallHeatmap />
  ) : activePage === "Store Analysis" ? (
    <StoreAnalysis />
  ) : activePage === "Mobility Patterns" ? (
    <MobilityPatterns />
     ) : activePage === "Overview" ? (
            <>
              <div style={{ marginBottom: "25px" }}>
                <h1 style={{ fontSize: "25px", margin: "0 0 8px" }}>
                  Retail Analytics Overview
                </h1>
                <p style={{ color: muted, margin: 0 }}>
                  Monitor store performance and customer activity across your retail network
                </p>
              </div>

              {loading ? (
                <div style={{ color: muted }}>Loading overview data...</div>
              ) : (
                <>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                      gap: "16px",
                      marginBottom: "22px",
                    }}
                  >
                    {[
                      ["Tracked Devices", totalDevices.toLocaleString("en-IN"), "Unique mobility devices"],
                      ["Total Footfall", totalVisits.toLocaleString("en-IN"), "Recorded store visits"],
                      ["Active Stores", totalStores, "Retail locations tracked"],
                      ["Avg Daily Visits", averageDailyVisits.toLocaleString("en-IN"), "Across the dataset"],
                    ].map(([label, value, note]) => (
                      <div key={label} style={cardStyle}>
                        <div style={{ color: muted, fontSize: "13px" }}>{label}</div>
                        <div
                          style={{
                            fontSize: "27px",
                            fontWeight: 750,
                            margin: "12px 0 6px",
                          }}
                        >
                          {value}
                        </div>
                        <div style={{ color: muted, fontSize: "12px" }}>{note}</div>
                      </div>
                    ))}
                  </div>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                      gap: "16px",
                    }}
                  >
                    <div style={cardStyle}>
                      <h3 style={{ marginTop: 0 }}>Dataset Snapshot</h3>
                      <div style={{ color: muted, fontSize: "13px", lineHeight: 2 }}>
                        <div>Observation period: 90 days</div>
                        <div>Stores: 100</div>
                        <div>Devices: 5,000</div>
                        <div>Districts: 12</div>
                        <div>Competitors: 60</div>
                        <div>Categories: 10</div>
                      </div>
                    </div>

                    <div style={cardStyle}>
                      <h3 style={{ marginTop: 0 }}>Hourly Footfall</h3>
                      <div style={{ color: muted, fontSize: "13px", marginBottom: "15px" }}>
                        Visits recorded by hour
                      </div>

                      <div style={{ display: "flex", alignItems: "end", gap: "5px", height: "160px" }}>
                        {events.map((item, index) => {
                          const value = Number(item.Total_Visits || item.Visits || 0);
                          const max = Math.max(
                            ...events.map((e) => Number(e.Total_Visits || e.Visits || 0)),
                            1
                          );

                          return (
                            <div
                              key={index}
                              title={`${item.Hour ?? item.hour ?? index}: ${value} visits`}
                              style={{
                                flex: 1,
                                height: `${Math.max((value / max) * 100, 3)}%`,
                                background: "linear-gradient(180deg, #22D3EE, #6366F1)",
                                borderRadius: "4px 4px 0 0",
                              }}
                            />
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </>
              )}
            </>
          ) : (
            <div style={cardStyle}>
              <h1 style={{ marginTop: 0 }}>{activePage}</h1>
              <p style={{ color: muted }}>
                This analytics module is coming next. The Overview, Footfall Heatmap,
                and Store Analysis modules are available.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;

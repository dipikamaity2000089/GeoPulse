import { useEffect, useState } from "react";
import Papa from "papaparse";
import HeatmapPage from "./HeatmapPage";
import {
  LayoutDashboard,
  Map,
  Store,
  Activity,
  Target,
  Users,
  SlidersHorizontal,
  TrendingUp,
  Clock,
  MapPin,
  BarChart3,
  AlertCircle
} from "lucide-react";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart as ReBarChart,
  Bar
} from "recharts";

import "./App.css";

function App() {
  const [data, setData] = useState([]);
  const [selectedStore, setSelectedStore] = useState("All");
  const [activePage, setActivePage] = useState("Overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/data/hourly_footfall.csv")
      .then((response) => {
        if (!response.ok) {
          throw new Error("CSV file not found");
        }
        return response.text();
      })
      .then((csv) => {
        const result = Papa.parse(csv, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true
        });

        setData(result.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const navigation = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "Footfall Heatmap", icon: Map },
    { name: "Store Analysis", icon: Store },
    { name: "Mobility Analysis", icon: Activity },
    { name: "Cannibalization", icon: Target },
    { name: "Competitor Analysis", icon: Users },
    { name: "Store Recommendation", icon: TrendingUp },
    { name: "What-If Simulator", icon: SlidersHorizontal }
  ];

  const stores = [
    ...new Set(
      data.map((item) => item.Nearest_Store_ID).filter(Boolean)
    )
  ];

  const filteredData = data.filter((item) =>
    selectedStore === "All" ||
    item.Nearest_Store_ID === selectedStore
  );

  const totalPings = filteredData.reduce(
    (sum, item) =>
      sum + (Number(item.Total_GPS_Pings) || 0),
    0
  );

  const totalVisitors = filteredData.reduce(
    (sum, item) =>
      sum + (Number(item.Unique_Visitors) || 0),
    0
  );

  const peak = [...filteredData].sort(
    (a, b) =>
      (Number(b.Unique_Visitors) || 0) -
      (Number(a.Unique_Visitors) || 0)
  )[0];

  const hourlyData = Object.values(
    filteredData.reduce((groups, item) => {
      const hour = Number(item.Hour);

      if (!Number.isFinite(hour)) return groups;

      if (!groups[hour]) {
        groups[hour] = {
          hour: `${hour}:00`,
          hourNumber: hour,
          visitors: 0,
          pings: 0
        };
      }

      groups[hour].visitors +=
        Number(item.Unique_Visitors) || 0;

      groups[hour].pings +=
        Number(item.Total_GPS_Pings) || 0;

      return groups;
    }, {})
  ).sort((a, b) => a.hourNumber - b.hourNumber);

  const storeData = Object.values(
    filteredData.reduce((groups, item) => {
      const store = item.Nearest_Store_ID;

      if (!store) return groups;

      if (!groups[store]) {
        groups[store] = {
          store,
          visitors: 0,
          pings: 0
        };
      }

      groups[store].visitors +=
        Number(item.Unique_Visitors) || 0;

      groups[store].pings +=
        Number(item.Total_GPS_Pings) || 0;

      return groups;
    }, {})
  );

  const pageDescriptions = {
    "Footfall Heatmap":
      "Explore high and low foot-traffic areas using geographic heatmaps.",

    "Store Analysis":
      "Compare store performance, visitor activity and footfall patterns.",

    "Mobility Analysis":
      "Understand movement patterns across morning, afternoon, evening and night.",

    "Cannibalization":
      "Evaluate overlapping store catchments and potential shared traffic.",

    "Competitor Analysis":
      "Explore competitor density and proximity around proposed locations.",

    "Store Recommendation":
      "Rank potential store locations using footfall, coverage and risk scores.",

    "What-If Simulator":
      "Compare proposed store locations through interactive scenarios."
  };

  function renderOverview() {
    return (
      <>
        <section className="welcome">
          <div>
            <span>YOUR RETAIL NETWORK</span>
            <h2>Location intelligence at a glance</h2>
            <p>
              Explore footfall patterns and store performance.
            </p>
          </div>
          <MapPin size={42} />
        </section>

        <section className="kpi-grid">
          <div className="kpi-card">
            <div className="kpi-icon blue">
              <Store />
            </div>
            <p>Stores Analyzed</p>
            <h2>{stores.length}</h2>
            <span>Stores with recorded footfall</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon teal">
              <Activity />
            </div>
            <p>Total GPS Pings</p>
            <h2>{totalPings.toLocaleString()}</h2>
            <span>Recorded location events</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon purple">
              <Users />
            </div>
            <p>Hourly Visitor Counts</p>
            <h2>{totalVisitors.toLocaleString()}</h2>
            <span>Sum of store-hour counts</span>
          </div>

          <div className="kpi-card">
            <div className="kpi-icon orange">
              <Clock />
            </div>
            <p>Peak Traffic Hour</p>
            <h2>{peak ? `${peak.Hour}:00` : "--"}</h2>
            <span>
              {peak ? peak.Nearest_Store_ID : "No data"}
            </span>
          </div>
        </section>

        <section className="chart-grid">
          <div className="panel">
            <div className="panel-heading">
              <div>
                <h3>Hourly Mobility Trend</h3>
                <p>Visitor counts across recorded hours</p>
              </div>
              <TrendingUp size={20} />
            </div>

            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={hourlyData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="visitors"
                  stroke="#12A89D"
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <div>
                <h3>Store Performance</h3>
                <p>Hourly visitor counts by store</p>
              </div>
              <Store size={20} />
            </div>

            <ResponsiveContainer width="100%" height={280}>
              <ReBarChart data={storeData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />
                <XAxis dataKey="store" />
                <YAxis />
                <Tooltip />
                <Bar
                  dataKey="visitors"
                  fill="#3978C5"
                  radius={[6, 6, 0, 0]}
                />
              </ReBarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel data-panel">
          <div className="panel-heading">
            <div>
              <h3>Footfall Records</h3>
              <p>Loaded synthetic dataset</p>
            </div>

            <span className="record-count">
              {filteredData.length} records
            </span>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Store ID</th>
                  <th>Hour</th>
                  <th>GPS Pings</th>
                  <th>Unique Visitors</th>
                </tr>
              </thead>

              <tbody>
                {filteredData.map((item, index) => (
                  <tr key={index}>
                    <td>{item.Nearest_Store_ID}</td>
                    <td>{item.Hour}:00</td>
                    <td>{item.Total_GPS_Pings}</td>
                    <td>{item.Unique_Visitors}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </>
    );
  }

  function renderFeaturePage() {
    const selected = navigation.find(
      (item) => item.name === activePage
    );

    const Icon = selected?.icon || BarChart3;

    return (
      <section className="feature-page">
        <div className="feature-header">
          <div className="feature-icon">
            <Icon size={30} />
          </div>

          <h2>{activePage}</h2>

          <p>
            {pageDescriptions[activePage]}
          </p>

          <span className="development-tag">
            <Clock size={14} />
            Development in progress
          </span>
        </div>

        <div className="feature-info-grid">
          <div className="panel">
            <MapPin size={23} />
            <h3>Location Intelligence</h3>
            <p>
              Geographic analysis using store and GPS location data.
            </p>
          </div>

          <div className="panel">
            <BarChart3 size={23} />
            <h3>Data Analytics</h3>
            <p>
              Analyze existing footfall records and store performance.
            </p>
          </div>

          <div className="panel">
            <TrendingUp size={23} />
            <h3>Business Insights</h3>
            <p>
              Generate useful insights for retail location decisions.
            </p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">
            <MapPin size={23} />
          </div>

          <div>
            <h2>GeoPulse</h2>
            <span>RETAIL INTELLIGENCE</span>
          </div>
        </div>

        <p className="menu-label">WORKSPACE</p>

        <nav>
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.name}
                className={`nav-item ${
                  activePage === item.name ? "active" : ""
                }`}
                onClick={() => setActivePage(item.name)}
                type="button"
              >
                <Icon size={18} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>
          <span>Analytics System</span>
          <strong>Online</strong>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              RETAIL LOCATION INTELLIGENCE
            </p>

            <h1>{activePage}</h1>

            <p className="subtitle">
              Understand movement. Discover opportunities.
            </p>
          </div>

          {activePage === "Overview" && (
            <div className="filter">
              <Store size={17} />

              <select
                value={selectedStore}
                onChange={(e) =>
                  setSelectedStore(e.target.value)
                }
              >
                <option value="All">All Stores</option>

                {stores.map((store) => (
                  <option key={store} value={store}>
                    {store}
                  </option>
                ))}
              </select>
            </div>
          )}
        </header>

        {activePage === "Footfall Heatmap" ? (
  <HeatmapPage />
):loading ? (
          <p className="message">
            Loading GeoPulse analytics...
          </p>
        ) : error ? (
          <div className="message error-message">
            <AlertCircle />
            <h3>Unable to load footfall data</h3>
            <p>{error}</p>
            <p>
              Check that hourly_footfall.csv is inside
              frontend/public/data/.
            </p>
          </div>
        ) : data.length === 0 ? (
          <p className="message">
            No data found in the CSV file.
          </p>
        ) : activePage === "Overview" ? (
          renderOverview()
        ) : (
          renderFeaturePage()
        )}
      </main>
    </div>
  );
}

export default App;
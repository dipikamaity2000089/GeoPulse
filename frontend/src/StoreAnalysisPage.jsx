
import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
import {
  Store,
  Users,
  Activity,
  Clock,
  TrendingUp,
  Award,
  BarChart3
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from "recharts";
import "./StoreAnalysisPage.css";

function StoreAnalysisPage() {
  const [data, setData] = useState([]);
  const [selectedStore, setSelectedStore] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/data/hourly_footfall.csv")
      .then((response) => {
        if (!response.ok) throw new Error("Unable to load footfall data");
        return response.text();
      })
      .then((csv) => {
        const parsed = Papa.parse(csv, {
          header: true,
          dynamicTyping: true,
          skipEmptyLines: true
        });
        setData(parsed.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const stores = useMemo(
    () =>
      [...new Set(data.map((row) => row.Nearest_Store_ID).filter(Boolean))]
        .sort(),
    [data]
  );

  const storeStats = useMemo(() => {
    return stores.map((store) => {
      const records = data.filter(
        (row) => row.Nearest_Store_ID === store
      );

      const visitors = records.reduce(
        (sum, row) => sum + (Number(row.Unique_Visitors) || 0),
        0
      );

      const pings = records.reduce(
        (sum, row) => sum + (Number(row.Total_GPS_Pings) || 0),
        0
      );

      const peak = [...records].sort(
        (a, b) =>
          (Number(b.Unique_Visitors) || 0) -
          (Number(a.Unique_Visitors) || 0)
      )[0];

      return {
        store,
        visitors,
        pings,
        average: records.length ? Math.round(visitors / records.length) : 0,
        peakHour: peak?.Hour ?? "--",
        records: records.length
      };
    }).sort((a, b) => b.visitors - a.visitors);
  }, [data, stores]);

  const currentStats = selectedStore === "All"
    ? {
        store: "All Stores",
        visitors: storeStats.reduce((sum, s) => sum + s.visitors, 0),
        pings: storeStats.reduce((sum, s) => sum + s.pings, 0),
        average: data.length
          ? Math.round(
              data.reduce(
                (sum, row) => sum + (Number(row.Unique_Visitors) || 0),
                0
              ) / data.length
            )
          : 0,
        peakHour: data.length
          ? [...data].sort(
              (a, b) =>
                (Number(b.Unique_Visitors) || 0) -
                (Number(a.Unique_Visitors) || 0)
            )[0]?.Hour ?? "--"
          : "--"
      }
    : storeStats.find((s) => s.store === selectedStore) || {
        store: selectedStore,
        visitors: 0,
        pings: 0,
        average: 0,
        peakHour: "--"
      };

  const hourlyData = useMemo(() => {
    const filtered = selectedStore === "All"
      ? data
      : data.filter((row) => row.Nearest_Store_ID === selectedStore);

    const groups = Array.from({ length: 24 }, (_, hour) => ({
      hour,
      label: `${String(hour).padStart(2, "0")}:00`,
      visitors: 0,
      pings: 0
    }));

    filtered.forEach((row) => {
      const hour = Number(row.Hour);
      if (hour >= 0 && hour < 24) {
        groups[hour].visitors += Number(row.Unique_Visitors) || 0;
        groups[hour].pings += Number(row.Total_GPS_Pings) || 0;
      }
    });

    return groups;
  }, [data, selectedStore]);

  const selectedRank = storeStats.findIndex(
    (s) => s.store === selectedStore
  );

  const bestStore = storeStats[0];

  const rankingData = selectedStore === "All"
    ? storeStats.slice(0, 10)
    : storeStats.slice(0, 10);

  const insight = useMemo(() => {
    if (!storeStats.length) return "No store data available yet.";

    if (selectedStore === "All") {
      return `${bestStore.store} has the highest recorded visitor activity in the dataset.`;
    }

    const selected = storeStats.find((s) => s.store === selectedStore);
    if (!selected) return "No data available for this store.";

    const networkAverage = storeStats.reduce(
      (sum, s) => sum + s.visitors,
      0
    ) / storeStats.length;

    if (selected.visitors > networkAverage) {
      return `${selected.store} is performing above the network average based on recorded visitor counts.`;
    }

    if (selected.visitors < networkAverage) {
      return `${selected.store} is performing below the network average based on recorded visitor counts.`;
    }

    return `${selected.store} is around the network average in recorded visitor counts.`;
  }, [storeStats, selectedStore, bestStore]);

  if (loading) {
    return <div className="sa-message">Loading store analytics...</div>;
  }

  if (error) {
    return <div className="sa-message sa-error">{error}</div>;
  }

  return (
    <div className="sa-page">
      <div className="sa-header">
        <div>
          <span className="sa-eyebrow">RETAIL PERFORMANCE</span>
          <h2>Store Analysis</h2>
          <p>Explore individual store performance and compare activity.</p>
        </div>

        <div className="sa-select-wrap">
          <Store size={17} />
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
          >
            <option value="All">All Stores</option>
            {stores.map((store) => (
              <option key={store} value={store}>
                {store}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="sa-kpi-grid">
        <div className="sa-card">
          <div className="sa-card-top">
            <span className="sa-label">Stores Analyzed</span>
            <span className="sa-icon sa-blue"><Store size={19} /></span>
          </div>
          <h3>{selectedStore === "All" ? stores.length : 1}</h3>
          <span className="sa-caption">{currentStats.store}</span>
        </div>

        <div className="sa-card">
          <div className="sa-card-top">
            <span className="sa-label">Total Visitors</span>
            <span className="sa-icon sa-teal"><Users size={19} /></span>
          </div>
          <h3>{currentStats.visitors.toLocaleString()}</h3>
          <span className="sa-caption">Recorded visitor counts</span>
        </div>

        <div className="sa-card">
          <div className="sa-card-top">
            <span className="sa-label">GPS Pings</span>
            <span className="sa-icon sa-purple"><Activity size={19} /></span>
          </div>
          <h3>{currentStats.pings.toLocaleString()}</h3>
          <span className="sa-caption">Total recorded location events</span>
        </div>

        <div className="sa-card">
          <div className="sa-card-top">
            <span className="sa-label">Peak Traffic Hour</span>
            <span className="sa-icon sa-amber"><Clock size={19} /></span>
          </div>
          <h3>{currentStats.peakHour}:00</h3>
          <span className="sa-caption">Highest visitor record</span>
        </div>
      </div>

      <div className="sa-insight">
        <div className="sa-insight-icon"><TrendingUp size={20} /></div>
        <div>
          <span className="sa-insight-label">STORE PERFORMANCE INSIGHT</span>
          <p>{insight}</p>
        </div>
      </div>

      <div className="sa-chart-grid">
        <section className="sa-panel">
          <div className="sa-panel-heading">
            <div>
              <h3>Hourly Visitor Activity</h3>
              <p>Visitor distribution across 24 hours</p>
            </div>
            <BarChart3 size={20} />
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" interval={2} />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="visitors"
                fill="#16A394"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="sa-panel">
          <div className="sa-panel-heading">
            <div>
              <h3>GPS Ping Trend</h3>
              <p>Location activity throughout the day</p>
            </div>
            <Activity size={20} />
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" interval={2} />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="pings"
                stroke="#527EDB"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </section>
      </div>

      <section className="sa-panel sa-ranking-panel">
        <div className="sa-panel-heading">
          <div>
            <h3>Store Performance Ranking</h3>
            <p>Stores ranked by total recorded visitors</p>
          </div>
          <Award size={20} />
        </div>

        <div className="sa-table-wrap">
          <table className="sa-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Store</th>
                <th>Total Visitors</th>
                <th>GPS Pings</th>
                <th>Avg / Record</th>
                <th>Peak Hour</th>
              </tr>
            </thead>
            <tbody>
              {rankingData.map((store, index) => (
                <tr
                  key={store.store}
                  className={store.store === selectedStore ? "sa-selected-row" : ""}
                >
                  <td>
                    <span className={`sa-rank ${index === 0 ? "sa-rank-first" : ""}`}>
                      {index + 1}
                    </span>
                  </td>
                  <td className="sa-store-name">{store.store}</td>
                  <td>{store.visitors.toLocaleString()}</td>
                  <td>{store.pings.toLocaleString()}</td>
                  <td>{store.average.toLocaleString()}</td>
                  <td>{store.peakHour}:00</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default StoreAnalysisPage;


import { useEffect, useMemo, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Store, Users, Clock, TrendingUp, Search } from "lucide-react";
import { loadCSV } from "./csvLoader";

const COLORS = ["#13B8A6", "#38BDF8", "#818CF8", "#F59E0B", "#F472B6", "#A78BFA"];

const panel = {
  background: "#111827",
  border: "1px solid #253247",
  borderRadius: "14px",
  padding: "20px",
};

const muted = "#94A3B8";

function MetricCard({ icon, title, value, subtitle, color }) {
  return (
    <div style={panel}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ color: muted, fontSize: "13px" }}>{title}</span>
        <span style={{ color, background: `${color}18`, padding: "9px", borderRadius: "10px" }}>
          {icon}
        </span>
      </div>
      <h2 style={{ fontSize: "26px", margin: "14px 0 6px", color: "#F1F5F9" }}>{value}</h2>
      <span style={{ fontSize: "12px", color: muted }}>{subtitle}</span>
    </div>
  );
}

export default function StoreAnalysis() {
  const [stores, setStores] = useState([]);
  const [category, setCategory] = useState("All Categories");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadCSV("store_footfall_analysis.csv")
      .then((data) => setStores(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(
    () => [...new Set(stores.map((s) => s.Store_Category).filter(Boolean))].sort(),
    [stores]
  );

  const filtered = useMemo(
    () =>
      stores.filter((s) => {
        const matchCategory = category === "All Categories" || s.Store_Category === category;
        const matchSearch =
          `${s.Store_ID} ${s.Store_Name} ${s.District}`
            .toLowerCase()
            .includes(search.toLowerCase());
        return matchCategory && matchSearch;
      }),
    [stores, category, search]
  );

  const totalVisits = filtered.reduce((sum, s) => sum + Number(s.Total_Visits || 0), 0);
  const totalDevices = filtered.reduce((sum, s) => sum + Number(s.Unique_Devices || 0), 0);
  const avgDwell = filtered.length
    ? Math.round(filtered.reduce((sum, s) => sum + Number(s.Average_Dwell_Minutes || 0), 0) / filtered.length)
    : 0;

  const topStore = [...filtered].sort((a, b) => Number(b.Total_Visits) - Number(a.Total_Visits))[0];

  const categoryData = useMemo(() => {
    const map = {};
    filtered.forEach((s) => {
      const name = s.Store_Category || "Unknown";
      map[name] = (map[name] || 0) + Number(s.Total_Visits || 0);
    });
    return Object.entries(map)
      .map(([name, visits]) => ({ name, visits }))
      .sort((a, b) => b.visits - a.visits);
  }, [filtered]);

  const ranking = useMemo(
    () => [...filtered].sort((a, b) => Number(b.Total_Visits) - Number(a.Total_Visits)),
    [filtered]
  );

  if (loading) return <div style={{ color: "#E2E8F0", padding: "30px" }}>Loading store analysis...</div>;
  if (error) return <div style={{ color: "#F87171", padding: "30px" }}>Error: {error}</div>;

  return (
    <div style={{ display: "grid", gap: "22px", color: "#E2E8F0" }}>
      <div>
        <h1 style={{ margin: "0 0 8px", fontSize: "26px" }}>Store Analysis</h1>
        <p style={{ margin: 0, color: muted }}>Detailed performance comparison across retail locations</p>
      </div>

      <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
        <select value={category} onChange={(e) => setCategory(e.target.value)} style={selectStyle}>
          <option>All Categories</option>
          {categories.map((c) => <option key={c}>{c}</option>)}
        </select>

        <div style={{ display: "flex", alignItems: "center", gap: "8px", ...selectStyle }}>
          <Search size={16} color={muted} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search store or district..."
            style={{ background: "transparent", border: "none", outline: "none", color: "#E2E8F0", width: "210px" }}
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "14px" }}>
        <MetricCard icon={<Store size={18} />} title="Stores Analyzed" value={filtered.length} subtitle="Matching current filters" color="#38BDF8" />
        <MetricCard icon={<Users size={18} />} title="Total Visits" value={totalVisits.toLocaleString("en-IN")} subtitle="Recorded store visits" color="#13B8A6" />
        <MetricCard icon={<Clock size={18} />} title="Avg. Dwell Time" value={`${avgDwell} min`} subtitle="Average per store" color="#F59E0B" />
        <MetricCard icon={<TrendingUp size={18} />} title="Top Store" value={topStore?.Store_ID || "—"} subtitle={topStore ? `${Number(topStore.Total_Visits).toLocaleString("en-IN")} visits` : "No matching store"} color="#A78BFA" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "18px" }}>
        <div style={panel}>
          <h3 style={{ margin: "0 0 18px" }}>Top 10 Stores by Visits</h3>
          <ResponsiveContainer width="100%" height={330}>
            <BarChart data={ranking.slice(0, 10)} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <CartesianGrid stroke="#263448" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="Store_ID" stroke={muted} tick={{ fill: muted, fontSize: 11 }} />
              <YAxis stroke={muted} tick={{ fill: muted, fontSize: 11 }} />
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }} />
              <Bar dataKey="Total_Visits" fill="#13B8A6" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={panel}>
          <h3 style={{ margin: "0 0 18px" }}>Category Footfall Share</h3>
          <ResponsiveContainer width="100%" height={330}>
            <PieChart>
              <Pie data={categoryData} dataKey="visits" nameKey="name" cx="50%" cy="50%" outerRadius={112} innerRadius={65} paddingAngle={3}>
                {categoryData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "#111827", border: "1px solid #334155", borderRadius: "8px", color: "#F1F5F9" }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "grid", gap: "9px" }}>
            {categoryData.map((entry, index) => (
              <div key={entry.name} style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                <span><span style={{ color: COLORS[index % COLORS.length] }}>● </span>{entry.name}</span>
                <strong>{entry.visits.toLocaleString("en-IN")}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={panel}>
        <h3 style={{ margin: "0 0 16px" }}>Store Performance Ranking</h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "700px" }}>
            <thead>
              <tr>
                {["Rank", "Store ID", "Category", "District", "Visits", "Unique Devices", "Avg Dwell (min)"].map((heading) => (
                  <th key={heading} style={thStyle}>{heading}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ranking.map((store, index) => (
                <tr key={store.Store_ID}>
                  <td style={tdStyle}>{index + 1}</td>
                  <td style={{ ...tdStyle, color: "#38BDF8", fontWeight: 600 }}>{store.Store_ID}</td>
                  <td style={tdStyle}>{store.Store_Category}</td>
                  <td style={tdStyle}>{store.District}</td>
                  <td style={tdStyle}>{Number(store.Total_Visits).toLocaleString("en-IN")}</td>
                  <td style={tdStyle}>{Number(store.Unique_Devices).toLocaleString("en-IN")}</td>
                  <td style={tdStyle}>{Number(store.Average_Dwell_Minutes).toFixed(1)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

const selectStyle = {
  background: "#1E293B",
  border: "1px solid #334155",
  color: "#E2E8F0",
  padding: "10px 12px",
  borderRadius: "8px",
  outline: "none",
};

const thStyle = {
  textAlign: "left",
  color: "#94A3B8",
  fontSize: "12px",
  fontWeight: 600,
  padding: "12px 10px",
  borderBottom: "1px solid #334155",
  whiteSpace: "nowrap",
};

const tdStyle = {
  padding: "12px 10px",
  borderBottom: "1px solid #253247",
  fontSize: "13px",
  whiteSpace: "nowrap",
};


import { useEffect, useMemo, useState } from "react";
import { loadCSV } from "./csvLoader";

const panel = {
  background: "#111827",
  border: "1px solid #253247",
  borderRadius: "12px",
  padding: "18px",
};

const muted = "#94A3B8";

const formatNumber = (value) => Number(value || 0).toLocaleString("en-IN");

function getField(row, candidates) {
  const keys = Object.keys(row || {});
  const normalized = keys.map((key => ({
    original: key,
    clean: key.toLowerCase().replace(/[^a-z0-9]/g, ""),
  })));

  for (const candidate of candidates) {
    const match = normalized.find(
      (key) => key.clean === candidate.toLowerCase().replace(/[^a-z0-9]/g, "")
    );
    if (match) return row[match.original];
  }

  return "";
}

function parseDate(value) {
  if (!value) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

export default function MobilityPatterns() {
  const [rawVisits, setRawVisits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStore, setSelectedStore] = useState("All Stores");

  useEffect(() => {
    loadCSV("store_visits.csv")
      .then((data) => setRawVisits(data))
      .catch((error) => console.error("Mobility data loading error:", error))
      .finally(() => setLoading(false));
  }, []);

  const visits = useMemo(() => {
    return rawVisits
      .map((row) => {
        const device = getField(row, [
          "Device_ID",
          "DeviceID",
          "Device",
          "Visitor_ID",
          "Customer_ID",
          "Device",
        ]);

        const store = getField(row, [
          "Store_ID",
          "StoreID",
          "Store",
          "Location_ID",
        ]);

       const time = getField(row, [
  "Arrival_Time",
  "Departure_Time",
  "Visit_Start",
  "Visit_Start_Time",
  "Start_Time",
  "Timestamp",
  "Visit_Timestamp",
  "DateTime",
  "Date",
]);
      

        const date = parseDate(time);

        return {
          device: String(device || ""),
          store: String(store || ""),
          date,
          hour: date ? date.getHours() : null,
        };
      })
      .filter((row) => row.device && row.store && row.date)
      .sort((a, b) => a.date - b.date);
  }, [rawVisits]);

  const storeOptions = useMemo(
    () => [...new Set(visits.map((v) => v.store))].sort(),
    [visits]
  );

  const filteredVisits = useMemo(
    () =>
      selectedStore === "All Stores"
        ? visits
        : visits.filter((v) => v.store === selectedStore),
    [visits, selectedStore]
  );

  const transitions = useMemo(() => {
    const deviceGroups = {};

    visits.forEach((visit) => {
      if (!deviceGroups[visit.device]) deviceGroups[visit.device] = [];
      deviceGroups[visit.device].push(visit);
    });

    const transitionMap = {};
    const hourly = Array.from({ length: 24 }, (_, hour) => ({
      hour,
      count: 0,
    }));

    let totalTransitions = 0;

    Object.values(deviceGroups).forEach((group) => {
      group.sort((a, b) => a.date - b.date);

      for (let i = 0; i < group.length - 1; i++) {
        const current = group[i];
        const next = group[i + 1];

        if (current.store === next.store) continue;

        const gapHours = (next.date - current.date) / 3600000;
        if (gapHours < 0 || gapHours > 6) continue;

        const key = `${current.store} → ${next.store}`;

        if (!transitionMap[key]) {
          transitionMap[key] = {
            from: current.store,
            to: next.store,
            count: 0,
          };
        }

        transitionMap[key].count += 1;
        hourly[current.hour].count += 1;
        totalTransitions += 1;
      }
    });

    const sortedTransitions = Object.values(transitionMap).sort(
      (a, b) => b.count - a.count
    );

    return {
      transitionMap: sortedTransitions,
      hourly,
      totalTransitions,
    };
  }, [visits]);

  const storeTransitions = useMemo(() => {
    if (selectedStore === "All Stores") return transitions.transitionMap;

    return transitions.transitionMap.filter(
      (item) => item.from === selectedStore || item.to === selectedStore
    );
  }, [transitions, selectedStore]);

  const repeatData = useMemo(() => {
    const deviceStoreCount = {};

    filteredVisits.forEach((visit) => {
      const key = `${visit.device}_${visit.store}`;
      deviceStoreCount[key] = (deviceStoreCount[key] || 0) + 1;
    });

    const repeated = Object.values(deviceStoreCount).filter(
      (count) => count > 1
    ).length;

    const uniqueDevices = new Set(filteredVisits.map((v) => v.device)).size;

    return {
      uniqueDevices,
      repeatRecords: repeated,
      repeatRate: deviceStoreCount.length
        ? ((repeated / Object.keys(deviceStoreCount).length) * 100).toFixed(1)
        : "0.0",
    };
  }, [filteredVisits]);

  const topTransitions = storeTransitions.slice(0, 10);

  const maxTransition = Math.max(
    ...topTransitions.map((t) => t.count),
    1
  );

  const peakHour = [...transitions.hourly].sort(
    (a, b) => b.count - a.count
  )[0];

  const selectStyle = {
    background: "#1E293B",
    border: "1px solid #334155",
    color: "#E2E8F0",
    padding: "10px 12px",
    borderRadius: "8px",
    minWidth: "180px",
  };

  if (loading) {
    return <div style={{ color: "#E2E8F0", padding: "25px" }}>Loading mobility data...</div>;
  }

  if (!visits.length) {
    return (
      <div style={{ color: "#F87171", padding: "25px" }}>
        No mobility records with recognized device, store and timestamp fields were found.
        Check the columns in store_visits.csv.
      </div>
    );
  }

  const kpis = [
    {
      label: "Valid Visit Records",
      value: formatNumber(filteredVisits.length),
      color: "#22D3EE",
    },
    {
      label: "Unique Devices",
      value: formatNumber(repeatData.uniqueDevices),
      color: "#818CF8",
    },
    {
      label: "Store Transitions",
      value: formatNumber(transitions.totalTransitions),
      color: "#34D399",
    },
    {
      label: "Peak Movement Hour",
      value: peakHour ? `${peakHour.hour}:00` : "—",
      color: "#F59E0B",
    },
  ];

  return (
    <div style={{ display: "grid", gap: "20px", color: "#E2E8F0" }}>
      <div>
        <h1 style={{ fontSize: "25px", margin: "0 0 8px" }}>
          Mobility Patterns
        </h1>
        <p style={{ color: muted, margin: 0 }}>
          Explore visitor movement, store transitions and repeat visitation behavior
        </p>
      </div>

      <select
        value={selectedStore}
        onChange={(e) => setSelectedStore(e.target.value)}
        style={selectStyle}
      >
        <option>All Stores</option>
        {storeOptions.map((store) => (
          <option key={store}>{store}</option>
        ))}
      </select>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "14px",
        }}
      >
        {kpis.map((item) => (
          <div key={item.label} style={panel}>
            <div style={{ color: muted, fontSize: "13px" }}>{item.label}</div>
            <div
              style={{
                fontSize: "27px",
                fontWeight: 750,
                color: item.color,
                marginTop: "12px",
              }}
            >
              {item.value}
            </div>
            <div style={{ color: muted, fontSize: "12px", marginTop: "6px" }}>
              Mobility analytics
            </div>
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
        <div style={panel}>
          <h3 style={{ marginTop: 0 }}>Hourly Movement Activity</h3>
          <p style={{ color: muted, fontSize: "12px" }}>
            Transitions by hour of the day
          </p>

          <div
            style={{
              height: "190px",
              display: "flex",
              alignItems: "end",
              gap: "4px",
              marginTop: "20px",
            }}
          >
            {transitions.hourly.map((item) => {
              const max = Math.max(
                ...transitions.hourly.map((h) => h.count),
                1
              );

              return (
                <div
                  key={item.hour}
                  title={`${item.hour}:00 — ${formatNumber(item.count)} movements`}
                  style={{
                    flex: 1,
                    height: `${Math.max((item.count / max) * 100, 2)}%`,
                    background:
                      item.hour === peakHour?.hour
                        ? "#F59E0B"
                        : "linear-gradient(180deg, #22D3EE, #6366F1)",
                    borderRadius: "4px 4px 0 0",
                  }}
                />
              );
            })}
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              color: muted,
              fontSize: "11px",
              marginTop: "8px",
            }}
          >
            <span>00:00</span>
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
            <span>23:00</span>
          </div>
        </div>

        <div style={panel}>
          <h3 style={{ marginTop: 0 }}>Movement Insights</h3>

          <div style={{ padding: "14px 0", borderBottom: "1px solid #253247" }}>
            <div style={{ color: muted, fontSize: "12px" }}>Most Frequent Transition</div>
            <div style={{ fontSize: "17px", fontWeight: 700, marginTop: "8px" }}>
              {transitions.transitionMap[0]
                ? `${transitions.transitionMap[0].from} → ${transitions.transitionMap[0].to}`
                : "No transitions found"}
            </div>
            <div style={{ color: "#22D3EE", fontSize: "12px", marginTop: "5px" }}>
              {formatNumber(transitions.transitionMap[0]?.count)} movements
            </div>
          </div>

          <div style={{ padding: "14px 0", borderBottom: "1px solid #253247" }}>
            <div style={{ color: muted, fontSize: "12px" }}>Total Movement Records</div>
            <div style={{ fontSize: "22px", fontWeight: 700, marginTop: "8px" }}>
              {formatNumber(transitions.totalTransitions)}
            </div>
          </div>

          <div style={{ padding: "14px 0" }}>
            <div style={{ color: muted, fontSize: "12px" }}>Repeat Device-Store Records</div>
            <div style={{ fontSize: "22px", fontWeight: 700, marginTop: "8px" }}>
              {formatNumber(repeatData.repeatRecords)}
            </div>
          </div>
        </div>
      </div>

      <div style={panel}>
        <h3 style={{ marginTop: 0 }}>Top Store-to-Store Transitions</h3>
        <p style={{ color: muted, fontSize: "12px" }}>
          Visits to different stores by the same device within six hours
        </p>

        {topTransitions.length === 0 ? (
          <p style={{ color: muted }}>No transitions available for this selection.</p>
        ) : (
          topTransitions.map((item, index) => (
            <div key={`${item.from}-${item.to}`} style={{ marginBottom: "16px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: "13px",
                  marginBottom: "7px",
                  gap: "10px",
                }}
              >
                <span>
                  <span style={{ color: muted, marginRight: "10px" }}>{index + 1}.</span>
                  {item.from} <span style={{ color: "#22D3EE" }}>→</span> {item.to}
                </span>
                <strong>{formatNumber(item.count)}</strong>
              </div>

              <div
                style={{
                  height: "8px",
                  background: "#263449",
                  borderRadius: "8px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${(item.count / maxTransition) * 100}%`,
                    height: "100%",
                    background: "linear-gradient(90deg, #22D3EE, #6366F1)",
                    borderRadius: "8px",
                  }}
                />
              </div>
            </div>
          ))
        )}
      </div>

      <div style={panel}>
        <h3 style={{ marginTop: 0 }}>Transition Details</h3>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: "500px" }}>
            <thead>
              <tr style={{ color: muted, textAlign: "left", borderBottom: "1px solid #334155" }}>
                <th style={{ padding: "12px 8px" }}>Rank</th>
                <th style={{ padding: "12px 8px" }}>Origin Store</th>
                <th style={{ padding: "12px 8px" }}>Destination Store</th>
                <th style={{ padding: "12px 8px" }}>Movement Count</th>
              </tr>
            </thead>
            <tbody>
              {storeTransitions.slice(0, 20).map((item, index) => (
                <tr key={`${item.from}-${item.to}`} style={{ borderBottom: "1px solid #253247" }}>
                  <td style={{ padding: "12px 8px", color: muted }}>{index + 1}</td>
                  <td style={{ padding: "12px 8px" }}>{item.from}</td>
                  <td style={{ padding: "12px 8px" }}>{item.to}</td>
                  <td style={{ padding: "12px 8px", fontWeight: 600 }}>
                    {formatNumber(item.count)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

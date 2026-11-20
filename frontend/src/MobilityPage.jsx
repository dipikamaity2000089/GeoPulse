
import { useEffect, useMemo, useState } from "react";
import Papa from "papaparse";
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

import "./MobilityPage.css";

function MobilityPage() {
  const [gpsData, setGpsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [timeFilter, setTimeFilter] = useState("All");

  useEffect(() => {
    fetch("/data/raw_gps_pings.csv")
      .then((response) => {
        if (!response.ok) throw new Error("GPS dataset not found");
        return response.text();
      })
      .then((csv) => {
        const result = Papa.parse(csv, {
          header: true,
          skipEmptyLines: true
        });

        const validRecords = result.data
          .map((item) => ({
            DeviceID: item.DeviceID,
            Latitude: Number(item.Latitude),
            Longitude: Number(item.Longitude),
            Timestamp: item.Timestamp,
            date: new Date(String(item.Timestamp).replace(" ", "T"))
          }))
          .filter(
            (item) =>
              item.DeviceID &&
              Number.isFinite(item.Latitude) &&
              Number.isFinite(item.Longitude) &&
              !Number.isNaN(item.date.getTime())
          );

        setGpsData(validRecords);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filteredData = useMemo(() => {
    return gpsData.filter((item) => {
      const hour = item.date.getHours();

      if (timeFilter === "Morning") return hour >= 6 && hour < 12;
      if (timeFilter === "Afternoon") return hour >= 12 && hour < 17;
      if (timeFilter === "Evening") return hour >= 17 && hour < 21;
      if (timeFilter === "Night") return hour >= 21 || hour < 6;

      return true;
    });
  }, [gpsData, timeFilter]);

  const hourlyData = useMemo(() => {
    return Array.from({ length: 24 }, (_, hour) => {
      const records = filteredData.filter(
        (item) => item.date.getHours() === hour
      );

      return {
        hour: `${String(hour).padStart(2, "0")}:00`,
        pings: records.length,
        devices: new Set(records.map((item) => item.DeviceID)).size
      };
    });
  }, [filteredData]);

  const locationData = useMemo(() => {
    const locations = {};

    filteredData.forEach((item) => {
      const key = `${item.Latitude.toFixed(3)}, ${item.Longitude.toFixed(3)}`;

      if (!locations[key]) {
        locations[key] = {
          location: key,
          visits: 0,
          devices: new Set()
        };
      }

      locations[key].visits += 1;
      locations[key].devices.add(item.DeviceID);
    });

    return Object.values(locations)
      .map((item) => ({
        location: item.location,
        visits: item.visits,
        devices: item.devices.size
      }))
      .sort((a, b) => b.visits - a.visits)
      .slice(0, 8);
  }, [filteredData]);

  const activeDevices = new Set(
    filteredData.map((item) => item.DeviceID)
  ).size;

  const peakHour = hourlyData.reduce(
    (peak, item) => (item.pings > peak.pings ? item : peak),
    { hour: "N/A", pings: 0 }
  );

  const activeHours = hourlyData.filter((item) => item.pings > 0);

  const quietHour = activeHours.length
    ? activeHours.reduce((quiet, item) =>
        item.pings < quiet.pings ? item : quiet
      )
    : { hour: "N/A", pings: 0 };

  const morningCount = gpsData.filter(
    (item) => item.date.getHours() >= 6 && item.date.getHours() < 12
  ).length;

  const afternoonCount = gpsData.filter(
    (item) => item.date.getHours() >= 12 && item.date.getHours() < 17
  ).length;

  const activityComparison =
    morningCount > afternoonCount
      ? "Morning"
      : afternoonCount > morningCount
        ? "Afternoon"
        : "Equal";

  const activityInsight =
    morningCount === afternoonCount
      ? "Morning and afternoon have equal GPS activity."
      : `${activityComparison} activity is higher, with ${
          Math.max(morningCount, afternoonCount).toLocaleString()
        } GPS records compared with ${
          Math.min(morningCount, afternoonCount).toLocaleString()
        } in the other period.`;

  if (loading) {
    return <div className="mob-message">Loading mobility data...</div>;
  }

  if (error) {
    return <div className="mob-message">Error: {error}</div>;
  }

  return (
    <div className="mob-page">
      {/* Header */}
      <div className="mob-header">
        <div className="mob-title-block">
          <p className="mob-eyebrow">GEO PULSE / LOCATION INTELLIGENCE</p>
          <h2>Mobility Analysis</h2>
          <p>Understand movement patterns and geographic activity across your retail area.</p>
        </div>

        <div className="mob-filter-wrap">
          <label htmlFor="mob-time-filter">Time Period</label>
          <select
            id="mob-time-filter"
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value)}
            className="mob-filter"
          >
            <option value="All">All Day</option>
            <option value="Morning">Morning</option>
            <option value="Afternoon">Afternoon</option>
            <option value="Evening">Evening</option>
            <option value="Night">Night</option>
          </select>
        </div>
      </div>

      {/* KPI cards */}
      <div className="mob-stats">
        <div className="mob-card">
          <div className="mob-card-top">
            <span className="mob-card-label">GPS RECORDS</span>
            <span className="mob-card-icon mob-icon-blue">⌖</span>
          </div>
          <h2>{filteredData.length.toLocaleString()}</h2>
          <p>Records in selected period</p>
        </div>

        <div className="mob-card">
          <div className="mob-card-top">
            <span className="mob-card-label">ACTIVE DEVICES</span>
            <span className="mob-card-icon mob-icon-teal">◉</span>
          </div>
          <h2>{activeDevices.toLocaleString()}</h2>
          <p>Unique device identifiers</p>
        </div>

        <div className="mob-card">
          <div className="mob-card-top">
            <span className="mob-card-label">PEAK ACTIVITY</span>
            <span className="mob-card-icon mob-icon-amber">↗</span>
          </div>
          <h2>{peakHour.hour}</h2>
          <p>{peakHour.pings.toLocaleString()} GPS records</p>
        </div>

        <div className="mob-card">
          <div className="mob-card-top">
            <span className="mob-card-label">LOCATION CLUSTERS</span>
            <span className="mob-card-icon mob-icon-purple">⌘</span>
          </div>
          <h2>{locationData.length}</h2>
          <p>Top geographic coordinates</p>
        </div>
      </div>

      {/* Insights */}
      <section className="mob-insights">
        <div className="mob-insights-heading">
          <div className="mob-insights-title">
            <span className="mob-insights-icon">✦</span>
            <div>
              <h3>Mobility Insights</h3>
              <p>Quick observations from the GPS dataset</p>
            </div>
          </div>
          <span className="mob-insights-tag">AUTO ANALYSIS</span>
        </div>

        <div className="mob-insights-grid">
          <div className="mob-insight-item">
            <span className="mob-insight-label">BUSIEST HOUR</span>
            <strong>{peakHour.hour}</strong>
            <p>{peakHour.pings.toLocaleString()} GPS records</p>
          </div>

          <div className="mob-insight-item">
            <span className="mob-insight-label">QUIETEST ACTIVE HOUR</span>
            <strong>{quietHour.hour}</strong>
            <p>{quietHour.pings.toLocaleString()} GPS records</p>
          </div>

          <div className="mob-insight-item">
            <span className="mob-insight-label">HIGHER ACTIVITY PERIOD</span>
            <strong>{activityComparison}</strong>
            <p>Morning compared with afternoon</p>
          </div>
        </div>

        <div className="mob-insight-summary">
          <span className="mob-summary-mark">i</span>
          {activityInsight}
        </div>
      </section>

      {/* Charts */}
      <div className="mob-chart-grid">
        <section className="mob-panel">
          <div className="mob-panel-heading">
            <div>
              <h3>Hourly GPS Activity</h3>
              <p>GPS records collected throughout the day</p>
            </div>
            <span className="mob-chart-unit">RECORDS</span>
          </div>

          <ResponsiveContainer width="100%" height={290}>
            <BarChart data={hourlyData} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
              <CartesianGrid stroke="#edf2f7" vertical={false} />
              <XAxis dataKey="hour" interval={2} tick={{ fontSize: 11, fill: "#7b8798" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#7b8798" }} axisLine={false} tickLine={false} />
              <Tooltip />
              <Bar dataKey="pings" name="GPS Records" fill="#3978e8" radius={[5, 5, 0, 0]} maxBarSize={22} />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="mob-panel">
          <div className="mob-panel-heading">
            <div>
              <h3>Active Device Trend</h3>
              <p>Unique devices recorded each hour</p>
            </div>
            <span className="mob-chart-unit">DEVICES</span>
          </div>

          <ResponsiveContainer width="100%" height={290}>
            <LineChart data={hourlyData} margin={{ top: 10, right: 10, left: -15, bottom: 5 }}>
              <CartesianGrid stroke="#edf2f7" vertical={false} />
              <XAxis dataKey="hour" interval={2} tick={{ fontSize: 11, fill: "#7b8798" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#7b8798" }} axisLine={false} tickLine={false} />
              <Tooltip />
              <Line type="monotone" dataKey="devices" name="Active Devices" stroke="#0d9488" strokeWidth={3} dot={false} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </section>
      </div>

      {/* Locations table */}
      <section className="mob-panel mob-location-panel">
        <div className="mob-panel-heading">
          <div>
            <h3>Popular GPS Locations</h3>
            <p>Coordinate groups ranked by GPS record activity</p>
          </div>
          <span className="mob-chart-unit">TOP {locationData.length}</span>
        </div>

        <div className="mob-table-wrap">
          <table>
            <thead>
              <tr>
                <th>RANK</th>
                <th>LOCATION COORDINATES</th>
                <th>GPS RECORDS</th>
                <th>UNIQUE DEVICES</th>
              </tr>
            </thead>
            <tbody>
              {locationData.map((item, index) => (
                <tr key={item.location}>
                  <td>
                    <span className={`mob-rank ${index === 0 ? "mob-rank-first" : ""}`}>
                      {String(index + 1).padStart(2, "0")}
                    </span>
                  </td>
                  <td>{item.location}</td>
                  <td>{item.visits.toLocaleString()}</td>
                  <td>{item.devices.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <p className="mob-note">
        Mobility insights are based on synthetic GPS data. Coordinate groups are approximate and do not represent verified real-world visits.
      </p>
    </div>
  );
}

export default MobilityPage;

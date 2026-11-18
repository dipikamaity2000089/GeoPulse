
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
        if (!response.ok) {
          throw new Error("GPS dataset not found");
        }
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
            date: new Date(
              String(item.Timestamp).replace(" ", "T")
            )
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

      if (timeFilter === "Morning") {
        return hour >= 6 && hour < 12;
      }

      if (timeFilter === "Afternoon") {
        return hour >= 12 && hour < 17;
      }

      if (timeFilter === "Evening") {
        return hour >= 17 && hour < 21;
      }

      if (timeFilter === "Night") {
        return hour >= 21 || hour < 6;
      }

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
        devices: new Set(
          records.map((item) => item.DeviceID)
        ).size
      };
    });
  }, [filteredData]);

  const locationData = useMemo(() => {
    const locations = {};

    filteredData.forEach((item) => {
      const key =
        `${item.Latitude.toFixed(3)}, ${item.Longitude.toFixed(3)}`;

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
    (peak, item) =>
      item.pings > peak.pings ? item : peak,
    { hour: "N/A", pings: 0 }
  );

  if (loading) {
    return (
      <div className="mob-message">
        Loading mobility data...
      </div>
    );
  }

  if (error) {
    return (
      <div className="mob-message">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="mob-page">

      <div className="mob-header">
        <div>
          <p className="mob-eyebrow">
            RETAIL LOCATION INTELLIGENCE
          </p>
          <h2>Mobility Analysis</h2>
          <p>
            Explore GPS movement patterns, active devices
            and popular geographic locations.
          </p>
        </div>

        <select
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

      <div className="mob-stats">
        <div className="mob-card">
          <span>Total GPS Records</span>
          <h2>{filteredData.length.toLocaleString()}</h2>
        </div>

        <div className="mob-card">
          <span>Active Devices</span>
          <h2>{activeDevices.toLocaleString()}</h2>
        </div>

        <div className="mob-card">
          <span>Peak Activity Hour</span>
          <h2>{peakHour.hour}</h2>
        </div>

        <div className="mob-card">
          <span>Locations Identified</span>
          <h2>{locationData.length}</h2>
        </div>
      </div>

      <div className="mob-chart-grid">

        <div className="mob-panel">
          <h3>Hourly GPS Activity</h3>
          <p>GPS records collected during each hour</p>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar
                dataKey="pings"
                fill="#2563EB"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mob-panel">
          <h3>Active Device Trend</h3>
          <p>Unique devices recorded during each hour</p>

          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="devices"
                stroke="#0D9488"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

      </div>

      <div className="mob-panel mob-location-panel">
        <h3>Popular GPS Locations</h3>
        <p>
          Geographic coordinate groups ranked by GPS record count
        </p>

        <div className="mob-table-wrap">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Location Coordinates</th>
                <th>GPS Records</th>
                <th>Unique Devices</th>
              </tr>
            </thead>

            <tbody>
              {locationData.map((item, index) => (
                <tr key={item.location}>
                  <td>{index + 1}</td>
                  <td>{item.location}</td>
                  <td>{item.visits}</td>
                  <td>{item.devices}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="mob-note">
        Note: Mobility insights are calculated from synthetic
        GPS records. Coordinate groups are approximate
        geographic clusters, not verified real-world visits.
      </p>

    </div>
  );
}

export default MobilityPage;

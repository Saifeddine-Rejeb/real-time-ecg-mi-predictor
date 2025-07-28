import React from 'react';
import './home.css';

export default function Home() {
  // Example stats
  const stats = [
    { label: 'Patients', value: 8, icon: '🧑‍⚕️', color: '#0077b6' },
    { label: 'Active Devices', value: 6, icon: '📟', color: '#4caf50' },
    { label: 'Alerts', value: 4, icon: '🚨', color: '#f44336' },
  ];

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="dashboard-cards">
        {stats.map((stat) => (
          <div className="dashboard-card" key={stat.label} style={{ borderColor: stat.color }}>
            <span className="dashboard-icon" style={{ color: stat.color }}>{stat.icon}</span>
            <div className="dashboard-value">{stat.value}</div>
            <div className="dashboard-label">{stat.label}</div>
          </div>
        ))}
      </div>
      <div className="dashboard-welcome">
        <h2>Welcome!</h2>
        <p>This is your medical monitoring dashboard. Use the sidebar to navigate between patients, alerts, and device reports.</p>
      </div>
    </div>
  );
}

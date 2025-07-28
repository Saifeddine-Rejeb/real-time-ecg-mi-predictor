import React from 'react';
import './alerts.css';
import { useNavigate } from 'react-router-dom';

// Simulated MI alerts based on files in back/test/mi(crise)
const alerts = [
  { id: '02331_hr', message: 'MI Alert for Patient 02331', time: '2025-06-19 09:12' },
  { id: '03829_hr', message: 'MI Alert for Patient 03829', time: '2025-06-19 10:05' },
  { id: '00867_hr', message: 'MI Alert for Patient 00867', time: '2025-06-19 10:10' },
  { id: '00868_hr', message: 'MI Alert for Patient 00868', time: '2025-06-19 10:15' },
];

export default function Alerts() {
  const navigate = useNavigate();
  return (
    <div className="alerts-list">
      <h2>MI Alerts</h2>
      <ul>
        {alerts.map((alert) => (
          <li key={alert.id} onClick={() => navigate(`/alerts/${alert.id}`)} style={{ cursor: 'pointer' }}>
            <span className="alert-id">{alert.id}</span>
            {alert.message}
            <span style={{ color: '#888', fontSize: '0.95em', marginLeft: 12 }}>
              {alert.time}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

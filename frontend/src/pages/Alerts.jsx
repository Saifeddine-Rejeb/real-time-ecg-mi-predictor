import React from 'react';
import './alerts.css';
import { useNavigate } from 'react-router-dom';

// Simulated MI alerts based on files in back/test/mi(crise)
const alerts = [
  { id: '02331_hr', message: 'MI Alert', time: '2025-06-19 09:12' },
  { id: '03829_hr', message: 'MI Alert', time: '2025-06-19 10:05' },
  { id: '00867_hr', message: 'MI Alert', time: '2025-06-19 10:10' },
  { id: '00868_hr', message: 'MI Alert', time: '2025-06-19 10:15' },
];

export default function Alerts() {
  const navigate = useNavigate();
  return (
    <div className="alerts-list">
      <h2>MI Alerts</h2>
      <table>
        <thead>
          <tr>
            <th>Alert ID</th>
            <th>Message</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id} onClick={() => navigate(`/alerts/${alert.id}`)} style={{ cursor: 'pointer' }}>
              <td>{alert.id}</td>
              <td>{alert.message}</td>
              <td>{alert.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

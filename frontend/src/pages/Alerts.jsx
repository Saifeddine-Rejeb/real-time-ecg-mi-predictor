import React from 'react';
import './alerts.css';
import { useNavigate } from 'react-router-dom';
import { alertExamples } from '../data/alert_examples';

const alerts = alertExamples.map(example => ({
  id: example.id,
  Patient: example.name,
  classification: example.predicted_full_name,
  confidence: `${(example.confidence * 100).toFixed(2)}%`,
  time: example.time,
}));


export default function Alerts() {
  const navigate = useNavigate();
  return (
    <div className="alerts-list">
      <h2>MI Alerts</h2>
      <table>
        <thead>
          <tr>
            <th>Patient</th>
            <th>Classification</th>
            <th>Confidence</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr key={alert.id} onClick={() => navigate(`/alerts/${alert.id}`)} style={{ cursor: 'pointer' }}>
              <td>{alert.Patient}</td>
              <td>{alert.classification}</td>
              <td>{alert.confidence}</td>
              <td>{alert.time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}



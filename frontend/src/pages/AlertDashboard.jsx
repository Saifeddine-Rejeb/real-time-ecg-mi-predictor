import React, { useEffect, useState } from 'react';
import Example from '../components/chart';
import Prediction from '../components/prediction';
import Vitals from '../components/vitals';
import { useParams } from 'react-router-dom';
import './alertDashboard.css';

export default function AlertDashboard() {
  const { alertId } = useParams();
  const [ecgData, setEcgData] = useState(null);
  const [predictedClass, setPredictedClass] = useState('');
  const [vitals, setVitals] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:5000/api/ecg?file=mi(crise)/${alertId}`)
      .then(res => res.json())
      .then(data => setEcgData(data));
    // Fetch vitals for this alert (using alertId as patient param)
    fetch(`http://localhost:5000/api/vitals?patient=${alertId}`)
      .then(res => res.json())
      .then(data => setVitals(data));
  }, [alertId]);

  useEffect(() => {
    if (ecgData) {
      fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file: `mi(crise)/${alertId}` }),
      })
        .then(res => res.json())
        .then(data => setPredictedClass(data.class));
    }
  }, [ecgData, alertId]);

  return (
    <div className="chart">
      <div className="patient-info">
        <h2 className="alert-dashboard-title">Alert for Patient {alertId}</h2>
        <p className="alert-time">{'2025-06-19 09:12'}</p>
      </div>
  
      <Prediction predictedClass={predictedClass} />
      <Vitals vitals={vitals} />
      <Example data={ecgData} />
    </div>
  );
}

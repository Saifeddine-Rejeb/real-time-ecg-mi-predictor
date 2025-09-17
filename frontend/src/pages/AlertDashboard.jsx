import React, { useEffect, useState } from 'react';
import Chart from '../components/chart';
import Prediction from '../components/prediction';
import Vitals from '../components/vitals';
import { useParams } from 'react-router-dom';
import { alertExamples } from '../data/alert_examples';
import './alertDashboard.css';

export default function AlertDashboard() {
  const { alertId } = useParams();
  const [ecgData, setEcgData] = useState(null);
  const [predictedClass, setPredictedClass] = useState('');
  const [predictedText, setPredictedText] = useState('');
  const [predictedConfidence, setPredictedConfidence] = useState(null);
  const [vitals, setVitals] = useState(null);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    const foundAlert = alertExamples.find(a => a.id === alertId);
    setAlert(foundAlert || null);

    if (foundAlert) {
      // Set prediction data from alert examples
      setPredictedClass(foundAlert.predicted_class_name);
      setPredictedText(foundAlert.predicted_full_name);
      setPredictedConfidence(foundAlert.confidence);
      
      // Set vitals from alert examples
      setVitals(foundAlert.vitals);

      // Fetch ECG data using sourcePath
      const source = encodeURIComponent(foundAlert.sourcePath);
      fetch(`http://localhost:5000/api/ecg?file=${source}`)
        .then(res => res.json())
        .then(data => setEcgData(data))
        .catch(() => setEcgData(null));
    }
  }, [alertId]);

  return (
    <div className="chart">
      <div className="patient-info">
        <h2 className="alert-dashboard-title">Alert for {alert?.name || `Patient ${alertId}`}</h2>
        <p className="alert-time">{alert?.time || '2025-06-19 09:12'}</p>
      </div>
  
      <Prediction 
        predictedClass={predictedClass} 
        displayText={predictedText} 
        confidence={predictedConfidence} 
      />
      <Vitals vitals={vitals} />
      <Chart data={ecgData} />
    </div>
  );
}

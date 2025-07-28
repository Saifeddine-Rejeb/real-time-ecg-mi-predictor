import React from 'react';
import './vitals.css';
import PCGChart from './PCGChart';
import RRChart from './RRChart';

export default function Vitals({ vitals }) {
  if (!vitals) return <div className="vitals-loading">Loading vitals...</div>;
  return (
    <div className="vitals-container">
      <div className="vital-item">
        <span className="vital-label">Heart Rate:</span>
        <span className="vital-value">{vitals.heartRate ?? '--'} bpm</span>
      </div>
      <div className="vital-item">
        <span className="vital-label">PCG:</span>
        <span className="vital-value">{vitals.pcg ?? '--'}</span>
      </div>
      <div className="vital-item">
        <span className="vital-label">Skin Temperature:</span>
        <span className="vital-value">{vitals.skinTemp ?? '--'} °C</span>
      </div>
      <div className="vital-item">
        <span className="vital-label">Heart Rate Variability:</span>
        <span className="vital-value">{vitals.hrv ?? '--'} ms</span>
      </div>
      <div className="vital-item">
        <span className="vital-label">Respiratory Rate:</span>
        <span className="vital-value">{vitals.respiratoryRate ?? '--'} rpm</span>
      </div>
      <div className="vital-item">
        <span className="vital-label">Average RR Interval:</span>
        <span className="vital-value">{vitals.rrIntervalAvg ?? '--'} ms</span>
      </div>
      <div className="vital-chart-wrapper">
        <RRChart data={vitals.rrDistances} />
      </div>
      <div className="vital-chart-wrapper">
        <PCGChart data={vitals.pcgSignal} />
      </div>
    </div>
  );
}

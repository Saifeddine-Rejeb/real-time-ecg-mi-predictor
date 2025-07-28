
import React from 'react';
import './PatientInfo.css';

export default function StreamingPatientInfo({ patient }) {
  if (!patient) return null;

  const now = new Date();
  const formattedTime = now.toLocaleString();

  const capitalize = (str) => str ? str.charAt(0).toUpperCase() + str.slice(1) : '';

  const lastAlert = patient.alerts?.length > 0 ? patient.alerts.at(-1) : null;

  const statusMap = {
    active: { label: 'Active', color: 'active' },
    alert: { label: 'Alert', color: 'alert' },
    offline: { label: 'Offline', color: 'offline' }
  };

  const status = statusMap[patient.status?.toLowerCase()] || { label: 'Unknown', color: 'offline' };

  return (
    <div className="patient-info">
      <div className="patient-header">
        <div className="patient-main-line">
          <h1>{patient.name}</h1>
          <div className="status-chip">
            <span className={`status-circle ${status.color}`} />
            <span className="status-label">{status.label}</span>
          </div>
        </div>

        <div className="patient-sub-line">
          <span>{patient.deviceId}</span>
          <br />
          {patient.gender && patient.age && (
            <span>{capitalize(patient.gender)}, {patient.age}</span>
          )}
          {patient.status === 'offline' && patient.lastTimeOnline && (
            <div className="patient-last-online">Last time online: {patient.lastTimeOnline}</div>
          )}
        </div>
      </div>

      {lastAlert && (
        <div className="patient-alert">
          <strong>Last Alert:</strong> {lastAlert.problem}
          <span className="alert-time">{lastAlert.time}</span>
        </div>
      )}

      <div className="patient-footer">
        <span>🕒 {formattedTime}</span>
        <span style={{ marginLeft: 16 }}><strong>Last HR:</strong> {patient.lastHR}</span>
      </div>
    </div>
  );
}

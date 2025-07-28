import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './reportEditor.css';

export default function ReportEditor() {
  const location = useLocation();
  const navigate = useNavigate();
  const { patient, vitals, prediction, ecgData } = location.state || {};

  // Simulate AI-generated report
  const defaultReport = `Patient: ${patient?.name || ''}\nDevice ID: ${patient?.deviceId || ''}\nStatus: ${patient?.status || ''}\nAge/Gender: ${patient?.age || ''} / ${patient?.gender || ''}\n\nVitals:\nHeart Rate: ${vitals?.heartRate ?? '--'} bpm\nHRV: ${vitals?.hrv ?? '--'} ms\nRespiratory Rate: ${vitals?.respiratoryRate ?? '--'} rpm\n\nPrediction: ${prediction || '--'}\n\nECG Data: ${ecgData ? 'Available' : 'Not available'}\n\nAI Summary:\nThis is an AI-generated summary based on the latest patient data. Please review, modify, or reject as needed.`;

  const [reportText, setReportText] = useState(defaultReport);
  const [doctorNotes, setDoctorNotes] = useState('');
  const [status, setStatus] = useState('pending');

  const handleValidate = () => {
    setStatus('validated');
    alert('Report validated and saved!');
    // Here you would send the report to backend for saving
  };
  const handleReject = () => {
    setStatus('rejected');
    alert('Report rejected.');
    // Here you would notify backend or log rejection
  };

  return (
    <div className="report-editor">
      <h2>AI Generated Report</h2>
      <textarea
        className="report-textarea"
        value={reportText}
        onChange={e => setReportText(e.target.value)}
        rows={16}
      />
      <h3>Doctor's Notes</h3>
      <textarea
        className="notes-textarea"
        value={doctorNotes}
        onChange={e => setDoctorNotes(e.target.value)}
        rows={6}
        placeholder="Add your notes here..."
      />
      <div className="report-actions">
        <button className="validate-btn" onClick={handleValidate} disabled={status==='validated'}>Validate</button>
        <button className="reject-btn" onClick={handleReject} disabled={status==='rejected'}>Reject</button>
        <button className="back-btn" onClick={() => navigate(-1)}>Back</button>
      </div>
      <div className="report-status">Status: <strong>{status}</strong></div>
    </div>
  );
}

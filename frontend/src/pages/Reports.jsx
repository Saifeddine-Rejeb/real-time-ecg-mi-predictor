import React from 'react';
import './reports.css';

const exampleReports = [
  {
    id: 1,
    patient: 'Patient 06187',
    diagnosis: 'MI',
    timestamp: '2025-07-10 14:23',
    pdfUrl: '#',
  },
  {
    id: 2,
    patient: 'Patient 04842',
    diagnosis: 'Normal',
    timestamp: '2025-07-09 09:10',
    pdfUrl: '#',
  }
];

export default function Reports() {
  return (
    <div className="reports-container">
      <h2 style={{ color: '#1976d2', marginBottom: 18 }}>Reports</h2>
      <table className="reports-table">
        <thead>
          <tr>
            <th>Patient</th>
            <th>Report</th>
            <th>Diagnosis</th>
            <th>Timestamp</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {exampleReports.map((report) => (
            <tr key={report.id}>
              <td>{report.patient}</td>
              <td>
                <button className="reports-action-btn" onClick={() => window.open(report.pdfUrl, '_blank')}>Open PDF</button>
              </td>
              <td>{report.diagnosis}</td>
              <td>{report.timestamp}</td>
              <td>
                <button className="reports-action-btn edit">Edit</button>
                <button className="reports-action-btn remove">Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

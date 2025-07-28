import React, { useState } from 'react';
import './patients.css';
import { useNavigate } from 'react-router-dom';

// Example patient data with deviceId, status, alerts, and lastHR
import { patients } from '../data/patients'; 

function getStatusClass(status) {
  if (status === 'active') return 'status-green';
  if (status === 'offline') return 'status-grey';
  if (status === 'alert') return 'status-red';
  return '';
}

function getStatusLabel(status) {
  if (status === 'active') return 'Active';
  if (status === 'offline') return 'Offline';
  if (status === 'alert') return 'Alert';
  return '';
}

function Patients() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [testPatient] = useState({
    id: 'stream-test',
    deviceId: 'stream-001',
    status: 'active',
    name: 'Stream Test Patient',
    alerts: [],
    lastHR: '-',
  });

  // Optionally, you could fetch initial vitals/HR here if desired

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const filteredPatients = patients.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.deviceId.toLowerCase().includes(search.toLowerCase())
  );

  // Add the test patient to the list
  const allPatients = [...filteredPatients, testPatient];

  // Sort so that 'alert' status is always on top
  const sortedPatients = [...allPatients].sort((a, b) => {
    if (a.status === 'alert' && b.status !== 'alert') return -1;
    if (a.status !== 'alert' && b.status === 'alert') return 1;
    // Then apply the selected sort
    let valA = a[sortBy];
    let valB = b[sortBy];
    if (sortBy === 'lastHR') {
      valA = Number(valA);
      valB = Number(valB);
    } else {
      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
    }
    if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
    if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="patients-list">
      <h2>Patients List</h2>
      <div className="patients-controls">
        <input
          type="text"
          placeholder="Search by name or device ID..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="patients-search"
        />
        <select value={sortBy} onChange={e => setSortBy(e.target.value)} className="patients-sort">
          <option value="name">Sort by Patient</option>
          <option value="deviceId">Sort by Device ID</option>
          <option value="status">Sort by Status</option>
          <option value="lastHR">Sort by Last HR</option>
        </select>
        <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')} className="patients-sort-btn">
          {sortOrder === 'asc' ? '▲' : '▼'}
        </button>
      </div>
      <table className="patients-table">
        <thead>
          <tr>
            <th onClick={() => handleSort('deviceId')}>Device ID</th>
            <th onClick={() => handleSort('status')}>Status</th>
            <th onClick={() => handleSort('name')}>Patient</th>
            <th>Alerts</th>
            <th onClick={() => handleSort('lastHR')}>Last HR</th>
          </tr>
        </thead>
        <tbody>
          {sortedPatients.map((patient) => (
            <tr key={patient.id} onClick={() => {
              if (patient.id === 'stream-test') {
                navigate(`/patients/${patient.id}?stream=1`);
              } else {
                navigate(`/patients/${patient.id}`);
              }
            }}>
              <td>{patient.deviceId}</td>
              <td>
                <span className={`status-circle ${getStatusClass(patient.status)}`}></span>
                {getStatusLabel(patient.status)}
              </td>
              <td>{patient.name}</td>
              <td>
                {patient.alerts.length === 0 ? (
                  <span>-</span>
                ) : (
                  (() => {
                    const latestAlert = patient.alerts[patient.alerts.length - 1];
                    return (
                      <span><strong>{latestAlert.problem}</strong>, <span style={{ color: '#888', fontSize: '0.95em' }}>{latestAlert.time}</span></span>
                    );
                  })()
                )}
              </td>
              <td>{patient.lastHR}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Patients;

import React, { useEffect, useState, useRef } from 'react';
import Chart from '../components/chart';
import Prediction from '../components/prediction';
import { useParams } from 'react-router-dom';
import Vitals from '../components/vitals';
import PatientInfo from '../components/PatientInfo';
import { patients } from '../data/patients';

export default function PatientDashboard() {
  const { patientId } = useParams();
  const [ecgData, setEcgData] = useState(null);
  const [predictedClass, setPredictedClass] = useState('');
  const [vitals, setVitals] = useState(null);
  const [patient, setPatient] = useState(null);
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const chartRef = useRef();

  useEffect(() => {
    fetch(`http://localhost:5000/api/ecg?file=normal/${patientId}`)
      .then(res => res.json())
      .then(data => setEcgData(data));

    fetch(`http://localhost:5000/api/vitals?patient=${patientId}`)
      .then(res => res.json())
      .then(data => setVitals(data));

    const found = patients.find(p => p.id === patientId);
    setPatient(found || null);
  }, [patientId]);

  useEffect(() => {
    if (ecgData) {
      fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file: `normal/${patientId}` }),
      })
        .then(res => res.json())
        .then(data => setPredictedClass(data.class));
    }
  }, [ecgData, patientId]);

  const handleGenerateReport = async () => {
    // Dynamically import jsPDF and html2canvas
    const [{ default: jsPDF }, html2canvas] = await Promise.all([
      import('jspdf'),
      import('html2canvas').then(m => m.default)
    ]);

    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text('Patient ECG Report', 14, 18);
    doc.setFontSize(12);
    doc.text(`Name: ${patient?.name || ''}`, 14, 30);
    doc.text(`ID: ${patient?.id || ''}`, 14, 38);
    doc.text(`Age: ${patient?.age || ''}`, 14, 46);
    doc.text(`Gender: ${patient?.gender || ''}`, 14, 54);
    doc.text(`Status: ${patient?.status || ''}`, 14, 62);
    doc.text(`Prediction: ${predictedClass || ''}`, 14, 74);
    doc.text(`Last HR: ${vitals?.heartRate || '-'}`, 14, 82);
    doc.text('---', 14, 90);
    doc.text('ECG Data (first 10 values):', 14, 98);
    if (ecgData && Array.isArray(ecgData) && ecgData.length > 0) {
      const firstRow = Array.isArray(ecgData[0]) ? ecgData[0] : Object.values(ecgData[0]);
      doc.setFontSize(10);
      doc.text(firstRow.slice(0, 10).map(v => String(v)).join(', '), 14, 106);
    }

    // Add ECG chart as image
    if (chartRef.current) {
      const canvas = await html2canvas(chartRef.current, { backgroundColor: '#fff', scale: 2 });
      const imgData = canvas.toDataURL('image/png');
      doc.addPage();
      doc.setFontSize(16);
      doc.text('ECG Signal', 14, 20);
      doc.addImage(imgData, 'PNG', 10, 30, 190, 80);
    }

    // Show PDF in modal
    const pdfBlob = doc.output('blob');
    const url = URL.createObjectURL(pdfBlob);
    setPdfUrl(url);
    setShowPdfModal(true);
  };

  return (
    <div className="chart">
      <div id="patient-info">
        <PatientInfo patient={patient} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button className="report-btn" onClick={handleGenerateReport}>Generate Report</button>
      </div>

      <div id="vitals-section">
        <Vitals vitals={vitals} />
      </div>

      <div id="prediction-section">
        <Prediction predictedClass={predictedClass} />
      </div>

      <div id="chart-section" ref={chartRef} style={{ background: '#fff', padding: 8, borderRadius: 8 }}>
        <Chart data={ecgData} />
      </div>

      {showPdfModal && pdfUrl && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ background: '#fff', padding: 24, borderRadius: 8, maxWidth: '90vw', maxHeight: '90vh', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <h2>PDF Preview</h2>
            <iframe src={pdfUrl} title="PDF Preview" style={{ width: '60vw', height: '70vh', border: '1px solid #ccc', marginBottom: 16 }}></iframe>
            <div style={{ display: 'flex', gap: 12 }}>
              <a href={pdfUrl} download={`patient_${patient?.id || 'report'}.pdf`} className="report-btn">Download PDF</a>
              <button className="report-btn" onClick={() => {
                setShowPdfModal(false);
                URL.revokeObjectURL(pdfUrl);
                setPdfUrl(null);
              }}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

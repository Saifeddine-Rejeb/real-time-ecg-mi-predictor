import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import './chart.css';

const LEAD_LABELS = [
  'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
  'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
];

const ECGVisualizer = ({ height = 250, data }) => {
  const [gridColumns, setGridColumns] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [modalLeadIdx, setModalLeadIdx] = useState(null);

  const getGridColumns = useCallback(() => {
    const w = window.innerWidth;
    if (w < 900) return 1;
    if (w < 2500) return 1;
    return 2;
  }, []);

  useEffect(() => {
    const handleResize = () => {
      setGridColumns(getGridColumns());
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [getGridColumns]);

  const openModal = (idx) => {
    setModalLeadIdx(idx);
    setModalOpen(true);
  };
  const closeModal = () => {
    setModalOpen(false);
    setModalLeadIdx(null);
  };

  // Helper to render millimetric grid as SVG background
  const renderMillimetricGrid = (props) => {
    const { width, height } = props;
    const mmPerPx = 4; // 1mm = 4px (adjust as needed)
    const majorEvery = 5; // major line every 5mm
    let lines = [];
    for (let x = 0; x < width; x += mmPerPx) {
      lines.push(
        <line
          key={`v-${x}`}
          x1={x}
          y1={0}
          x2={x}
          y2={height}
          stroke={x % (mmPerPx * majorEvery) === 0 ? '#e57373' : '#ffcdd2'}
          strokeWidth={x % (mmPerPx * majorEvery) === 0 ? 1.2 : 0.5}
        />
      );
    }
    for (let y = 0; y < height; y += mmPerPx) {
      lines.push(
        <line
          key={`h-${y}`}
          x1={0}
          y1={y}
          x2={width}
          y2={y}
          stroke={y % (mmPerPx * majorEvery) === 0 ? '#e57373' : '#ffcdd2'}
          strokeWidth={y % (mmPerPx * majorEvery) === 0 ? 1.2 : 0.5}
        />
      );
    }
    return (
      <g>{lines}</g>
    );
  };

  return (
    <div className="ecg-wrapper">
      <div
        className="ecg-grid"
        style={{ gridTemplateColumns: `repeat(${gridColumns}, 1fr)` }}
      >
        {LEAD_LABELS.map((label, idx) => (
          <div key={label} className="ecg-lead-container" onClick={() => openModal(idx)} style={{ cursor: 'pointer' }}>
            <div className="ecg-lead-label">{label}</div>
            <ResponsiveContainer width="100%" height={height}>
              <LineChart
                data={data}
                margin={{ top: 10, right: 20, left: 10, bottom: 10 }}
                syncId="ecgSync"
                // Add millimetric grid as SVG background
                background={{
                  render: renderMillimetricGrid
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
                <XAxis dataKey="time" type="number" domain={[0, 5000]} tick={{ fontSize: 14 }} />
                <YAxis domain={[-1.5, 1.5]} tick={{ fontSize: 14 }} />
                <Tooltip
                  content={({ label, payload }) => (
                    <div className="ecg-tooltip">
                      <div>{`Echantillon: ${label}`}</div>
                      {payload && payload.length > 0 && (
                        <div>{`Amplitude: ${payload[0].value.toFixed(2)}`}</div>
                      )}
                    </div>
                  )}
                />
                <Line
                  type="monotone"
                  dataKey={`lead${idx + 1}`}
                  stroke="#82ca9d"
                  dot={false}
                  isAnimationActive={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>
      {/* Modal for enlarged chart */}
      {modalOpen && modalLeadIdx !== null && (
        <div className="ecg-modal-overlay" onClick={closeModal}>
          <div className="ecg-modal-content ecg-modal-large" onClick={e => e.stopPropagation()}>
            <div className="ecg-modal-header">
              <span className="ecg-modal-title">{LEAD_LABELS[modalLeadIdx]}</span>
              <button className="ecg-modal-close" onClick={closeModal}>&times;</button>
            </div>
            <ResponsiveContainer width="100%" height={500}>
              <LineChart
                data={data}
                margin={{ top: 20, right: 60, left: 40, bottom: 20 }}
                // Add millimetric grid as SVG background in modal too
                background={{
                  render: renderMillimetricGrid
                }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
                <XAxis dataKey="time" type="number" domain={[0, 5000]} tick={{ fontSize: 18 }} />
                <YAxis domain={[-1.5, 1.5]} tick={{ fontSize: 18 }} />
                <Tooltip
                  content={({ label, payload }) => (
                    <div className="ecg-tooltip">
                      <div>{`Echantillon: ${label}`}</div>
                      {payload && payload.length > 0 && (
                        <div>{`Amplitude: ${payload[0].value.toFixed(2)}`}</div>
                      )}
                    </div>
                  )}
                />
                <Line
                  type="monotone"
                  dataKey={`lead${modalLeadIdx + 1}`}
                  stroke="#82ca9d"
                  dot={false}
                  isAnimationActive={false}
                  strokeWidth={4}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
};

export default ECGVisualizer;

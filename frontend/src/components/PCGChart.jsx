import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './PCGChart.css';

export default function PCGChart({ data }) {
  const [open, setOpen] = useState(false);
  if (!Array.isArray(data) || data.length === 0) return <div className="vital-chart-empty">No PCG data</div>;
  const chartData = data.map((v, i) => ({ x: i, y: v }));

  return (
    <>
      <div className="vital-chart-container" style={{ cursor: 'pointer' }} onClick={() => setOpen(true)}>
        <div className="vital-chart-title">PCG Signal</div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
            <XAxis dataKey="x" label={{ value: 'Sample', position: 'insideBottomRight', offset: -5 }} tick={false} />
            <YAxis domain={['auto', 'auto']} label={{ value: 'Amplitude', angle: -90, position: 'insideLeft', offset: 10 }} tick={{ fontSize: 12 }} />
            <Tooltip formatter={v => v.toFixed(3)} labelFormatter={i => `Sample ${i}`} />
            <Line type="monotone" dataKey="y" stroke="#1976d2" dot={false} strokeWidth={2} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {open && (
        <div className="pcg-modal-overlay" onClick={() => setOpen(false)}>
          <div className="pcg-modal-content" onClick={e => e.stopPropagation()}>
            <button className="pcg-modal-close" onClick={() => setOpen(false)} aria-label="Close">&times;</button>
            <div className="vital-chart-title" style={{ marginBottom: 8 }}>PCG Signal</div>
            <ResponsiveContainer width="100%" height={600}>
              <LineChart data={chartData} margin={{ top: 10, right: 40, left: 40, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
                <XAxis dataKey="x" label={{ value: 'Sample', position: 'insideBottomRight', offset: -5 }} tick={false} />
                <YAxis domain={['auto', 'auto']} label={{ value: 'Amplitude', angle: -90, position: 'insideLeft', offset: 10 }} tick={{ fontSize: 14 }} />
                <Tooltip formatter={v => v.toFixed(3)} labelFormatter={i => `Sample ${i}`} />
                <Line type="monotone" dataKey="y" stroke="#1976d2" dot={false} strokeWidth={2} isAnimationActive={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </>
  );
}

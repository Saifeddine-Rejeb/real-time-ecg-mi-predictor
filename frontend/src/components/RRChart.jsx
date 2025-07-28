import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function RRChart({ data }) {
  if (!Array.isArray(data) || data.length === 0) return <div className="vital-chart-empty">No RR data</div>;
  const chartData = data.map((v, i) => ({ beat: i + 1, rr: v }));
  return (
    <div className="vital-chart-container">
      <div className="vital-chart-title">RR Intervals</div>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
          <XAxis dataKey="beat" label={{ value: 'Beat', position: 'insideBottom', offset: -5 }} />
          <YAxis domain={['auto', 'auto']} label={{ value: 'ms', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={v => v + ' ms'} labelFormatter={i => `Beat ${i}`} />
          <Line type="monotone" dataKey="rr" stroke="#388e3c" dot={true} strokeWidth={2} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

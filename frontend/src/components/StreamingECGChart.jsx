import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';


export default function StreamingECGChart({ batches, error }) {
  if (error) return <div className="ecg-error">Error loading ECG: {error}</div>;
  if (!batches || batches.length === 0) return <div className="ecg-wrapper"><div className="stream-ecg">Loading ECG...</div></div>;
  let allSamples = [];
  batches.forEach(batch => {
    if (batch && Array.isArray(batch.ecg)) {
      allSamples.push(...batch.ecg);
    }
  });
  const chartData = allSamples.slice(0, 5000).map((row, i) => {
    let obj = { time: i };
    for (let l = 0; l < 12; l++) {
      obj[`lead${l+1}`] = row[l];
    }
    return obj;
  });
  const LEAD_LABELS = [
    'I', 'II', 'III', 'aVR', 'aVL', 'aVF',
    'V1', 'V2', 'V3', 'V4', 'V5', 'V6'
  ];
  return (
    <div className="ecg-wrapper">
      <div className="ecg-title">ECG Chart </div>
      <div className="ecg-grid">
        {LEAD_LABELS.map((label, idx) => (
          <div key={label} className="ecg-lead-container">
            <div className="ecg-lead-label">{label}</div>
            <ResponsiveContainer width="100%" height={140}>
              <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 10 }} syncId="ecgSync">
                <CartesianGrid strokeDasharray="3 3" stroke="#bdbdbd" />
                <XAxis dataKey="time" type="number" domain={[0, 5000]} tick={{ fontSize: 14 }} />
                <YAxis domain={['auto', 'auto']} tick={{ fontSize: 14 }} />
                <Tooltip content={({ label, payload }) => (
                  <div className="ecg-tooltip">
                    <div>{`Echantillon: ${label}`}</div>
                    {payload && payload.length > 0 && (
                      <div>{`Amplitude: ${payload[0].value?.toFixed(2)}`}</div>
                    )}
                  </div>
                )} />
                <Line type="monotone" dataKey={`lead${idx+1}`} stroke="#1976d2" dot={false} name={label} isAnimationActive={false} strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ))}
      </div>
    </div>
  );
}

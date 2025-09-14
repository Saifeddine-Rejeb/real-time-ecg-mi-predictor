import { useEffect, useRef, useState } from 'react';
import StreamingVitals from '../components/StreamingVitals';
import StreamingPatientInfo from '../components/StreamingPatientInfo';
import StreamingECGChart from '../components/StreamingECGChart';
import Prediction from '../components/prediction';
import './StreamingDashboard.css'; 

export default function StreamingDashboard() {
  const [batches, setBatches] = useState([]);
  const [vitals, setVitals] = useState(null); 
  const [prediction, setPrediction] = useState({});
  const [patient, setPatient] = useState({
    id: 'stream-test',
    deviceId: 'stream-001',
    status: 'active',
    name: 'Stream Test Patient',
    alerts: [],
    lastHR: '-',
    gender: 'Male',
    age: 20
  });
  const timerRef = useRef();
  const window = 10;
  const [nextBatchStart, setNextBatchStart] = useState(0);
  const [ecgError, setEcgError] = useState(null);
  const [vitalsError, setVitalsError] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:5000/api/mongo/stream?start=0&count=10`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch ECG data');
        return res.json();
      })
      .then(data => {
        setBatches(data);
        setNextBatchStart(data.length);
        setEcgError(null);
        const startIdx = Math.max(0, data.length - 10);
        fetch(`http://localhost:5000/api/mongo/vitals?window=10&start=${startIdx}`)
          .then(res => {
            if (!res.ok) throw new Error('Failed to fetch vitals');
            return res.json();
          })
          .then(vitalsData => {
            setVitals(vitalsData);
            setVitalsError(null);
            setPatient(p => ({
              ...p,
              lastHR: vitalsData.heartRate || '-'
            }));
          })
          .catch(err => {
            setVitalsError(err.message);
          });
      })
      .catch(err => {
        setEcgError(err.message);
      });
  }, []);

  useEffect(() => {
    if (batches.length === 0) return;
    timerRef.current = setInterval(() => {
      fetch(`http://localhost:5000/api/mongo/stream?start=${nextBatchStart}&count=1`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch ECG data');
          return res.json();
        })
        .then(newBatchArr => {
          if (Array.isArray(newBatchArr) && newBatchArr.length > 0) {
            setBatches(prev => {
              const updated = [...prev, ...newBatchArr];
              return updated.length > window ? updated.slice(updated.length - window) : updated;
            });
            setNextBatchStart(prev => prev + 1);
            setEcgError(null);
            const startIdx = Math.max(0, nextBatchStart - window + 1);
            fetch(`http://localhost:5000/api/mongo/vitals?window=10&start=${startIdx}`)
              .then(res => {
                if (!res.ok) throw new Error('Failed to fetch vitals');
                return res.json();
              })
              .then(vitalsData => {
                setVitals(vitalsData);
                setVitalsError(null);
                setPatient(p => ({
                  ...p,
                  lastHR: vitalsData.heartRate || '-'
                }));
              })
              .catch(err => {
                setVitalsError(err.message);
              });

            const windowBatches = batches.length >= window
              ? batches.slice(-window)
              : [...batches, ...newBatchArr].slice(-window);
            const allSamples = windowBatches.flatMap(batch => batch.ecg || []);
            // Prepare 1D array for model: extract first lead, resample to 187, normalize
            const flatSamples = allSamples.map(row => Array.isArray(row) ? row[0] : 0); // first lead
            // Resample to 187
            let resampled = flatSamples;
            if (flatSamples.length !== 187) {
              // Linear interpolation
              const n = flatSamples.length;
              resampled = Array.from({ length: 187 }, (_, i) => {
                const idx = (i * (n - 1)) / (187 - 1);
                const low = Math.floor(idx);
                const high = Math.ceil(idx);
                if (low === high) return flatSamples[low];
                const weight = idx - low;
                return flatSamples[low] * (1 - weight) + flatSamples[high] * weight;
              });
            }
            // Min-max normalize
            const min = Math.min(...resampled);
            const max = Math.max(...resampled);
            const normed = (max - min > 0)
              ? resampled.map(v => (v - min) / (max - min))
              : resampled.map(() => 0);
            fetch('http://localhost:5000/api/realtime/predict', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ ecg: normed })
            })
              .then(res => res.json())
              .then(data => {
                // Accepts both {prediction: {...}} and flat {...}
                const pred = data.prediction || data;
                setPrediction(pred);
              })
              .catch(() => {
                setPrediction({});
              });
          }
        })
        .catch(err => {
          setEcgError(err.message);
        });
    }, 1000);
    return () => {
      clearInterval(timerRef.current);
    };
  }, [batches, nextBatchStart]);

  return (
    <div className="stream-dashboard">
      <StreamingPatientInfo patient={patient} />
      <StreamingVitals vitals={vitals} error={vitalsError} />
      <Prediction
        predictedClass={prediction.predicted_class_name || prediction.class || prediction.predicted_class || ''}
        displayText={prediction.predicted_full_name || prediction.predicted_class_name || ''}
        confidence={prediction.confidence}
      />
      <StreamingECGChart batches={batches} error={ecgError} />
      <div style={{ marginTop: 16 }}>
        <span>Streaming batch {nextBatchStart} (showing last {window})</span>
      </div>  
    </div>
  );
}

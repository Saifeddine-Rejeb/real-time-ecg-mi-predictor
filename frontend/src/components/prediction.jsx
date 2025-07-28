import React from 'react'
import './prediction.css'

export default function Prediction({ predictedClass }) {
  const normalized = (predictedClass || '').toUpperCase();
  let boxClass = 'prediction-box';
  if (normalized === 'UNKNOWN') boxClass += ' prediction-norm';
  if (normalized === 'NORM') boxClass += ' prediction-norm';
  if (normalized === 'MI') boxClass += ' prediction-mi';
  return (
    <div className={boxClass}>
      <h1>ECG Prediction</h1>
      <p>Predict the ECG signal class: <strong> <span id="predicted-class">{normalized ? normalized : ''}</span></strong> </p>
    </div>
  )
}

import React from 'react'
import './prediction.css'

export default function Prediction({ predictedClass, displayText, confidence }) {
  let text = '';
  if (typeof predictedClass === 'string') {
    text = predictedClass;
  } else if (predictedClass == null) {
    text = '';
  } else if (typeof predictedClass === 'number') {
    text = String(predictedClass);
  } else if (typeof predictedClass === 'object') {
    try {
      text = predictedClass.label || predictedClass.class || '';
      if (!text) text = JSON.stringify(predictedClass);
    } catch {
      text = '';
    }
  }
  // Prepare two views: classKey for styling; label for display
  const label = (typeof displayText === 'string' && displayText.trim().length > 0) ? displayText : text;
  const classKey = (typeof predictedClass === 'string' && predictedClass.trim().length > 0)
    ? predictedClass.trim().toUpperCase()
    : (label || '').toString().toUpperCase();
  const normalizedLabel = (label || '').toString().toUpperCase();

  const pretty = (() => {
    if (!normalizedLabel) return '';
    // Normalize common labels (English + French) for display
    if (normalizedLabel === 'NORM' || normalizedLabel === 'NORMAL' || normalizedLabel === 'NO' ||
        normalizedLabel.includes("PAS D'INSUFFISANCE CARDIAQUE") ||
        normalizedLabel.includes('PAS D’INSUFFISANCE CARDIAQUE')) {
      return 'Normal';
    }
    return label
      .replace(/_/g, ' ')
      .replace(/\bMI\b/g, 'MI')
      .replace(/\bCARDIAC\b/gi, 'Cardiac')
      .replace(/\bINSUFFICIENCY\b/gi, 'Insufficiency')
      .replace(/\bNO\b/gi, 'No')
      .replace(/\bPOSSIBLE\b/gi, 'Possible')
      .replace(/\bMILD\b/gi, 'Mild')
      .replace(/\bMODERATE\b/gi, 'Moderate')
      .replace(/\bSEVERE\b/gi, 'Severe');
  })();

  let boxClass = 'prediction-box';
  if (classKey.includes('SEVERE')) boxClass += ' prediction-severe';
  else if (classKey.includes('MODERATE')) boxClass += ' prediction-moderate';
  else if (classKey.includes('MILD')) boxClass += ' prediction-mild';
  else if (classKey.includes('POSSIBLE')) boxClass += ' prediction-possible';
  else if (classKey === 'NORM' || classKey === 'NORMAL' || classKey.startsWith('NO')) boxClass += ' prediction-norm';
  else if (classKey.includes('MI')) boxClass += ' prediction-mi';
  else if (normalizedLabel.includes("PAS D'INSUFFISANCE CARDIAQUE") || normalizedLabel.includes('PAS D’INSUFFISANCE CARDIAQUE')) boxClass += ' prediction-norm';
  else boxClass += ' prediction-unknown';

  const labelWithConfidence = (() => {
    if (pretty) {
      if (typeof confidence === 'number') {
        return `${pretty} (${(confidence * 100).toFixed(1)}%)`;
      }
      return pretty;
    }
    return 'Unknown';
  })();
  return (
    <div className={boxClass}>
      <h1>ECG Prediction</h1>
      <p>Predict the ECG signal class: <strong> <span id="predicted-class">{labelWithConfidence}</span></strong> </p>
    </div>
  )
}

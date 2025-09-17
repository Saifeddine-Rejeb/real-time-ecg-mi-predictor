// Example alert data for demo/testing
export const alertExamples = [
  {
    id: "06187_hr",
    name: "Patient 06187",
    sourcePath: "Possible_Cardiac_Insufficiency/patient_classe_1_746",
    time: "2025-06-19 09:12",
    predicted_class: 1,
    predicted_class_name: "Insuffisance_Legere",
    predicted_full_name: "Insuffisance Cardiaque Légère",
    confidence: 0.8096547722816467,
    all_probabilities: [0.0718, 0.8097, 0.1048, 0.0045],
    vitals: {
      heartRate: 45,
      rrIntervals: [0.8, 0.85, 0.78, 0.82],
      status: "alert",
    },
  },
  {
    id: "18787_hr",
    name: "Patient 18787",
    sourcePath: "Severe_Cardiac_Insufficiency/patient_classe_3_374",
    time: "2025-06-19 10:10",
    predicted_class: 3,
    predicted_class_name: "Insuffisance_Severe",
    predicted_full_name: "Insuffisance Cardiaque Sévère",
    confidence: 0.92,
    all_probabilities: [0.01, 0.03, 0.04, 0.92],
    vitals: {
      heartRate: 102,
      rrIntervals: [0.6, 0.62, 0.59, 0.61],
      status: "alert",
    },
  },
];

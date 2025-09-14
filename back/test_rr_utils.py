import wfdb
from utils import calculate_rr_intervals

if __name__ == "__main__":
    ecg_file_path = "web/back/patients_test/Mild_Cardiac_Insufficiency/patient_classe_0_001"
    try:
        signal, fields = wfdb.rdsamp(ecg_file_path)
        rr_intervals, r_peaks = calculate_rr_intervals(signal)
        print("RR intervals (ms):", rr_intervals)
        print("Average RR interval (ms):", sum(rr_intervals) / len(rr_intervals) if rr_intervals else 0)
        print("R peak indices:", r_peaks)
    except Exception as e:
        print("Error:", e)

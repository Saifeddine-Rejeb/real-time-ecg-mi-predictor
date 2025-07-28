import numpy as np

import numpy as np
import scipy.signal as signal

def calculate_rr_intervals(ecg_signal, fs=500, lead=0):
    """
    Calculate RR intervals from ECG using filtering and peak detection.
    Args:
        ecg_signal: 2D numpy array (samples x leads)
        fs: sampling frequency in Hz
        lead: which lead to use
    Returns:
        rr_intervals: list of RR intervals in ms
        r_peaks: list of R-peak indices
    """
    ecg = ecg_signal[:, lead]

    # 1. Bandpass filter (0.5 - 40 Hz typical for ECG)
    nyq = fs / 2
    b, a = signal.butter(3, [0.5/nyq, 40/nyq], btype='band')
    filtered_ecg = signal.filtfilt(b, a, ecg)

    # 2. Derivative (optional for sharper peaks)
    diff_ecg = np.diff(filtered_ecg, prepend=filtered_ecg[0])

    # 3. Squaring to enhance peaks
    squared_ecg = diff_ecg ** 2

    # 4. Moving average to smooth signal
    window_size = int(0.150 * fs)  # 150ms window
    ma_ecg = np.convolve(squared_ecg, np.ones(window_size)/window_size, mode='same')

    # 5. Peak detection
    distance = int(0.25 * fs)  # at least 250ms apart (~240 bpm)
    peaks, _ = signal.find_peaks(ma_ecg, distance=distance, height=np.mean(ma_ecg))

    # 6. RR intervals (in milliseconds)
    rr_intervals = [int(1000 * (peaks[i] - peaks[i-1]) / fs) for i in range(1, len(peaks))]

    return rr_intervals, peaks

def heart_rate(rr_intervals):
    """
    Calculate heart rate from RR intervals.
    Args:
        rr_intervals: list of RR intervals in ms
    Returns:
        heart_rate: average heart rate in bpm
    """
    if not rr_intervals:
        return None
    avg_rr = sum(rr_intervals) / len(rr_intervals)
    return round(60000 / avg_rr, 2) if avg_rr > 0 else None

def heart_rate_variability(rr_intervals):
    """
    Calculate heart rate variability (HRV) from RR intervals.
    Args:
        rr_intervals: list of RR intervals in ms
    Returns:
        hrv: standard deviation of RR intervals
    """
    if not rr_intervals:
        return None
    return round(np.std(rr_intervals), 2)


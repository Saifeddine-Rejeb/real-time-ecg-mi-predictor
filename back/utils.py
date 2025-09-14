import numpy as np
import scipy.signal as signal

def calculate_rr_intervals(ecg_signal, fs=500, lead=0):
    """
    Calculate RR intervals from ECG using filtering and peak detection.
    Args:
        ecg_signal: numpy array of shape (samples, leads) or (samples,)
        fs: sampling frequency in Hz
        lead: which lead to use (ignored for 1D input)
    Returns:
        rr_intervals: list of RR intervals in ms
        r_peaks: list of R-peak indices
    """
    if ecg_signal is None:
        return [], []

    ecg_arr = np.asarray(ecg_signal)
    if ecg_arr.ndim == 1:
        ecg = ecg_arr.astype(np.float64)
    elif ecg_arr.ndim == 2:
        if lead < 0 or lead >= ecg_arr.shape[1]:
            lead = 0
        ecg = ecg_arr[:, lead].astype(np.float64)
    else:
        return [], []

    # Guard: need enough samples
    if ecg.size < max(10, int(0.3 * fs)):
        return [], []

    # 1. Bandpass filter (0.5 - 40 Hz typical for ECG)
    nyq = max(1.0, fs / 2.0)
    low = 0.5 / nyq
    high = 40.0 / nyq
    low = max(1e-6, min(low, 0.99))
    high = max(low + 1e-6, min(high, 0.999))
    b, a = signal.butter(3, [low, high], btype='band')
    try:
        filtered_ecg = signal.filtfilt(b, a, ecg, method='pad', padlen=min(3 * max(len(a), len(b)), ecg.size - 1))
    except Exception:
        filtered_ecg = signal.filtfilt(b, a, ecg)

    # 2. Derivative (optional for sharper peaks)
    diff_ecg = np.diff(filtered_ecg, prepend=filtered_ecg[0])

    # 3. Squaring to enhance peaks
    squared_ecg = diff_ecg * diff_ecg

    # 4. Moving average to smooth signal
    window_size = max(1, int(0.150 * fs))  # 150ms window
    kernel = np.ones(window_size, dtype=np.float64) / window_size
    ma_ecg = np.convolve(squared_ecg, kernel, mode='same')

    # 5. Peak detection
    distance = max(1, int(0.25 * fs))  # at least 250ms apart (~240 bpm)
    height = float(np.mean(ma_ecg)) if ma_ecg.size else 0.0
    peaks, _ = signal.find_peaks(ma_ecg, distance=distance, height=height)

    # 6. RR intervals (in milliseconds)
    if peaks.size < 2:
        return [], peaks.tolist()
    rr_intervals = [int(round(1000.0 * (peaks[i] - peaks[i-1]) / float(fs))) for i in range(1, len(peaks))]

    return rr_intervals, peaks.tolist()

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


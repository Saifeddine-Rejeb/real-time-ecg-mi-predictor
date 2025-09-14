import os
import argparse
import numpy as np
import wfdb
import matplotlib.pyplot as plt


def read_ecg(base_dir: str, record_path: str):
	"""Read an ECG record using WFDB. record_path can include or omit extension."""
	# Normalize separators and strip extension if provided
	record_path = record_path.replace('\\', '/').strip()
	base = os.path.join(base_dir, *record_path.split('/'))
	base_no_ext, _ = os.path.splitext(base)
	signal, fields = wfdb.rdsamp(base_no_ext)
	return signal, fields


def plot_ecg(signal: np.ndarray, fs: float, lead: int = 0, duration_s: float | None = None, title: str = "ECG Waveform"):
	if signal.ndim == 2:
		y = signal[:, lead]
	else:
		y = signal

	if duration_s is not None and fs is not None and fs > 0:
		n = min(len(y), int(duration_s * fs))
		y = y[:n]

	n_samples = len(y)
	t = np.arange(n_samples) / float(fs if fs else 1.0)

	plt.figure(figsize=(12, 4))
	plt.plot(t, y, linewidth=1.0)
	plt.xlabel("Time (s)")
	plt.ylabel("Amplitude")
	plt.title(title + f"  |  fs={fs} Hz, samples={n_samples}")
	plt.grid(True, alpha=0.3)
	plt.tight_layout()
	plt.show()


def main():
	parser = argparse.ArgumentParser(description="Plot an ECG record from patients_test using Matplotlib")
	parser.add_argument("--record", type=str, default="Mild_Cardiac_Insufficiency/patient_classe_0_020",
						help="Relative record path under patients_test (e.g., 'Class/record_basename' or with extension)")
	parser.add_argument("--lead", type=int, default=0, help="Lead index to plot (0-based if multi-lead)")
	parser.add_argument("--duration", type=float, default=10.0, help="Duration in seconds to display (use <=0 for full)")
	args = parser.parse_args()

	base_dir = os.getenv("ECG_DATA_DIR", os.path.join(os.path.dirname(__file__), "patients_test"))

	try:
		signal, fields = read_ecg(base_dir, args.record)
		fs = int(fields.get('fs', 500)) if isinstance(fields, dict) else 500
		title = f"ECG: {args.record} (lead {args.lead})"
		duration = None if args.duration is None or args.duration <= 0 else args.duration
		plot_ecg(signal, fs=fs, lead=args.lead, duration_s=duration, title=title)
	except Exception as e:
		print(f"Failed to plot ECG for '{args.record}': {e}")


if __name__ == "__main__":
	main()


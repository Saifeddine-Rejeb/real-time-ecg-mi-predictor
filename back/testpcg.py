import wfdb
import matplotlib.pyplot as plt
# Load only the first signal (PCG)
record = wfdb.rdrecord('web/back/test/pcg/a0409', channels=[0])
pcg_signal = record.p_signal[:, 0]
fs = record.fs  # Sampling frequency (should be 2000 Hz)

# Compute number of samples for the first 10 seconds
duration_sec = 10
num_samples = int(fs * duration_sec)

# Create time axis
time = [i / fs for i in range(num_samples)]

# Plot first 10 seconds
plt.figure(figsize=(12, 4))
plt.plot(time, pcg_signal[:num_samples], color='darkgreen')
plt.title("First 10 Seconds of PCG Signal from a0409.wav")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()

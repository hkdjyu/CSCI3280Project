# reference: https://pypi.org/project/noisereduce/

from scipy.io import wavfile
from scipy.io.wavfile import write
import noisereduce as nr
import numpy as np

class AudioNoiseRemover:
    def __init__(self):
        pass

    def remove_noise(self, audio_path, output_path=None, level = 1):
        audio_path = str(audio_path)
        if output_path is None:
            output_path = audio_path.replace(".wav", "_noise_removed.wav")

        # load data
        rate, data = wavfile.read(audio_path)
        orig_shape = data.shape
        data = np.reshape(data, (2, -1))

        noise_file = self.generate_noise(duration_seconds=10, sample_rate=rate)

        # perform noise reduction
        # optimized for speech
        reduced_noise = nr.reduce_noise(
            y=data, 
            y_noise=noise_file, 
            sr=rate,
            stationary=False,  # Set to True if the noise is stationary
            prop_decrease=level,  # Reduce noise by 100%, default is 1
            time_constant_s = 0.5,  # Time constant of the filter, defaults is 2
            freq_mask_smooth_hz = 100,  # Frequency mask smoothing, defaults is 500
            time_mask_smooth_ms = 50,  # Noise threshold, defaults is 50
        )

        wavfile.write(output_path, rate, reduced_noise.reshape(orig_shape))

    def generate_noise(self, duration_seconds=10, sample_rate=44100):
        # Generate random noise samples
        num_samples = duration_seconds * sample_rate
        noise_samples = np.random.randn(num_samples)

        # Scale the noise to a suitable amplitude (optional)
        max_amplitude = 0.5  # Maximum amplitude of the noise (adjust as needed)
        noise_samples *= max_amplitude / np.max(np.abs(noise_samples))

        # Write the noise samples to a WAV file
        noise_file = "noise.wav"
        write(noise_file, sample_rate, noise_samples.astype(np.float32))
        return noise_file
        
        
        
import streamlit as st
import librosa
import numpy as np



def record_audio(filename, duration=5, sr=44100):
    import sounddevice as sd
    from scipy.io.wavfile import write

    # Record audio
    recording = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished

    # Save recording to file
    write(filename, sr, recording)

    return recording

# Streamlit interface
st.title("Voice Authentication")

# Button to start and stop recording
record_button = st.button("Record")

if record_button:
    st.write("Recording... Speak now.")
    recorded_audio = record_audio("recorded_audio.wav", duration=5)
    st.write("Recording finished.")

    # Authenticate user
    stored_audio_path = "omkar.wav"  # Path to stored audio file
    test_audio_path = "recorded_audio.wav"  # Path to recorded audio file

    # Load stored audio
    stored_audio, _ = librosa.load(stored_audio_path, sr=44100)

    # Load recorded audio
    test_audio, _ = librosa.load(test_audio_path, sr=44100)

    # Calculate correlation coefficient
    min_length = min(len(stored_audio), len(test_audio))
    stored_audio = stored_audio[:min_length]
    test_audio = test_audio[:min_length]
    r = np.corrcoef(stored_audio, test_audio)[0, 1]

    # Authenticate user based on correlation coefficient
    threshold = 0  # Adjust the threshold as needed
    if r > threshold:
        st.success(f'User authenticated ')
    else:
        st.error(f'User authentication failed !')

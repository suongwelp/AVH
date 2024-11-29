import librosa
import numpy as np
import soundfile as sf
import sounddevice as sd

# Load two sounds
sound1, sr1 = librosa.load("C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/VP11/raw/eq_dur_target_0500/Arm.wav", sr=None)
sound2, sr2 = librosa.load("C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/other/raw/DE/male/eq_dur_target_0500/Arm.wav", sr=None)

# Blend the sounds using a ratio (0.5 for equal mix)
ratio = 0.5
morphed_sound = (1 - ratio) * sound1 + ratio * sound2

# Save or play the morphed sound
sf.write("path/to/morphed_sound.wav", morphed_sound, sr1)
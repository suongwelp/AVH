""
#Load in recordings and perform vocode
""

import slab
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import pickle
participant = input("Enter the participant ID: ")
vp = 'VP' + participant
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/'
stim_path = os.path.join(main_path,vp,'raw','_Intensity75/pitch_shifted').replace("\\", "/")

def load_stims(dir, stim_name):
    speech = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(('.wav'))]

    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files[0:9]:
        file_path = os.path.join(dir, audio_file)
        sound = slab.Sound.read(file_path)
        #sound = sound.vocode(bandwidth= 0.1)
        speech.append(sound)

    # Create a Precomputed object with the list of sounds
    stims = slab.Precomputed(speech)

    # Assign the created Precomputed object and labels to a variable with the given name
    global_var_name = f"{stim_name}"
    globals()[global_var_name] = stims
    return globals()[global_var_name]

load_stims(stim_path, 'stim_list')

#file_path = stim_other_path = os.path.join(main_path, 'other','vocoded',sex).replace("\\", "/")
os.chdir(stim_path)
with open('stim_list.pkl', 'wb') as f:
    pickle.dump(stim_list, f)
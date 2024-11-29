"""
Example of interleaved staircases that measure tone-in-noise detection thresholds at 4 frequencies
"""
import slab 
import os
import numpy as np
import threading
import time
import pickle
from numpy import random
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import matplotlib.pyplot as plt


#Define paths & variables
participant = input("Enter the participant ID: ")
vp = 'VP' + participant
main_path = 'C:/phD/MPI/Experiments/1.Voice_Detection_and_Discrimination/Stimuli/'
noise_path = main_path + 'speech_shaped_noise_dichotic.wav'
stim_other_path = os.path.join(main_path, vp, 'other').replace("\\", "/")
stim_own_path = os.path.join(main_path, vp, 'own').replace("\\", "/")
#all_files = os.listdir(stim_other_path)       # List all files in the directory
#audio_files = [file for file in all_files if file.endswith('.wav')]         # Filter for audio files (assuming they are .wav files)
#stim_label = ['Haus','Tag']     dont need this if it draws randomly from the set

# List audio devices
#print(sd.query_devices())

# Set output devices: replace 'Laptop Speaker' and 'Headphone' with the actual device names or indices
speakers = sc.all_speakers()
laptop_speaker_index = speakers[1]
headphone_index = speakers[2]


def load_stims(dir, stim_name):
    speech = []
    labels = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(('.wav'))]

    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files:
        file_path = os.path.join(dir, audio_file)
        sound = slab.Sound.read(file_path)
        sound.label = {audio_file}  # Add a custom attribute to store the file name
        speech.append(sound)

    # Create a Precomputed object with the list of sounds
    stims = slab.Precomputed(speech)

    # Assign the created Precomputed object and labels to a variable with the given name
    globals()[stim_name] = stims
    return globals()[stim_name]



# Example usage
load_stims(stim_other_path, 'stim_other')
load_stims(stim_own_path, 'stim_own')

conditions = [
    {"stim": stim_own, "device": laptop_speaker_index, "label": 'own_behind'},
    {"stim": stim_other, "device": laptop_speaker_index, "label": 'other_behind'},
    {"stim": stim_own, "device": headphone_index, "label":'own_central'},
    {"stim": stim_other, "device": headphone_index, "label": 'other_central'},
]

sequence = slab.Trialsequence(conditions=len(conditions), kind='infinite') # pseudorandom sequence of which staircase a trial comes from
stairs = []
for i in range(len(conditions)):
    stair = slab.Staircase(start_val=50,
                                  min_val=20,
                                  step_sizes=[10,5,2],
                                  n_reversals=4,
                                  label = conditions[i]["label"])
    stairs.append(stair)


def play_noise():
    global stop_event
    # Load the noise sound
    noise, fs = sf.read(noise_path, dtype='float32')
    noise = np.tile(noise, (100, 1))
    sd.default.device = 1   #headphone                                                                                                   #making the noise coming from the headset
     # Play the noise until stop_event is set or interrupted
    while not stop_event.is_set():
        sd.play(noise, samplerate=fs)
        sd.wait()  # Wait until playback is finished
        if stop_event.is_set():
            break

# Play probe stimulus
#for i in range(5):
    #stim_list = conditions[3]["stim"]
    #stim = stim_list[np.random.randint(20)]
    #stim.play()
    #time.sleep(1.5)


time.sleep(3)
# Event to signal when to stop the noise thread
stop_event = threading.Event()
# Start playing noise in a separate thread
noise_thread = threading.Thread(target=play_noise)
noise_thread.start()


time.sleep(5)
all_finished = False
trial_num = 0
while not all_finished:
    idx = next(sequence) - 1 # trialsequence produces numbers 1-4, subtract 1 to get an index
    if not stairs[idx].finished:
        level = next(stairs[idx])
        print(f'Trial {trial_num}, using staircase {idx}:')
        # present stimulus
        stim_list = conditions[idx]["stim"]
        stim = stim_list[np.random.randint(20)]
        #stim = conditions[idx]["stim"][np.random.randint(len(conditions[idx]["stim"]))]   #test if works
        if idx in [0, 1]:
            stim.level = level + 25  # Apply the adaptive level from the staircase, need to equalize
        else:
            stim.level = level
        print(stim.level)
        stim = stim.ramp()
        stairs[idx].present_tone_trial(stim, device_index = conditions[idx]["device"])
        stairs[idx].plot()

    # test if all staircases are finished
    all_finished = all([stairs[i].finished for i in range(2)])
    trial_num += 1
    #time.sleep(random.uniform(1.0, 5.0))       # need to think about expectation/conditioning

# Signal the noise thread to stop
stop_event.set()
# Stop any ongoing playback
sd.stop()

# print results
print('Thresholds:')
for i in range(len(conditions)):
    print(f'stimulus {conditions[i]["label"]} \t {stairs[i].threshold()}')

## save to external for tests
with open('stairs_00.pkl', 'wb') as f:
    pickle.dump(stairs, f)

#with open('C:/Users/nguye/PycharmProjects/SilenttoVoiced/stairs.pkl', 'rb') as file:
    #
# Create subplots
#fig, axs = plt.subplots(len(conditions), 2, figsize=(10, 5 * len(conditions)))

## plot all subplots
#for i, ax in enumerate(axs):
    #axis = plt.subplot()
    #axis.scatter(range(self.n_trials), self.trials)
    #axis.set(title='Trial sequence', xlabel='Trials', ylabel='Condition index')
# Adjust layout
#plt.tight_layout()
#plt.show()

# change speech to badly vocoded speech? batter masking effect?



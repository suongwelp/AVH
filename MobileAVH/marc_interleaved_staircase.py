"""
Example of interleaved staircases that measure tone-in-noise detection thresholds at 4 frequencies
"""
import slab
import sounddevice as sd
import numpy as np
import pickle
import time
import soundcard as sc

# List audio devices
#print(sd.query_devices())

# Set output devices: replace 'Laptop Speaker' and 'Headphone' with the actual device names or indices
speakers = sc.all_speakers()
laptop_speaker_index = 1 #speakers[1]
headphone_index = 0 #speakers[0]             # 3 and 6 also work

conditions = [
    {"frequency": 250, "device": laptop_speaker_index, "label": "250 Hz Laptop"},
    {"frequency": 1000, "device": laptop_speaker_index, "label": "1000 Hz Laptop"},
    {"frequency": 250, "device": headphone_index, "label": "250 Hz Headphone"},
    {"frequency": 1000, "device": headphone_index, "label": "1000 Hz Headphone"},
]

# Pseudorandom sequence of which staircase a trial comes from
sequence = slab.Trialsequence(conditions=len(conditions), kind='infinite')  #pseudorandom sequence of which staircase a trial comes from

stairs = []
for i in range(len(conditions)):
    stair = slab.Staircase(start_val=50,
                                  min_val=20,
                                  step_sizes=[10,5,2],
                                  n_reversals=4)
    stairs.append(stair)

all_finished = False
trial_num = 0
while not all_finished:
    idx = next(sequence) - 1 # trialsequence produces numbers 1-4, subtract 1 to get an index
    if not stairs[idx].finished:
        level = next(stairs[idx])
        print(f'Trial {trial_num}, using staircase {idx}:')
        # Select output device
        #device_index = 1#conditions[idx]["device"]
        # make stimulus
        noise = slab.Sound.pinknoise(duration=0.3,level=50)
        freq = conditions[idx]["frequency"]
        tone = slab.Sound.tone(frequency=freq,duration=0.3,level=level)
        stim = noise + tone
        stim = stim.ramp()
        stairs[idx].present_tone_trial(stim, device_index = conditions[idx]["device"])

    # test if all staricases are finished
    all_finished = all([stairs[i].finished for i in range(len(conditions))])
    trial_num += 1

# print results
print('Thresholds:')
for i in range(len(conditions)):
    print(f'frequency {conditions[i]["frequency"]} \t {stairs[i].threshold()}')


bi_vowel = slab.Binaural(vowel)
bi_vowel.left.level = 75
bi_vowel.right.level = 85
bi_vowel.play()
bi_vowel.ild(-15) #doesnt work

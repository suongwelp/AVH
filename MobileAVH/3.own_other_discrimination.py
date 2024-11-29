"""
Example of interleaved staircases that measure tone-in-noise detection thresholds at 4 frequencies
"""
import slab 
import os
import numpy as np
import time
import pickle
from numpy import random
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.stats import sem
from collections import defaultdict

#Define paths & variables
participant = input("Enter the participant ID: ")
vp = 'VP' + participant
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/'
noise_path= os.path.join(main_path, 'speech_shaped_noise_dichotic_28s.wav').replace("\\", "/")
noise = slab.Sound.read(noise_path)
stim_shifted_path = os.path.join(main_path, vp, 'raw','_Intensity75','pitch_shifted').replace("\\", "/")
# load in filter function
inverse_s = slab.Filter.load(main_path + '/equalize/inverse_s.npy')
inverse_h = slab.Filter.load(main_path + '/equalize/inverse_h.npy')

def load_stims(dir, stim_name):
    speech = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(('.wav'))]

    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files:
        file_path = os.path.join(dir, audio_file)
        sound = slab.Sound.read(file_path)
        sound.name = audio_file
        speech.append(sound)

    # Create a Precomputed object with the list of sounds
    stims = slab.Precomputed(speech)

    global_var_name = f"{stim_name}"
    globals()[global_var_name] = stims
    return globals()[global_var_name],audio_files

stim_shifted, audio_files = load_stims(stim_shifted_path,'stim_shifted')

# List audio devices
#sd.query_devices()
#device_names = [device['name'] for device in sd.query_devices()]
headphone_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Kopfhörer (Realtek(R) Audio)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")
speaker_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Lautsprecher (USB Sound Blaster HD)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")

stim_device = [(stim, headphone_index) for stim in stim_shifted] + \
                   [(stim, speaker_index) for stim in stim_shifted]        ##first 9 vocodes are own, next 6 vocodes are other

seq = slab.Trialsequence(conditions=stim_device, n_reps=3)  # 1 repetitions per condition
noise.level = 25
noise.play_background()

time.sleep(3)

for stim_device in seq:
    stim_current = stim_device
    stimulus = stim_current[0]       # index 1 sound object in array
    stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)
    device_idx = stim_current[1]  # index device
    stimulus.level = 60
    if device_idx == speaker_index:
        stimulus = inverse_s.apply(stimulus)
    else:
        stimulus = inverse_h.apply(stimulus)
    stimulus.ramp(duration=0.02)
    stimulus.play(device=device_idx)
    with slab.key() as key:
        response = key.getch()
        seq.add_response(response)
        #seq.print_trial_info()


noise.stop_background()

seq.response_summary()
print(seq.response_summary())

file_path = os.path.join(main_path,vp)
os.chdir(file_path)
with open('seq_exp2_'+ time.strftime("%m_%d_%H_%M")+'.pkl', 'wb') as f:
    pickle.dump(seq, f)


### load seq back in to check results#############################################################################

#file_path = os.path.join(main_path,vp, "seq_exp2.pkl").replace("\\", "/")
#with open(file_path, 'rb') as file:
    #seq = pickle.load(file)

## Condition mean and plot
res_tempt = [[0 if value == 50 else 1 if value == 49 else value for value in sublist] for sublist in seq.data]


trial_condition_response_mapping = []

for i, trial_result in enumerate(seq.trials):
    condition_index = i % len(seq.conditions)  # Get the corresponding condition index
    condition = seq.conditions[condition_index]  # Get the condition associated with this trial
    response = res_tempt[i]  # Get the corresponding response data
    trial_condition_response_mapping.append((trial_result, condition, response))


#audio_name = trial_condition_response_mapping[trial][1][0].name  # Extract the audio name

groups = defaultdict(list)

for trial in range(len(trial_condition_response_mapping)):
    #trial_result, (sound_obj, device_number), response = trial
    audio_name = trial_condition_response_mapping[trial][1][0].name  # Extract the audio name
    # Grouping logic based on audio name and device number
    if '_shift2st' in audio_name:
        group_key = f'shift2st_{trial_condition_response_mapping[trial][1][1]}'
    elif '_shift4st' in audio_name:
        group_key = f'shift4st_{trial_condition_response_mapping[trial][1][1]}'
    else:
        group_key = f'no_shift_{trial_condition_response_mapping[trial][1][1]}'

    # Add the trial's result to the corresponding group
    groups[group_key].append(trial_condition_response_mapping[trial][2])




# Calculate the mean for each group
group_means = {group: np.mean(values) for group, values in groups.items()}


## plot
# Prepare data for plotting
conditions = ['no_shift', 'shift2st', 'shift4st']
means_0 = [group_means[f'{condition}_'+ str(speaker_index)] for condition in conditions]
means_2 = [group_means[f'{condition}_'+ str(headphone_index)] for condition in conditions]

# Define the position of the bars on the x-axis
x = np.arange(len(conditions))

# Define the width of the bars
bar_width = 0.35

# Create the bar plot
fig, ax = plt.subplots()
bars1 = ax.bar(x - bar_width/2, means_0, bar_width, label='speaker')
bars2 = ax.bar(x + bar_width/2, means_2, bar_width, label='headphone')

# Add some text for labels, title, and custom x-axis tick labels
ax.set_xlabel('Condition')
ax.set_ylabel('Mean Value')
#ax.set_title('Comparison of Mean Values Between Device 0 and Device 2')
ax.set_xticks(x)
ax.set_xticklabels(conditions)
ax.legend()

# Attach a text label above each bar, displaying its height
def autolabel(bars):
    """Attach a text label above each bar in *bars*, displaying its height."""
    for bar in bars:
        height = bar.get_height()
        ax.annotate('{}'.format(height),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(bars1)
autolabel(bars2)

plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_allconditions_discrimination_exp2_'+time.strftime("%d%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()


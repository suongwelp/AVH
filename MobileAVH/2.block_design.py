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


#Define paths & variables

vp = input("Enter the participant ID: VPXX ")
#vp = 'VP' + participant
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/'
noise_path = os.path.join(main_path, 'speech_shaped_noise_dichotic_28s.wav').replace("\\", "/")
noise = slab.Sound.read(noise_path)
bands = ['Voice_0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', 'Noise_0.9']
file_path = os.path.join(main_path, vp,"stim_list.pkl").replace("\\", "/")
# load in filter function
inverse_s = slab.Filter.load(main_path + '/equalize/noear3/inverse_s.npy')
inverse_h = slab.Filter.load(main_path + '/equalize/noear3/inverse_h.npy')

with open(file_path, 'rb') as file:
    stim_list = pickle.load(file)
n_stim = 10

# List audio devices
#sd.query_devices()

device_names = [device['name'] for device in sd.query_devices()]
headphone_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Kopfhörer (Realtek(R) Audio)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")
speaker_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Lautsprecher (USB Sound Blaster HD)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")

stim_device = [(stim, headphone_index) for stim in stim_list] + \
                   [(stim, speaker_index) for stim in stim_list]        ##first 9 vocodes are own, next 9 vocodes are other

def get_random_number(last_number, choices):
    new_number = np.random.choice(choices)
    # Keep generating until get a different number
    while new_number == last_number:
        new_number = np.random.choice(choices)
    return new_number

last_trial = np.random.choice(n_stim)

seq = slab.Trialsequence(conditions=stim_device, n_reps=5)  # 2 repetitions per condition

noise.level = 30
noise.play_background()

time.sleep(3)
count = 0
for stim_device in seq:
    stim_current = stim_device
    last_trial = get_random_number(last_trial, n_stim)
    stimulus = stim_current[0][last_trial]         # index 1 sound object in array
    stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)   #pad zeros
    device_idx = stim_current[1]  # index device
    stimulus.level = 70
    if device_idx == speaker_index:
       stimulus = inverse_s.apply(stimulus)
    else:
       stimulus = inverse_h.apply(stimulus)
    stimulus.ramp(duration = 0.02)
    #stimulus.waveform()
    stimulus.play(device=device_idx)
    with slab.key() as key:
        response = key.getch()
        seq.add_response(response)
    count = count + 1
    if count == 90:
        tone = slab.Sound.tone(frequency=500, duration=0.5)
        tone.level = 50
        tone.play()
        input("Press Enter to continue...")
        time.sleep(3)
    time.sleep(1)

noise.stop_background()

seq.response_summary()
print(seq.response_summary())

############################## Save raw data #####################################################
file_path = os.path.join(main_path,vp)
os.chdir(file_path)
file_name = 'seq_exp1_'+ time.strftime("%m_%d_%H_%M")+'.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(seq, f)
#################################################################################################

### load seq back in to check results#############################################################################
file_path = os.path.join(main_path,vp,'seq_exp1_09_20_17_27.pkl').replace("\\", "/")
#file_path = os.path.join(main_path,vp,file_name).replace("\\", "/")
with open(file_path, 'rb') as file:
    seq = pickle.load(file)

## Condition mean and plot
res = [item for sublist in seq.data for item in sublist]
dat_raw = np.column_stack((seq.trials,res))
dat = np.array([[row[0], 1 if row[1] == 49 else 0] for row in dat_raw])
unique_conditions = np.unique(dat[:, 0])
# Calculate the mean for each condition
condition_means = []
for condition in unique_conditions:
    mean_value = np.mean(dat[dat[:, 0] == condition][:, 1])
    condition_means.append([condition, mean_value])
    print(f"Condition {condition} has the mean of {mean_value}")

## plot
data = np.array(condition_means)
plot_title = ['own_central','other_central','own_behind','other_behind']

def plot_conditions(data, start, end, subplot_index, title):
    # First data subset
    subset = data[start:end]
    x = np.arange(len(subset))  # Generate indices for x
    y = subset[:, 1]  # y-axis is the mean

    # Second data subset
    subset2 = data[start+18:end+18]
    x2 = np.arange(len(subset2))  # Generate indices for x2
    y2 = subset2[:, 1]

    # Interpolation for the first subset
    x_new = np.linspace(x.min(), x.max(), 300)  # Interpolation points for smooth curve
    f = interp1d(x, y, kind='cubic')
    y_smooth = f(x_new)

    # Interpolation for the second subset
    x_new2 = np.linspace(x2.min(), x2.max(), 300)
    f2 = interp1d(x2, y2, kind='cubic')
    y_smooth2 = f2(x_new2)

    # Standard error for confidence intervals
    y_err = sem(y)
    y_err2 = sem(y2)

    plt.subplot(1, 2, subplot_index)
    plt.plot(x_new[::-1], y_smooth, linestyle='-', color='r', label=plot_title[subplot_index-1])
    plt.plot(x_new2[::-1], y_smooth2, linestyle='-', color='b', label=plot_title[subplot_index+1])
    plt.fill_between(x_new[::-1], y_smooth - y_err, y_smooth + y_err, color='r', alpha=0.2)
    plt.fill_between(x_new2[::-1], y_smooth2 - y_err2, y_smooth2 + y_err2, color='b', alpha=0.2)
    plt.title(title)
    plt.xlabel('vocode_bandwidth')
    plt.ylabel('Voice')
    plt.grid(True)
    plt.xticks(ticks=x, labels=bands[::-1])  # Use consistent xticks for the bands
    plt.ylim(0, 1)
    plt.legend()

# Create subplots
plt.figure(figsize=(12, 10))

# Plot first 6 conditions
plot_conditions(data, 0, 9, 1, "own")

# Plot next 6 conditions
plot_conditions(data, 9, 18, 2, "other")
plt.suptitle(f'{vp}_vocode_central VS behind')
plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_vocode_exp1_central_VS_behind' + time.strftime("%d%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()


################### SECOND PLOT###########################################
plot_title = ['own_central','other_central','own_behind','other_behind']

def plot_conditions2(data, start, end, subplot_index, title):
    # First data subset
    subset = data[start:end]
    x = np.arange(len(subset))  # Generate indices for x
    y = subset[:, 1]  # y-axis is the mean

    # Second data subset
    subset2 = data[start+9:end+9]
    x2 = np.arange(len(subset2))  # Generate indices for x2
    y2 = subset2[:, 1]

    # Interpolation for the first subset
    x_new = np.linspace(x.min(), x.max(), 300)  # Interpolation points for smooth curve
    f = interp1d(x, y, kind='cubic')
    y_smooth = f(x_new)

    # Interpolation for the second subset
    x_new2 = np.linspace(x2.min(), x2.max(), 300)
    f2 = interp1d(x2, y2, kind='cubic')
    y_smooth2 = f2(x_new2)

    # Standard error for confidence intervals
    y_err = sem(y)
    y_err2 = sem(y2)

    plt.subplot(1, 2, subplot_index)
    plt.plot(x_new[::-1], y_smooth, linestyle='-', color='r', label=plot_title[subplot_index-1])
    plt.plot(x_new2[::-1], y_smooth2, linestyle='-', color='b', label=plot_title[subplot_index+1])
    plt.fill_between(x_new[::-1], y_smooth - y_err, y_smooth + y_err, color='r', alpha=0.2)
    plt.fill_between(x_new2[::-1], y_smooth2 - y_err2, y_smooth2 + y_err2, color='b', alpha=0.2)
    plt.title(title)
    plt.xlabel('vocode_bandwidth')
    plt.ylabel('Voice')
    plt.grid(True)
    plt.xticks(ticks=x, labels=bands[::-1])  # Use consistent xticks for the bands
    plt.ylim(0, 1)
    plt.legend()

# Create subplots
plt.figure(figsize=(12, 10))

# Plot first 6 conditions
plot_conditions2(data, 0, 9, 1, "central")

# Plot next 6 conditions
plot_conditions2(data, 18, 27, 2, "behind")

plt.suptitle(f'{vp}_vocode_own VS other')
plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_vocode_exp1_own_VS_other' + time.strftime("%d%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()

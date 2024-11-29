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
noise_path= os.path.join(main_path, 'speech_shaped_noise_dichotic_28s.wav').replace("\\", "/")
morph_path = os.path.join(main_path, vp, 'morphed/').replace("\\", "/")
noise = slab.Sound.read(noise_path)
inverse_s = slab.Filter.load(main_path + '/equalize/noear3/inverse_s.npy')
inverse_h = slab.Filter.load(main_path + '/equalize/noear3/inverse_h.npy')
### for real voice 50% filter works, for vocode not
file_path = os.path.join(morph_path,"stim_list.pkl").replace("\\", "/")
with open(file_path, 'rb') as file:
    stim_list = pickle.load(file)
n_stim = 10
# List audio devices
#sd.query_devices()
#device_names = [device['name'] for device in sd.query_devices()]
headphone_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Kopfhörer (Realtek(R) Audio)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")
speaker_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Lautsprecher (USB Sound Blaster HD)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")
#speaker_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Lautsprecher (Realtek(R) Audio)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")

stim_device = [(stim, headphone_index) for stim in stim_list] + \
                   [(stim, speaker_index) for stim in stim_list]
# 0-9  central, 10-19  behind

#####
def get_random_number(last_number, choices):
    new_number = np.random.choice(choices)
    # Keep generating until we get a different number
    while new_number == last_number:
        new_number = np.random.choice(choices)
    return new_number
last_trial = np.random.choice(n_stim)


seq = slab.Trialsequence(conditions=stim_device, n_reps=7)  # 1 repetitions per condition
noise.level = 30
noise.play_background()

time.sleep(3)
count = 0
for stim_device in seq:
    stim_current = stim_device
    last_trial = get_random_number(last_trial, n_stim)
    stimulus = stim_current[0][last_trial]
    stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)
    device_idx = stim_current[1]  # index device
    stimulus.level = 70
    if device_idx == speaker_index:
        stimulus = inverse_s.apply(stimulus)
    else:
        stimulus = inverse_h.apply(stimulus)
    stimulus.ramp(duration=0.02)
    stimulus.play(device=device_idx)
    with slab.key() as key:
        response = key.getch()
        seq.add_response(response)
    count = count + 1
    if count == 63:
        tone = slab.Sound.tone(frequency=500, duration=0.5)
        tone.level = 50
        tone.play()
        input("Press Enter to continue...")
        time.sleep(3)
    time.sleep(1)

noise.stop_background()

seq.response_summary()
print(seq.response_summary())

################################### Save raw data ##############################################################
file_path = os.path.join(main_path,vp)
os.chdir(file_path)
with open('seq_exp2_revised_'+ time.strftime("%m_%d_%H_%M")+'.pkl', 'wb') as f:
    pickle.dump(seq, f)
################################################################################################################

### load seq back in to check results#############################################################################
#file_path = os.path.join(main_path,vp,'seq_exp2_revised_09_05_12_06.pkl').replace("\\", "/")
#with open(file_path, 'rb') as file:
    #seq = pickle.load(file)

## Condition mean and plot
res = [item for sublist in seq.data for item in sublist]
dat_raw= np.column_stack((seq.trials,res))
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
plot_title = ['central','behind']

def plot_conditions(data, start, end, title):
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

    plt.plot(x_new[::-1], y_smooth, linestyle='-', color='r', label=plot_title[0])
    plt.plot(x_new2[::-1], y_smooth2, linestyle='-', color='b', label=plot_title[1])
    plt.fill_between(x_new[::-1], y_smooth - y_err, y_smooth + y_err, color='r', alpha=0.2)
    plt.fill_between(x_new2[::-1], y_smooth2 - y_err2, y_smooth2 + y_err2, color='b', alpha=0.2)
    plt.title(title)
    plt.xlabel('morph_ratios')
    plt.ylabel('own_voice')
    plt.grid(True)
    plt.xticks(ticks=x, labels=bands[::-1])  # Use consistent xticks for the bands
    plt.ylim(0, 1)
    plt.legend()

# Create subplots
plt.figure(figsize=(12, 10))

# Plot first 6 conditions
bands = ['Own','10','20','30','40','50','60','80','Other'];        #bands = morph_ratios
plot_conditions(data, 0, 9, "own voice recognition at different morph ratios")

plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_exp2_own_other_dis_' + time.strftime("%d_%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()



"""
Block design vocoded voice detection
Suong Welp
17.12.2024
"""


import slab
import freefield
import os
import numpy as np
import time
import pickle
from numpy import random
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict
import csv
import csv
import statistics
from scipy.interpolate import CubicSpline, interp1d

proc_list = [['RP2', 'RP2', freefield.DIR / 'data' / 'rcx' / 'bi_play_buf.rcx'],
             ['RX81', 'RX8', freefield.DIR / 'data' / 'rcx' / 'play_buf.rcx'],
             ['RX82', 'RX8', freefield.DIR / 'data' / 'rcx' / 'play_buf.rcx']]
freefield.initialize(setup='dome', device=proc_list)
freefield.PROCESSORS.mode = 'play_birec'
fs = 48828
slab.Signal.set_default_samplerate(fs)

### load equalization
calibration_path = freefield.DIR / 'data' / 'headphone_equalization_1212.pkl'
with open(calibration_path, 'rb') as f:  # read the saved calibration
    headphone_equalization = pickle.load(f)

table_file = freefield.DIR / 'data' / 'tables' / (f'speakertable_dome.txt')
speaker_table = np.loadtxt(table_file, skiprows=1, usecols=(0, 3, 4,), delimiter=",", dtype=float)
headphone_calibration = freefield.load_equalization(calibration_path)
headphone_speaker_list = (speaker_table[-2:, 0]).astype('int')
speakers = freefield.pick_speakers(headphone_speaker_list)

#Define paths & variables

#vp = input("Enter the participant ID: VPXX ")
vp = input("Enter the participant ID VPXX: ")
main_path = Path('C:/projects/AVH/stimuli/')
noise_path = main_path /'noise'/ 'speech_shaped_noise_dichotic_13s.wav'
noise = slab.Sound.read(noise_path)
noise = slab.Signal.resample(noise,fs)
noise.level = 50
bands = ['Voice_0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', 'Noise_0.9']
stim_path = Path('C:/projects/AVH/stimuli/') / vp / 'vocoded' / '_Intensity75' / 'stim_list.pkl'
with open(stim_path, 'rb') as file:
    stim_list = pickle.load(file)

n_stim = 10  #number of vocoding bands
n_rep = 15   #Marc: 12-15 repetition

stim_list2 = [(stim, "own") for stim in stim_list[0:9]] + \
                   [(stim, "other") for stim in stim_list[9:19]]        ##first 9 vocodes are own, next 9 vocodes are other

def play_noise_headphones(signal,equalize=False, data_tags=['noise_l', 'noise_r'], chan_tags=['chan_l', 'chan_r'],         #have to set back to False when start raw recording
                          n_samples_tag='playbuflen1'):
    # get speaker id's for each headphone speaker
    table_file = freefield.DIR / 'data' / 'tables' / (f'speakertable_dome.txt')
    speaker_table = np.loadtxt(table_file, skiprows=1, usecols=(0, 3, 4), delimiter=",", dtype=float)
    headphone_speaker_list = (speaker_table[-2:, 0]).astype('int')
    speakers = freefield.pick_speakers(headphone_speaker_list)
    if signal.n_channels == 1:
        signal = slab.Binaural(signal)
    freefield.PROCESSORS.write(tag=n_samples_tag, value=signal.n_samples, processors='RP2')
    for i, (speaker, ch_tag, data_tag) in enumerate(zip(speakers, chan_tags, data_tags)):
        if equalize:
            freefield.logging.info('Applying calibration.')  # apply level and frequency calibration
            to_play = freefield.apply_equalization(signal.channel(i),speaker=speaker).data
        elif not equalize:
            to_play = signal.channel(i).data
        freefield.PROCESSORS.write(tag=ch_tag, value=speaker.analog_channel, processors=speaker.analog_proc)
        freefield.PROCESSORS.write(tag=data_tag, value=to_play, processors=speaker.analog_proc)
        #freefield.PROCESSORS.trigger(kind='zBusB', proc='RP2')
    freefield.play(kind='zBusB', proc='RP2')


def set_signal_headphones(signal,equalize=True, data_tags=['data_l', 'data_r'], chan_tags=['chan_l', 'chan_r'],         #have to set back to False when start raw recording
                          n_samples_tag='playbuflen'):
    # get speaker id's for each headphone speaker
    table_file = freefield.DIR / 'data' / 'tables' / (f'speakertable_dome.txt')
    speaker_table = np.loadtxt(table_file, skiprows=1, usecols=(0, 3, 4), delimiter=",", dtype=float)
    headphone_speaker_list = (speaker_table[-2:, 0]).astype('int')
    speakers = freefield.pick_speakers(headphone_speaker_list)
    if signal.n_channels == 1:
        signal = slab.Binaural(signal)
    freefield.PROCESSORS.write(tag=n_samples_tag, value=signal.n_samples, processors='RP2')
    for i, (speaker, ch_tag, data_tag) in enumerate(zip(speakers, chan_tags, data_tags)):
        if equalize:
            freefield.logging.info('Applying calibration.')  # apply level and frequency calibration
            to_play = freefield.apply_equalization(signal.channel(i),speaker=speaker).data
        elif not equalize:
            to_play = signal.channel(i).data
        freefield.PROCESSORS.write(tag=ch_tag, value=speaker.analog_channel, processors=speaker.analog_proc)
        freefield.PROCESSORS.write(tag=data_tag, value=to_play, processors=speaker.analog_proc)

def interplay (signal,equalize=True, device = "h"):
    if device == "h":
        set_signal_headphones(signal=signal, equalize=True)
        freefield.write(tag='chan', value=99, processors=['RX81', 'RX82'])
        freefield.play(kind=1, proc='RP2')
    elif device == "s":
        freefield.set_signal_and_speaker(signal=signal, speaker=23, equalize=True)
        # freefield.write(tag='chan_l', value=99, processors='RP2')
        # freefield.write(tag='chan_r', value=99, processors='RP2')
        freefield.play(kind=1, proc='RX81')
    freefield.wait_to_finish_playing()


def get_random_number(last_number, choices):
    new_number = np.random.choice(choices)
    # Keep generating until get a different number
    while new_number == last_number:
        new_number = np.random.choice(choices)
    return new_number

def collect_response():
    response = None; reaction_time = None
    start_time = time.time()
    timeout_duration = 2
    while not freefield.read(tag="response", processor="RP2"):
        # Check if 2 seconds have passed
        if time.time() - start_time > timeout_duration:
            # Timeout reached, break out of the loop
            response = 0;reaction_time = 0
            break
        time.sleep(0.01)
    # If a response was received before the timeout
    if response is None:
        curr_response = int(freefield.read(tag="response", processor="RP2"))
        if curr_response != 0:
            reaction_time = int(round(time.time() - start_time, 3) * 1000)
            response = int(np.log2(curr_response)) -1
    return response, reaction_time


last_trial = np.random.choice(n_stim)
stim_device = [(stim, "h") for stim in stim_list2] + \
                   [(stim, "s") for stim in stim_list2]
seq = slab.Trialsequence(conditions=stim_device, n_reps=n_rep)  # 2 repetitions per condition

### START NOISE
play_noise_headphones(noise)

#time.sleep (20)
########################################## START EXPERIMENT ##########################################################

results=dict()
count = 0

for stim_device in seq:
    stim_current = stim_device
    last_trial = get_random_number(last_trial, n_stim)
    stimulus = stim_current[0][0][last_trial]     # index 1 sound object in array, same vocode level, different words
    #stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)   #pad zeros
    stimulus.level = 70
    if stim_current[1] == 's':
        stimulus.level = 73
    stimulus.ramp(duration = 0.01)
    interplay(stimulus, equalize=True, device= stim_current[1])
    response, reaction_time = collect_response()
    results[str(seq.this_n)] = {'Response': response,
                                'Word played': stimulus.name.split('_')[0],
                                'Vocode band': stimulus.name.split('_')[1].split('.')[0],
                                'Device': stim_current[1],
                                'Voice': stim_current[0][1],
                                'Reaction time': reaction_time}
    count = count + 1
    if count % 100 == 0:
        tone = slab.Sound.tone(frequency=500, duration=0.5);tone.level = 70
        time.sleep(3)
        interplay(tone, equalize=True, device='s')
        input("Press Enter to continue...")
        time.sleep(10)
    if response == 2: time.sleep(2)
    else: time.sleep(1)


freefield.halt()

########################################## END EXPERIMENT ##########################################################

########################################## Save raw data ###########################################################
file_path = main_path/vp
os.chdir(file_path)
file_name = 'exp1_vocode_'+ time.strftime("%m_%d_%H_%M")+'.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(results, f)

file_name = 'exp1_vocode_'+ time.strftime("%m_%d_%H_%M")+'.csv'
fieldnames = list(next(iter(results.values())).keys())
# Open the file and write the CSV
with open(file_name, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()  # Write the header (column names)
    # Write the rows of data, where each row is a dictionary from `results`
    for key, value in results.items():
        writer.writerow(value)  # Write the data row
#################################################################################################

### load seq back in to check results#############################################################################
#file_path = os.path.join(main_path,vp,'exp1_vocode_12_18_12_53.pkl').replace("\\", "/")
#file_path = os.path.join(main_path,vp,file_name).replace("\\", "/")
#with open(file_path, 'rb') as file:
    results = pickle.load(file)


##################################################################################################
################################## MEAN per CONDITION ############################################

grouped_results = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for key, value in results.items():
    device = value['Device']
    vocode_band = value['Vocode band']
    voice = value['Voice']  # Keep 'own' and 'other' as they are
    response = value['Response']
    grouped_results[device][vocode_band][voice].append(response)


# Function to calculate mean and standard error
def calculate_mean_and_stderr(grouped_data):
    mean_responses = {}
    stderr_responses = {}

    for key, responses in grouped_data.items():
        mean_responses[key] = statistics.mean(responses)
        stderr_responses[key] = statistics.stdev(responses) / len(responses) ** 0.5  # Standard error

    return mean_responses, stderr_responses


# Create figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Prepare the data for plotting
for device, ax in zip(['s', 'h'], axs):
    # Rename devices: s -> external, h -> internal
    device_name = 'external' if device == 's' else 'internal'

    # Extract the data for the current device
    device_data = grouped_results[device]

    # Prepare lists to store vocode_band, mean responses, and standard errors for both own and other
    vocode_band_values_own = []
    means_own = []
    stderr_own = []

    vocode_band_values_other = []
    means_other = []
    stderr_other = []

    # Loop over vocode band and voice combinations
    for vocode_band in sorted(device_data):
        for voice in ['own', 'other']:  # Loop for both 'own' and 'other'
            responses = device_data[vocode_band].get(voice, [])

            if len(responses) == 0:  # Skip if there are no responses for this condition
                continue

            mean_responses, stderr_responses = calculate_mean_and_stderr({(vocode_band, voice): responses})

            if voice == 'own':
                vocode_band_values_own.append(float(vocode_band))  # Convert vocode_band to float for interpolation
                means_own.append(mean_responses[(vocode_band, voice)])
                stderr_own.append(stderr_responses[(vocode_band, voice)])
            elif voice == 'other':
                vocode_band_values_other.append(float(vocode_band))
                means_other.append(mean_responses[(vocode_band, voice)])
                stderr_other.append(stderr_responses[(vocode_band, voice)])

    # Ensure the vocode_band_values are sorted and unique for 'own' and 'other'
    sorted_indices_own = np.argsort(vocode_band_values_own)
    vocode_band_values_own = np.array(vocode_band_values_own)[sorted_indices_own]
    means_own = np.array(means_own)[sorted_indices_own]
    stderr_own = np.array(stderr_own)[sorted_indices_own]

    sorted_indices_other = np.argsort(vocode_band_values_other)
    vocode_band_values_other = np.array(vocode_band_values_other)[sorted_indices_other]
    means_other = np.array(means_other)[sorted_indices_other]
    stderr_other = np.array(stderr_other)[sorted_indices_other]

    # Now we can apply interpolation (spline) to smooth the curve for both 'own' and 'other'
    if len(vocode_band_values_own) > 1:  # Ensure we have at least two points for interpolation
        spline_own = CubicSpline(vocode_band_values_own, means_own)
        x_smooth_own = np.linspace(min(vocode_band_values_own), max(vocode_band_values_own), 500)
        stderr_interp_own = interp1d(vocode_band_values_own, stderr_own, kind='linear', fill_value="extrapolate")
        stderr_smooth_own = stderr_interp_own(x_smooth_own)

        ax.plot(x_smooth_own, spline_own(x_smooth_own), label='own')
        ax.fill_between(x_smooth_own,
                        spline_own(x_smooth_own) - stderr_smooth_own,
                        spline_own(x_smooth_own) + stderr_smooth_own,
                        alpha=0.2)

    if len(vocode_band_values_other) > 1:  # Ensure we have at least two points for interpolation
        spline_other = CubicSpline(vocode_band_values_other, means_other)
        x_smooth_other = np.linspace(min(vocode_band_values_other), max(vocode_band_values_other), 500)
        stderr_interp_other = interp1d(vocode_band_values_other, stderr_other, kind='linear', fill_value="extrapolate")
        stderr_smooth_other = stderr_interp_other(x_smooth_other)

        ax.plot(x_smooth_other, spline_other(x_smooth_other), label='other')
        ax.fill_between(x_smooth_other,
                        spline_other(x_smooth_other) - stderr_smooth_other,
                        spline_other(x_smooth_other) + stderr_smooth_other,
                        alpha=0.2)

    ax.set_title(f'{device_name}')
    ax.set_xlabel('Vocode Band')
    ax.set_ylabel('Mean Response')
    ax.legend()

plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_exp1_vocode_ownVSother_' + time.strftime("%d_%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()


########################################### PLOT External vs internal ##################################################
#region <External vs internal>
vocode_band_values_external_own = []
means_external_own = []
stderr_external_own = []

vocode_band_values_internal_own = []
means_internal_own = []
stderr_internal_own = []

vocode_band_values_external_other = []
means_external_other = []
stderr_external_other = []

vocode_band_values_internal_other = []
means_internal_other = []
stderr_internal_other = []

# Process the data for both devices (external 's' and internal 'h')
for device in ['s', 'h']:
    for vocode_band in sorted(grouped_results[device]):
        # Get responses for 'own' and 'other' voice conditions
        responses_own = grouped_results[device][vocode_band].get('own', [])
        responses_other = grouped_results[device][vocode_band].get('other', [])

        if len(responses_own) > 0:
            mean_responses_own, stderr_responses_own = calculate_mean_and_stderr({(vocode_band, 'own'): responses_own})
            if device == 's':  # External device
                vocode_band_values_external_own.append(float(vocode_band))
                means_external_own.append(mean_responses_own[(vocode_band, 'own')])
                stderr_external_own.append(stderr_responses_own[(vocode_band, 'own')])
            else:  # Internal device
                vocode_band_values_internal_own.append(float(vocode_band))
                means_internal_own.append(mean_responses_own[(vocode_band, 'own')])
                stderr_internal_own.append(stderr_responses_own[(vocode_band, 'own')])

        if len(responses_other) > 0:
            mean_responses_other, stderr_responses_other = calculate_mean_and_stderr(
                {(vocode_band, 'other'): responses_other})
            if device == 's':  # External device
                vocode_band_values_external_other.append(float(vocode_band))
                means_external_other.append(mean_responses_other[(vocode_band, 'other')])
                stderr_external_other.append(stderr_responses_other[(vocode_band, 'other')])
            else:  # Internal device
                vocode_band_values_internal_other.append(float(vocode_band))
                means_internal_other.append(mean_responses_other[(vocode_band, 'other')])
                stderr_internal_other.append(stderr_responses_other[(vocode_band, 'other')])


# Sort the data before interpolation
def sort_data(vocode_band_values, means, stderr):
    sorted_indices = np.argsort(vocode_band_values)
    return np.array(vocode_band_values)[sorted_indices], np.array(means)[sorted_indices], np.array(stderr)[
        sorted_indices]


# Sort the data for each condition before interpolation
vocode_band_values_external_own, means_external_own, stderr_external_own = sort_data(vocode_band_values_external_own,
                                                                                     means_external_own,
                                                                                     stderr_external_own)
vocode_band_values_internal_own, means_internal_own, stderr_internal_own = sort_data(vocode_band_values_internal_own,
                                                                                     means_internal_own,
                                                                                     stderr_internal_own)
vocode_band_values_external_other, means_external_other, stderr_external_other = sort_data(
    vocode_band_values_external_other, means_external_other, stderr_external_other)
vocode_band_values_internal_other, means_internal_other, stderr_internal_other = sort_data(
    vocode_band_values_internal_other, means_internal_other, stderr_internal_other)


# Interpolation (splining) to smooth the curves
def interpolate_data(vocode_band_values, means, stderr):
    spline = CubicSpline(vocode_band_values, means)
    x_smooth = np.linspace(min(vocode_band_values), max(vocode_band_values), 500)
    stderr_interp = interp1d(vocode_band_values, stderr, kind='linear', fill_value="extrapolate")
    stderr_smooth = stderr_interp(x_smooth)

    return x_smooth, spline(x_smooth), stderr_smooth


# Interpolate for 'own' voice condition
x_smooth_external_own, means_smooth_external_own, stderr_smooth_external_own = interpolate_data(
    vocode_band_values_external_own, means_external_own, stderr_external_own)
x_smooth_internal_own, means_smooth_internal_own, stderr_smooth_internal_own = interpolate_data(
    vocode_band_values_internal_own, means_internal_own, stderr_internal_own)

# Interpolate for 'other' voice condition
x_smooth_external_other, means_smooth_external_other, stderr_smooth_external_other = interpolate_data(
    vocode_band_values_external_other, means_external_other, stderr_external_other)
x_smooth_internal_other, means_smooth_internal_other, stderr_smooth_internal_other = interpolate_data(
    vocode_band_values_internal_other, means_internal_other, stderr_internal_other)

# Create figure with two subplots
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Plot for 'own' condition in the first subplot
ax = axs[0]
ax.plot(x_smooth_external_own, means_smooth_external_own, label='External', color='blue')
ax.fill_between(x_smooth_external_own,
                means_smooth_external_own - stderr_smooth_external_own,
                means_smooth_external_own + stderr_smooth_external_own,
                alpha=0.2, color='blue')

ax.plot(x_smooth_internal_own, means_smooth_internal_own, label='Internal', color='red')
ax.fill_between(x_smooth_internal_own,
                means_smooth_internal_own - stderr_smooth_internal_own,
                means_smooth_internal_own + stderr_smooth_internal_own,
                alpha=0.2, color='red')

ax.set_title("Voice Condition: Own")
ax.set_xlabel('Vocode Band')
ax.set_ylabel('Mean Response')
ax.legend()

# Plot for 'other' condition in the second subplot
ax = axs[1]
ax.plot(x_smooth_external_other, means_smooth_external_other, label='External', color='blue')
ax.fill_between(x_smooth_external_other,
                means_smooth_external_other - stderr_smooth_external_other,
                means_smooth_external_other + stderr_smooth_external_other,
                alpha=0.2, color='blue')

ax.plot(x_smooth_internal_other, means_smooth_internal_other, label='Internal', color='red')
ax.fill_between(x_smooth_internal_other,
                means_smooth_internal_other - stderr_smooth_internal_other,
                means_smooth_internal_other + stderr_smooth_internal_other,
                alpha=0.2, color='red')

ax.set_title("Voice Condition: Other")
ax.set_xlabel('Vocode Band')
ax.set_ylabel('Mean Response')
ax.legend()

plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_exp1_vocode_externalVSinternal_' + time.strftime("%d_%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()

# endregion
"""
Example of interleaved staircases that measure tone-in-noise detection thresholds at 4 frequencies
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


#vp = input("Enter the participant ID: VPXX ")
vp = input("Enter the participant ID VPXX: ")
main_path = Path('C:/projects/AVH/stimuli/')
noise_path = main_path /'noise'/ 'speech_shaped_noise_dichotic_13s.wav'
noise = slab.Sound.read(noise_path)
noise = slab.Signal.resample(noise,fs)
noise.level = 50
m_ratio = ['own', '10', '20', '30', '40', '50', '60', '80', 'other']
stim_path = Path('C:/projects/AVH/stimuli/') / vp / 'morphed' / '_Intensity75' / 'stim_list.pkl'
with open(stim_path, 'rb') as file:
    stim_list = pickle.load(file)

n_stim = 10  #number of vocoding bands
n_rep = 15   #Marc: 12-15 repetition


############################## CUSTOM FUNCTIONS###################################################################
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
stim_device = [(stim, 'h') for stim in stim_list] + \
                   [(stim, 's') for stim in stim_list]      # 0-9  central, 10-19  behind
seq = slab.Trialsequence(conditions=stim_device, n_reps=n_rep)  # 1 repetitions per condition

play_noise_headphones(noise)

count = 0
results=dict()
for stim_device in seq:
    stim_current = stim_device
    last_trial = get_random_number(last_trial, n_stim)
    stimulus = stim_current[0][last_trial]     # index 1 sound object in array, same vocode level, different words
    #stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)   #pad zeros
    stimulus.level = 70
    if stim_current[1] == 's':
        stimulus.level = 73
    stimulus.ramp(duration = 0.02)
    interplay(stimulus, equalize=True, device= stim_current[1])
    response, reaction_time = collect_response()
    results[str(seq.this_n)] = {'Response': response,
                                'Word played': stimulus.name.split('_')[0],
                                'Morph played': stimulus.name[stimulus.name.find('_')+7:stimulus.name.rfind('.')],
                                'Device': stim_current[1],
                                'Reaction time': reaction_time}
    count = count + 1
    if count % 135 == 0:
        time.sleep(3)
        tone = slab.Sound.tone(frequency=500, duration=0.5);tone.level = 70
        interplay(tone, equalize=True, device='s')
        input("Press Enter to continue...")
        time.sleep(10)
    if response == 2: time.sleep(2)
    else: time.sleep(1)

freefield.halt()

################################### Save raw data ##############################################################
file_path = main_path/vp
os.chdir(file_path)
file_name = 'exp1_morph_'+ time.strftime("%m_%d_%H_%M")+'.pkl'
with open(file_name, 'wb') as f:
    pickle.dump(results, f)

file_name = 'exp1_morph_'+ time.strftime("%m_%d_%H_%M")+'.csv'
fieldnames = list(next(iter(results.values())).keys())
# Open the file and write the CSV
with open(file_name, mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()  # Write the header (column names)
    # Write the rows of data, where each row is a dictionary from `results`
    for key, value in results.items():
        writer.writerow(value)  # Write the data row

################################### CONDITION MEAN ############################################################
################################################################################################################

### load seq back in to check results#############################################################################
#file_path = os.path.join(main_path,vp,'seq_exp2_revised_09_05_12_06.pkl').replace("\\", "/")
#with open(file_path, 'rb') as file:
    #seq = pickle.load(file)

## Condition mean and plot
def convert_morph(morph):
    if morph == '_0':
        return 0
    return int(morph)

# Group the data by Device and Morph played
grouped_results = defaultdict(list)

for key, value in results.items():
    device = value['Device']
    morph_played = value['Morph played']
    response = value['Response']
    morph_played_int = convert_morph(morph_played)  # Convert the morph played to integer
    grouped_results[(device, morph_played_int)].append(response)

# Calculate the mean and standard error for each group
mean_responses = defaultdict(list)
stderr_responses = defaultdict(list)

for (device, morph), responses in grouped_results.items():
    mean_responses[(device, morph)] = statistics.mean(responses)
    stderr_responses[(device, morph)] = statistics.stdev(responses) / len(responses) ** 0.5  # Standard error

# Prepare data for plotting
devices = ['h', 's']  # 'h' for headphones, 's' for speaker
morph_values = sorted(set(morph for _, morph in mean_responses.keys()))  # Unique sorted morph values
means_h = []
stderr_h = []
means_s = []
stderr_s = []

for morph in morph_values:
    if ('h', morph) in mean_responses:
        means_h.append(mean_responses[('h', morph)])
        stderr_h.append(stderr_responses[('h', morph)])
    if ('s', morph) in mean_responses:
        means_s.append(mean_responses[('s', morph)])
        stderr_s.append(stderr_responses[('s', morph)])

# Interpolation (spline) to make the curve smooth
spline_h = CubicSpline(morph_values[:len(means_h)], means_h)
spline_s = CubicSpline(morph_values[:len(means_s)], means_s)

# Create smooth x-values for plotting
x_smooth = np.linspace(min(morph_values), max(morph_values), 500)

# Interpolate the standard error to match the smooth x-values
stderr_h_interp = interp1d(morph_values[:len(stderr_h)], stderr_h, kind='linear', fill_value="extrapolate")
stderr_s_interp = interp1d(morph_values[:len(stderr_s)], stderr_s, kind='linear', fill_value="extrapolate")

# Calculate the standard error values for the smooth curve
stderr_h_smooth = stderr_h_interp(x_smooth)
stderr_s_smooth = stderr_s_interp(x_smooth)

# Plotting
plt.figure(figsize=(10, 6))

# Plot Headphones ('h') with smooth curve
plt.plot(x_smooth, spline_h(x_smooth), label='central', color='blue')
plt.fill_between(x_smooth,
                 spline_h(x_smooth) - stderr_h_smooth,
                 spline_h(x_smooth) + stderr_h_smooth,
                 color='blue', alpha=0.2)

# Plot Speaker ('s') with smooth curve
plt.plot(x_smooth, spline_s(x_smooth), label='external', color='red')
plt.fill_between(x_smooth,
                 spline_s(x_smooth) - stderr_s_smooth,
                 spline_s(x_smooth) + stderr_s_smooth,
                 color='red', alpha=0.2)

# Adding labels and title
plt.xlabel('Morph played')
plt.ylabel('Voice recognition Mean Response')
plt.title('Voice recognition by Location (central vs external) ' + vp)
plt.legend()

# Customizing x-axis labels to relabel 0 to 'own' and 100 to 'other'
plt.xticks(
    ticks=[0, 20, 40, 60, 80, 100],  # Add any other values you'd like
    labels=['100%_own', '80%_own', '60%_own', '60%_other', '80%_other', '100%_other']  # Change 0 to 'own' and 100 to 'other'
)

# Show plot
plt.xticks(rotation=45)
plt.tight_layout()
save_path = os.path.join(main_path,vp,f'{vp}_exp2_own_other_dis_' + time.strftime("%d_%m_%H_%M") +'.svg').replace("\\", "/")
plt.savefig(save_path,format='svg')
plt.show()



import slab
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import time
import threading
import pickle

### Simple version
# make noise 100-4k, pink or white noise
# play 10s sound
# record 3s
# look at the level
# make them the same way

main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/equalize'
slab.set_default_samplerate(44100)
pink_noise = slab.Sound.pinknoise(duration=10.0)
# bandpass filter from 80Hz to 4000Hz
pink_noise.filter(frequency=(80, 4000), kind='bp')
dev_diff = 20.56
pink_noise.level = 70 #+ dev_diff
speakers = sc.all_speakers()
dev_index = 1
device_name = speakers[dev_index]


def record_audio(duration, samplerate, file_name, buffer_size):
    data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        data.append(indata.copy())

    # Combine the file path and file name
    full_file_name = os.path.join(main_path, file_name).replace("\\", "/")

    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=buffer_size):
        sd.sleep(int(duration * 1000))
    recording = np.concatenate(data, axis=0)
    sf.write(full_file_name, recording, samplerate)


recording_thread = threading.Thread(target=record_audio, args=(5.0, 44100, 'pink_noise_equalize_'+device_name +'.wav', 1024))
recording_thread.start()
pink_noise.play(device_index=dev_index)
recording_thread.join()







#participant = input("Enter the participant ID: ")
vp = 'VP00' #+ participant
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli'
bands = ['0.1', '0.3', '0.5', '0.7', '0.9', '1.1', '1.3', '1.5', '1.7']
file_path = os.path.join(main_path, vp,"stim_list.pkl").replace("\\", "/")
with open(file_path, 'rb') as file:
    stim_list = pickle.load(file)

device_names = [device['name'] for device in sd.query_devices()]
default_device = device_names.index("Kopfhörer (Realtek(R) Audio)")

# Set output devices: replace 'Laptop Speaker' and 'Headphone' with the actual device names or indices
speakers = sc.all_speakers()
speaker_index = 2
headphone_index = 3

stim_device = [(stim, headphone_index) for stim in stim_list] + \
                   [(stim, speaker_index) for stim in stim_list]        ##first 9 vocodes are own, next 6 vocodes are other
import soundfile as sf


def record_audio(duration, samplerate, file_name, buffer_size):
    data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        data.append(indata.copy())

    # Combine the file path and file name
    full_file_name = os.path.join(main_path, vp,'equalize', file_name).replace("\\", "/")

    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=buffer_size):
        sd.sleep(int(duration * 1000))
    recording = np.concatenate(data, axis=0)
    sf.write(full_file_name, recording, samplerate)

seq_equal = slab.Trialsequence(conditions=stim_device, n_reps=1)  # 2 repetitions per condition

for stim_device in seq_equal:
    stim_current = stim_device
    stimulus = stim_current[0][np.random.choice(n_stim)]         # index 1 sound object in array
    stimulus.level = 65
    device_idx = stim_current[1]                           # index device
    file_name = f'{seq_equal.this_n} recorded_65DB.wav'
    # Start recording in a separate thread
    recording_thread = threading.Thread(target=record_audio, args=(1.0, 44100, file_name, 1024))
    recording_thread.start()

    #time.sleep(0.5)
    stimulus.play(device_index=device_idx)
    #time.sleep(1.0)
    recording_thread.join()


#######################
def record_and_play_stimulus(duration, samplerate, file_name, buffer_size, file_path, device_idx, stimulus):
    data = []

    def callback(indata, frames, time, status):
        if status:
            print(status)
        data.append(indata.copy())

    # Ensure the directory exists
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # Combine the file path and file name
    full_file_name = os.path.join(file_path, file_name)

    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=buffer_size):
        # Play the stimulus immediately after the stream starts
        stimulus.play(device_index=device_idx)
        sd.sleep(int(duration * 1000))

    recording = np.concatenate(data, axis=0)
    sf.write(full_file_name, recording, samplerate)


# Example usage in your loop
for stim_device in seq_equal:
    stim_current = stim_device
    stimulus = stim_current[0][np.random.choice(n_stim)]  # index 1 sound object in array
    stimulus.level = 65
    device_idx = stim_current[1]  # index device

    # File name for the recording
    file_name = f'{seq_equal.this_n} recorded_65DB.wav'
    file_path = os.path.join(main_path, vp,'equalize', file_name).replace("\\", "/")

    # Perform recording and stimulus playback in the same thread
    record_and_play_stimulus(1.0, 44100, file_name, 1024, file_path, device_idx, stimulus)

### so its working, but sometimes, the stimulus is delayed so its not in the recording anymore
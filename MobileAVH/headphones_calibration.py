
import slab
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import time
import pickle
import threading

### Simple version
# make noise 100-4k, pink or white noise
# play 10s sound
# record 3s
# look at the level
# make them the same way
device_names = [device['name'] for device in sd.query_devices()]
headphone_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Kopfhörer (Realtek(R) Audio)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")
speaker_index = next(idx for idx, device in enumerate(sd.query_devices()) if device['name'] == "Lautsprecher (USB Sound Blaster HD)" and sd.query_hostapis()[device['hostapi']]['name'] == "Windows DirectSound")

main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/equalize/noear3/'
slab.set_default_samplerate(44100)
noise = slab.Sound.pinknoise(duration=10.0)             #pink or white noise
#noise.spectrum()
# bandpass filter from 80Hz to 4000Hz
filters = []
low_cutoff_freqs = [80]
high_cutoff_freqs = [16000]
for low, high in zip(low_cutoff_freqs, high_cutoff_freqs):
    filters.append(slab.Filter.band(frequency=(low, high), kind='bp'))
fbank = slab.Filter(filters)  # put the list into a single filter object
sound = fbank.apply(noise)  # apply each filter to a copy of sound


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


### recording loops for HEADPHONE
intensity = [80,85]
device_name = 'headphone_'
for i in range(len(intensity)):
    recording_thread = threading.Thread(target=record_audio, args=(5.0, 44100, 'pinknoise_equalize_noear_'+device_name + str(intensity[i]) +'.wav', 1024))
    recording_thread.start()
    current = sound       #sound is the filtered pinknoise (80-4000)
    current.level = intensity[i]
    current.play(device=headphone_index)
    recording_thread.join()
    time.sleep(3)
#####################

### recording loops for SPEAKER
intensity = [40,45,50,55,60,65,70,75]
device_name = 'speaker_'
for i in range(len(intensity)):
    recording_thread = threading.Thread(target=record_audio, args=(5.0, 44100, 'pinknoise_equalize_noear_'+device_name + str(intensity[i]) +'.wav', 1024))
    recording_thread.start()
    current = sound        #sound is the filtered pinknoise (80-4000)
    current.level = intensity[i]
    current.play(device=speaker_index)
    recording_thread.join()
    time.sleep(3)
#####################

########################## CREATE INVERSE FILTER ###########################################
sound.level = 65    ####final value w/o ears 65
recording_speaker = slab.Sound.read(main_path + 'pinknoise_equalize_noear_speaker_65.wav')
recording_speaker.spectrum()
inverse_s = slab.Filter.equalizing_filterbank(reference=sound, sound=recording_speaker)
equalized = inverse_s.apply(recording_speaker)
equalized.spectrum()
slab.Filter.save(inverse_s, main_path + 'inverse_s')

###
sound.level = 65    #####final value w/o ears: 70
recording_headphone = slab.Sound.read(main_path + 'pinknoise_equalize_noear_headphone_75.wav')
recording_headphone.spectrum()
inverse_h = slab.Filter.equalizing_filterbank(reference=sound, sound=recording_headphone)
equalized = inverse_h.apply(recording_headphone)
equalized.spectrum()
slab.Filter.save(inverse_h, main_path + 'inverse_h')


################Load in filter
inverse_s = slab.Filter.load(main_path + 'inverse_s.npy')
inverse_h = slab.Filter.load(main_path + 'inverse_h.npy')

#################test filter################################
sound.level = 70#####use this value
device_name = 'headphone_'
recording_thread = threading.Thread(target=record_audio, args=(5.0, 44100, 'equalize_withear_wf1'+device_name +'.wav', 1024))
recording_thread.start()
current = inverse_h.apply(sound)       #sound is the filtered pinknoise (80-4000)
current.play(device=headphone_index)
recording_thread.join()

#####################

### recording test filter
sound.level = 70######use this value
device_name = 'speaker_'
recording_thread = threading.Thread(target=record_audio, args=(5.0, 44100, 'equalize_withear_wf1'+device_name +'.wav', 1024))
recording_thread.start()
current = inverse_s.apply(sound)        #sound is the filtered pinknoise (80-8000)
current.play(device=speaker_index)
recording_thread.join()

#####################Check morph home
#### REAL AUDIOS#######
inverse_s = slab.Filter.load(main_path + 'inverse_s.npy')
inverse_h = slab.Filter.load(main_path + 'inverse_h.npy')
##########
#inverse_h.data = inverse_h.data * 0.5
#inverse_s.data = inverse_s.data * 0.5
####################

stimulus = slab.Sound.read("C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/X00Y00Z/vocoded/_Intensity75/Gain_01.wav")
stimulus.level = 70#####use this value
device_name = 'headphone_'
recording_thread = threading.Thread(target=record_audio, args=(3.0, 44100, 'Arm_withear_wf1'+device_name +'.wav', 1024))
recording_thread.start()
current = inverse_h.apply(stimulus)       #sound is the filtered pinknoise (80-4000)
current.play(device=headphone_index)
recording_thread.join()

#####################

### recording test filter
stimulus.level = 70######use this value
device_name = 'speaker_'
recording_thread = threading.Thread(target=record_audio, args=(3.0, 44100, 'Arm_withear_wf1'+device_name +'.wav', 1024))
recording_thread.start()
current = inverse_s.apply(stimulus)        #sound is the filtered pinknoise (80-8000)
current.play(device=speaker_index)
recording_thread.join()


####Still cannot tell quite well with 0.5 filter, had to increase level to 80
#just the same as keeping 1.0 filter and level at 70, dont see the point, its only affecting the loudness, not the location per say
# test again on monday with 0.5 filter if localize better

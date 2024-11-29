# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
import freefield
import slab
import time
import numpy
from pathlib import Path
from copy import deepcopy
import pickle

# initialize setup with standard samplerate (48824)
proc_list = [['RP2', 'RP2', freefield.DIR / 'data' / 'rcx' / 'bi_play_rec_buf.rcx'],
             ['RX81', 'RX8', freefield.DIR / 'data' / 'rcx' / 'play_buf.rcx'],
             ['RX82', 'RX8', freefield.DIR / 'data' / 'rcx' / 'play_buf.rcx']]
freefield.initialize(setup='dome', device=proc_list)
freefield.PROCESSORS.mode = 'play_birec'

# freefield.set_logger('warning')
fs = 48828
slab.Signal.set_default_samplerate(fs)  # default samplerate for generating sounds, filters etc.

# dome parameters
reference_speaker = 23          #this is the index of the central speaker

# signal parameters             # change this to speech spectrum white noise
low_cutoff = 80
high_cutoff = 8000
rec_repeat = 5  # how often to repeat measurement for averaging
# signal for loudspeaker calibration
signal_length = 2.0  # how long should the chirp be?
ramp_duration = signal_length / 50
# use quadratic chirp to gain power in low freqs
# signal = slab.Sound.chirp(duration=signal_length, level=85, from_frequency=low_cutoff, to_frequency=high_cutoff,
#                           kind='linear')
# signal = slab.Sound.ramp(signal, when='both', duration=ramp_duration)

# equalization parameters           # dont think I need this
level_threshold = 0.3  # correct level only for speakers that deviate more than <threshold> dB from reference speaker
freq_bins = 1000  # can not be changed as of now
# filter bank parameters
bandwidth = 1 / 50
alpha = 1.0

### Pink noise
noise = slab.Sound.whitenoise(duration =2.0)
filters = slab.Filter.band(frequency=(low_cutoff,high_cutoff), kind='bp')
fbank = slab.Filter(filters)
signal = fbank.apply(noise)
signal.level = 85
### Physical difference: headphone is about 5db louder than speaker
signal = slab.Sound.ramp(signal, when='both', duration=ramp_duration)

### SET SIGNAL & FUNCTIONS for headphone
def set_signal_headphones(signal,equalize=False, data_tags=['data_l', 'data_r'], chan_tags=['chan_l', 'chan_r'],         #have to set back to False when start raw recording
                          n_samples_tag='playbuflen'):
    # get speaker id's for each headphone speaker
    table_file = freefield.DIR / 'data' / 'tables' / Path(f'speakertable_dome.txt')
    speaker_table = numpy.loadtxt(table_file, skiprows=1, usecols=(0, 3, 4), delimiter=",", dtype=float)
    headphone_speaker_list = (speaker_table[-2:, 0]).astype('int')
    speakers = freefield.pick_speakers(headphone_speaker_list)
    if signal.n_channels == 1:
        signal = slab.Binaural(signal)
    freefield.PROCESSORS.write(tag=n_samples_tag, value=signal.n_samples, processors='RP2')
    for i, (speaker, ch_tag, data_tag) in enumerate(zip(speakers, chan_tags, data_tags)):
        if equalize:
            freefield.logging.info('Applying calibration.')  # apply level and frequency calibration
            to_play = freefield.apply_equalization(signal.channel(i),speaker=speakers).data
        elif not equalize:
            to_play = signal.channel(i).data
        freefield.PROCESSORS.write(tag=ch_tag, value=speaker.analog_channel, processors=speaker.analog_proc)
        freefield.PROCESSORS.write(tag=data_tag, value=to_play, processors=speaker.analog_proc)

def play_and_record_headphones(signal,equalize=False):
    n_delay = freefield.get_recording_delay(play_from="RP2", rec_from="RP2", sample_rate=fs)
    n_delay += 50  # make the delay a bit larger to avoid missing the sound's onset
    rec_n_samples = int(signal.duration * fs)
    freefield.write(tag="recbuflen", value=rec_n_samples + n_delay, processors="RP2")
    if equalize:
        set_signal_headphones(signal=signal, equalize=True)
    elif not equalize:
        set_signal_headphones(signal=signal, equalize=False)
    freefield.write(tag='chan', value=99, processors=['RX81', 'RX82'])
    freefield.play()
    freefield.wait_to_finish_playing()
    rec = slab.Binaural([freefield.read(tag='datal', processor='RP2', n_samples=rec_n_samples + n_delay)[n_delay:],
                         freefield.read(tag='datar', processor='RP2', n_samples=rec_n_samples + n_delay)[n_delay:]],
                        samplerate=fs)

    return rec

# SPEAKER recording

#filt = slab.Filter.band(frequency=60, kind='hp')        # filter out the strange line noise (or whatever that was causing the sine wave)
reference_speaker = freefield.pick_speakers(reference_speaker)[0]
temp_recs = []
n_delay = freefield.get_recording_delay(play_from="RX8", rec_from="RP2")
n_delay += 50  # make the delay a bit larger to avoid missing the sound's onset
freefield.set_signal_and_speaker(speaker=reference_speaker, signal=signal, equalize=False)
freefield.write(tag="recbuflen", value=signal.n_samples + n_delay, processors="RP2")
freefield.write(tag='chan_l', value=99, processors='RP2')
freefield.write(tag='chan_r', value=99, processors='RP2')
temp_recs = []
speaker_rec = []
for i in range(rec_repeat):
    freefield.play()
    #time.sleep(3)
    rec_l = freefield.read(tag='datal', processor='RP2', n_samples=signal.n_samples + n_delay)[n_delay:]
    rec_r = freefield.read(tag='datar', processor='RP2', n_samples=signal.n_samples + n_delay)[n_delay:]
    rec = slab.Binaural([rec_l, rec_r], samplerate=fs)
    freefield.wait_to_finish_playing()
    temp_recs.append(rec.data)
speaker_rec = slab.Sound(data=numpy.mean(temp_recs, axis=0))        #need to match this to the target signal
#speaker_rec = filt.apply(speaker_rec)
speaker_rec.channel(1).waveform()
speaker_rec.channel(1).spectrum()

### Match speaker recording with target signal, only for transfer function
#speaker_filter_bank_l = slab.Filter.equalizing_filterbank(reference= signal, sound = speaker_rec.channel(0))
speaker_filter_bank_r = slab.Filter.equalizing_filterbank(reference= signal, sound = speaker_rec.channel(1),length=1000, bandwidth=1/8, low_cutoff=80, high_cutoff=16000,
                              alpha=1.0, filt_meth='filtfilt')
# test filter bank for speaker (to match target signal)

speaker_filtered_signal = deepcopy(signal)
#speaker_filtered_signal = slab.Binaural(speaker_filtered_signal)
#speaker_filtered_signal.data[:, 0] = speaker_filter_bank_l.apply(speaker_filtered_signal.channel(0)).data[:, 0]
speaker_filtered_signal = speaker_filter_bank_r.apply(speaker_filtered_signal)
# record speaker again to test tf
freefield.set_signal_and_speaker(speaker=reference_speaker, signal=speaker_filtered_signal, equalize=False)
freefield.write(tag="recbuflen", value=signal.n_samples + n_delay, processors="RP2")
freefield.write(tag='chan_l', value=99, processors='RP2')
freefield.write(tag='chan_r', value=99, processors='RP2')
temp_recs = []
speaker_rec_tf = []
for i in range(rec_repeat):
    freefield.play()
    #time.sleep(2)
    rec_l = freefield.read(tag='datal', processor='RP2', n_samples=signal.n_samples + n_delay)[n_delay:]
    rec_r = freefield.read(tag='datar', processor='RP2', n_samples=signal.n_samples + n_delay)[n_delay:]
    rec = slab.Binaural([rec_l, rec_r], samplerate=fs)
    freefield.wait_to_finish_playing()
    temp_recs.append(rec.data)
speaker_rec_tf = slab.Sound(data=numpy.mean(temp_recs, axis=0))        #need to match this to the target signal
#speaker_rec_tf = filt.apply(speaker_rec_tf)
#speaker_rec_tf.waveform()
speaker_rec_tf.channel(1).spectrum()
speaker_rec.channel(1).spectrum()
signal.spectrum()


# ---- START calibration ----#
# step 1: level equalization
"""
Record the signal from each speaker in the list and return the level of each
speaker relative to the target speaker(target speaker must be in the list)
"""
freefield.PROCESSORS.mode = 'bi_play_rec'
temp_recs = []
for i in range(rec_repeat):
    rec = play_and_record_headphones(signal,equalize=False)
    #time.sleep(2)
    temp_recs.append(rec.data)
headphone_rec = (slab.Sound(data=numpy.mean(temp_recs, axis=0)))

#left_level = headphone_rec.channel(0).level
#right_level = headphone_rec.channel(1).level
#headphone_level_cor = left_level - right_level
headphone_rec.waveform()
headphone_rec.channel(1).spectrum()

### correct left_right difference, I hope Thomas will fix this so it can be gone
#signal_level_cor = deepcopy(signal)
#signal_level_cor = slab.Binaural(signal_level_cor)
#signal_level_cor.channel(1).level = headphone_rec.channel(0).level + headphone_level_cor
#temp_recs = []
#for i in range(rec_repeat):
    #rec = play_and_record_headphones(signal_level_cor,equalize=False)
    #temp_recs.append(rec.data)
#headphone_rec = (slab.Sound(data=numpy.mean(temp_recs, axis=0)))
#headphone_rec.waveform()
#headphone_rec.spectrum()

headphone_filter_bank_l = slab.Filter.equalizing_filterbank(reference= speaker_rec_tf.channel(1), sound = headphone_rec.channel(0),length=1000, bandwidth=1/8, low_cutoff=80, high_cutoff=16000,
                              alpha=1.0, filt_meth='filtfilt')
headphone_filter_bank_r = slab.Filter.equalizing_filterbank(reference= speaker_rec_tf.channel(1), sound = headphone_rec.channel(1),length=1000, bandwidth=1/8, low_cutoff=80, high_cutoff=16000,
                              alpha=1.0, filt_meth='filtfilt')
# thresholding
equalization_levels = speaker_rec.level - headphone_rec.level

# step 2: frequency equalization
"""
play the level-equalized signal, record and compute a bank of inverse filters
to equalize each speakers frequency response relative to the target speaker
"""
# filter raw signal with headphone inverse
headphone_filtered_signal = deepcopy(signal)
headphone_filtered_signal = slab.Binaural(headphone_filtered_signal)
headphone_filtered_signal.data[:, 0] = headphone_filter_bank_l.apply(headphone_filtered_signal.channel(0)).data[:, 0]
headphone_filtered_signal.data[:, 1] = headphone_filter_bank_r.apply(headphone_filtered_signal.channel(1)).data[:, 0]

headphone_rec_tf = []  # store all recordings from the dome for final spectral difference
equalization = dict()  # dictionary to hold equalization parameters
temp_recs = []
attenuated = deepcopy(headphone_filtered_signal)
#attenuated.level += equalization_levels
#freefield.PROCESSORS.mode = 'bi_play_rec'
# record new filtered data through headphone
for i in range(rec_repeat):
    rec = play_and_record_headphones(attenuated,equalize=False)
    temp_recs.append(rec.data)
headphone_rec_tf = (slab.Sound(data=numpy.mean(temp_recs, axis=0)))
#headphone_rec_tf = filt.apply(headphone_rec_tf)
headphone_rec_tf.channel(0).waveform()
headphone_rec_tf.channel(1).spectrum()
headphone_rec.channel(1).spectrum()
speaker_rec_tf.channel(1).spectrum()

# todo check if filter bank reduces audible differences between speaker and headphones:have to sit down and watch myself

# save equalization
headphone_equalization = {'23': None,'47': None, '48': None}
headphone_equalization['23'] = {"level": equalization_levels[0]+5, "filter": None}
headphone_equalization['47'] = {"level": equalization_levels[0], "filter": headphone_filter_bank_l}
headphone_equalization['48'] = {"level": equalization_levels[1], "filter": headphone_filter_bank_r}

# write final equalization to pkl file
calibration_path = freefield.DIR / 'data' / 'headphone_equalization.pkl'
# project_path = Path.cwd() / 'data' / 'calibration'
# equalization_path = project_path / f'calibration_dome_100k_31.10.pkl'
with open(calibration_path, 'wb') as f:  # save the newly recorded calibration
    pickle.dump(headphone_equalization, f, pickle.HIGHEST_PROTOCOL)

# todo make sure that equalization works with the freefield package - check the load_equalization function in freefield.py

table_file = freefield.DIR / 'data' / 'tables' / Path(f'speakertable_dome.txt')
speaker_table = numpy.loadtxt(table_file, skiprows=1, usecols=(0, 3, 4,), delimiter=",", dtype=float)
headphone_calibration = freefield.load_equalization(calibration_path)
headphone_speaker_list = (speaker_table[-2:, 0]).astype('int')
speakers = freefield.pick_speakers(headphone_speaker_list)

### complete test after calibrating headphone
headphone_rec_full = []  # store all recordings from the dome for final spectral difference
temp_recs = []
final = deepcopy(signal)
#attenuated.level += equalization_levels
freefield.PROCESSORS.mode = 'bi_play_rec'
# record new filtered data through calibrated headphone
for i in range(rec_repeat):
    rec = play_and_record_headphones(final,equalize=True)
    temp_recs.append(rec.data)
headphone_rec_full = (slab.Sound(data=numpy.mean(temp_recs, axis=0)))
headphone_rec_full = filt.apply(headphone_rec_full)

headphone_rec_full.waveform()
headphone_rec_full.spectrum()

speaker_rec.waveform()
speaker_rec.spectrum()
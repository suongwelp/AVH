import slab
import freefield
import copy
import pathlib
import numpy
import time
import os
from EEG_voice_detection.experiment.config import get_config
from EEG_voice_detection.experiment.trial_sequence import generate_slab_freq
from datetime import datetime
import pandas as pd
import random

participant_id = 'sub_02'
stimulus_level=70


slab.set_default_samplerate(44100)
DIR = pathlib.Path(os.getcwd())

config = get_config()
proc_list = config['proc_list']
freefield.initialize('dome', zbus=True, device=proc_list)
freefield.set_logger('WARNING')


def crop_sound(sound, isi):
    isi = slab.Sound.in_samples(isi, sound.samplerate)
    out = copy.deepcopy(sound)
    if sound.n_samples < isi:
        silence_length = isi - sound.n_samples
        silence = slab.Sound.silence(duration=silence_length, samplerate=sound.samplerate)
        left = slab.Sound.sequence(sound.left, silence)
        right = slab.Sound.sequence(sound.right, silence)
        out = slab.Binaural([left, right])
    else:
        out.data = sound.data[: isi]
    out = out.ramp(duration=0.01)
    return out

def load_to_buffer(sound, isi=2.0):
    out = crop_sound(sound, isi)
    isi = slab.Sound.in_samples(isi, 48828)
    freefield.write(tag="playbuflen", value=isi, processors="RP2")
    freefield.write(tag="data_l", value=out.left.data.flatten(), processors="RP2")
    freefield.write(tag="data_r", value=out.right.data.flatten(), processors="RP2")

'''
def collect_responses(seq, results_file):
    response = None
    reaction_time = None
    start_time = time.time()
    while not freefield.read(tag="response", processor="RP2"):
        time.sleep(0.01)
    curr_response = int(freefield.read(tag="response", processor="RP2"))
    if curr_response != 0:
        reaction_time = int(round(time.time() - start_time, 3) * 1000)
        response = int(numpy.log2(curr_response))
        # response for deviant stimulus is reset to 0
    is_correct = response == seq.trials[seq.this_n]
    results_file.write(seq.trials[seq.this_n], tag='solution')
    results_file.write(response, tag='response')
    results_file.write(is_correct, tag='is_correct')
    results_file.write(reaction_time, tag='reaction_time')
    print('Response:' + str(response) +'; RT: ' + str(reaction_time))

def collect_trial(seq, results_file):
    results_file.write(seq.trials[seq.this_n], tag='morph_played')
'''
def collect_response():
    response = None
    reaction_time = None
    start_time = time.time()
    while not freefield.read(tag="response", processor="RP2"):
        time.sleep(0.01)
    curr_response = int(freefield.read(tag="response", processor="RP2"))
    if curr_response != 0:
        reaction_time = int(round(time.time() - start_time, 3) * 1000)
        response = int(numpy.log2(curr_response))
        # response for deviant stimulus is reset to 0
    return response, reaction_time


results_folder = 'C:\\projects\\EEG_voice_detection\\experiment\\results\\EEG'
results_folder_participant= results_folder + '\\' + participant_id
if not os.path.isdir(results_folder_participant):
    os.makedirs(results_folder_participant)
now=datetime.now()
results_file_name = participant_id + '_EEG_'+now.strftime('%y-%m-%d_%H-%M-%S')+'.csv'


#Get list of stimuli in slab format
stim_dict=dict()
stim_path= 'C:\\projects\\EEG_voice_detection\\experiment\\stimuli_peak_aligned'
for sound_file in os.listdir(os.path.join(stim_path)):
    sound = slab.Sound.read(os.path.join(stim_path, sound_file))
    sound.level= stimulus_level
    sound =slab.Binaural(sound)
    morph_ratio = sound_file[-7:-4]
    stim_dict[morph_ratio] = sound

# Define the deviant sound
deviant_sound = slab.Binaural('C:\\projects\\EEG_voice_detection\\experiment\\octave_0.5_morph-1.0_female.wav')
deviant_sound.level = stimulus_level

#morph_ratios= list(stim_dict.keys())
morph_ratios= ['0.0', '0.4', '0.6', '1.0']
#morph_seq = slab.Trialsequence(conditions=[1,2, 3, 4,5, 6], n_reps=5, deviant_freq=0.1)

morph_seq=generate_slab_freq(n_conditions=4, n_reps=40)

input('Press enter to start the experiment')

results={}
for morph in morph_seq:
    print('###Trial', morph_seq.this_n+1, '/', morph_seq.n_trials, '####')

    if random.randint(0,10)==10: # Play Deviant with probability of 10 %
        load_to_buffer(deviant_sound)
        trig_value = len(morph_ratios) + 1 # Trigger Value Deviant is n_conditions+1
        freefield.write(tag='trigcode', value=trig_value, processors='RX82')
        freefield.play()
        print('Playing deviant')
        response, reaction_time = collect_response()
        results[str(morph_seq.this_n)+'_deviant'] = {'Response': response,
                                          'Morph played':'Deviant',
                                          'Reaction time': reaction_time
                                          }
        #collect_responses(morph_seq, results_file)
        freefield.wait_to_finish_playing()

    #print(results)

    stimulus = stim_dict[morph_ratios[morph-1]]
    stimulus.level = stimulus_level
    load_to_buffer(stimulus)
    trig_value = morph
    freefield.write(tag='trigcode', value=trig_value, processors='RX82')
    freefield.play()
    print('Playing morph ', morph_ratios[morph-1])
     #collect_trial(morph_seq, results_file)
    results[str(morph_seq.this_n)] = {'Response': 'Nan',
                                          'Morph played': morph_ratios[morph - 1],
                                          'Reaction time':'Nan',
                                          'Participant': participant_id,
                                          'Phase': 'EEG'
                                          }
    freefield.wait_to_finish_playing(proc="RP2", tag="playback")


results_df=pd.DataFrame.from_dict(results)
results_df=results_df.swapaxes('index', 'columns')
results_df.to_csv(results_folder_participant + '\\'+ results_file_name)
#results_file.write(morph_seq, tag='sequence')
print("Saved participant responses")

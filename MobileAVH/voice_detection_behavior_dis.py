import slab
import freefield
import pathlib
import numpy
import os
from EEG_voice_detection.experiment.config import get_config
import time
from EEG_voice_detection.experiment.trial_sequence import generate_slab_freq
import pandas as pd
from datetime import datetime


participant_id = 'sub_02'
stimulus_level= 70
phase= 'experiment'# Can either be training or experiment

slab.set_default_samplerate(44100)
DIR = pathlib.Path(os.getcwd())

config = get_config()
proc_list = config['proc_list']
freefield.initialize('dome', zbus=True, device=proc_list)
freefield.set_logger('WARNING')


def crop_sound(sound):
    left = slab.Sound.sequence(sound.left)
    right = slab.Sound.sequence(sound.right)
    out = slab.Binaural([left, right])
    return out

def load_to_buffer(sound):
    out = crop_sound(sound)
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
    # while freefield.read(tag="playback", n_samples=1, processor="RP2"):
        # time.sleep(0.01)
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

results_folder = 'C:\\projects\\EEG_voice_detection\\experiment\\results\\behavior'
results_folder_participant= results_folder + '\\' + participant_id
if not os.path.isdir(results_folder_participant):
    os.makedirs(results_folder_participant)
now=datetime.now()
results_file_name = participant_id +  '_'+ phase +'_'+now.strftime('%y-%m-%d_%H-%M-%S')+'.csv'
#results_file = slab.ResultsFile(subject=participant_id, folder=results_folder)
#results_file.write(phase, tag='stage')

# Get list of stimuli in slab format
stim_dict=dict()
stim_path= 'C:\\projects\\EEG_voice_detection\\experiment\\stimuli_peak_aligned'
for sound_file in os.listdir(os.path.join(stim_path)):
    sound = slab.Sound.read(os.path.join(stim_path, sound_file))
    sound.level= stimulus_level
    sound =slab.Binaural(sound)
    morph_ratio = sound_file[-7:-4]
    stim_dict[morph_ratio] = sound

morph_ratios= list(stim_dict.keys())


input('Press enter to start the experiment')

if phase=='training':
    morph_seq = slab.Trialsequence(conditions=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], trials=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], n_reps=1)
if phase=='experiment':
    #morph_seq = slab.Trialsequence(conditions=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], n_reps=1, kind='random_permutation')
   morph_seq = generate_slab_freq(n_conditions=11, n_reps=11)


results=dict()
for morph in morph_seq:
    print('###Trial', morph_seq.this_n +1, '/', morph_seq.n_trials, '###')
    stimulus= stim_dict[morph_ratios[morph-1]]
    load_to_buffer(stimulus)
    print('Playing morph ', morph_ratios[morph-1])
    freefield.play()
    #collect_responses(morph_seq, results_file)
    response, reaction_time=collect_response()
    results[str(morph_seq.this_n)]= {'Response': response,
                                     'Morph played': morph_ratios[morph-1],
                                     'Reaction time': reaction_time,
                                     'Participant': participant_id,
                                     'Phase': phase
                               }
    freefield.wait_to_finish_playing(proc="RP2", tag="playback")
    #print('End of stimulus')
    #collect_responses(morph_seq, results_file)
    time.sleep(0.5) #wait 0.5 secs before playing the next stimulus-> in a sense the isi


print('##End of the experiment###')

results_df=pd.DataFrame.from_dict(results)
results_df=results_df.swapaxes('index', 'columns')
results_df.to_csv(results_folder_participant + '\\'+ results_file_name)
#results_file.write(morph_seq, tag='sequence')
print("Saved participant responses")
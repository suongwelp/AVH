""
#Load in recordings and perform vocode
""

import slab
import os
import numpy as np
import soundfile as sf
import sounddevice as sd
import soundcard as sc
import pickle
import parselmouth
import subprocess
import cupy as cp


language = input("EN/DE?: EN(1)/DE(0) ")
vp = input("Enter the participant ID VPXX: ")
sex = input("male/female: ")
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/'
#vp = 'VP' + participant
stim_other_path = os.path.join(main_path, 'other','vocoded', 'DE', sex,'stim_list.pkl').replace("\\", "/")
if language == '1':
    lan = 'EN'
    stim_other_path = os.path.join(main_path, 'other','vocoded', 'EN', sex,'stim_list.pkl').replace("\\", "/")
else:
    lan = 'DE'
stim_own_path = os.path.join(main_path, vp, 'raw').replace("\\", "/")
os.makedirs(stim_own_path, exist_ok=True)
bands = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
vocode_path = os.path.join(main_path, vp,'vocoded/').replace("\\", "/")
os.makedirs(vocode_path, exist_ok=True)
morph_path = os.path.join(main_path, vp, 'morphed/').replace("\\", "/")

#maybe here a short script to check how many audios were extracted, if it's not 10, then dont proceed

############Cut recording to words#######################################################
praat_executable = "C:/Program Files/Praat/Praat.exe"
praat_script = main_path +"process_own_stimuli_new.txt"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, vp,lan)
# this crash a lot if praat cant tell how many audios  there are

############Scale duration of the raw data to 0.5 with Praat##############################
praat_script = main_path +"Equalize_duration.txt"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, "stretch/shrink_duration","specific duration (in s) below", 0.5,
                           "sounds in a folder:",stim_own_path, "yes", "")
stim_own_path = os.path.join(main_path, vp, 'raw','eq_dur_target_0500').replace("\\", "/")
##########################################################################################

# load other vocoded
with open(stim_other_path, 'rb') as file:
    stim_other = pickle.load(file)

##############Load in raw wav and vocode and save as wav again########################
def load_stims(path_in,path_out, band):
    speech = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(path_in) if os.path.isfile(os.path.join(path_in, f)) and f.endswith(('.wav'))]

    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files:
        file_path = os.path.join(path_in, audio_file)
        sound = slab.Sound.read(file_path)
        sound = sound.vocode(bandwidth= band)       #after vocoding, audio doesnt end at 0
        output_filename = f"{os.path.splitext(audio_file)[0]}_{str(band).replace('.', '')}.wav"
        sound.write(os.path.join(path_out, output_filename).replace("\\", "/"),normalise=False)

for i in range(len(bands)):
    load_stims(stim_own_path,vocode_path, bands[i])

############Scale intensity of the vocoded wav with Praat##############################
praat_script = main_path +"2.scale_intensity.praat"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, 75,vocode_path, 'intensity_info.txt')

########## Load in the scaled wav #######################################
def load_stims2(dir, stim_name,band):
    speech = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(band + '.wav')]
    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files:
        file_path = os.path.join(dir, audio_file).replace("\\", "/")
        sound = slab.Sound.read(file_path)
        sound.name = audio_file
        speech.append(sound)
    # Create a Precomputed object with the list of sounds
    stims = slab.Precomputed(speech)

    # Assign the created Precomputed object and labels to a variable with the given name
    band = "_" + str(band).replace('.', '')
    global_var_name = f"{stim_name}{band}"
    globals()[global_var_name] = stims
    return globals()[global_var_name]

bands = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
for i in range(len(bands)):
    load_stims2(os.path.join(vocode_path,'_Intensity75/').replace("\\", "/"), 'stim_own', bands[i])

stim_list = [stim_own_01,stim_own_02,stim_own_03,stim_own_04,stim_own_05,stim_own_06,stim_own_07,stim_own_08,stim_own_09,
             stim_other[0],stim_other[1],stim_other[2],stim_other[3],stim_other[4],stim_other[5],stim_other[6],stim_other[7],stim_other[8]]

file_path = os.path.join(main_path, vp).replace("\\", "/")
os.chdir(file_path)
with open('stim_list.pkl', 'wb') as f:
    pickle.dump(stim_list, f)



##############################MOPRH OWN and OTHER#######################################

def call_matlab(vp, language, sex):
    # Create a string to call the MATLAB function with input arguments
    matlab_command = (
        f"matlab -batch \"addpath('C:/Program Files/MATLAB/R2024a/STRAIGHT/legacy_STRAIGHT-master/morphing_src');"
        f"morph_voice('{vp}', '{language}', '{sex}')\""
    )
    # Run the MATLAB command
    subprocess.run(matlab_command, shell=True, check=True)

# Example usage
call_matlab(vp, lan, sex)

############ Scale intensity of the vocoded wav with Praat ##############################
praat_script = main_path +"2.scale_intensity.praat"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, 75,morph_path, 'intensity_info.txt')

############load in all morphed audios#################################################
bands = ['_0','10','20','30','40','50','60','80','100'];        #bands = morph_ratios
for i in range(len(bands)):
    load_stims2(os.path.join(morph_path,'_Intensity75/').replace("\\", "/"), 'stim_morph', bands[i])


######################safe as list###############################
stim_list = [stim_morph__0,stim_morph_10,stim_morph_20,stim_morph_30,stim_morph_40,stim_morph_50,stim_morph_60,stim_morph_80,stim_morph_100]

os.chdir(morph_path)
with open('stim_list.pkl', 'wb') as f:
    pickle.dump(stim_list, f)
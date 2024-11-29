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

sex = input("male/female: ")
lan = input("EN/DE?: EN(1)/DE(0) ")
if lan == '1':
    lan = 'EN'
else:
    lan = 'DE'
main_path = 'C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/'
stim_other_path = os.path.join(main_path, 'other','raw',lan,sex).replace("\\", "/")
bands = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
vocode_path = os.path.join(main_path, 'other','vocoded',lan,sex).replace("\\", "/")

############Scale duration of the raw data to 0.5 with Praat##############################
praat_executable = "C:/Program Files/Praat/Praat.exe"
praat_script = main_path +"Equalize_duration.txt"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, "stretch/shrink_duration","specific duration (in s) below", 0.5,
                           "sounds in a folder:",stim_other_path, "yes", "")
stim_other_path = os.path.join(main_path, 'other','raw',lan,sex,'eq_dur_target_0500').replace("\\", "/")
##########################################################################################

##############Load in raw wav and vocode and save as wav again########################
def load_stims(path_in,path_out, band):
    speech = []
    # Get list of audio files in the specified directory
    audio_files = [f for f in os.listdir(path_in) if os.path.isfile(os.path.join(path_in, f)) and f.endswith(('.wav'))]

    # Load each audio file and append the sound to the speech list
    for audio_file in audio_files:
        file_path = os.path.join(path_in, audio_file).replace("\\", "/")
        sound = slab.Sound.read(file_path)
        sound = sound.vocode(bandwidth= band)
        #speech.append(sound)
        #os.chdir(path_out)
        output_filename = f"{os.path.splitext(audio_file)[0]}_{str(band).replace('.', '')}.wav"
        sound.write(os.path.join(path_out, output_filename).replace("\\", "/"),normalise=False)

for i in range(len(bands)):
    load_stims(stim_other_path,vocode_path, bands[i])

############Scale intensity of the vocoded wav with Praat##############################

praat_script = main_path +"2.scale_intensity.praat"  # Path to the Praat script
parselmouth.praat.run_file(praat_script, 75,vocode_path, 'intensity_info.txt')


##########Load in the scaled wav#######################################
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
    load_stims2(vocode_path+'/_Intensity75', 'stim_other', bands[i])


######################safe as list###############################
stim_list = [stim_other_01,stim_other_02,stim_other_03,stim_other_04,stim_other_05,stim_other_06,
                stim_other_07,stim_other_08,stim_other_09]

os.chdir(vocode_path)
with open('stim_list.pkl', 'wb') as f:
    pickle.dump(stim_list, f)

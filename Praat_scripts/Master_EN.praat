###MASTER ENGLISH SCRIPT 04.09.2024


vp$ = "VP13"

# Load the sound file
Read from file: "C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/" + vp$ + "/" + vp$ + ".wav"
pathout$ = "C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/" + vp$ + "/raw/" 
createDirectory: pathout$

createDirectory: pathout$
# Define the list of names
names$# = {"Home", "Arm", "Bus", "Ball","Can", "Day", "Ice","Gain","Lay","Rye"}


# Segment the sound into silent and sounding intervals
select Sound 'vp$'
To TextGrid (silences): 80, 0, -30, 0.2, 0.15, "silent", "sounding"

#for manual
#vp$ = "VP01"
#names$# = {"Home", "Arm", "Bus", "Ball","Can", "Day", "Ice","Gain","Lay","Rye"}

# Segment the sound into silent and sounding intervals
select Sound 'vp$'
To TextGrid (silences): 80, 0, -30, 0.2, 0.15, "silent", "sounding"

# Extract the sounding intervals
select Sound 'vp$'
plus TextGrid 'vp$'
Extract intervals where: 1, "no", "is equal to", "sounding"

# Loop through the extracted sound objects, rename, and save them
for i from 1 to 10
    name$ = names$#[i]
    selectObject: "Sound "+ vp$+ "_sounding_" + string$(i)
    #Rename... name$
    Save as WAV file: pathout$ + name$ + ".wav"
    
endfor

##########################################################
runScript ("2.scale_intensity.praat",75,pathout$,"intensity_info.txt")

##########################################################

directory$ = "C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/" + vp$ + "/raw/_Intensity75/"
pathout1$ = "C:/phD/MPI/2.Experiments/1.Voice_Detection_and_Discrimination/stimuli/" + vp$ + "/raw/_Intensity75/pitch_shifted/"
createDirectory: pathout1$

# Create a list of all WAV files in the directory
Create Strings as file list: "File List", directory$ + "*.wav"
file_list = selected("Strings")
number_of_files = Get number of strings

# Loop through the extracted sound objects, rename, and save them
for i from 1 to number_of_files
    select Strings File_List
    fileName$ = Get string... i
    name$ = fileName$ 
    full_path$ = directory$ + name$
    
    # Read the sound file
    Read from file: full_path$
    name_without_extension$ = name$ - ".wav"
    Save as WAV file: pathout1$ + name_without_extension$ + ".wav"
    
       
    # Pitch shift by -2 semitones
    selectObject: "Sound " + name_without_extension$
    To Manipulation: 0.01, 75, 600
    Extract pitch tier
    selectObject: "PitchTier " + name_without_extension$
    totalDuration = Get total duration
    Multiply frequencies: 0, totalDuration, 0.8909
    plusObject: "Manipulation " + name_without_extension$
    Replace pitch tier
    selectObject: "Manipulation " + name_without_extension$
    Get resynthesis (overlap-add)
    Save as WAV file: pathout1$ + name_without_extension$ + "_shift2st_down.wav"
    selectObject: "Sound " + name_without_extension$
    Remove

    # Pitch shift by -4 semitones
    Read from file: full_path$
    To Manipulation: 0.01, 75, 600
    Extract pitch tier
    selectObject: "PitchTier " + name_without_extension$
    totalDuration = Get total duration
    Multiply frequencies: 0, totalDuration, 0.7937
    plusObject: "Manipulation " + name_without_extension$
    Replace pitch tier
    selectObject: "Manipulation " + name_without_extension$
    Get resynthesis (overlap-add)
    Save as WAV file: pathout1$ + name_without_extension$ + "_shift4st_down.wav"
    selectObject: "Sound " + name_without_extension$
    Remove

    
endfor

# Clean up the file list
selectObject: file_list
Remove



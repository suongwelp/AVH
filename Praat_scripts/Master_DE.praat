###MASTER DEUTSCH SCRIPT 12.12.2024
### SUONG WELP


vp$ = "VP20"

# Load the sound file
Read from file: "C:/projects/AVH/stimuli/" + vp$ + "/" + vp$ + ".wav"
pathout$ = "C:/projects/AVH/stimuli/" + vp$ + "/raw/" 
createDirectory: pathout$

createDirectory: pathout$
# Define the list of names
names$# = {"Bein", "Huhn", "Wurm", "Buch","Bahn", "Baum", "Heim","Lamm","Arm","Helm"}

# Segment the sound into silent and sounding intervals
select Sound 'vp$'
To TextGrid (silences): 80, 0, -30, 0.1, 0.15, "silent", "sounding"

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
#runScript ("2.scale_intensity.praat",75,pathout$,"intensity_info.txt")

##########################################################



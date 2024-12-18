### Extract onset, offset, duration of phonemes


# Define the TextGrid file path
filePath$ = "C:/phD/Muenster/Stimulus/Data_Alex/Suong/01/results-2024-08-22_19-18-55/samir_1.TextGrid"  ; Replace with your TextGrid file path
fileOut$ = "C:/phD/Muenster/Stimulus/Phonemes/samir_1_p.csv"  ; Replace with your desired output file path

# Read the TextGrid file
Read from file: filePath$

# Get the name of the TextGrid object
textgridName$ = selected$("TextGrid")

# Set up a table to store results
clearinfo
writeFileLine: fileOut$, "Phoneme,tOnset,tOffset,tDuration"


# Define the tier you want to process (Tier 3)
tierNumber = 3

# Get the number of intervals in the specified tier
numIntervals = Get number of intervals: tierNumber

# Loop through each interval in the tier
for i from 1 to numIntervals
    # Get the phoneme label
    label$ = Get label of interval: tierNumber, i

    # Skip if the label is empty
    if label$ <> ""
        # Get the onset and offset of the interval
        onset = Get start time of interval: tierNumber, i
        offset = Get end time of interval: tierNumber, i

        # Calculate the duration
        duration = offset - onset

        # Print the results in the info window
        appendFileLine: fileOut$, label$, ",", onset, ",", offset, ",", duration
    endif
endfor





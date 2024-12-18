import freefield
import slab
import time
from pathlib import Path
import os


freefield.initialize('dome', 'play_rec')
fs = 48828
#time.sleep()

#freefield.set_signal_and_speaker(speaker=23, signal=slab.Sound.tone(frequency=500, duration=0.5), equalize=False)
#freefield.play()
time.sleep(1)
rec = freefield.play_and_record(speaker=23, sound=slab.Sound.silence(duration=12.0), equalize=False)


rec.play()
rec.waveform()

language = input("DE/EN?: DE(0)/EN(1)")
vp = input("Enter the participant ID VPXX: ")
sex = input("male/female: ")
main_path = Path('C:/projects/AVH/stimuli/')
stim_path = main_path / vp
os.makedirs(stim_path, exist_ok=True)
rec.write(stim_path / (vp + '.wav'))



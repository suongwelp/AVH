stimulus = stim_list[9][0]
stimulus.data = np.pad(stimulus.data, pad_width=((3, 3), (0, 0)), mode='constant', constant_values=0)   #
stimulus.level = 70

stimulus_h = inverse_h.apply(stimulus)
stimulus_h.play(device = headphone_index)

stimulus_s = inverse_s.apply(stimulus)
stimulus_s.play(device = speaker_index)
%% Active Voice veridical Listen Condition + audio check
%% Suong Welp
%% 21.03.2023

close all; clear all; clc;

% cut only voice part out of the recorded audios
% play it back
PP_num = input('Participant number (iii)? ');

%% Praat done?
praat = input('Did you run praat sounding extraction, [y/n] ? ','s');
if strcmp(praat, 'y')
    stimulus_path = ['C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\P',num2str(PP_num),'\Clean\'];   %update path file
elseif strcmp(sex, 'n')
    disp('Please run praat first')
else
    error('Stop and run praat');
end

%% Please define:
number_trial = 50;                                                          % set to 30 or 50 later, depending on exp length

RUNTIME = 5000;   %set runtime value in ms
mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
                                                                
path_to_rcx = [mainpath,'ActiveVoiceTDT_stranger_listen.rcx'];
TDT = TDTRP(path_to_rcx, 'RP2');
pause(0.5)

% only save EEG data

%% Read veridical audio + check bad recordings
FILES      = dir( fullfile(stimulus_path, '*.wav') );
FILES      = cellfun(@(x) x,{FILES.name},'UniformOutput',false);

a=1;
for i = 1: length(FILES)
    stimulus_voice =  [stimulus_path,FILES{1,i}];
    tempt = audioread(stimulus_voice);
    if length(tempt) <= 80000;
        keep{a} = FILES{1,i};
        y_voice{a} = tempt;
        FILES{2,i} = 1;
        a = a+1;
    else
        FILES{2,i} = 0;
    end

    %lengthBuff(i) = length(y_voice{i});
end


%maxBuff = max(lengthBuff);

for i = 1:a-1
    if length(y_voice{1,i}) < 80000
        y_voice{1,i}(end+1:80000) = 0;
    end
    y_voice{1,i} = [0;y_voice{1,i}];
end

%% Experiment starts

% TDT
TDT.write('BufferSize',80000);  

                                                              % b: 2 blocks
for i = 1:a-1
    
    % start playing
    TDT.write('datain', y_voice{1,i});   
                                           
    disp(num2str(i));
    TDT.trg(1);

    pause
    
    
end

% stop acquiring
TDT.halt();

%% good audios
good = input('Which audio to keep? [....] ');

for i = 1: length(good)
    veridical_playback(:,i) = y_voice{1,good(i)};
end

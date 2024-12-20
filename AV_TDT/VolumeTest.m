%% Volume test
%% Suong Welp
%% 21.03.2023

close all; clear all; clc;

mainpath = 'C:\Users\statistics\Documents\Suong_N1\';
beep = fullfile(mainpath,'2. Data','Audio','Stimulus','volume_test.mat');                                                     
path_to_rcx = fullfile(mainpath,'1. Experiment','ActiveVoiceTDT_stranger_listen.rcx'); 
TDT = TDTRP(path_to_rcx, 'RP2');
pause(0.5)

load('volume_test.mat');
volume_test = volume_test/3;


%% Experiment starts


% TDT
TDT.write('BufferSize',12543);  
                                                             
for i = 1:5
        
    % start playing
    TDT.write('datain', volume_test);   
                                        
    pause(0.5)

    TDT.trg(1);
    
    disp(num2str(i));

    pause(2)
end

% stop 
TDT.halt();




%% Active Voice Con 0 baseline recording
%% Suong Welp, Mark Hanus
%% 17.03.2023

close all; clear all; clc;

%% Please define:
number_trial = 10;                                                          % set to 30 or 50 later, depending on exp length
PP_num = input('Participant number (iii)? ');
stimulus_record = input('Stimulus record? [y/n] ','s');
mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
RUNTIME = 3000;                                                                % set runtime value in ms (originally: 3000)
path_to_rcx = [mainpath,'ActiveVoiceTDT_veridical.rcx'];
plusSize = 200;

% Path for saving audio data
path_audio = 'C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\';          % save recorded audio
if ~exist(fullfile(path_audio,['P',num2str(PP_num)]),'dir')
       mkdir(path_audio,['P',num2str(PP_num),'\']);
end

participant_path = fullfile(path_audio,['P',num2str(PP_num)]);

if ~exist(fullfile(participant_path,'Stimulus'),'dir')
       mkdir(participant_path,'Stimulus');
end

if strcmp(stimulus_record,'y')
    pathout = fullfile(participant_path,'Stimulus');
else
    pathout = fullfile(participant_path,'Veridical');
end

% Path for Praat Clean audio playback
if ~exist(fullfile(pathout,'Clean'),'dir')
       mkdir(pathout,'Clean\');
end

TDT = TDTRP(path_to_rcx, 'RP2');
pause(0.5)


%% Experiment starts

%interfacce

close all
sca

Screen('Preference', 'SkipSyncTests', 2); 
screenNumber = 1;                                                           %1 is participant screen
[window,rect] = Screen('OpenWindow',screenNumber,  [169,169,169]); %draw a window which is a rect [50 50 800 500]
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german
instruction = 'Bitte kurz /ah/ sagen, nachdem das Plus auf dem Bildschirm verschwunden ist.\n \n JA = Leertaste';

condition = 'veridical_talk';
begin = 'Drücken Sie die Leertaste, um zu beginnen.';

DrawFormattedText(window,instruction,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(0.5);
 
%TDT
TDT.write('RunTime',RUNTIME);
TDT.write('gain',1.5);                                                      % at gain 0, no more change
[keyIsDown,~,keyCode,~] = KbCheck;
running = 1;

for b = 1:2                                                                 % b: 2 blocks
    
    if running == 0
        break
    end
    DrawFormattedText(window,begin,'center','center',[0 0 0]);
    Screen('Flip',window);
    KbWait;                                                                 %wait for any key
    
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(2);


for i = 1:number_trial
    pause(0.5)
    if running == 0
        break
    end
    [keyIsDown,~,keyCode,~] = KbCheck;
	if keyIsDown
		if keyCode(27)	%escape button
            running = 0;
		    break
            SCREEN('closeall');
		end
	end

   %psychtoolbox
    TDT.trg(1);                                                              % S 16
    Screen('TextSize',window, plusSize)
    DrawFormattedText(window,'+','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(0.5);                                                           % deduct this from reaction time
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    %tic
    Screen('Flip',window);

    % begin acquiring
    % S 32 is voice detection + audio playback onset

    %eeg trigger HERE (Mark): veridical talk_ "S  1" (write from TDT now)

    curindex = TDT.read('index');
    %maxAmp(b,i) = TDT.read('maxAmp');
    %disp(maxAmp);
    
    %disp(['Current buffer index: ' num2str(curindex)]); %to check buffer
    %point
 
    
    % main looping section (TDT)
    bDone = 0;

        while TDT.read('stop') == 1
            pause(0.1)
        end
    
    curindex = TDT.read('index'); 
    %disp(['Current buffer index: ' num2str(curindex)]);
    noise = TDT.read('data_out', 'OFFSET', 0, 'SIZE', curindex);            %noise is participant voice
    %noise_normalized = noise/(max(abs(noise)));
    % save audio
    fileName = sprintf('P%3d_Stimulus_Block_%d_Trial_%d_veridical_Talk_%s.wav',PP_num,b,i,datestr(now,'yyyy-mm-dd_HH-MM'));
    cd(pathout)
    save([fileName,'.mat']);
    audiowrite(fileName,noise,int32(TDT.FS));  
    
  
    v = noise(noise>0.01);
    v = round(length(v)/48828*1000);

    fprintf(1,'Trial %d done',i);
    plot(noise)
    yline(0.4)
    yline(0.1)
    ylim([-0.5 0.5])
    title(sprintf('Block %d Trial %d, voice interval %d ms',b,i,v));
    

    if b == 1 && i == number_trial
        Screen('TextSize',window, 40);
        DrawFormattedText(window,'PAUSE','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(2);  
        
         
        DrawFormattedText(window,'Es geht weiter','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(0.5);

        
        DrawFormattedText(window,'Drücken Sie die Leertaste, um fortzufahren.','center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);
        
        DrawFormattedText(window,' ','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(0.5);
    end
    
end
end

% stop acquiring
TDT.halt();
% display experiment ended
Screen('TextSize',window, 20);
DrawFormattedText(window,'Diese Probe ist zu Ende. \n \n Vielen Dank! ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);
Stimmwahrnehmung
close all
sca

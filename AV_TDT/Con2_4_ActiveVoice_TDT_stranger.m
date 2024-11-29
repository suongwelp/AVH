%% Active Voice Stranger Condition
%% Suong Welp, Mark Hanus
%% 10.03.2023

close all; clear all; clc;

%% Please define:
number_trial = 50;                                                          % set to 30 or 50 later, depending on exp length
PP_num = input('Participant number (iii)? ');
match = input('Con2_matched or Con4_mismatched? [2/4]? ', 's');
if strcmp(match,'2')
    match = 'match';
elseif strcmp(match,'4')
    match = 'mis';
end

mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
stimulus_path = 'C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\Stimulus';
RUNTIME = 3000;                                                             %set runtime value in ms
path_to_rcx = [mainpath,'ActiveVoiceTDT_stranger_rainer.rcx'];
plusSize = 200;

% Path for saving audio data
path_audio = 'C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\';          % save recorded audio
if ~exist(fullfile(path_audio,['P',num2str(PP_num)]),'dir')
       mkdir(path_audio,['P',num2str(PP_num),'\']);
end
mkdir(path_audio,['P',num2str(PP_num),'\',match,'\']);

pathout = [path_audio,['P',num2str(PP_num),'\',match,'\']];

TDT = TDTRP(path_to_rcx, 'RP2');
pause(0.5)


%% SEX & stimuli
sex = input('Participant sex Male/Female, [m/f] ? ','s');
if isempty(sex)
    sex = input('Must input Participant sex [m/f] ? ','s');
end
if strcmp(sex, 'f')
    load(fullfile('C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\Stimulus\',sex,'y_voice1.mat'));
elseif strcmp(sex, 'm')
    load(fullfile('C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\Stimulus\',sex,'y_voice.mat'));
else
    error('Please give a valid input [m/f]');
end



%% Start experiment

%interfacce
close all
sca
Screen('Preference', 'SkipSyncTests', 2); 

screenNumber = 1;                                                          % 1 is participant screen, 2 test screen
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect [50 50 800 500]
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german
consent = 'Ich habe die Instruktionen von diesem Durchlauf des Experiments verstanden. \n \n JA = Leertaste';
if strcmp(match,'match')
    instruction = 'Bitte kurz /ah/ sagen, nachdem das Plus auf dem Bildschirm verschwunden ist.\n \n JA = Leertaste';
else
    instruction = 'Bitte kurz /bi/ sagen, nachdem das Plus auf dem Bildschirm verschwunden ist.\n \n JA = Leertaste';
end

message = 'Setzen Sie sich bequem hin, \n um sich während des Experiments so wenig wie möglich zu bewegen.\n \n Bereit = Leertaste';
focus = 'Bitte achten Sie auf den Ton, der vom Kopfhörer kommt.  \n \n VERSTANDEN = Leertaste';
condition = 'stranger_match/mis';
begin = 'Drücken Sie die Leertaste, um zu beginnen.';

DrawFormattedText(window,instruction,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,consent,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);


DrawFormattedText(window,message,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,focus,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,begin,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(1);

start = input('Did you mark the start ','s');

% TDT
% if strcmp(sex,'f')
%     TDT.write('gain',2);
% end

TDT.write('RunTime',RUNTIME);
TDT.write('voice_out', y_voice);
[keyIsDown,~,keyCode,~] = KbCheck;
running = 1;

for b = 1:2                                                                 % b: 2 blocks
    if running == 0
        break
    end
    DrawFormattedText(window,begin,'center','center',[0 0 0]);
    Screen('Flip',window);
    KbWait;                 %wait for any key
    WaitSecs(0.5);

    DrawFormattedText(window,' ','center','center',[0 0 0]);
    Screen('Flip',window);
    


for i = 1:number_trial
    if running == 0
        break
    end
    [keyIsDown,~,keyCode,~] = KbCheck;
	if keyIsDown
		if keyCode(27)	%escape button
            running = 0;
		    break
            SCREEN('closeall');
        elseif keyCode(162)
            sca
            disp(i);
            pause
            Screen('Preference', 'SkipSyncTests', 2);
            screenNumber = 1;                                                           %1 is participant screen
            [window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); % draw a window which is a rect [50 50 800 500]
            [mx,my] = RectCenter(rect);
            pause(2)
		end
    end

   % begin acquiring
    TDT.trg(1);
    Screen('TextSize',window, plusSize)
    %psychtoolbox
    DrawFormattedText(window,'+','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(0.5);
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    %tic
    Screen('Flip',window);
    
    % begin acquiring
    % S 32 is voice detection + audio playback onset

    curindex = TDT.read('index');
        
    %disp(['Current buffer index: ' num2str(curindex)]);
    
    % main looping section
    bDone = 0;

        while TDT.read('stop') == 1
            pause(0.1)
        end
    
    curindex = TDT.read('index');
    %disp(['Current buffer index: ' num2str(curindex)]);
    noise = TDT.read('data_out', 'OFFSET', 0, 'SIZE', curindex);            %noise is participant's voice
    %noise_normalized = noise/(max(abs(noise)));

    % save audio
    fileName = sprintf('P%3d_Block_%d_Trial_%d_stranger_Talk_%s_%s.wav',PP_num,b,i,match,datestr(now,'yyyy-mm-dd_HH-MM'));
    cd(pathout)
    save([fileName,'.mat']);
    %audiowrite(fileName,noise_normalized,int32(TDT.FS));

    % voice interval
    v = noise(noise>0.01);
    v = round(length(v)/48828*1000);

    fprintf(1,'Trial %d done',i);
    plot(noise)
    yline(0.4)
    yline(0.1)
    ylim([-0.5 0.5])
    title(sprintf('Block %d Trial %d, voice interval %d ms',b,i,v));
    
    pause(1)


%     reply = input('Do you want more? Y/N [Y]:','s');
%     if isempty(reply)
%         reply = 'Y';
%     end
%     if ~strcmp(reply, 'Y')
%         break
%     end

if b == 1 && i == number_trial
        Screen('TextSize',window, 40);
        DrawFormattedText(window,'PAUSE \n \n Bitte den Fragebogen ausfüllen.','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(2);
        disp('show Fragebogen & mark EEG PAUSE');
        
        Mpause = input('Did you mark the pause ','s');
        if isempty(Mpause)
            Mpause = input('Must input pause','s');
        end
        if strcmp(strtrim(Mpause), 'y')
            sca;
            Stimmwahrnehmung
        end
        
        pause
        % redraw psychtoolbox
                
        [keyIsDown,~,keyCode,~] = KbCheck;
        if keyIsDown
            if keyCode(81)          %check for letter Q keycode
                Screen('Preference', 'SkipSyncTests', 2);
                [window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect
                [mx,my] = RectCenter(rect);
            else
                disp('Press q to continue');
            end
        end
        
        Screen('TextSize',window, 40);
        DrawFormattedText(window,'Es geht weiter','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(2);
        
        DrawFormattedText(window,instruction,'center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);
       
        DrawFormattedText(window,message,'center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);

        DrawFormattedText(window,focus,'center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);

        
        DrawFormattedText(window,'Drücken Sie die Leertaste, um fortzufahren.','center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);

        DrawFormattedText(window,' ','center','center',[0 0 0]);
        Screen('Flip',window); 

        Mpause = input('Did you mark the start ','s');

        pause(2)
        
end

end
end

% stop acquiring
TDT.halt();

% display experiment ended
Screen('TextSize',window, 40);
DrawFormattedText(window,'Dieser Durchgang ist zu Ende.','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);
disp('Mark the end');
Stimmwahrnehmung
close all
sca




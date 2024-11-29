%% Con 3 stranger listen

%% Active Voice Stranger Listen Condition
%% Suong Welp
%% 23.03.2023

close all; clear all; clc;

%% SEX & stimuli

sex = input('Participant sex Male/Female, [m/f] ? ','s');
if isempty(sex)
    sex = input('Must input Participant sex [m/f] ? ','s');
end  
if strcmp(sex, 'f')
    stimulus_path = ['C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\Stimulus\',sex,'\'];
elseif strcmp(sex, 'm')
    stimulus_path = ['C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\Stimulus\',sex,'\'];
else
    error('Please give a valid input [m/f]');
end

cd(stimulus_path)
load('y_voice.mat');
y_voice = [0; y_voice;0];

%% Please define:
number_trial = 50;                                                          % set to 30 or 50 later, depending on exp length

RUNTIME = 3000;   %set runtime value in ms
mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
                                                                
path_to_rcx = [mainpath,'ActiveVoiceTDT_stranger_listen.rcx'];
TDT = TDTRP(path_to_rcx, 'RP2');
plusSize = 200;
pause(0.5)

% only save EEG data


%% Experiment starts

%interfacce
close all
sca
Screen('Preference', 'SkipSyncTests', 2); 
screenNumber = 1;                                                          
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german
consent = 'Ich habe die Instruktionen von diesem Durchlauf des Experiments verstanden. \n \n JA = Leertaste';
instruction = 'Bitte achten Sie auf den Ton \n Sie brauchen nichts zu tun. \n \n JA = Leertaste';
message = 'Setzen Sie sich bequem hin, \n um sich während des Experiments so wenig wie möglich zu bewegen. \n \n Bereit = Leertaste';
begin = 'Drücken Sie die Leertaste, um zu beginnen.';
condition = 'stranger_listen';



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

DrawFormattedText(window,begin,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);


start = input('Did you mark the start ','s');

pause(3)

% TDT
TDT.write('BufferSize',18198);  
[keyIsDown,~,keyCode,~] = KbCheck;
%TDT.write('gain',2);
running = 1;
                                                              % b: 2 blocks
for i = 1:number_trial*2
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
            [window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect [50 50 800 500]
            [mx,my] = RectCenter(rect);
            pause(2)
		end
	end
    
    % start playing
    TDT.write('datain', y_voice);   
                                         
     
    %psychtoolbox
    Screen('TextSize',window, plusSize);
    DrawFormattedText(window,'+','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(0.5);
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    %tic
    Screen('Flip',window);
    
    %eeg trigger HERE (Mark): veridical talk_ "S 2"
    pause(1);

    TDT.trg(1);
    %Screen('TextSize',window, 100);
    curindex = TDT.read('index');
    disp(['Current buffer index: ' num2str(curindex)]);
    disp(num2str(i));

    pause(3)
    
    if i == number_trial
        Screen('TextSize',window, 40);
        DrawFormattedText(window,'PAUSE \n \n Sie können sich entspannen.\n \n Um fortzufahren, bitte die Leertaste drücken','center','center',[0 0 0]);
        Screen('Flip',window);
        Mpause = input('Did you mark the pause ','s');
        if isempty(Mpause)
            Mpause = input('Must input pause','s');
        end
        
        WaitSecs(2);
        KbWait;     %wait for any key
%         disp('show Fragebogen & mark EEG PAUSE');
        
        
%         if strcmp(strtrim(Mpause), 'y')
%             sca;
%             Stimmwahrnehmung
%         end
        
        pause
        % redraw psychtoolbox
                
%         [keyIsDown,~,keyCode,~] = KbCheck;
%         if keyIsDown
%             if keyCode(81)          %check for letter Q keycode
%                 Screen('Preference', 'SkipSyncTests', 2);
%                 [window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect
%                 [mx,my] = RectCenter(rect);
%             else
%                 disp('Press q to continue');
%             end
%         end
        
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

% stop acquiring
TDT.halt();

% display experiment ended
Screen('TextSize',window, 40);
DrawFormattedText(window,'Dieser Durchgang ist zu Ende.','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);
disp('Mark the end');
close all
sca

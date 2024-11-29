%% Active Voice Stranger Listen Condition
%% Suong Welp
%% 10.03.2023

close all; clear all; clc;

% cut only voice part out of the recorded audios
% play it back
PP_num = input('Participant number (iii)? ');
audio_path = 'C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\';

%% Praat done?
praat = input('Did you run praat sounding extraction, [y/n] ? ','s');
if strcmp(praat, 'y')
    stimulus_path = fullfile(audio_path,['P',num2str(PP_num)],'Stimulus','Clean');   %update path file
elseif strcmp(sex, 'n')
    disp('Please run praat first')
else
    error('Stop and run praat');
end

%% Please define:
number_trial = 50;                                                          % set to 30 or 50 later, depending on exp length

RUNTIME = 4000;   %set runtime value in ms
mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
                                                                
path_to_rcx = [mainpath,'ActiveVoiceTDT_veridical_listen.rcx'];
TDT = TDTRP(path_to_rcx, 'RP2');
plusSize = 200;
pause(0.5)

% only save EEG data

%% Read veridical audio
FILES      = dir( fullfile(stimulus_path, '*.wav') );
FILES      = cellfun(@(x) x,{FILES.name},'UniformOutput',false);

a= 1;
bad = [];
for i = 1: length(FILES)
    stimulus_voice =  [stimulus_path,'\',FILES{i}];
    tempt = audioread(stimulus_voice);
    if length(tempt) <= 80000;
        y_voice{a} = tempt;
        lengthBuff(a) = length(y_voice{a});
        a= a+1;
    else
        bad = [bad, FILES{i}];
    end

end

if a < number_trial*2
    for j = a:number_trial*2
        y_voice{j} = y_voice{a-1};
    end
end

maxBuff = max(lengthBuff);

for i = 1:number_trial*2
    if length(y_voice{1,i}) < 80000
        y_voice{1,i}(end+1:80000) = 0;
    end
    y_voice{1,i} = [0;y_voice{1,i}];
end

%y_voice = repmat(veridical_playback,1,10);


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
WaitSecs(1);

start = input('Did you mark the start ','s');
WaitSecs(2);


% TDT
TDT.write('BufferSize',80000);
%TDT.write('gain',2);
[keyIsDown,~,keyCode,~] = KbCheck;
running = 1;


                                                              
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
    TDT.write('datain', y_voice{1,i});   
                                         
     
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
    Screen('TextSize',window, plusSize)
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


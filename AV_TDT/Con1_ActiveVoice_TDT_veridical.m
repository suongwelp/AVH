%% Active Voice Veridical Talk Condition
%% Suong Welp, Mark Hanus
%% 10.03.2023

close all; clear all; clc;

%% Please define:
number_trial = 50;                                                          % set to 30 or 50 later, depending on exp length
PP_num = input('Participant number (iii)? ');
mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
RUNTIME = 3000;                                                              % set runtime value in ms (originally: 3000)
path_to_rcx = [mainpath,'ActiveVoiceTDT_veridical.rcx'];
plusSize = 200;

% Path for saving audio data
path_audio = 'C:\Users\statistics\Documents\Suong_N1\2. Data\Audio\';          % save recorded audio
if ~exist(fullfile(path_audio,['P',num2str(PP_num)]),'dir')
       mkdir(path_audio,['P',num2str(PP_num),'\']);
end

if ~exist(fullfile(path_audio,'P',num2str(PP_num),'Veridical'),'dir')
       mkdir(path_audio,['P',num2str(PP_num),'\Veridical\']);
end

pathout = [path_audio,'P',num2str(PP_num),'\Veridical\'];

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
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect [50 50 800 500]
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german
consent = 'Ich habe die Instruktionen von diesem Durchlauf des Experiments verstanden. \n \n JA = Leertaste';
instruction = 'Bitte kurz /ah/ sagen, nachdem das Plus auf dem Bildschirm verschwunden ist.\n \n JA = Leertaste';
message = 'Setzen Sie sich bequem hin, \n um sich während des Experiments so wenig wie möglich zu bewegen.\n \n Bereit = Leertaste';
focus = 'Bitte achten Sie auf den Ton, der vom Kopfhörer kommt.  \n \n VERSTANDEN = Leertaste';
condition = 'veridical_talk';
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

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);



start = input('Did you mark the start ','s');
WaitSecs(2);


%TDT
TDT.write('RunTime',RUNTIME);
TDT.write('gain',1.5);
[keyIsDown,~,keyCode,~] = KbCheck;
running = 1;


for b = 1:2                                                                 % b: 2 blocks
    
    if running == 0
        break
    end

    DrawFormattedText(window,begin,'center','center',[0 0 0]);
    Screen('Flip',window);
    KbWait;
    
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    Screen('Flip',window);
    

    
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
    
    %disp(['Current buffer index: ' num2str(curindex)]); %to check buffer
    %point
 
    
    % main looping section (TDT)
    bDone = 0;

        while TDT.read('stop') == 1
            pause(0.1)
        end
    
    curindex = TDT.read('index'); 
    
    noise = TDT.read('data_out', 'OFFSET', 0, 'SIZE', curindex);            %noise is participant voice
    %noise_normalized = noise/(max(abs(noise)));
    %curLoudness(b,i) = max(noise_normalized);
    %disp(['Current loudness is ', num2str(max(noise_normalized))]);

    % save audio
    fileName = sprintf('P%3d_Block_%d_Trial_%d_veridical_Talk_%s.wav',PP_num,b,i,datestr(now,'yyyy-mm-dd_HH-MM'));
    cd(pathout)
    save([fileName,'.mat']);
    %audiowrite(fileName,noise,int32(TDT.FS));  
    
    v = noise(noise>0.01);
    v = round(length(v)/48828*1000);

    fprintf(1,'Trial %d done',i);
    plot(noise)
    yline(0.4)
    yline(0.1)
    ylim([-0.5 0.5])
    title(sprintf('Block %d Trial %d, voice interval %d ms',b,i,v));
    
    pause(0.5)

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
DrawFormattedText(window,'Dieser Durchgang ist zu Ende. Bitte den Fragebogen ausfüllen. ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);

disp('Mark the end');
Stimmwahrnehmung
close all
sca

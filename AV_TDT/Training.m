%% Training

%% Suong Welp
%% 23.03.2023

close all; clear all; clc;


%% Please define:
number_trial = 10;                                                          % set to 30 or 50 later, depending on exp length


mainpath = 'C:\Users\statistics\Documents\Suong_N1\1. Experiment\';
                                                                

%% Experiment starts

%interfacce
close all
sca
Screen('Preference', 'SkipSyncTests', 2); 
screenNumber = 1;                                                          
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect
[mx,my] = RectCenter(rect);

                                                                            %change all these messages to german
consent = 'Ich habe die Instruktionen von diesem Durchlauf des Experiments verstanden. \n \n JA = Leertaste';
instruction = 'Bitte achten Sie auf den Ton \n Sie brauchen nichts zu tun. \n \n JA = Leertaste';
message = 'Setzen Sie sich bequem hin, \n um sich während des Experiments so wenig wie möglich zu bewegen. \n \n Bereit = Leertaste';
begin = 'Drücken Sie die Leertaste, um zu beginnen.';
condition = 'stranger_listen';


DrawFormattedText(window,consent,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key 
WaitSecs(0.5);

DrawFormattedText(window,instruction,'center','center',[0 0 0]);
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


[keyIsDown,~,keyCode,~] = KbCheck;
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
		end
    end
                                         
     
    %psychtoolbox
    DrawFormattedText(window,'+','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(0.5);
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    %tic
    Screen('Flip',window);


    pause(3)
    
    if i == number_trial
        DrawFormattedText(window,'PAUSE \n \n Bitte den Fragebogen ausfüllen.','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(2);
        disp('show Fragebogen');
        
        sca

        % Stimmwahrnehmung Fragebogen
        
        Stimmwahrnehmung

        % redraw psychtoolbox
        pause

        Screen('Preference', 'SkipSyncTests', 2);                                                       
        [window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect
        [mx,my] = RectCenter(rect);

        DrawFormattedText(window,'Es geht weiter','center','center',[0 0 0]);
        Screen('Flip',window);
        WaitSecs(3);

        DrawFormattedText(window,message,'center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);

        DrawFormattedText(window,'Drücken Sie irgendeinen Knopf, um fortzufahren.','center','center',[0 0 0]);
        Screen('Flip',window);
        KbWait;     %wait for any key
        WaitSecs(0.5);
    end
end

 
% display experiment ended
DrawFormattedText(window,'Dieser Training ist zu Ende.','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);
close all
sca


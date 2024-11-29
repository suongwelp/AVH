  %% EEG Baseline recording
%% Suong Welp
%% 08.05.2023

close all; clear all; clc;

close all
sca

Screen('Preference', 'SkipSyncTests', 2); 

screenNumber = 1;                                                           %1 is participant screen
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect [50 50 800 500]
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german
instruction = 'Bitte still sitzen für 5 Minuten. \n \n Die Augen dabei nicht zumachen. \n \n BEREIT = Leertaste';

DrawFormattedText(window,instruction,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(300);

% finish
Screen('TextSize',window, 40);
DrawFormattedText(window,'Diese Baseline-Aufnahme ist zu Ende. \n \n Vielen Dank! ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(1);

close all
sca
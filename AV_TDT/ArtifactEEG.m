%% Artifacts /ah/ and /bi/
%% Suong Welp
%% 08.05.2023

close all; clear all; clc;

instructionAh = 'Bitte öffnen Sie den Mund als würden Sie /ah/ sagen, \n \n so wie in den vorherigen Durchläufen, ohne dabei einen Laut von sich zu geben. \n \n Wenn Sie Fragen haben, bitte an Versuchsleiter wenden.\n \n BEREIT = Leertaste';
instructionBi = 'Bitte bewegen Sie den Mund als würden Sie /bi/ sagen, \n \n so wie in den vorherigen Durchläufen, ohne dabei einen Laut von sich zu geben. \n \n Wenn Sie Fragen haben, bitte an Versuchsleiter wenden.\n \n BEREIT = Leertaste';

artifact = input('/ah/ or /bi/? [a/b]? ', 's');

if strcmp(strtrim(artifact),'a')
    instruction = instructionAh;
else
    instruction = instructionBi;
end

number_trial = 30;
plusSize = 200;

sca

Screen('Preference', 'SkipSyncTests', 2); 

screenNumber = 1;                                                           %1 is participant screen
[window,rect] = Screen('OpenWindow',screenNumber, [169,169,169]); %draw a window which is a rect [50 50 800 500]
[mx,my] = RectCenter(rect);
Screen('TextSize',window, 40);
                                                                            %change all these messages to german

DrawFormattedText(window,'Sie haben fast geschafft, wir messen kurz noch die Muskel-Aktivität.','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(3);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(0.5);

%% /ah/
DrawFormattedText(window,instruction,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(0.5);
Screen('TextSize',window, plusSize);

for i = 1:number_trial
    pause(0.5)
    DrawFormattedText(window,'+','center','center',[0 0 0]);
    Screen('Flip',window);
    WaitSecs(0.5);                                                           % deduct this from reaction time
    DrawFormattedText(window,' ','center','center',[0 0 0]);
    %tic
    Screen('Flip',window);
    WaitSecs(2);
end

Screen('TextSize',window, 40);
DrawFormattedText(window,'Danke','center','center',[0 0 0]);
Screen('Flip',window);
WaitSecs(2);

close all
sca
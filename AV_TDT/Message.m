%% Message to participant

%% Write message

louder = 'Können Sie bitte Lauter sprechen? \n \n OKAY = Leertaste'


%% Send message
DrawFormattedText(window,louder,'center','center',[0 0 0]);
Screen('Flip',window);
KbWait;     %wait for any key
WaitSecs(0.5);

DrawFormattedText(window,' ','center','center',[0 0 0]);
Screen('Flip',window);
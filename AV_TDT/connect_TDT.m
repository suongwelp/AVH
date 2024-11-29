function RP=connect_TDT(path_to_rcx)
    RP=actxserver('RPco.x');
    RP.ConnectRP2('GB',1);
    clear_result = RP.ClearCOF;
    if clear_result == 0
        fprintf(1,'\nError clearing circuit');
    end
    RP.LoadCOF(path_to_rcx);
    RP.Run;
    status=double(RP.GetStatus);
    fprintf(1,'\n')
    if bitget(status,1) == 0
        fprintf(1,'Error connecting to RP2\n'); return;
    elseif bitget(status,2) == 0
        fprintf(1,'\Error loading circuit\n'); return;
    elseif bitget(status,3) == 0
        fprintf(1,' Error running circuit\n'); return;
    else
        fprintf(1,'Circuit loaded and running\n'); return;
    end
end
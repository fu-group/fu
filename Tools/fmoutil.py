#!/bin/sh

def exec_fmoutil():
    # fmoutil is a external program
    prgnam='futools.exe'
    prg='fmoutil.exe'
    exedir=lib.GetExeDir(prgnam)
    prg=os.path.join(exedir,prg)
    #
    time1=time.clock()
    os.system(prg)
    time2=time.clock(); etime=time2-time1
    futoolslib.MessJobEnd(prgnam,etime)
    
exec_fmoutil()
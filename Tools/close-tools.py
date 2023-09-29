#!/bin/sh
# -*- coding: utf-8

def SaveLogFile(closesession):
    logfile=''
    if closesession:
        print('---  closing futools session ---\n')
        prmpt='do you want to save log of this session? 1:yes, 2:no.'
        savopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)            
        if savopt == 1:
            endmess='### futools session ended at '+lib.DateTimeText()+'\n'
            futoolslib.TMPLOGDEV.write(endmess)
        else: return savopt,logfile
    #
    prmpt='logfile to save (full path).'
    logfile=futoolslib.ConsoleInputOfOutputFileName(prmpt,False)    
    if len(logfile) > 0:
        if os.path.isfile(logfile):
            futoolslib.TMPLOGDEV.close()
            f=open(futoolslib.TMPLOGFILE,'r'); buf2=f.read(); f.close()
            f=open(logfile,'r'); buf1=f.read(); f.close()
            f=open(logfile,'w'); f.write(buf1+buf2); f.close()
        else:
            futoolslib.TMPLOGDEV.close()
            shutil.copy(futoolslib.TMPLOGFILE,logfile)
        print(('log was saved in '+logfile))
    else:
        print('no file name. skipped to save log file.')
        #logdev=open(TMPLOGFILE,'a')
        #TMPLOGDEV=logdev
    return savopt,logfile

if not futoolslib.QUIT:
    futoolslib.QUIT=True
    savopt,logfile=SaveLogFile(True)
    mess='futools session ended. '
    if savopt == 1: print((mess+'log was saved in '+logfile))
    else: print((mess+'log was not saved.'))
    logdev=futoolslib.TMPLOGDEV
    tmplogfile=futools.TMPLOGFILE
    try: logdev.close()
    except: pass
    try: os.remove(tmplogfile)
    except: print('failed to delete tmplogfile.')


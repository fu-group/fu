#!/bin/sh
# -*- coding: utf-8

def make_filelst_file():
    # arguments: idir='directory name',iexr='extension'('.pdb'),ofile='filename'
    # cmd='quit',char='#'
    # program name
    prgnam='make_filelst_file'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        indir=futoolslib.GetSysArgs('idir')
        if not indir:
            # read directory name
            indir=futoolslib.ConsoleInputOfDirectoryName('',False)
            if indir == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        inext=futoolslib.GetSysArgs('iext')
        if not inext:
            inext=futoolslib.ConsoleInputOfStringData('input file extension, i.e. .pdb,...')
        prichar=''
        chartxt="'','@','!','$','%'" # # is used for comment
        prichar=futoolslib.GetSysArgs('char')
        if not prichar:
            prmpt='input priority character at the end of base name, '+chartxt #+'\n'
            #prmpt=prmpt+'in form "$" or ["","$",...] or {} '
            prichar=futoolslib.ConsoleInputOfStringData(prmpt)[0]             
        #srtopt=futoolslib.GetSysArgs('srtopt')
        #if not srtopt:
        #    prmpt='do you want to sort file names? 1:yes, 2:no.'
        #    jobopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)            
        srtopt=1
        outfile=futoolslib.GetSysArgs('outfile')
        if not outfile:
            prmpt='filelst-file '
            outfile=futoolslib.ConsoleInputOfOutputFileName(prmpt,True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        filelst=lib.GetFilesInDirectory(indir,inext)
        if prichar != '':
            sortopt=False
            if srtopt == 1: sortopt=True
            filelst=futoolslib.PickUpFilesWithSpecialChar(filelst,prichar,sortopt)
        futoolslib.WriteFilelstFile(outfile,filelst)
        #
        print((outfile+' file is created.'))
        print(('number of files: ',len(filelst)))
        if srtopt == 1:  print('files are sorted.')
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        # end message
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)
make_filelst_file()

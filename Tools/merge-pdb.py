#!/bin/sh
# -*- coding: utf-8

def merge_pdb():
    # arguments:lstfile='filename', 'outopt'=1(pdb,2(xyz),
    # frgopt=1(no),2(yes),frgfilopt=1(dir),2(file),frgdatfilesfile='filename'
    # teropt=1(with),2(without ter)(outopt=1), frgfile='output frg file name'
    # program name
    prgnam='merge_pdb'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        filelst=futoolslib.GetSysArgs('pdbfile')
        if not filelst:
            prmpt='input pdb files to be merged. i.e. "file1,.." or "< file-lst file" (do not type quotes)'
            filelst=futoolslib.ConsoleInputOfStringData(prmpt)
            err,filelst=futoolslib.GetFileNamesInInputString(filelst)
            if err:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        npdb=futoolslib.CountFilesInFileLst(filelst,'.pdb')
        if npdb <= 0:
            print('no pdb file is given. quit the job.')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        outfile=futoolslib.GetSysArgs('ofile')
        if not outfile:
            outfile=futoolslib.ConsoleInputOfOutputFileName('output pdb file(full path)',True)
        if outfile == '':
            print('output file name is null. quit the job.')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        molnam=lib.MakeMolNamFromFileName(outfile)
        #    if frgopt == 1:
        teropt=2
        #teropt=futoolslib.GetSysArgs('teropt')
        #if not teropt: teropt=futoolslib.InputTEROption()
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        pdbatm,pdbcon=futoolslib.MergePdbFiles(filelst,teropt)
        #
        natm=len(pdbatm)
        print(('total number of atoms',natm))
        mark='REMARK '
        comment=mark+'created by '+prgnam+' at '+lib.DateTimeText()+'\n'
        comment=comment+mark+'merged pdb files:\n'
        for fil in filelst: comment=comment+mark+fil+'\n'
        comment=comment[:-1]
        rwfile.WritePDBAtom(outfile,pdbatm,pdbcon,comment)
        #-----------
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

merge_pdb()

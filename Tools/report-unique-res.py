#!/bin/sh
# -*- coding: utf-8

def report_unique_res():
    # arguments: ipdb='filename.pdb',kndopt=1 2,or 3,cmd='quit'
    # uniopt=1:unique,2:all
    # program name
    prgnam='report-unique-res'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        # read PDB file name
        filename=futoolslib.GetSysArgs('ipdb')
        if not filename:                
            filename=futoolslib.ConsoleInputOfFileName('input PDB data',True)
            if filename == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=filename
        #
        kndopt=futoolslib.GetSysArgs('kndopt')
        if not kndopt:
            prmpt='enter 1:AA, 2:Non-AA, or 3:all kind residues'
            kndopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        txt=['AA','Non-AA','all kind']
        print(('report residues:',txt[kndopt-1]+' residues'))            
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        pdbatm,pdbcon=rwfile.ReadPDBAtom(filename)
        #
        reslst=futoolslib.MakeUniqueResList(pdbatm,kndopt)
        nres=0
        for res, nmb in reslst: nres += nmb
        #
        print(('number of total and unique residues',nres,len(reslst)))
        print(('residue list',reslst))
        
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        # end message
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

report_unique_res()

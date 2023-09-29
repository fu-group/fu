#!/bin/sh
# -*- coding: utf-8

def set_chain_name():
    # arguments: ipdb='filename',reffile='filename',
    # opdb, logopt
    #program name
    prgnam='set_chain_name'    
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        trgfile=futoolslib.GetSysArgs('ipdb')
        if not trgfile:
            # read PDB file name
            trgfile=futoolslib.ConsoleInputOfFileName('target pdb file',True)
            if trgfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=trgfile
        reffile=futoolslib.GetSysArgs('reffile')
        if not reffile:
            reffile=futoolslib.ConsoleInputOfFileName('reference pdb file',True)
            if reffile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        outfile=futoolslib.GetSysArgs('opdb')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('output PDB file',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        # read base name of created PDB files
        #print 'base name of created files=',base
        logopt=futoolslib.GetSysArgs('logopt')
        if not logopt:
            prmpt='Do you want to output log file? 1:no, 2:yes'
            logopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        #
        #if logopt == 2:
        #    logfile=toolslib.ConsoleInputOfFileName(True,'of log file')
        base=os.path.basename(outfile)
        base=os.path.splitext(base)[0]
        logfile=outfile.replace('.pdb','.log')
        #
        print('this job may take several minutes for 100,000 atomic system.')
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        trgatm,trgcon=fumole.fuMole.ReadPDBAtom(trgfile)
        refatm,refcon=fumole.fuMole.ReadPDBAtom(reffile)
        # make atom order dic of amino acid residues
        trgamiresdic=futoolslib.MakeAmiResAtomOrderDic(trgatm)
        refamiresdic=futoolslib.MakeAmiResAtomOrderDic(refatm)
        #
        trgresdic=futoolslib.MakeResAtmDic(trgatm,False)
        refresdic=futoolslib.MakeResAtmDic(refatm,False)
        #
        trgatm,matchlst,missinglst=futoolslib.FindChainName(trgatm,refatm,trgresdic,refresdic,trgamiresdic,refamiresdic)
        #print 'matchlst',matchlst
        #print 'missinglst',missinglst
        trgatm=futoolslib.SetChainName(trgatm,matchlst)
        comment='REMARK created by '+prgnam+' at '+lib.DateTimeText()+'\n' 
        comment=comment+'REMARK reference pdb file='+reffile
        fumole.fuMole.WritePDBAtom(outfile,trgatm,trgcon,comment)
        print(('number of assigned/total residues= '+str(len(matchlst))+'/'+str(len(trgresdic))))
        #
        if logopt == 2:
            comment='# created by set-chain.py at '+lib.DateTimeText()+'\n'
            comment=comment+'# traget pdb file='+trgfile+'\n'
            comment=comment+'# reference pdb file='+reffile
            futoolslib.WriteSetChainLog(logfile,matchlst,missinglst,comment)
            print(('log file is created',logfile))
        #
        time2=time.clock(); etime=time2-time2
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)
set_chain_name()


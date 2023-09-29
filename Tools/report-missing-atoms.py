#!/bin/sh
# -*- coding: utf-8

def report_missing_atoms():
    """
    # args:
    # jobopt=(1:non-aa residues,2:aa-residues),
    # ipdb='input pdb file name',
    # mhtfile='mht files-lst file'(in case of mhtopt=2)
    # logopt=(1:create log, 2:do not),
    """
    # program name
    prgnam='report_missing_atoms'

    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        jobopt=-1; pdbfile=''; outfile=''; logopt=-1; logfile=''
        jobopttxt=['non-aa residues','aa-residues']
        #
        jobopt=futoolslib.GetSysArgs('jobopt')
        if not jobopt:
            # job option
            prmpt='select job option. 1:non-aa residues, 2:aa-residues.'
            jobopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        #
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file(.pdb)',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        # frame file
        if jobopt == 1:
            frmfilelst=[]
            #frmopt=futoolslib.GetSysArgs('frmopt')
            frmfile=futoolslib.GetSysArgs('frmfile')
            if not frmfile: #frmfilelst=futoolslib.ReadMhtLstFile(frmfile)
                prmpt='input frame file(s). i.e. "file1,.." or "< file-lst file" (do not type quotes)'
                frmfilelst=futoolslib.ConsoleInputOfStringData(prmpt)
                err,frmfilelst=futoolslib.GetFileNamesInInputString(frmfilelst)
                if err:
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            nfrm=futoolslib.CountFilesInFileLst(frmfilelst,'.frm')
            #for fil in frmfilelst:
            #    base,ext=os.path.splitext(fil)
            #    if ext == '.frm': nfrmfile += 1
            if nfrm <= 0:
                print('no frame file is given. quit the job.')
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            #logopt=1
        logopt=futoolslib.GetSysArgs('logopt')
        if not logopt:
            prmpt="do you want to output in log file? 1:yes, 2:no"
            logopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        logfile=pdbfile.replace('.pdb','.log')
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        # write session log
        battxt=futoolslib.BatchText(prgnam,jobopt,pdbfile,outfile,logopt,logfile,'quit')
        addtxt=''
        """
        if filopt == 1:
        for fil in frmfilelst:
            addtxt=addtxt+",frmopt="+str(frmopt)
            addtxt=addtxt+",frmfile='"+fil+"'"
            if len(addtxt) > 0: battxt=futoolslib.BatchTextAppend(battxt,addtxt)
        """
        futoolslib.WriteSessionLog(battxt)
        # read base name of created PDB file
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        #
        print(('jobopt: ',jobopttxt[jobopt-1]))
        if jobopt == 1:
            misatmdic=futoolslib.MissingChmResAtomDic(pdbatm,frmfilelst)
        else: misatmdic=futoolslib.MissingAAResAtomDic(pdbatm)
        #
        mislst=list(misatmdic.keys())
        nmisatm=0
        print(('report missing atoms of '+pdbfile))
        for res in mislst: nmisatm += len(misatmdic[res])
        if nmisatm <= 0:
            print('no missing atom was found (checked heavy atom only)')
        else:
            print('missing atoms: resnam, number of missing atoms and atmnam list (heavy atom only)')
            for res in mislst:
                if len(misatmdic[res]) <= 0:
                    print((res+' 0'))
                else:    
                    print((res+', '+str(len(misatmdic[res]))+',',misatmdic[res])) 
                    futoolslib.SELECTRES.append(res)
        #
        if logopt == 1:
            comment='[input pdb file] '+pdbfile
            futoolslib.WriteMissingAtomLog(logfile,comment,frmfilelst,mislst,misatmdic)
        #-----
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

report_missing_atoms()


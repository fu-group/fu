#!/bin/sh
# -*- coding: utf-8

def replace_res():
    # relace residues in traget mol with those in resfile.
    # arguments: ipdb,opdb,resfile=['resfile1,resfile2,...}
    # program name
    prgnam='replace_res'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:            
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input target pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        filelst=futoolslib.GetSysArgs('respdb')
        if not filelst:
            # read PDB file name
            filelst=futoolslib.ConsoleInputOfStringData('input residue pdb file(s)')
            if len(filelst) <= 0:
                print('input null. quit the job.')
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            resfile='console'  
            if filelst[0][:1] == '<':
                if len(filelst) == 1: file=filelst[0][1:]
                else: file=filelst[1]
                file=file.strip()
                if not os.path.isfile(file):
                    print((file+' file not found. job quit.'))
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
                else: filelst=futoolslib.ReadFileNamesInFile(file)
                resfile=file
            if len(filelst) <= 0:
                    print('no resdiue pdb files to be replaced. quit the job.')
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        envopt=futoolslib.GetSysArgs('envopt')
        for fil in filelst:
            if fil.rfind('-e') >= 0:
                env=True; envopt=1
            else: env=False; envopt=2
        if not envopt and env:
            envopt=futoolslib.ConsoleInputOfIntegerOption('remove environment residues? 1:yes, 2:no',1,2,1)                 
        #
        outfile=futoolslib.GetSysArgs('opdb')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('output pdb files',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        #
        base=os.path.basename(pdbfile)
        base=os.path.splitext(base)[0]
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        pdbatm,reslst=futoolslib.ReplaceRes(pdbatm,filelst,envopt)
        nter=0
        #if len(pdbcon) > 0:
        #    pdbcon=[]
        #    nter,pdbatm=futoolslib.DeleteTER(pdbatm)
        # write pdb file
        pdbatm=futoolslib.RenumberAtmNmbInPdbAtm(pdbatm)
        if len(pdbcon) > 0:
            pdbcon=futoolslib.MakePdbCon(pdbatm)
        #    if nter > 0: print str(nter)+' TER(s) were deleted.'
            print('note: connect data were recreated based on distance.')
        comment='REMARK created by '+prgnam+' at '+lib.DateTimeText()+'\n'
        comment=comment+'REMARK parent pdb file='+pdbfile+'\n'
        if len(filelst) > 0:
            for fil in filelst:
                comment=comment+'REMARK replaced residues: '+fil+'\n'
        if len(reslst) > 0:
            comment=comment+'REMARK number of replaced resdiues='+str(len(reslst))+'\n'
        comment=comment[:-1]    
        #
        if len(filelst) == 1: futoolslib.SELECTRES=reslst
        rwfile.WritePDBAtom(outfile,pdbatm,pdbcon,comment)
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

replace_res()


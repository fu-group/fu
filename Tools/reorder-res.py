#!/bin/sh
# -*- coding: utf-8

def reorder_res():
    # arguments: jobopt=1(reorder),2(make res sequentila file)
    # ipdb,opdb(jobopt=1)
    # program name
    prgnam='reorder_res'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        jobopt=futoolslib.GetSysArgs('jobopt')
        if not jobopt:
            # option
            prmpt='select job options. 1:reooder resdiues, 2:make residue sequential file.'
            jobopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read fuPDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file(.pdb)',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        # sequential file    
        if jobopt == 1:
            seqfile=futoolslib.GetSysArgs('seqfile')
            if not seqfile:
                seqfile=futoolslib.ConsoleInputOfFileName('residue sequential data(.seq)',True)
                if seqfile == '':
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            outfile=futoolslib.GetSysArgs('opdb')
            if not outfile:
                outfile=futoolslib.ConsoleInputOfOutputFileName('reordered pdb data',True)
                if outfile == '':
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            futoolslib.OUTPUTPDBFILE=outfile
        #base,ext=os.path.split(filename)
        base=os.path.basename(pdbfile)
        base=os.path.splitext(base)[0]
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        reslst,resdic=futoolslib.MakeResAtmDicInRes(pdbatm,'')
        watlst=futoolslib.ListWatRes(reslst)
        #
        if jobopt == 1:
            resseq=futoolslib.ReadResSeq(seqfile)
            watatend=False
            if len(resseq) != len(reslst):
                if len(reslst) == len(resseq)+len(watlst):
                    watatend=True; print('waters will be put at the end.')
                    resseq=reslst
                else:
                    print(('error: number of residues are different in pdb and seq file, ',len(reslst),len(resseq)))
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            pdbatm=futoolslib.ReorderRes(pdbatm,resseq,resdic,watatend)
            comment='REMARK created by '+prgnam+' at '+lib.DateTimeText()+'\n'
            comment=comment+'REMARK parent pdb file='+pdbfile
            pdbatm=futoolslib.RenumberAtmNmbInPdbAtm(pdbatm)
            fumole.fuMole.WritePDBAtom(outfile,pdbatm,[],comment)
        else:
            seqfile=pdbfile.replace('.pdb','.seq')
            comment='# created by '+prgnam+' at '+lib.DateTimeText()+'\n'
            comment=comment+'# input pdbfile='+pdbfile
            futoolslib.WriteResSeq(seqfile,reslst,comment)
            print(('residue sequential data file is created',seqfile))
        #
        print(('numbers of residues and atoms(include TER)=',len(reslst),len(pdbatm)))
        print(('number of water(WAT,HOH) or solvent(SOL) residues=',len(watlst)))
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)

        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

reorder_res()

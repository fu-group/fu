#!/bin/sh
# -*- coding: utf-8

def extract_res():
    # arguments: ipdb,opdb,cmd,reslst=['resname'('ALA:1:a'),...}
    #  jobopt=1(res),2(res with env), rcut=x (if jobopt=2)
    # program name
    prgnam='extract_res'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:            
        reslst=futoolslib.GetSysArgs('reslst')
        if not reslst:
            # read res
            prmpt='input resdiue data in full form, like "ALA:1:A"(do not type quotes)'
            reslst=futoolslib.ConsoleInputOfStringData(prmpt)
            if len(reslst) <= 0:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        # chack input resdat
        ans=lib.CheckResDatForm(reslst,True)
        corereslst=[]
        for res in reslst: corereslst.append(res)

        envopt=futoolslib.GetSysArgs('envopt')
        if not envopt:
            prmpt='with environment? 1:no, 2:yes, 3:quit'
            envopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        if envopt == 3:
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        rcut=-1.0
        if envopt == 2:
            rcut=futoolslib.GetArgs(args,'rcut')
            if not rcut:
                prmpt='input cut-off distance(A) of environment.'
                rcut=futoolslib.ConsoleInputOfStringData(prmpt)[0]
                try: rcut=float(rcut)
                except:
                    print('error (extract_res): input error in rcut. it should be a number.')
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        if not ans: 
            print('error (extract_res): input error in residue data. it should be in full form, i.e. ALA:1:A')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        pdbfile=futoolslib.GetArgs(args,'ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outfile=futoolslib.GetArgs(args,'opdb')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('output pdb files',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        # read base name of created PDB files
        #base,ext=os.path.split(filename)
        base=os.path.basename(pdbfile)
        base=os.path.splitext(base)[0]
        #print 'base name of created files=',base
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        nearreslst=[]
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        pdbatm,corereslst,nearreslst=futoolslib.ExtractResWithEnv(pdbatm,corereslst,rcut)
        print(('extracted residues: ',corereslst))
        if len(pdbatm) <= 0:
            print('no extracted atoms. quit the job.')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        if envopt == 2:
            print(('cut off distance of environmental resiue=',rcut))
            print(('emvironmental residues: ',nearreslst))
        print(('number of atoms in extracted residue=',len(pdbatm)))
        #
        pdbatm=futoolslib.RenumberAtmNmbInPdbAtm(pdbatm)
        comment='REMARK created by '+prgnam+'at '+lib.DateTimeText()+'\n'
        comment=comment+'REMARK parent pdb file='+pdbfile+'\n'
        if rcut > 0:
            comment=comment+'REMARK environment residues are with rcut='+('%6.2f' % rcut)+'\n'
            comment=comment+'REMARK core residues are:\n'
            for res in corereslst:
                comment=comment+'REMARK '+res+'\n'
        comment=comment[:-1]    
        futoolslib.SELECTRES=corereslst
        fumole.fuMole.WritePDBAtom(outfile,pdbatm,[],comment)

        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

extract_res()


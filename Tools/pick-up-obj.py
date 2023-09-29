#!/bin/sh
# -*- coding: utf-8

def pick_up_obj():
    # arguments: ipdb,opdb,cmd,reslst=['resname'('ALA:1:a'),...}
    #  jobopt=1(res),2(res with env), rcut=x (if jobopt=2)
    # program name
    prgnam='pick_up_obj'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        objnam=futoolslib.GetSysArgs('objnam')
        if not objnam:
            # read res
            prmpt='input object name, i.e. "ALA", "chm", "pro"(do not type quotes).'
            objlst=futoolslib.ConsoleInputOfStringData(prmpt)
            if len(objlst) <= 0:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        if objlst[0] == 'chm': objopt=2
        elif objlst[0] == 'pro': objopt=3
        elif objlst[0] == 'unique': objopt=4 # not debug yet. 07May2014
        else: objopt=1
        envopt=futoolslib.GetSysArgs('envopt')
        if not envopt:
            prmpt='with environment? 1:no, 2: yes, 3:quit'
            envopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        if envopt == 3:
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        rcut=-1.0
        if envopt == 2:
            rcut=futoolslib.GetSysArgs('rcut')
            if not rcut:
                prmpt='input cut-off distance(in A) of environment.'
                rcut=futoolslib.ConsoleInputOfStringData(prmpt)[0]
                try: rcut=float(rcut)
                except:
                    print(('error ('+prgnam+'): input error in rcut. it should be a number.'))
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outdir=futoolslib.GetSysArgs('odir')
        if not outdir:
            # read output directory name    
            outdir=futoolslib.outdir=futoolslib.ConsoleInputOfDirectoryName('of output PDB files',True)
            if outdir == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.PDBDIR=outdir
        # read base name of created PDB files
        #base,ext=os.path.split(filename)
        base=os.path.basename(pdbfile)
        base=os.path.splitext(base)[0]
        #print 'base name of created files=',base
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        filelst=[]
        nearreslst=[]
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        if objopt == 1: # residue
            resnam=objlst[0]
            reslst=futoolslib.MakeResLst(pdbatm,resnam,rcut)
        if objopt == 2: # non-aa residues
            reslst=futoolslib.MakeChmResLst(pdbatm,rcut)
        if objopt == 3: #polypeptide chain
            chainlst,reslst=futoolslib.MakeProResLst(pdbatm,rcut)
        if objopt == 4: # unique residues
            res='*:*:*'
            filelst,reslst=futoolslib.PickUpUniqueRes(res,pdbatm,outdir,base)
        #hislst=futoolslib.MakeHisResLst(pdbatm)
        print(('reslst',reslst))
        for i in range(len(reslst)):
            lst=reslst[i]
            respdbatm,corereslst,nearreslst=futoolslib.ExtractResWithEnv(pdbatm,lst,rcut)
            print(('picked-up residue(s) : ',lst))
            if len(respdbatm) <= 0:
                print('no picked-up atoms. skip.')
            print(('number of atoms in picked-up residue=',len(respdbatm)))
            #
            respdbatm=futoolslib.RenumberAtmNmbInPdbAtm(respdbatm)
            comment='REMARK created by '+prgnam+'at '+lib.DateTimeText()+'\n'
            comment=comment+'REMARK parent pdb file='+pdbfile+'\n'
            if rcut > 0:
                comment=comment+'REMARK environment residues are with rcut='+('%6.2f' % rcut)+'\n'
                comment=comment+'REMARK core residues are:\n'
                for res in corereslst:
                    comment=comment+'REMARK '+res+'\n'
            comment=comment[:-1]
            #futoolslib.SELECTRES=corereslst
            #if jobopt == 2: res=res+'-e'+str(int(10*rcut))
            if objopt == 3:
                chain=chainlst[i]
                outfile=futoolslib.MakeProFileNameEnv(base,'.pdb',chain,rcut)
            else:
                res=lst[0]
                outfile=futoolslib.MakeFileNameEnv(base,'.pdb',res,rcut)
            outfile=os.path.join(outdir,outfile)    
            #
            fumole.fuMole.WritePDBAtom(outfile,respdbatm,[],comment)
            filelst.append(outfile)
        print(('number of created PDB files=',len(filelst)))
        if len(filelst) > 0:
            if objopt == 3: splfile=base+'-pick-up-pro-chain'
            else: splfile=base+'-pick-up-'+lst[0][:3]
            if rcut > 0:
                srcut=str(int(10*rcut)); splfile=splfile+'-e'+srcut 
            splfile=splfile+'.spl'    
            splfile=os.path.join(outdir,splfile)
            comment='# created by '+prgnam+' at '+lib.DateTimeText()+'\n'
            comment=comment+'# parent pdb file'+pdbfile
            futoolslib.WriteFileNames(splfile,filelst,[],comment)
            print(('split fileslst file is created ',splfile))
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

pick_up_obj()

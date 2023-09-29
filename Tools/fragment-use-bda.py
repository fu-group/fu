#!/bin/sh
# -*- coding: utf-8

def fragment_use_bda():
    # arguments:ipdb='file name', bdafile='file name'
    # conopt=1(create bond),2(no); ovrwrt=1(yes),2(no)
    # program name
    prgnam='fragment_use_bda'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file(.pdb)',True)
        frgfile=pdbfile.replace('.pdb','.frg')
        futoolslib.INPUTPDBFILE=pdbfile            
        # read bda file
        bdafile=futoolslib.GetSysArgs('bdafile')
        if not bdafile:
            # read PDB file name
            bdafile=futoolslib.ConsoleInputOfFileName('bda file(.bda)',True)
        #frgfile=futoolslib.GetSysArgs('frgfile')
        #if not frgfile:
        #    # read PDB file name
        #    frgfile=futoolslib.ConsoleInputOfOutputFileName('frgment file(.frg)',True)            
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        # read pdb file
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        #pdbatm=futoolslib.AddItemToPDBAtm(pdbatm)
        pdbatm=futoolslib.InitAddFragmentData(pdbatm,'')
        pdbatm=futoolslib.SetPdbCon(pdbatm,pdbcon)
        nter=0
        nter,pdbatm=futoolslib.DeleteTER(pdbatm)

        if nter > 0:
            print(('TERs were deleted. nter=',nter))
            #pdbcon=futoolslib.MakeConectList(pdbatm)     
            comment='REMARK '+prgnam+' removed TERs in '+pdbfile
            pdbcon=futoolslib.MakeConectList(pdbatm)
        else: pdbcon=futoolslib.MakeConectList(pdbatm)
        #
        mkbnd=False
        if len(pdbcon) <= 0:
            print('no connect data in the pdb file.')
            conopt=futoolslib.GetSysArgs('conopt')
            if not conopt:
                prmpt='do you want to create? 1:yes, 2:no, quit the job.'
                conopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
                pdbcon=futoolslib.MakePdbCon(pdbatm)
                mkbnd=True
            if conopt == 2:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        if nter > 0 or mkbnd:
            newpdbfile=futoolslib.InsertChrInFileName(pdbfile,'$')
            frgfile=newpdbfile.replace('.pdb','.frg')
        #
        grpnam=futoolslib.MakeMolNamFromFileName(pdbfile)
        # read bda file
        molnam,bdadic=futoolslib.ReadBDAFile(bdafile)
        if len(bdadic) <= 0:
            print('Error (fragment_use_bda): bda data is empty. quit.')
            cmd='quit'; break
        if molnam != '':
            if molnam != grpnam:
                print(('Error (fragment_use_bda): molnam created from pdb filename, '+grpnam+ \
                      'is different from that defined in bda file, '+molnam))
                print('quit this job.')                
                cmd='quit'; break
        # set bda-baa in pdbatm (res=ALA:123:A case for future extension            bdaresdic=futoolslib.MakeBDAResDic(bdadic)        
        #futoolslib.ClearBDAInRes(bdaresdic)
        # set bda-baa
        for res,atmnamlst in list(bdadic.items()):
            pdbatm=futoolslib.SetBDABAAToPdbAtm(pdbatm,res,atmnamlst)
        # make fragments based on BDA (set frgnam to pdbatm)
        pdbatm,frgnam,nfatm=futoolslib.SetFrgNamBasedOnBDABAA(pdbatm,pdbcon)
        nfrg=futoolslib.RenumberFrgNam(pdbatm,1)
        #
        if os.path.isfile(frgfile):
            wrtopt=futoolslib.GetSysArgs('wrtopt')
            if not wrtopt:
                prmpt='fragment data file, '+frgfile+' exsists. overwrite ? 1:yes, 2:no,quit'
                wrtopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
                if wrtopt == 2:
                    print('quit this job.')                
                    cmd='quit'; break
        #
        resnam,bdalst,frgtbl,frglst=futoolslib.MakeFragmentDataForWrite(pdbatm)
        fumole.fuMole.WriteFrgDat(frgfile,molnam,resnam,bdalst,frgtbl,frglst)
        print(('number of created fragmnets: '+str(len(nfatm))))
        print('fragment charge was calculated using chg in PDB data. if they are not correct, ')
        print('please post-edit the created fragment data file(.frg)')
        #
        unfrg=futoolslib.CountUnFrgmentedAtoms(pdbatm)
        print(('total number of fragments: ',nfrg))
        print(('number of unfragmented atoms:',unfrg))
        #
        if nter > 0 or mkbnd:                
            pdbcon=futoolslib.MakeConectList(pdbatm)
            comment=''
            if nter > 0:
                comment='REMARK created by fragment_use_bda removing TERs in '+pdbfile
                if mkbnd: comment=comment+'\n'
            if mkbnd > 0:
                comment='REMARK created by fragment_use_bda adding CONECT data to '+pdbfile
            fumole.fuMole.WritePDBAtom(newpdbfile,pdbatm,pdbcon,comment)
            print(('new pdb file was created removing TERs or adding connect data. '+newpdbfile))
        #
        if len(frgfile) > 0: print(('fragment data file is created. file='+frgfile))
        futoolslib.OUTPUTFRGFILE=frgfile
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

        #self.ToolsCmd(cmd,prgnam)

fragment_use_bda()

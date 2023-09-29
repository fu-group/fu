#!/bin/sh
# -*- coding: utf-8

def set_res_frgdat():
    # arguments: ipdb,frgopt=1(update),2(new),inpfrgfile='filename'(frgopt=1)
    # filopt=1:console, 2:list file, 3:directory
    # frgfilelst=  , setopt=set residue fragment to, 1:unassingned, 2:all residues
    # program name
    prgnam='set_res_frgdat'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read input pdb file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input PDB data (.pdb)',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        frgfile=pdbfile.replace('.pdb','.frg')
        futoolslib.OUTPUTFRGFILE=frgfile
        # xyz file
        xyzopt=1
        """ not completed yet. for writexyzatom, bond, resfrg are not set.
        prmpt='do you want to create xyz file? 1:no, 2:yes'
        xyzopt=toolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        """
        xyzfile=pdbfile.replace('.pdb','.xyz')
        if xyzopt == 2: print(('xyz file '+xyzfile+' will be created.'))
        frgopt=futoolslib.GetSysArgs('frgopt')
        if not frgopt:
            # option, 1:create nre fragment file, 2:update
            prmpt='fragment file option. 1: update, 2:create new file.'
            frgopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        if frgopt == 1:
            inpfrgfile=futoolslib.GetSysArgs('inpfrgfile')
            if not inpfrgfile:
                inpfrgfile=futoolslib.ConsoleInputOfFileName('input existing fragment data (.frg)',True)
                if inpfrgfile == '':
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            if frgfile == inpfrgfile:
                print(('fragment file: '+frgfile+' will be overwritten.'))
        filopt=futoolslib.GetSysArgs('filopt')
        if not filopt:
            # read residue fragment file name
            prmpt='input residue fragment file form 1:console, 2:list file, 3:directory'
            filopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        frgfilelst=futoolslib.GetSysArgs('frgfilelst')
        if not frgfilelst:
            frgfilelst=futoolslib.InputResFrgFiles(filopt)#
        setopt=futoolslib.GetSysArgs('setopt')
        if not setopt:
            # set fragment options
            prmpt='set residue fragment to, 1:unassingned, 2:all residues.'
            setopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        # read pdb data
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        #pdbatm=futoolslib.AddItemToPDBAtm(pdbatm)
        pdbatm=futoolslib.InitAddFragmentData(pdbatm,'')
        pdbatm=futoolslib.SetPdbCon(pdbatm,pdbcon)
        nter,pdbatm=futoolslib.DeleteTER(pdbatm)
        if nter > 0:
            print((str(nter)+' TERs were deleted.'))
            print(('number of atoms in pdbatm=',len(pdbatm)))
        # add fragment items to pdbatm
        grpnam=lib.MakeMolNamFromFileName(pdbfile)
        pdbatm=futoolslib.InitAddFragmentData(pdbatm,grpnam)
        #
        if frgopt == 1:
            nsize=futoolslib.GetNumberOfAtomsInFrgDatFile(inpfrgfile)
            ns=len(pdbatm)
            if ns != nsize:
                print(('error: numbers of atoms are different in pdb and fragment data, '+str(ns)+','+str(nsize)))
                print('quit job.')
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            resnam,bdalst,frgchglst,frgnamlst=fumole.fuMole.ReadFrgDat(inpfrgfile,nsize)    
            pdbatm=futoolslib.SetFragmentData(pdbatm,bdalst,frgchglst,frgnamlst)
            nfrg=futoolslib.CountFragments(pdbatm,True)
            print(('number of initial fragments: ',nfrg))
        else:
            nsize=len(pdbatm)
            bdalst=[]; frgchglst=nsize*[0.0]; frgnamlst=nsize*['???001']
            pdbatm=futoolslib.SetFragmentData(pdbatm,bdalst,frgchglst,frgnamlst)
        #
        reslst=[]; frgnmb=0
        for resfrgfile in frgfilelst:
            # read fragment data file
            nsize=futoolslib.GetNumberOfAtomsInFrgDatFile(resfrgfile)
            resnam,bdalst,frgchglst,frgnamlst=fumole.fuMole.ReadFrgDat(resfrgfile,nsize)
            # set fragment data in pdbatm
            print(('residue fragment name',frgnamlst[0][:3]))
            frgnam=frgnamlst[0][:3]
            resdic,pdbatm=futoolslib.SetResFrgDat(pdbatm,resnam,bdalst,frgchglst,frgnam,setopt)
            lst=list(resdic.keys())
            reslst.append(lst)
        #
        if len(reslst) > 0:
            # output fragment data file
            ini=1
            nfrg=futoolslib.RenumberFrgNam(pdbatm,ini)
            molnam=lib.MakeMolNamFromFileName(pdbfile)
            bdalst=futoolslib.MakeBDALstFromPDBAtm(pdbatm)
            grpdic=futoolslib.MakeGrpDicFromPDBAtm(pdbatm)
            resnam,frglst=futoolslib.MakeFrgLstFromPDBAtm(pdbatm,grpdic)
            frgtbl=futoolslib.MakeFrgTblFromPDBAtm(frglst)
            fumole.fuMole.WriteFrgDat(frgfile,molnam,resnam,bdalst,frgtbl,frglst)
            print('fragment data were set to resdiues: ')
            for lst in reslst: print(lst)
            mess='updated.'
            if frgopt == 2: mess='created.'
            print(('fragment data file '+frgfile+' is '+mess)) 
        else:
            print('failed to created fragment data.') 
        # save pdb ?
        if nter > 0:
            #prmpt='pdb data has changed (removed TERs). do you want to save ? 1:yes, 2:no, save later.'
            #updopt=futoolslib.GetSysArgs('updop')
            #if not updopt:
            #    updopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
            #if updopt == 1:
            pdbcon=futoolslib.MakeConectList(pdbatm)
            comment='REMARK removed TERs in '+pdbfile
            newpdbfile=futoolslib.InsertChrInFileName(pdbfile,'$')
            fumole.fuMole.WritePDBAtom(pdbfile,pdbatm,pdbcon,comment)
            print(('new pdb file was created removing TERs. '+newpdbfile))
        # xyz file
        if xyzopt == 2:
            """ note: bond and resfrg data not set yet """
            outxyz=futoolslib.GetSysArgs('outxyz')
            if not outxyz:
                prmpt='do you want to save xyzfile (.xyz)? 1:no, 2:yes.'
                outxyz=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
            if outxyz == 2:
                bond=[]; resfrg=[]
                fumole.fuMole.WriteXYZAtom(xyzfile,pdbatm,bond,resfrg,[],'')    
                print(('xyz file '+xyzfile+' is created.'))
        # count unassigned fragment
        unanmb=futoolslib.CountFragments(pdbatm,False)
        print(('number of unassigned fragments: ',unanmb))
        #-----------
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)
set_res_frgdat()


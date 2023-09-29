#!/bin/sh
# -*- coding: utf-8

def make_fmo_input():
    # arguments: ipdb,frgfile,fmofile,datfile(header),basnam,cmd
    # frgopt=1(dir),2(file)
    # program name
    prgnam='make_fmo_input'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read file names
            pdbfile=futoolslib.ConsoleInputOfFileName('PDB file(.pdb)',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        frgfile=futoolslib.GetSysArgs('frgfile')
        if not frgfile:
            frgfile=futoolslib.ConsoleInputOfFileName('fragment data(.frg)',True)
            if frgfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTFRGFILE=frgfile
        fmofile=futoolslib.GetSysArgs('fmofile')
        if not fmofile:
            fmofile=futoolslib.ConsoleInputOfOutputFileName('fmo input file(.inp)',True)
            if fmofile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        datfile=futoolslib.GetSysArgs('datfile')
        if not datfile:
            datfile=futoolslib.ConsoleInputOfFileName('FMO CTRL data',True)
        molnam=lib.MakeMolNamFromFileName(pdbfile)
        basnam=futoolslib.GetSysArgs('basnam')
        if not basnam:
            # read input options, read fragment data (.frg).     
            basnam=futoolslib.ConsoleInputOfStringData('basis set name, i.e. 6-31G*')
        #basnam=bastxt.split()
        basmin='MINI'
        
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        # read pdbatm
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        ctrldat=futoolslib.ReadFMOCtrlDat(datfile)
        # read frgment data file
        nsize=futoolslib.GetNumberOfAtomsInFrgDatFile(frgfile)
        resnam,frglst,frgchglst,bdalst,frgatmlst=fumole.fuMole.ReadDatInFrgDat(frgfile)#
        # write FMO input data
        #WiteFMO(fmofile,frgchglst,False)
        nfrg=len(frglst)
        if nfrg > 0:
            futoolslib.WriteFMONfrag(fmofile,nfrg,ctrldat)
            futoolslib.WriteFMOFrgNam(fmofile,frglst,True)
        if len(frgchglst) > 0: futoolslib.WriteFMOCharg(fmofile,frgchglst,True)
        if len(frgatmlst) > 0:
            futoolslib.WriteFMOIndat(fmofile,frgatmlst,True)
        if len(bdalst) > 0: futoolslib.WriteFMOBND(fmofile,bdalst,basnam,basmin,True)
        if len(pdbatm) > 0: futoolslib.WriteFMOXYZ(fmofile,pdbatm,True)
        print(('FMO input file is created. file=',fmofile))
        #-----------
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

make_fmo_input()


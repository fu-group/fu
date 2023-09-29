#!/bin/sh
# -*- coding: utf-8
#
global futoolslib

def split_pdb():
    # arguments: splopt=1(ter),2(chain),3(res),4(pro,chm,wat)
    # ipdb,odir,watopt=1(include),2(no),logopt=1(yes),2(no)
    # wrtopt=1(overwrite),2(no), cmd
    # program name
    prgnam='split-pdb'
    
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        splopt=futoolslib.GetSysArgs('splopt')
        if not splopt:
            # split option, 1: at TER, 2: chains, 3: residues, 4:into pro(aa residues), chm(non-aa residues), and wat(WAT,HOH or H2O). 
            splopttxt=['at TER','chains','into pro,chm,wat']
            prmpt='select split option. 1: at TER, 2:chains, 3: pro,chm,wat, 4:cancle'
            splopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,4,1)
        print(('split option: ',splopttxt[splopt-1]))
        if splopt == 4:
            print(('splopt',splopt))
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #if splopt == 2:
        #    watopt=futoolslib.GetSysArgs('watopt')
        #    if not watopt:
        #        watopt=futoolslib.ConsoleInputOfIntegerOption('including waters. 1:yes, 2:no',1,2,1)
        watopt=1
        #envopt=futoolslib.GetSysArgs('envopt')
        #if not envopt:
        #    prmpt='environment option, 1: no environment, 2:with environment'
        #    envopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        envopt=1
        rcut=-1.0
        #if envopt == 2:
        #    rcut=futoolslib.GetSysArgs('rcut')
        #    if not rcut:
        #        prmpt='input cut-off distance(A) of environment.'
        #        rcut=futoolslib.ConsoleInputOfStringData(prmpt)[0]
        #        try: rcut=float(rcut)
        #        except:
        #            print 'error (split_pdb): input error in rcut. it should be a number.'
        #            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outdir=futoolslib.GetSysArgs('odir')
        if not outdir:
            # read output file name    
            outdir=futoolslib.ConsoleInputOfDirectoryName('of output PDB files',True)
            if outdir == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.PDBDIR=outdir
        #
        #logopt=1
        logopt=futoolslib.GetSysArgs('logopt')
        if not logopt:
            prmpt="do you want to output in log file? 1:yes, 2:no"
            logopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        logfile=pdbfile.replace('.pdb','.log')
        # get base name
        base=os.path.basename(pdbfile)
        base=os.path.splitext(base)[0]
        print(('base name of created pdb files=',base))
        #
        time1=time.clock() # turn on timer
        futoolslib.MessJobStart(prgnam)
        # read pdb file
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        futoolslib.PDBCON=False
        if len(pdbcon) > 0: futoolslib.PDBCON=True
        # split pdb
        if splopt == 1: filelst=futoolslib.SplitAtTER(pdbatm,outdir,base,rcut)
        elif splopt == 2:
            #watopt=futoolslib.ConsoleInputOfIntegerOption('including waters. 1:yes, 2:no',1,2,1)
            if watopt == 1: print('split chains with waters')
            else: print('split chains excluding waters')
            filelst=futoolslib.SplitChains(pdbatm,outdir,base,watopt,rcut)
        #elif splopt == 3: filelst=futoolslib.SplitResidues(pdbatm,outdir,base,rcut)
        else: filelst=futoolslib.SplitProChmWat(pdbatm,outdir,base)
        # write split-files-list file
        splfileext=['-ter.spl','-chain.spl','-pro-chm-wat.spl']
        splfile=base+splfileext[splopt-1]
        splfile=os.path.join(outdir,splfile)
        # split-files-list file option
        wrtopt=1; spltxt='split-fileslst file '
        if os.path.isfile(splfile):
            wrtopt=futoolslib.GetSysArgs('wrtopt')
            if not wrtopt:
                prompt=splfile+spltxt+' exists. overwrite? 1:yes, 2:no.'
                wrtopt=futoolslib.ConsoleInputOfIntegerOption(prompt,1,2,1)
        if wrtopt == 1:
            comment='# created by '+prgnam+' at '+lib.DateTimeText()+'\n'
            comment=comment+'# parent pdb file'+pdbfile
            futoolslib.WriteFileNames(splfile,filelst,[],comment)
            print((spltxt+' is created',splfile))
        else:
            print(('warning: split-fileslst file '+splfile+' is not updated!'))
        print(('number of created split files=',len(filelst)))
        # print end job message
        #
        if logopt == 1:
            comment='[input pdb file] '+pdbfile+'\n'
            comment=comment+'[output directory] '+outdir+'\n'
            comment=comment+'[created split files-list-file] '+splfile+'\n'
            comment=comment+'[split option] '+splopttxt[splopt-1]
            futoolslib.WriteSplitPDBLog(logfile,comment,filelst)
        #-----
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)
    #futoolslib.ToolsCmd(cmd,prgnam)
    
split_pdb()

#!/bin/sh
# -*- coding: utf-8

def pick_up_unique_res():
    # arguments: ipdb,odir,cmd, res='resname (res or res:*:*)
    # program name
    prgnam='pick_up_unique_res'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        res=futoolslib.GetSysArgs('res')
        if not res:
            # read res
            prmpt='input resdiue name, like "***" for all kind and "UNL:*:* for all UNL" (" is not the input).'
            res=futoolslib.ConsoleInputOfStringData(prmpt)[0]
            if len(res) <= 0:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        print(('res in pick-up-unique-res',res))
        print(('unique residues with name, '+res+' will bepicked up.'))
        resnamdat,resnmbdat,chaindat=lib.ResolveResidueName(res)
        if chaindat.islower(): cndat='l'+chaindat
        else: cndat='u'+chaindat
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outdir=futoolslib.GetSysArgs('odir')
        if not outdir:
            # read output file name    
            outdir=futoolslib.ConsoleInputOfDirectoryName('of output pdb files',True)
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
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        filelst=futoolslib.PickUpUniqueRes(res,pdbatm,outdir,base)
        #
        uniq=res[:3]
        if uniq == '***': uniq='ALLKIND'
        if chaindat != '*' and chaindat != '': uniq=uniq+'-'+cndat
        splfile=base+'-'+uniq+'.spl'
        splfile=os.path.join(outdir,splfile)
        # grplst is written in splitpdb list file. 05Mar2014, KK
        #grplst=MakeGroupName(filelst)
        comment='# created by '+prgnam+' at '+lib.DateTimeText()+'\n'
        comment=comment+'# parent pdbfile='+pdbfile
        futoolslib.WriteFileNames(splfile,filelst,[],comment) #grplst)
        print(('unique '+res+' res-list file is created',splfile))
        print(('number of unique '+res+' residues=',len(filelst)))
        print('')
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

pick_up_unique_res()


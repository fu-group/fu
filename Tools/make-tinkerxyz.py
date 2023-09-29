#!/bin/sh
# -*- coding: utf-8

# read pbb
def ReadAtmTyp(fffile):
    atmtypdic={}
    f=open(fffile,'r')
    for s in f.readlines():
        s=futoolslib.RemoveNull(s)
        if s[:1] == '#': continue
        nc=s.find('#')
        if nc >= 0: s=s[:nc]
        if len(s) <= 0: continue
        if s[:4] == 'atom':
            s=s[4:]; item=s.split()
            elm=item[1].strip()
            if len(elm) == 1: elm=' '+elm
            atmtypdic[elm]=int(item[0])
    f.close()
    
    #print 'atmtypdic in ReadAtmType',atmtypdic    
    
    return atmtypdic

def MakeWatConDat(pdbatm):
    watcon=[]
    for i in range(len(pdbatm)): watcon.append([])
    #for i in xrange(0,len(pdbatm),3):
    natm=len(pdbatm); i=-1
    while i < natm-1:
        i += 1
        res=pdbatm[i][4]
        if res == 'WAT' or res == 'HOH':
            watcon[i]=watcon[i]+[i+1,i+2]
            watcon[i+1]=watcon[i+1]+[i]
            watcon[i+2]=watcon[i+2]+[i]
            i += 2
    #print 'watcon in makewatcondat',watcon
    return watcon

def AssignAtmTyp(pdbatm,atmtypdic):
    atomic=[]; nonbonded=[]
    for i in range(len(pdbatm)):
        res=res=pdbatm[i][4]; elm=pdbatm[i][10]
        if res == 'WAT' or res == 'HOH':
            if elm == ' O': atomic.append(atmtypdic['OW'])             
            elif elm == ' H': atomic.append(atmtypdic['HW'])
        else:
            atomic.append(atmtypdic[elm])
            nonbonded.append(i)
    return atomic,nonbonded

def WriteTinkerXYZ(outfile,pdbatm,watcon,atomic):
        fi6='%6d'; ff12='%12.6f';
        blk=' '
        f=open(outfile,'w') 
        s=fi6 % len(pdbatm)
        f.write(s+'\n')
        for i in range(len(pdbatm)):
            s=fi6 % (i+1)
            atmnam=pdbatm[i][10]+'  '
            atmnam=atmnam+4*blk
            s=s+blk+atmnam[0:4]
            cc=pdbatm[i][7]
            s=s+(ff12 % cc[0])+(ff12 % cc[1])+(ff12 % cc[2])
            s=s+fi6 % atomic[i]
            if len(watcon[i]) > 0:
                for j in watcon[i]: s=s+ (fi6 % (j+1))
            s=s+'\n'
            f.write(s)
        f.close()

def CompressIntForTinker(idata):
    dat=idata[:]
    for i in range(len(dat)): dat[i] += 1
    dattxt=lib.IntegersToText(dat)
    datlst=dattxt.split(",")
    dat=[]
    for s in datlst:
        if s.find("-") >= 0:
            ss=s.split("-"); ss[0]="-"+ss[0]
            dat.append(ss[0]); dat.append(ss[1]) 
        else: dat.append(s)
    return dat

def WriteTinkerKey(keyfile,fffile,nonbonded,active,maxiter):
    f=open(fffile,'r')
    act=CompressIntForTinker(active)
    inact=CompressIntForTinker(nonbonded)
    #
    f=open(keyfile,'w')
    f.write('parameters '+fffile+'\n')
    f.write('\n')
    f.write('maxiter '+str(maxiter)+'\n')
    f.write('\n')
    #
    text='active '; ndat=0
    for i in range(len(act)):
        seq=act[i]
        if len(text) >= 65:
            f.write(text+'\n')
            ndat=0
            text='active '    
        text=text+str(seq)+' '
        ndat += 1
    if ndat > 0: f.write(text+'\n')
    text='inactive '; ndat=0
    for i in range(len(inact)):
        seq=inact[i]
        if len(text) >= 65:
            f.write(text+'\n')
            ndat=0
            text='inactive '    
        text=text+str(seq)+' '
        ndat += 1
    if ndat > 0: f.write(text+'\n')
    f.write('\n')
    f.close()

def DeleteHydrogens(pdbatm):
    pdb=[]
    for i in range(len(pdbatm)):    
        if pdbatm[i][4] == 'HOH' or pdbatm[i][4] =='WAT':
            pdb.append(pdbatm[i])
        else:
            if pdbatm[i][10] != ' H': pdb.append(pdbatm[i])
    return pdb
        
def MakeActiveAtomLst(pdbatm,actopt):
    # actopt: 1= H's in HOH, 2=WAT, 3=both
    # hydrogen: False: remove h in inactive, True:include
    activelst=[]
    for i in range(len(pdbatm)):
        res=res=pdbatm[i][4]; elm=pdbatm[i][10]
        if actopt == 1 or actopt == 3:
            if res == 'HOH' and elm == ' H': activelst.append(i)            
        if actopt == 2 or actopt == 3:
            if res == 'WAT': activelst.append(i)                 

    return activelst

def make_tinker_xyz():
    prgnam='make_tinker_xyz'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        actopt=futoolslib.GetSysArgs('actopt')
        if not actopt:
            prmpt='active object. 1: Hs in HOH, 2:WAT, 3: both'
            actopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        hydopt=futoolslib.GetSysArgs('excrude')
        if not hydopt:
            prmpt='exclude hydrogens in inactive. 1: yes, 2:no'
            hydopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        itropt=futoolslib.GetSysArgs('itropt')
        if not itropt:
            item=futoolslib.ConsoleInputOfStringData('maxiter, conv (ex. 1000, 0.01)')
            if item[0] == '':
                maxiter=1000; conv=0.01
            else: maxiter=int(item[0]); conv=float(item[1])
        
        print(('maxiter and convergence threshold',maxiter,conv))
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outfile=futoolslib.GetSysArgs('tinxyzfile')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('of output TINKER xyz file',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
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
        #
        time1=time.clock() # turn on timer
        futoolslib.MessJobStart(prgnam)
        # read pdb file
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        if hydopt == 1: pdbatm=DeleteHydrogens(pdbatm)
        # read TINKER parameter file
        ffname='tip3p'
        fffile='e://tinker-6.2.06//params//tip3p.prm'
        keyfile=outfile.replace('.xyz','.key')
        atmtypdic=ReadAtmTyp(fffile)
        watcon=MakeWatConDat(pdbatm)
        atomic,nonbonded=AssignAtmTyp(pdbatm,atmtypdic)
        activelst=MakeActiveAtomLst(pdbatm,actopt)
        WriteTinkerXYZ(outfile,pdbatm,watcon,atomic)
        WriteTinkerKey(keyfile,fffile,nonbonded,activelst,maxiter)
        print(('keyfile',keyfile))
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,[])
        done=True
    
    #futoolslib.ToolsCmd(cmd,prgnam)
make_tinker_xyz()

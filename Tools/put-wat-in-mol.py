#!/bin/sh
# -*- coding: utf-8

def FindXYZMinMax(pdbatm):
    xyzminmax=[]
    x=[]; y=[]; z=[]
    for i in range(len(pdbatm)):
        x.append(pdbatm[i][7][0])
        y.append(pdbatm[i][7][1])
        z.append(pdbatm[i][7][2])
    xmin=min(x); xmax=max(x)
    ymin=min(y); ymax=max(y)
    zmin=min(z); zmax=max(z)
    xyzminmax=[[xmin,xmax],[ymin,ymax],[zmin,zmax]]
    
    print(('xyzminmax',xyzminmax))
    
    return xyzminmax

def MakeRectangleGrid(gridspace,xyzminmax):
    xgrid=[]; ygrid=[]; zgrid=[]
    xmin=xyzminmax[0][0]; xmax=xyzminmax[0][1]
    nx=int((xmax-xmin)/gridspace)
    for i in range(nx): xgrid.append(xmin+i*gridspace)
    ymin=xyzminmax[1][0]; ymax=xyzminmax[1][1]
    ny=int((ymax-ymin)/gridspace)
    for i in range(ny): ygrid.append(ymin+i*gridspace)
    zmin=xyzminmax[2][0]; zmax=xyzminmax[2][1]
    nz=int((zmax-zmin)/gridspace)
    for i in range(nz): zgrid.append(zmin+i*gridspace)
    
    mess='number of initial grid points='+str(nx*ny*nz)
    mess=mess+' ('+str(nx)+','+str(ny)+','+str(nz)+')'
    print(mess)
    return xgrid,ygrid,zgrid

def FindInnerGridPoints(pdbatm,xgrid,ygrid,zgrid):
    innerpntlst=[]
    #outerpntdic={}
    #ngrid=len(xgrid)*len(ygrid)*len(zgrid)
    gs=0.0; ninner=0 #nouter=0
    gs=0.5*(zgrid[1]-zgrid[0])
    #gs=0.8
    #except: gs=ygrid[1]-ygrid[0]
    #if gs == 0.0: gs=xgrid[1]-xgrid[0]
    for k in range(len(zgrid)):
        z=zgrid[k]; x=[]; y=[]    
        #print 'z,gs',z,gs
        for ii in range(len(pdbatm)):
            if pdbatm[ii][7][2] <= z-gs or pdbatm[ii][7][2] >= z+gs: continue
            x.append(pdbatm[ii][7][0]); y.append(pdbatm[ii][7][1])
        if len(x) > 0:
            
            print(('len(x,y)',len(x)))
            xmin=min(x); xmax=max(x); ymin=min(y); ymax=max(y)
            #print 'xmin,xmax,ymin,ymax',xmin,xmax,ymin,ymax
            # (+,+)
            for j in range(len(ygrid)/2):
                if ygrid[j] < ymin: break
                for i in range(len(xgrid)):
                    if xgrid[i] < xmin: break
                    innerpntlst.append([i,j,k]); ninner += 1
            # (+,-)
            for j in range(len(ygrid)/2):
                if ygrid[j] < ymin: break
                for i in range(len(xgrid)):
                    ii=len(xgrid)-i-1
                    if xgrid[ii] < xmin: break
                    innerpntlst.append([ii,j,k]); ninner += 1
            # (-,+)
            for j in range(len(ygrid)/2):
                jj=len(ygrid)-j-1
                if ygrid[jj] > ymax: break
                for i in range(len(xgrid)):
                    if xgrid[i] > xmax: break
                    innerpntlst.append([i,jj,k]); ninner += 1
            # (-,-)
            for j in range(len(ygrid)/2):
                jj=len(ygrid)-j-1
                if ygrid[jj] > ymax: break
                for i in range(len(xgrid)):
                    ii=len(xgrid)-i-1
                    if xgrid[ii] > xmax: break
                    innerpntlst.append([ii,jj,k]); ninner += 1
        
    print(('number of inner grid points=',ninner))    
    return innerpntlst #outerpntdic
    
def FindSpaceGridPoints(pdbatm,xgrid,ygrid,zgrid,radius):
    ninner=0; innerpntdic={}
    innerpntlst=FindInnerGridPoints(pdbatm,xgrid,ygrid,zgrid)
    cc1=[]
    for i in range(len(pdbatm)):
        if pdbatm[i][10] != ' H': cc1.append(pdbatm[i][7])
    cc2=[]; indx=[]
    for i,j,k in innerpntlst:
        cc2.append([xgrid[i],ygrid[j],zgrid[k]])
        indx.append([i,j,k])        
    #print 'cc2 in FindInnnerGridPoints',cc2
    rmin=radius; rmax=100.0
    npts,ipnts=fuflib.find_contact_atoms(cc1,cc2,rmin,rmax)
    for i in ipnts:
        if i < 0: continue
        ipt=indx[i]
        ii=ipt[0]; jj=ipt[1]; kk=ipt[2]
        #print 'ipt,ii,jj,kk',ipt,ii,jj,kk
        ijkstr=PackIJK(ii,jj,kk)
        innerpntdic[ijkstr]=[xgrid[ii],ygrid[jj],zgrid[kk]]
    
    print(('number of inner space grid points=',npts))
    return innerpntdic

def PutWatersInSpace(pdbatm,innerpntdic,radius,ndev):
    occupieddic={}
    atmseq=len(pdbatm); resseq=GetMaxResNmb(pdbatm)
    naddatm=-1; naddres=-1
    for ijkstr, cc in list(innerpntdic.items()):
        i,j,k=UnpackIJK(ijkstr)
        ans=IsSpace(i,j,k,innerpntdic,occupieddic,ndev)     
        
        ans=True
        
        
        if ans:
            occupieddic[ijkstr]=True; naddatm += 1; naddres += 1
            atom=MakeWaterAtomData(cc,atmseq+naddatm,resseq+naddres)
            pdbatm.append(atom)
    print(('number of added waters=',naddres+1))    
    return pdbatm

def IsSpace(i,j,k,innerpntdic,occupieddic,ndev):
    if ndev == 3:
        xneigbor=[i-1,i+1]; yneigbor=[j-1,j+1]; zneighbor=[k-1,k+1] 
    elif ndev == 5:
        xneigbor=[i-2,i-1,i+1,i+2]; yneigbor=[j-2,j-1,j+1,j+2];
        zneighbor=[k-2,k-1,k+1,k+2]    
    for ii in xneigbor:
        #if ii < 0: continue
        for jj in yneigbor:
            #if jj < 0: continue
            for kk in zneighbor:
                #if kk < 0: continue
                ijkstr=PackIJK(ii,jj,kk) 
                if ijkstr in occupieddic: return False
                if ijkstr not in innerpntdic: return False
    return True
    
def GetMaxResNmb(pdbatm):
    maxresnmb=0
    for i in range(len(pdbatm)):
        if pdbatm[i][6] > maxresnmb: maxresnmb=pdbatm[i][6]
    return maxresnmb

def MakeWaterAtomData(cc,iatm,ires):
    """  0:label,1:atmnmb,2:atmnam,3:alt,4:resnam,5:chain,
     6:resnmb,7:[fx,fy,fz],8:focc,9:fbfc,10:elm,11:chg      
     12:'grpnam',13:'frgnam',14:'frgchg',15:'baa',16:'conect' """  

    atom=[]
    atom.append('HETATM') 
    atom.append(iatm)
    atom.append(' OW ')
    atom.append('')
    atom.append('WAT')
    atom.append(' ')
    atom.append(ires)
    atom.append(cc)
    atom.append(1.0)
    atom.append(0.0)
    atom.append(' O')
    atom.append(0.0)
    #print 'atom in MakeWaterAtomData',atom
    return atom

def PackIJK(i,j,k):
    ijkstr=str(i)+'-'+str(j)+'-'+str(k)
    return ijkstr

def UnpackIJK(ijkstr):    
    item=ijkstr.split('-')
    i=int(item[0]); j=int(item[1]); k=int(item[2]) 
    return i,j,k

def put_wat_in_mol():
    prgnam='space_in_mol'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        radius=3.0; ndev=3
        radopt=futoolslib.GetSysArgs('radopt')
        if not radopt:
            item=futoolslib.ConsoleInputOfStringData('sphere radius, 3 or 5 for grid space(ex. 3.0, 3)')
            if len(item) >= 2:
                radius=float(item[0]); ndev=int(item[1])
                if ndev != 3 or ndev != 5: ndev=3 
        else: radius=float(radopt[0]); ndev=int(radopt[1])
        gridspace=radius/float(ndev)
        print(('sphere radius and grid space ',radius,gridspace))
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('input pdb file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outfile=futoolslib.GetSysArgs('opdb')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('of output pdb file',True)
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
        # find mix,max coordinates
        xyzminmax=FindXYZMinMax(pdbatm)
        xgrid,ygrid,zgrid=MakeRectangleGrid(gridspace,xyzminmax)
        innerpntdic=FindSpaceGridPoints(pdbatm,xgrid,ygrid,zgrid,radius)
        if len(innerpntdic) > 0:
            pdbatm=PutWatersInSpace(pdbatm,innerpntdic,radius,ndev)
            #pdbatm=RenumberAtmNmbInPdbAtm(pdbatm)
            comment=[]
            fumole.fuMole.WritePDBAtom(outfile,pdbatm,[],comment)
        else: 
            print('no innner space to pu waters.')
            print((outfile+' was not created.'))
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)
        done=True
    
    #futoolslib.ToolsCmd(cmd,prgnam)
put_wat_in_mol()

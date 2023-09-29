#!/bin/sh
# -*- coding: utf-8

#-----------------------------
# module: join-splitted-pdb.py
#-----------------------------
# join splitted pdb files (by split-pdb-at-ter.py) 
# filelst: [[file name, group name],...]
import os
import sys
import copy
import numpy

import lib
import molec
import const 
    
def AddHydrogenToMol(self,at,hname,htype,bndlst,rhx):
    # add hydrogen atom at 'at' atom using 'htype','bndlst' and 'rhx'.
    hnam=hname
    if len(hname) <= 0: hnam=[' H1 ',' H2 ',' H3 ']
    atmlst=[]; nh=0
    natm=len(self.mol)
    atoma=self.mol[at]
    elm=atoma.elm
    # find bond multiplicity
    if htype == 'non': return
    #
    atmlst.append(at)
    if htype == '1A1': atmlst=atmlst+bndlst
    elif htype == '1A2': atmlst=atmlst+bndlst
    elif htype == '1A3':
        ib=bndlst[1]
        atomb=self.mol[ib]
        if len(atomb.conect) <= 0:
            atmnam=atoma.atmnam+':'+str(atoma.atmnmb)
            mess='AddHydrogenToMol: unable to attach hydrogen at ',atmnam
            self.Message(mess,0,'blue')
            self.parent.ConsoleMessage(mess)
        else:    
            ic=atomb.conect[0]
            atmlst=atmlst+bndlst; atmlst.append(ic)
    elif htype == '2A1': atmlst=atmlst+bndlst
    elif htype == '2A2':
        ib=bndlst[1]
        atomb=self.mol[ib]
        if len(atomb.conect) < 1:
            atmnam=atoma.atmnam+':'+str(atoma.atmnmb)
            mess='AddHydrogenToMol: unable to attach hydrogen at ',atmnam
            self.Message(mess,0,'blue')
            self.parent.ConsoleMessage(mess)
        else:    
            ic=atomb.conect[0]
            if ic == at: ic=atomb.conect[1]
            atmlst=atmlst+bndlst; atmlst.append(ic)
    elif htype == '3A1':
        atmlst=atmlst+bndlst
        
    else:
        mess='AddHydrogenToMol: failed to Add hydrogen at '+str(at)+'.'
        self.Message(mess,0,'blue')
        self.parent.ConsoleMessage(mess)
    if htype == '1A1': nh,coord=self.GetCCAddAtmType1A1(atmlst,rhx)
    if htype == '1A2': nh,coord=self.GetCCAddAtmType1A2(atmlst,rhx)
    if htype == '1A3': nh,coord=self.GetCCAddAtmType1A3(atmlst,rhx,-1,True) # trans
    if htype == '2A1': nh,coord=self.GetCCAddAtmType2A1(atmlst,rhx)
    if htype == '2A2': nh,coord=self.GetCCAddAtmType2A2(atmlst,rhx)
    if htype == '3A1': nh,coord=self.GetCCAddAtmType3A1(atmlst,rhx)
    #check interatom distance
    nc=len(coord)
    shrt2=1.73*1.73
    if elm == ' N': shrt2=1.63*1.63
    for i in range(1,len(atmlst)):
        ia=atmlst[i]; ca=self.mol[ia].cc
        for j in range(len(coord)):
            cb=coord[j]
            #dist=numpy.sqrt((ca[0]-cb[0])**2+(ca[1]-cb[1])**2+(ca[2]-cb[2])**2)  
            dist2=(ca[0]-cb[0])**2+(ca[1]-cb[1])**2+(ca[2]-cb[2])**2  

            if dist2 < shrt2: # for C ( this code should be improved)
                nh -= 1
                break
    if nh < 0: nh=0
    if nh > 0:
        self.AddHydrogen(at,nh,coord,hnam) 
    return nh

def AddBondUseFrame(self,lst,framedatadic):
    # add bonds between heavy atoms using frame data.
    frameres=list(framedatadic.keys())
    for res in frameres:
        framedat=framedatadic[res]
        prvres=''
        for i in lst:
            atom=self.mol[i]
            resnam=atom.resnam; resnmb=atom.resnmb
            if resnam != res: continue
            curres=resnam+str(resnmb)
            if curres != prvres:
                ist=i
                for j in range(len(framedat)):
                    s1=framedat[j][0]
                    if s1[0:1] == 'H': continue
                    s1=' '+s1; s1=s1[0:4]
                    ia=self.FindAtmNamInRes(s1,ist,resnam,resnmb)
                    if ia < 0:
                        mess='Atom name '+s1+' is not found. Skipped'
                        self.Message(mess,0,'blue')
                        self.parent.ConsoleMessage(mess)
                        #
                        continue
                    for k in range(1,len(framedat[j])):
                        s2=framedat[j][k]
                        if s2[0] == 'H': continue
                        s2=' '+s2; s2=s2[0:4]
                        #    s2=sx[0:2]+s2[2:4]
                        ib=self.FindAtmNamInRes(s2,ist,resnam,resnmb)

                        if ib < 0:
                            mess='Atom name '+s2+' is not found. Skipped'
                            self.Message(mess,0,'blue')
                            self.parent.ConsoleMessage(mess)
                            continue
                        if ia >= 0 and ib >= 0: self.AddBond(ia,ib,1)
                prvres=curres

def AddHydrogenUseFrame(self,lst,framedatadic):
    na=0; nht=0
    frameres=list(framedatadic.keys())
    for res in frameres:
        framedat=framedatadic[res]
        prvres=''
        for i in lst:
            atom=self.mol[i]
            resnam=atom.resnam; resnmb=atom.resnmb
            if resnam != res: continue
            curres=resnam+str(resnmb)
            if curres != prvres:
                natm=self.CountAtomsInRes(resnam,resnmb)
                ist=i-1; na=0
                while na < natm:
                    ist += 1; na += 1
                    ia=ist+nht
                    nhatm=self.CountHydrogenOfAtom(ia)
                    if nhatm > 0:
                        mess=str(nhatm)+' hydrogens are already attached at '+str(ia)+'. Skipped.'
                        self.Message(mess,0,'blue')
                        self.parent.ConsoleMessage(mess)
                        continue
                    nh,htype,bndlst,rhx=self.FindAddHTypeFrame(ia,framedat)
                    if htype == 'non': continue
                    if len(bndlst) <= 1:
                        mess='Failed to attach hydroge atoms at '+str(ia)+'.'
                        self.Message(mess,0,'blue')
                        self.parent.ConsoleMessage(mess)
                        continue
                    nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                    nht += nh
                prvres=curres        

def GetCCAddAtmType1A1(self,atmlst,r):
    # calculate coordinate of 1A1 type atom added to x1. 
    # atmlst: [x1,x2,x3,x4], xi: sequence number of atom in Molecule() instance
    # r: bond length between add atom and x1
    #ex. H atom added at C in -CH3 results in HCH3 (CH4). 
    #           |-x2        
    # add atom-x1-x3      
    #           |-x4
    at=atmlst[0]
    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    x3=numpy.array(self.mol[atmlst[2]].cc)
    x4=numpy.array(self.mol[atmlst[3]].cc)
    #numpy.array(x1); numpy.array(x2); numpy.array(x3); numpy.array(x4)
    x2t=numpy.zeros(3); x3t=numpy.zeros(3); x4t=numpy.zeros(3)
    xc=numpy.zeros(3); xa=numpy.zeros(3) 
    x2t=numpy.subtract(x2,x1); x3t=numpy.subtract(x3,x1); x4t=numpy.subtract(x4,x1)
    x2t=numpy.divide(x2t,numpy.sqrt(numpy.dot(x2t,x2t)))               
    x3t=numpy.divide(x3t,numpy.sqrt(numpy.dot(x3t,x3t)))
    x4t=numpy.divide(x4t,numpy.sqrt(numpy.dot(x4t,x4t)))                 
    xc=numpy.divide(numpy.add(numpy.add(x2t,x3t),x4t),3.0)    
    xc=numpy.divide(xc,numpy.sqrt(numpy.dot(xc,xc)))
    xc=numpy.multiply(xc,r)
    xa=numpy.subtract(x1,xc)

    coord=[]; coord.append(xa); nh=1
    return nh,coord
     
def GetCCAddAtmType1A2(self,atmlst,r):
    # retuen added atom coordinate,xa
    # add 1A2 type atom to x1. the add atom and reference three atoms make 
    #ex. add atom H to C in -benzene. 
    #           |-x2        
    # add atom-x1     
    #           |-x3
    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    x3=numpy.array(self.mol[atmlst[2]].cc)

    #numpy.array(x1); numpy.array(x2); numpy.array(x3)
    x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    xc=numpy.zeros(3); xa=numpy.zeros(3) 
    x2t=numpy.subtract(x2,x1); x3t=numpy.subtract(x3,x1)
    x2t=numpy.divide(x2t,numpy.sqrt(numpy.dot(x2t,x2t)))               
    x3t=numpy.divide(x3t,numpy.sqrt(numpy.dot(x3t,x3t)))     
    xc=numpy.divide(numpy.add(x2t,x3t),2.0)    
    xc=numpy.divide(xc,numpy.sqrt(numpy.dot(xc,xc)))
    xc=numpy.multiply(xc,r)
    xa=numpy.subtract(x1,xc)
    coord=[]; coord.append(xa); nh=1

    return nh,coord

def GetCCAddAtmType1A3(self,atmlst,r,bang,trans):
    # retuen added atom coordinate,xa
    # add 1A2 type atom to x1. the add atom and reference three atoms make 
    # peudotetrahedron. x's are atom coodinates and r is bond length between add atom and x1.
    #ex. add atom H to C in -CH3 results in HCH3 (CH4). 
    #           |-x2        
    # add atom-x1-x3      
    #           |-x4
    u=numpy.identity(3)
    xh1t=numpy.zeros(3); xh2t=numpy.zeros(3)
    rad61=1.064650844; rad70=1.230963268 # bond angles in radianfor O and S, respectively
    #at=atmlst[0]
    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    x3=numpy.array(self.mol[atmlst[2]].cc)
    rad=bang
    if abs(bang) < 0:
        if self.mol[x1][2] == ' O': rad=rad61
        if self.mol[x1][2] == ' S': rad=rad70

    numpy.array(x1); numpy.array(x2); numpy.array(x3)
    #x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    xc=numpy.zeros(3); xa=numpy.zeros(3) 
    #r21=numpy.sqrt((x2[0]-x1[0])**2+(x2[1]-x1[1])**2+(x2[2]-x1[2])**2)
    #r32=numpy.sqrt((x3[0]-x2[0])**2+(x3[1]-x2[1])**2+(x3[2]-x2[2])**2)
    tmp=numpy.zeros(3)
    tmp=(numpy.subtract(x2,x1)); r21=numpy.sqrt(numpy.dot(tmp,tmp))
    tmp=(numpy.subtract(x3,x2)); r32=numpy.sqrt(numpy.dot(tmp,tmp))
    ra=numpy.subtract(x1,x2); rb=numpy.subtract(x3,x2)
    angl=lib.AngleT(ra,rb)
    #x2t[2]=r12; x3t[0]=r23*numpy.cos(angl)+x2t[2]
    x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    x2t[2]=r21; x3t[0]=r32*numpy.sin(angl); x3t[2]=r32*numpy.cos(angl)+x2t[2]
    if trans:
        xh1t[0]= r*numpy.sin(rad)
        xh1t[2]=-r*numpy.cos(rad)                
    else:
        xh1t[0]=-r*numpy.sin(rad)
        xh1t[2]=-r*numpy.cos(rad)
    xr=[]; xn=[]
    xr.append(x1t); xr.append(x2t); xr.append(x3t)
    xn.append(numpy.zeros(3)); xn.append(numpy.subtract(x2,x1))
    xn.append(numpy.subtract(x3,x1))
    # buck to the original orientation
    u=lib.RotMatPnts(xr,xn)
    xa=numpy.dot(u,xh1t); xa=numpy.add(xa,x1)

    coord=[]; coord.append(xa); nh=1
    return nh,coord

def GetCCAddAtmType2A1(self,atmlst,r):
    # retuen added atom coordinate,xa
    # add 1A2 type atom to x1. the add atom and reference three atoms make 
    # peudotetrahedron. x's are atom coodinates and r is bond length between add atom and x1.
    #ex. add atom H to C in -CH3 results in HCH3 (CH4). 
    #           |-x2        
    # add atom-x1-x3      
    #           |-x4
    u=numpy.identity(3); xr=numpy.zeros(3); xn=numpy.zeros(3)
    x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    xh1t=numpy.zeros(3); xh2t=numpy.zeros(3) 
    rad54=0.955314692
    #at=atmlst[0]
    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    x3=numpy.array(self.mol[atmlst[2]].cc)
    #r12=numpy.sqrt((x2[0]-x1[0])**2+(x2[1]-x1[1])**+(x2[2]-x1[2])**2)
    #r13=numpy.sqrt((x3[0]-x1[0])**2+(x3[1]-x1[1])**+(x3[2]-x1[2])**2)
    tmp=numpy.zeros(3)
    tmp=(numpy.subtract(x2,x1)); r12=numpy.sqrt(numpy.dot(tmp,tmp))
    tmp=(numpy.subtract(x3,x1)); r13=numpy.sqrt(numpy.dot(tmp,tmp))

    ra=numpy.subtract(x2,x1); rb=numpy.subtract(x3,x1)
    ang=lib.AngleT(ra,rb); angh=0.5*ang
    #x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    sint=numpy.sin(angh); cost=numpy.cos(angh)
    x2t[0]=r12*sint; x2t[2]=-r12*cost
    x3t[0]=-r13*sint; x3t[2]=-r13*cost
    xh1t[1]=-r*numpy.sin(rad54); xh1t[2]=r*numpy.cos(rad54)
    xh2t[1]=-xh1t[1]; xh2t[2]=xh1t[2]
    xr=[]
    xr.append(x1t); xr.append(x2t); xr.append(x3t)
    vzero=numpy.zeros(3)
    #xn=[]; xn.append(vzero); xn.append(vzero); xn.append(numpy.subtract(x3,x1))
    xn=[]
    xn.append(vzero); xn.append(numpy.subtract(x2,x1)); xn.append(numpy.subtract(x3,x1))
    u=lib.RotMatPnts(xr,xn)
    xh1=numpy.dot(u,xh1t); xh1=numpy.add(xh1,x1)
    xh2=numpy.dot(u,xh2t); xh2=numpy.add(xh2,x1)
    coord=[]; coord.append(xh1); coord.append(xh2); nh=2

    return nh,coord

def GetCCAddAtmType2A2(self,atmlst,r):
    u=numpy.identity(3); xr=numpy.zeros(3); xn=numpy.zeros(3)
    x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    xh1t=numpy.zeros(3); xh2t=numpy.zeros(3) 
    rad59=1.05068821
    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    x3=numpy.array(self.mol[atmlst[2]].cc)
    tmp=numpy.zeros(3)
    tmp=(numpy.subtract(x2,x1)); r12=numpy.sqrt(numpy.dot(tmp,tmp))
    tmp=(numpy.subtract(x3,x2)); r23=numpy.sqrt(numpy.dot(tmp,tmp))

    ra=numpy.subtract(x1,x2); rb=numpy.subtract(x3,x2)
    ang=lib.AngleT(ra,rb)
    #x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    x2t[2]=r12
    x3t[0]=r23*numpy.sin(ang); x3t[2]=r23*numpy.cos(ang)+x2t[2]
    xh1t[0]=-r*numpy.sin(rad59); xh1t[2]=-r*numpy.cos(rad59)
    xh2t[0]=-xh1t[0]; xh2t[2]=xh1t[2]
    xr=[]
    xr.append(x1t); xr.append(x2t); xr.append(x3t)
    xn=[]
    xn.append(numpy.subtract(x1,x1))
    xn.append(numpy.subtract(x2,x1))
    xn.append(numpy.subtract(x3,x1))
    u=lib.RotMatPnts(xr,xn)
    #
    xh1=numpy.dot(u,xh1t); xh1=numpy.add(xh1,x1)
    xh2=numpy.dot(u,xh2t); xh2=numpy.add(xh2,x1)
    coord=[]; coord.append(xh1); coord.append(xh2); nh=2
    #
    return nh,coord        

def GetCCAddAtmType3A1(self,atmlst,r):        
    # add three H's at sp3 atom. X3-X2-CH3 OR X3-X2-NH3(+).
    # r: bond length H-x1
    # (H3)x1-x2 with c3v symmetry. x3-x2-C-H(1) will be trans
    u=numpy.identity(3); xr=numpy.zeros(3); xn=numpy.zeros(3)
    x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
    xh1t=numpy.zeros(3); xh2t=numpy.zeros(3) 
    ex=numpy.array([-1.00000, 0.00000, 0.00000])
    ez=numpy.array([ 0.00000, 0.00000, 1.00000])
    h1=numpy.array([ 0.94281, 0.00000,-0.33333])
    h2=numpy.array([-0.47141,-0.81650,-0.33333])
    h3=numpy.array([-0.47141, 0.81650,-0.33333])

    x1=numpy.array(self.mol[atmlst[0]].cc)
    x2=numpy.array(self.mol[atmlst[1]].cc)
    #x3=list(self.mol[atmlst[2]][0])
    # scale bond length
    h1t=numpy.dot(h1,r); h2t=numpy.dot(h2,r); h3t=numpy.dot(h3,r)
    x1t=numpy.zeros(3); x2t=ez; x3t=ex 
    xr=[]; xr.append(x1t); xr.append(x2t)#; xr.append(x3t)
    xn=[]; xn.append(numpy.subtract(x1,x1))
    xn.append(numpy.subtract(x2,x1)) #; xn.append(numpy.subtract(x3,x1))
    u=lib.RotMatPnts(xr,xn)
    xh1=numpy.dot(u,h1t); xh1=numpy.add(xh1,x1)
    xh2=numpy.dot(u,h2t); xh2=numpy.add(xh2,x1)
    xh3=numpy.dot(u,h3t); xh3=numpy.add(xh3,x1)
    coord=[]; coord.append(xh1); coord.append(xh2); coord.append(xh3)
    nh=3
    #
    return nh,coord

def FindAddHType(elm,nb,nh):
    # find add h type using connect data.
    # only 'C', 'N','O' and 'S' are supported.
    htype=''; rhx=1.0
    #    
    if elm == ' C':
        if nb == 3 and nh == 1: 
            htype='1A1'; rhx=const.CovBndLen[' H C'][0]
        if nb == 2 and nh == 1:
            htype='1A2'; rhx=const.CovBndLen[' H C'][1]
        if nb == 1 and nh == 2:
            htype='2A2'; rhx=const.CovBndLen[' H C'][1]
        if nb == 2 and nh == 2:
            htype='2A1'; rhx=const.CovBndLen[' H C'][0]
        if nb == 1 and nh == 3:
            htype='3A1'; rhx=const.CovBndLen[' H C'][0]    
    elif elm == ' N':
        if nb == 2 and nh == 1:
            htype='1A2'; rhx=const.CovBndLen[' H N'][1]
        if nb == 1 and nh == 2:
            htype='2A2'; rhx=const.CovBndLen[' H N'][0]
    elif elm == ' O':
        if nb == 1 and nh == 1:
            htype='1A3'; rhx=const.CovBndLen[' H O'][0]
    elif elm == ' S':
        if nb == 1 and nh == 1:
            htype='1A3'; rhx=const.CovBndLen[' H S'][0]
    else:
        print(('sorry, element:'+elm+' is not supported.'))
        return htype,rhx
    #
    if nh > 0 and htype == '':
        mess='Program error(FindAddHtype): No addhtype is found. elm,nb,nh',elm,nb,nh
        print(mess)
    #
    return htype,rhx
    
def ReadFrameFileX(filcon):
    # 2013.2 KK
    blk=' '; blk4='    '; rcon='CONECT'; rnam='RESIDUE'
    ncon=0; condat=[]; resnam=''
    try:
        fcon=open(filcon)
    except IOError:
        print(('Error(ReadFrameFile): File not found. file name=', filcon))
    else:        
        for s in fcon.readlines():
            s=s.replace('\r','')
            s=s.replace('\n','')
            if s.startswith(rnam,0,7) == 1:
                resnam=s[10:13]
            if s.startswith(rcon,0,6) == 1:
                tmp=[]
                nl=len(s); s=s+blk*(80-nl)
                ncon += 1
                item=s.split(); del item[0] # 'CONECT'
                del item[1] # nbnd
                for i in range(len(item)):
                    if len(item[i]) < 4:
                        item[i]=' '+item[i]+'  '
                        item[i]=item[i][:4]
                condat.append(item)
        fcon.close()                           

    return resnam,condat

def FindMissingAtoms(pdbatm,resatm,framedat):
    framedic={}; misatmlst=[]
    for lst in framedat: framedic[lst[0]]=False
    for i in resatm:
        atmnam=pdbatm[i][2]
        if atmnam in framedic: framedic[atmnam]=True
    lst=list(framedic.keys())
    for atm in lst:
        if atm.strip()[:1] == 'H': continue
        if framedic[atm]: continue
        misatmlst.append(atm)
    return misatmlst

def CountNumberOfAtomsInFrame(framedat):
    nheavy=0; nhyd=0
    for i in range(len(framedat)):
        atm0=framedat[i][0]; atm0=atm0.strip()
        if atm0[:1] == 'H': nhyd += 1
        else: nheavy += 1  
    return nheavy,nhyd

def CountNumberOfAtomsInRes(pdbatm,resatm):    
    nheavy=0; nhyd=0
    for i in resatm:
        elm=pdbatm[i][10]
        if elm == ' H': nhyd += 1
        else: nheavy += 1
    return nheavy,nhyd

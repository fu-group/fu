#!/bin/sh
# -*- coding: utf-8


import os
#import sys
import wx
import wx.grid

import copy
#import shutil 
#import copy
import numpy
#import numpy
#import datetime
import fumodel
import fu_molec as molec
import const
import lib
import subwin
import rwfile
try: import fortlib
except: pass


class Geometry(object):
    def __init__(self,parent,pltwinpos=[],pltwinsize=[]):
        self.title='Geometry'
        if len(pltwinpos) <= 0: pltwinpos=lib.WinPos(parent)
        if len(pltwinsize) <= 0: pltwinsize=[640,250]
        self.pltwinpos=pltwinpos; self.pltwinsize=pltwinsize
        #
        self.mdlwin=parent
        self.model=self.mdlwin.model #self.parent.model
        #
        self.gparamlst=['Bond length','Bond angle','Hydrogen bond',
                        'Peptide angle']
        self.gparamnmb=-1
        self.gparam=''
        self.graphtype='bar'
        self.graphcolor='b'
        self.ylabel=['Angstroms','Degrees','Angstroms','Degrees']
        self.xlst=[]; self.ylst=[]; self.xvarlst=[]

        self.torad = 3.14159 / 180.0

        self.ahelixphi = -57 * self.torad
        self.ahelixpsi = -47 * self.torad
        # parallel beta strand
        self.bstrandphi1 = -119 * self.torad
        self.bstrandpsi1 = 113 * self.torad
        # anti-parallel beta strand
        self.bstrandphi2 = -139 * self.torad
        self.bstrandpsi2 = 135 * self.torad
        self.amergin = 20.0 * self.torad
        self.bmergin = 20.0 * self.torad

    def SetAlphaHelixPhiPsi(self,phi=-57.0,psi=-47.0,mergin=20.0,prt=True):
        """ Set phi and psi for alpha-helix

        :param float phi: phi(degrees) of alpha herix
        :param float psi: psi(degrees) of alpha helix
        :param float mergin: mergin(degrees) of phi and psi
        :return:
        """
        ff8 = '%8.2f'
        ff5 = '%5.2f'

        self.ahelixphi=phi
        self.ahelixpsi=psi
        self.amergin = mergin
        if prt:
            mess='Definition of alpha helix:\n'
            mess += '   alpha-herix: phi=' + (ff8 % self.ahelixphi) + '(+/-)' + (ff5 % self.amergin)
            mess += ' and psi=' + (ff8 % self.ahelixpsi) + '(+/-)' + (ff5 % self.amergin) + '\n'
            self.model.ConsoleMessage(mess)
        self.ahelixphi*=self.torad
        self.ahelixpsi*=self.torad
        self.amergin *= self.torad

    def SetBetaStrandPhiPsi(self, phi1=-119.0, psi1=113.0,phi2=-139.0,psi2=135.0,mergin=20.0,prt=True):
        """ Set phi and psi for beta-strand
            1: parallel beta strand
            2: anti-parallel beta strand
        :param float phi: phi1(degrees) of beta strand1
        :param float psi: psi1(degrees) of beta strand1
        :param float phi: phi2(degrees) of beta strand1
        :param float psi: psi2(degrees) of beta strand1
        :param float mergin: mergin(degrees) of phi and psi
        :return:
        """
        self.bstrandphi1 = phi1
        self.bstrandpsi1 = psi1
        self.bstrandphi2 = phi2
        self.bstrandpsi2 = psi2
        self.bmergin = mergin

        ff8 = '%8.2f'
        ff5 = '%5.2f'
        if prt:
            mess = 'Definition of beta strand (parallel and anti-parallel):\n'
            mess += '   parallel beta-strand: phi=' + (ff8 % self.bstrandphi1) + '(+/-)' + (ff5 % self.bmergin)
            mess += ' and psi=' + (ff8 % self.bstrandpsi1) + '(+/-)' + (ff5 % self.bmergin) + '\n'
            mess += '   anti-paralell beta-strand: phi=' + (ff8 % self.bstrandphi2) + '(+/-)' + (ff5 % self.bmergin)
            mess += ' and psi=' + (ff8 % self.bstrandpsi2) + '(+/-)' + (ff5 % self.bmergin) + '\n\n'
            self.model.ConsoleMessage(mess)

        self.bstrandphi1 *= self.torad
        self.bstrandpsi1 *= self.torad
        self.bstrandphi2 *= self.torad
        self.bstrandpsi2 *= self.torad
        self.bmergin *= self.torad

    def SetParamName(self,gparam):
        self.gparam=gparam
        try: self.gparamnmb=self.gparamlst.index(self.gparam)
        except: self.gpramnmb=-1
        
    def SetPlotData(self,xlst,ylst,varlst):
        self.xlst=xlst
        self.ylst=ylst
        self.varlst=varlst

    def SetGraphType(self,graphtype):
        self.graphtype
    
    def SetGraphColor(self,graphcolor):
        self.graphcolor=graphcolor
            
    def Plot(self,gparam):
        self.gparam=gparam
        try: self.gparamnmb=self.gparamlst.index(self.gparam)
        except: pass
        menulst=['by element(s)']
        if gparam == 'Bond length':
            self.xlst,self.ylst,self.xvarlst=self.ComputeBondLength()
        elif gparam == 'Bond angle':
            self.xlst,self.ylst,self.xvarlst=self.ComputeBondAngle()
        elif gparam == 'Hydrogen bond':
            self.xlst,self.ylst,self.xvarlst=self.ComputeHydrogenBond()
        elif gparam == 'Peptide angle':
            self.xlst,self.ylst,self.xvarlst=self.ComputePeptideAngle()
        else:
            mess='Program error: Not supported gparam='+gparam
            lib.model.Message(mess,'GeometryInspection(Plot)')        
            return
        if len(self.xlst) <= 0 or len(self.ylst) <= 0:
            mess='No data to plot.'
            lib.MessageBoxOK(mess,'GeometryInspection(Plot)')
            return
        #
        self.pltwin=subwin.PlotAndSelectAtoms(self.mdlwin,-1,self.model,
                         self.title,"other",button=True,onmolview=True,
                         resetmethod=None) #self.OnReset)
        self.pltwin.SetGraphType(self.graphtype)
        self.pltwin.SetColor(self.graphcolor)
        #
        self.pltwin.NewPlot()
        self.pltwin.PlotTitle(self.gparamlst[self.gparamnmb])
        self.pltwin.PlotXY(self.xlst,self.ylst)
        self.pltwin.PlotXLabel('Data Number')
        self.pltwin.PlotYLabel(self.ylabel[self.gparamnmb])
        self.pltwin.SetXVarData(self.xvarlst)
        if len(menulst) > 0: self.pltwin.AddExtractMenu(menulst,self.OnExtract)
    
    def ComputeBondAngle(self):
        def MakeIndex(i,j,k):
            minik=min(i,k); maxik=max(i,k)
            idx=str(minik)+'-'+str(j)+'-'+str(maxik)
            return idx,minik,j,maxik
        
        todeg=const.PysCon['rd2dg']
        xvalue=[]; yvalue=[]; xvarlst=[]
        natm=0; atmlst=[]; donedic={}
        for atom in self.model.mol.atm:
            if atom.elm == 'XX': continue # skip TER
            natm += 1; atmlst.append(atom.seqnmb)
        if natm <= 2: return xvalue,yvalue,xvarlst
        count=-1
        for i in atmlst:
            atom=self.model.mol.atm[i]
            if len(atom.conect) < 2: continue
            for j in range(len(atom.conect)-1):
                for k in range(j+1,len(atom.conect)):
                    ja=atom.conect[j]; ka=atom.conect[k]
                    idx,jj,ii,kk=MakeIndex(ja,i,ka) # i: center atom
                    if idx in donedic: continue
                    count += 1
                    xvalue.append(count)
                    cci=atom.cc[:]; ccj=self.model.mol.atm[ja].cc[:]
                    cck=self.model.mol.atm[ka].cc[:]
                    ang=lib.BendingAngle(ccj,cci,cck); ang=ang*todeg
                    yvalue.append(ang)
                    xvarlst.append([jj,ii,kk])
                    donedic[idx]=True
        return xvalue,yvalue,xvarlst
    
    def ComputeHydrogenBond(self):
        xvalue=[]; yvalue=[]; xvarlst=[]
        nhbnd,bnddic=self.model.mol.MakeHydrogenBond([])
        xvalue=list(range(nhbnd))
        for i in range(nhbnd): 
            yvalue.append(bnddic[i][2])
            xvarlst.append([bnddic[i][0],bnddic[i][1]])
        return xvalue,yvalue,xvarlst
        
    def XXComputeTorsionAngleOfPolypeptide(self,fumol,psi=True,phi=True,oemga=True,deg=True):
        """ Return peptide torsion angles
           psi:   N-Ca-C-N(+1)
           omega: Ca-C-N(+1)-Ca(+1)
           phi:   C-N(+1)-Ca(+1)-C(+1)

        :param obj fumol: fu mol object
        :return: psilst(lst),philst(lst),omglst(lst)
        """

        psilst=[] # [packed resnam,resnam+1,value]
        philst=[] # [packed resnam,resnam+1,value]
        omglst=[] # [packed resnam,resnam+1,value]


        return psilst,philst,omglst


    def ComputePeptideTorsionAngles(self,resnamlst=[],resatmlst=[],deg=True):
        """ Return torsion angle of O-C-N-H

        """
        def CheckError(resnam1,resnam2,cch,ccn,ccc,cco):
            err=''
            if cch is None: err += 'missing H(NH)'
            elif ccn is None: err += ', N(NH)'
            elif ccc is None: err += ', C(CO)'
            elif cco is None: err += ', O(CO)'
            if len(err) > 0: err+= ' in resnam1,resnam2='+resnam1+','+resnam2+'\n'
            return err

        if len(resnamlst) <= 0:
            resnamlst,resatmlst=self.model.ListResidueAtoms()
        torlst=[]
        mess=''
        for i in range(0,len(resnamlst)-1):
            resnam1=resnamlst[i]
            resnam2 = resnamlst[i+1]
            if resnam1[:3] not in const.AmiRes3: continue
            if resnam2[:3] not in const.AmiRes3: continue
            cch = None
            ccn=None
            ccc=None
            cco=None
            for j in resatmlst[i]:
                cc=self.model.mol.atm[j].cc[:]
                atmnam=self.model.mol.atm[j].atmnam.strip()
                if   atmnam == 'C': ccc=cc[:]
                elif atmnam == 'O': cco=cc[:]
            for j in resatmlst[i+1]:
                cc=self.model.mol.atm[j].cc[:]
                atmnam=self.model.mol.atm[j].atmnam.strip()
                if resnam2[:3] == 'PRO':
                    if atmnam == 'CD': cch=cc[:]
                else:
                    if atmnam == 'H': cch=cc[:]
                if atmnam == 'N': ccn=cc[:]

            errmess=CheckError(resnam1,resnam2,cch,ccn,ccc,cco)
            if len(errmess) > 0:
                mess+=errmess
                continue
            torang=lib.TorsionAngle(cco,ccc,ccn,cch,deg)
            torlst.append([resnam1,resnam2,torang])
        return torlst,mess

    def CheckPeptideTorsionAngles(self,resnamlst=[],resatmlst=[],maxdev=10.0):
        """

        """
        if len(resnamlst) <= 0:
            resnamlst,resatmlst=self.model.ListResidueAtoms()
        #cisdevlst=[]
        devlst=[]
        torlst,mess=self.ComputePeptideTorsionAngles(resnamlst=resnamlst,resatmlst=resatmlst,deg=True)
        for res1,res2,angle in torlst:
            resn1=int(res1.split(':')[1])
            resn2=int(res2.split(':')[1])
            if abs(resn1-resn2) != 1: continue
            tdev=abs(angle)-180.0
            #cdev = abs(angle)
            #if abs(angle) >= 90.0:
            if abs(tdev) > maxdev: devlst.append([res1,res2,angle])
            #else:
            #    if cdev > maxdev: cisdevlst.append([res1, res2, angle])
        return devlst,mess

    def PrintPeptidePhiPsiAngles(self,calcdeg=True) :
        # phi is the dihedral angle of C(i-1)-N(i)-Ca(i)-C(i),
        # psi is the dihedral angle of N(i)-Ca(i)-C(i)-N(i+1),
        # omega is the dihedral angle of Ca(i)-C(i)-N(i+1)-Ca(i+1)
        blk = 3*' '
        ff8 = '%8.2f'
        ff5 = '%5.2f'
        fi4 = '%4d'

        nres,resdic=self.model.CountResidues(messout=False)
        if nres <= 2:
            mess='No or less than 2 amino acid residues are selected'
            wx.MessageBox(mess,'geom.PrintPeptidePhiPsiAngles')
            return

        text='Peptide angles phi and psi(degrees):\n'
        text+='Molecule file="'+self.model.mol.inpfile+'"\n\n'

        text+='phi is the dihedral angle of C(i-1)-N(i)-Ca(i)-C(i) and\n'
        text += 'psi is the dihedral angle of N(i)-Ca(i)-C(i)-N(i+1)\n'
        text+='"999" indicates failure\n\n'

        todeg = 180.0 / 3.14159
        text+='Definition of alpha-helix and beta-strand(parallel and anti-parallel) are,\n'
        text+='   alpha-herix: phi='+(ff8 % (self.ahelixphi*todeg))+'(+/-)'+(ff5 % (self.amergin*todeg))
        text+=' and psi='+(ff8 % (self.ahelixpsi*todeg))+'(+/-)'+(ff5 % (self.amergin*todeg))+'\n'
        text+='   paralell beta-strand: phi='+(ff8 % (self.bstrandphi1*todeg))+'(+/-)'+(ff5 % (self.bmergin*todeg))
        text += ' and psi=' + (ff8 % (self.bstrandpsi1*todeg)) + '(+/-)' + (ff5 % (self.bmergin*todeg)) + '\n'
        text+='   anti-paralell beta-strand: phi='+(ff8 % (self.bstrandphi2*todeg))+'(+/-)'+(ff5 % (self.bmergin*todeg))
        text += ' and psi=' + (ff8 % (self.bstrandpsi2*todeg)) + '(+/-)' + (ff5 % (self.bmergin*todeg)) + '\n\n'

        phipsilst=self.PeptidePhiPsiAngles(calcdeg=True,secndstruct=True)
        text+='   res i-1   res i     res i+1       phi       psi         secondary structure\n'
        text+='------------------------------------------------------------------------------\n'
        for prvresdat,resdat,nxtresdat,phi,psi,sstruct in phipsilst:
            if phi == 999.0 and psi == 999.0: continue
            text+=blk+prvresdat+blk+resdat+blk+nxtresdat+blk+(ff8 % phi)+blk+(ff8 % psi)+4*blk+sstruct+'\n'

        winsize=[500,400]
        subwin.TextBox_Frm(self.mdlwin, winsize = winsize, title = 'Peptide angles', text = text,
                           ok = False, cancel = False, yes = False, no = False, retmethod = None)

    def PeptidePhiPsiAngles(self,calcdeg=True,secndstruct=False) :
        """ Return phi and psi torsion angles

        :param calcdeg:
        :return: phipsilst(lst) - [[resi-1,resi,res+1,phi,psi],...]
        """
        pepatmlstlst=self.model.ExtractPeptides()
        pepatmslst=[]
        npep=len(pepatmlstlst)
        for i in range(npep):
            atmlst=pepatmlstlst[i][:]
            nres,resdic=self.model.CountResidues( trgatmlst=atmlst, messout=False)
            if nres > 2:
                pepatmslst.append(atmlst)

        phipsilst=[]
        reslst=self.model.ListResDat()

        for i in range(1,len(reslst)-1):
            resdat=reslst[i]
            prvresdat=reslst[i-1]
            nxtresdat=reslst[i+1]
            if resdat[:3] not in const.AmiRes3: continue
            if prvresdat[:3] not in const.AmiRes3: continue
            if nxtresdat[:3] not in const.AmiRes3: continue
            phi,psi,sstruct=self.CalcPeptidePhiPsi(resdat, prvresdat,nxtresdat, calcdeg=calcdeg,secndstruct=secndstruct)
            phipsilst.append([prvresdat,resdat,nxtresdat,phi,psi,sstruct])
        return phipsilst

    def CalcPeptidePhiPsi(self,resdat, prvresdat, nxtresdat, calcdeg=True,secndstruct=False):
        """

        # phi is the dihedral angle of C(i-1)-N(i)-Ca(i)-C(i),
        # psi is the dihedral angle of N(i)-Ca(i)-C(i)-N(i+1),
        # cf.  omega is the dihedral angle of Ca(i)-C(i)-N(i+1)-Ca(i+1)
        """
        phi = 999 # indicates failed
        psi = 999

        resatmlst=[]
        prvresatmlst=[]
        nxtresatmlst=[]
        for i in range(len(self.model.mol.atm)):
            atom=self.model.mol.atm[i]
            res=lib.ResDat(atom)
            if res == resdat:
                resatmlst.append(i)
            elif res == prvresdat:
                prvresatmlst.append(i)
            elif res == nxtresdat:
               nxtresatmlst.append(i)

        if len(resatmlst) <= 0:
            wx.MessageBox('No atoms in resdat='+resdat,'CalcPeptidePhiPsi')
            return
        #
        pccc=None
        ncc=None
        cacc=None
        ccc=None
        nncc=None
        if len(prvresatmlst) >= 0:
            for i in prvresatmlst:
                if self.model.mol.atm[i].atmnam.strip() == "C":
                    pccc = self.model.mol.atm[i].cc[:]
                    break
        for i in resatmlst:
            if self.model.mol.atm[i].atmnam.strip() == "N":
                # print ' N2  found'
                ncc = self.model.mol.atm[i].cc[:]
                break
        for i in resatmlst:
            if self.model.mol.atm[i].atmnam.strip() == "CA":
                # print ' CA3  found'
                cacc = self.model.mol.atm[i].cc[:]
                break
        for i in resatmlst:
            if self.model.mol.atm[i].atmnam.strip() == "C":
                # print ' C4  found'
                ccc = self.model.mol.atm[i].cc[:]
                break
        if len(nxtresatmlst) >= 0:
            for i in nxtresatmlst:
                if self.model.mol.atm[i].atmnam.strip() == "N":
                    nncc = self.model.mol.atm[i].cc[:]
                    break
        #
        if pccc is not None and ncc is not None and cacc is not None and ccc is not None:
            phi = lib.TorsionAngle(pccc, ncc, cacc, ccc)
            #phi = lib.TorsionAngle(ccc, cacc, ncc,pccc)
        if ncc is not None and cacc is not None and ccc is not None and nncc is not None:
            psi = lib.TorsionAngle(ncc, cacc, ccc, nncc)
            #psi = lib.TorsionAngle(nncc, ccc, cacc, ncc)
        # compute secandary structure
        sstruct=None
        if secndstruct:
            """
            torad = 3.14159/180.0
            ahelixphi = -57*torad
            ahelixpsi = -47*torad
            bstrandphi1 = -119*torad
            bstrandpsi1 = 113*torad
            bstrandphi2 = -139*torad
            bstrandpsi2 = 135*torad
            amergin = 20.0*torad
            bmergin = 20.0*torad
            """
            sstruct='random-coil'
            if abs(phi - self.ahelixphi) < self.amergin and abs(psi - self.ahelixpsi) < self.amergin:
                sstruct='alpha-helix'
            elif abs(phi - self.bstrandphi1) < self.bmergin and abs(psi - self.bstrandpsi1) < self.bmergin:
                sstruct='beta-strand'
            elif abs(phi - self.bstrandphi2) < self.bmergin and abs(psi - self.bstrandpsi2) < self.bmergin:
                sstruct = 'beta-strand'

        # to degrees
        if calcdeg:
            todeg = 180.0 / 3.14159
            if phi != 999: phi*=todeg
            if psi != 999: psi*=todeg

        return phi, psi, sstruct

    def SecondaryStructureOfProtein(self,trgatmlst=[],amergin=20.0,bmergin=20.0,rmvshorthelix=False):
        """  Return list of secondary structures
        secondary structure         phi  psi
        ------------------------------------
        [alpha herix]
        right-hand alpha helix:    -57   -47
        left-hand alpha helix:       57   47
        [beta strand]
        parallel beta strand:      -119  113
        anti-parallel beta strand: -139  135
        [others]
        right-hand 3(10) helix:     -49  -26
        right-hand pi helix:        -57  -70
        2.2(7) ribon:               -78   59
        random coil

        :return: alphaherixlst(lst),betastandlst(lst),otherlst(lst) - [[resdatm...],[resdat,...]],
        """
        def RemoveShortHelix(ahelixlst):
            #ahelixlst.append([prvresdat, resdat, nxtresdat])
            shortlst=[]
            newlst=[]
            chaindic={}
            ig=0
            chaindic[0]=[]
            nhelix=len(ahelixlst)
            for i in range(nhelix-1):
                curnmb=int(ahelixlst[i][1].split(':')[1])
                nxtnmb=int(ahelixlst[i+1][1].split(':')[1])
                if nxtnmb-curnmb <= 1:
                    chaindic[ig].append(i)
                else:
                    ig+=1
                    chaindic[ig]=[i]
            ng=len(chaindic)
            for i in range(ng):
                if len(chaindic[i]) <= 4: # a trun of alpha-helix require 4 residues
                    shortlst+=chaindic[i][:]
            #shortlst.append(nhelix)
            #shortlst.append(0)
            oldlst=copy.deepcopy(otherlst)
            #print ('shortlst=',shortlst)

            if len(shortlst) >= 0:
                for i in range(len(ahelixlst)):
                    if not i in shortlst:
                        newlst.append(ahelixlst[i])
                    #else:
                    #    otherlst.append(ahelixlst[i][:])
            #print('ahelixlst before remove=', ahelixlst)
            #print('ahelixlst after remove=',newlst)
            #print('other before remove=', oldlst)
            #print('other after remove=', otherlst)
            ahelixlst=newlst


            return newlst

        if len(trgatmlst) <= 0:
            trgatmlst=self.model.ListTargetAtoms()

        phipsilst=self.PeptidePhiPsiAngles(calcdeg=True,secndstruct=True)
        """
        ahelixphi = -57
        ahelixpsi = -47
        bstrandphi1 = -119
        bstrandpsi1 =  113
        bstrandphi2 = -139
        bstrandpsi2 =  135
        """
        ahelixlst =[]
        bstrandlst=[]
        otherlst  =[]
        for prvresdat,resdat,nxtresdat,phi,psi,sstruct in phipsilst:
            ok=False
            #if abs(phi - ahelixphi) < amergin and abs(psi - ahelixpsi) < amergin:
            if sstruct == 'alpha-helix':
                ahelixlst.append([prvresdat, resdat, nxtresdat])
                ok=True
            elif sstruct == 'beta-strand':
            #elif abs(phi - bstrandphi1) < bmergin and abs(psi - bstrandpsi1) < bmergin:
                bstrandlst.append([prvresdat, resdat, nxtresdat])
                ok=True
            #else:
            #    otherlst.append([prvresdat, resdat, nxtresdat])

        if rmvshorthelix:
            newlst=RemoveShortHelix(ahelixlst)
            ahelixlst=copy.deepcopy(newlst)
            otherlst=[]
            for prvresdat,resdat,nxtresdat,phi,psi,sstruct in phipsilst:
                if [prvresdat,resdat,nxtresdat] in ahelixlst: continue
                if [prvresdat, resdat, nxtresdat] in bstrandlst: continue
                otherlst.append([prvresdat, resdat, nxtresdat])

        #print('ahelixlst=',ahelixlst)
        return ahelixlst,bstrandlst,otherlst

    def PrintNonPlanerPeptideBonds(self, maxdev=None,prtdevmax=True):
        def NamList(atmlst):
            namlst=[]
            for i in atmlst:
                resdat=lib.ResDat(self.model.mol.atm[i])
                if not resdat in namlst:
                    namlst.append(resdat)
            return namlst
        defval='10.0'
        if maxdev is None:
            tiptext='Input deviation angle threshold in degrees, default='+defval
            text=wx.GetTextFromUser(tiptext,'geom.PrintNonPlanerPeptideBonds')
            text=text.strip()
            if len(text) <= 0:
                text=defval
            try:
                maxdev=float(text)
            except:
                wx.MessageBox('Wrong input data. '+text,'PrintNonPlanerPeptideBonds')
                return

        text='Non-planer peptide bonds:\n'
        text+='Molecule file="'+self.model.mol.inpfile+'"\n\n'

        pepatmlstlst=self.model.ExtractPeptides()

        pepatmslst=[]
        pepnamlst=[]
        npep=len(pepatmlstlst)
        for i in range(npep):
            atmlst=pepatmlstlst[i][:]
            nres,resdic=self.model.CountResidues( trgatmlst=atmlst, messout=False)
            if nres > 2:
                pepatmslst.append(atmlst)

        #print('Number of peptide chains which are longer than 2=',len(pepatmslst))
        text+='Number of peptide chains which are longer than 2='+str(len(pepatmslst))+'\n\n'
        mess=''
        devlst=[]
        for atmlst in pepatmslst:
            namlst=NamList(atmlst)
            namlst, atmlst = self.model.ListResidueAtoms(trgatmlst=atmlst)
            devlst0, mess0=self.CheckPeptideTorsionAngles(resnamlst=namlst,resatmlst=atmlst,maxdev=maxdev)
            mess+=mess0
            devlst+=devlst0

        ff8 = '%8.2f'
        fi4 = '%4d'
        cislst=[]
        tranlst=[]
        for res1,res2,torang in devlst:
            if abs(torang) < maxdev: cislst.append([res1,res2,torang])
            else: tranlst.append([res1,res2,torang])
         #print ('Number of deviated peptide torsions from 180 degrees=',len(tranlst))
        i=0
        if len(tranlst) <= 0:
            #print ('No peptide bond whose torsion angle(omega, O-C-N-H) is deviated more than '+str(maxdev)+' degrees')
            text+='No peptide bond whose torsion angle(omega, O-C-N-H) is deviated more than '+str(maxdev)+' degrees\n'
        else:
            #print ('Peptide bond angles(omega, O-C-N-H) which are deviated more than '+str(maxdev)+' degrees;')
            text+='Peptide bond angles(omega, O-C-N-H) which are deviated more than '+str(maxdev)+' degrees;\n'
            maxval=0.0
            for res1,res2,angle in tranlst:
                #i+=1
                #text+=(fi4 % i)+' '+res1+'(O-C)  '+res2+'(N-H) '+(ff8 % angle)+' dev= '+(ff8 % (180.0-abs(angle)))+'\n'
                if abs(abs(angle)-180.0) > maxdev:
                    i += 1
                    # print (fi4 % i),res1+'(O-C)',res2+'(N-H)',(ff8 % angle), 'dev=',(ff8 % (180.0-abs(angle)))
                    text += (fi4 % i) + ' ' + res1 + '(O-C)  ' + res2 + '(N-H) ' + (ff8 % angle) + ' dev= ' + (
                                ff8 % (180.0 - abs(angle))) + '\n'
                    val=abs(abs(angle)-180.0)
                    if val > maxval:
                        maxi=i
                        maxval=val
                        maxres1=res1
                        maxres2=res2

            if prtdevmax:
                #print '  max. deviated angle=',(ff8 % maxval), 'of ', maxi,maxres1,maxres2,
                text+='  max. deviated angle='+(ff8 % maxval)+ ' of '+ str(maxi)+'-'+str(maxres1)
                text+= ','+str(maxres2)+'\n\n'

        if len(cislst) <= 0:
            #print('\nNo cis peptide bond O-C-N-H')
            text+='No cis peptide bond\n'
        else:
            #print('\nCis peptide bond torsion angle(omega, O-C-N-H);')
            text+='Cis peptide bond torsion angle(omega, O-C-N-H);\n'
            i=0
            for res1,res2,angle in cislst:
                i+=1
                print(((fi4 % i),res1+'(O-C)',res2+'(N-H)',(ff8 % angle)))
                text+=(fi4 % i)+' '+res1+'(O-C)'+' '+res2 +'(N-H)'+' '+(ff8 % angle)

        #print('text=',text)
        winpos=lib.WinPos(self.model.mdlwin)
        winsize=[500,400]
        subwin.TextBox_Frm(self.mdlwin, winpos=winpos,winsize = winsize, title = 'Non palner peptide angles', text = text,
                           ok = False, cancel = False, yes = False, no = False, retmethod = None)

    def ComputeBondLength(self,rmin=-1,rmax=-1):
        def BondIdx(i,j):
            minij=min(i,j); maxij=max(i,j)
            idx=str(minij)+':'+str(maxij)
            return idx
                
        xvalue=[]; yvalue=[]; xvarlst=[]
        natm=len(self.model.mol.atm); npair=0; donedic={}
        # fortran code
        try:
            if rmin < 0: rmin=0.5
            if rmax < 0: rmax=3.0
            cc=[]; iopt=0
            for i in range(natm): cc.append(self.model.mol.atm[i].cc[:])
            cc=numpy.array(cc)
            npair,iatm,jatm,rij=fortlib.find_contact_atoms2(cc,rmin,rmax,iopt)
            count=-1
            for k in range(npair):
                i=iatm[k]; j=jatm[k]; r=rij[k]
                if self.model.mol.atm[i].elm == 'XX': continue
                if self.model.mol.atm[j].elm == 'XX': continue
                if not j in self.model.mol.atm[i].conect: continue
                idx=BondIdx(i,j)
                if idx in donedic: continue
                count += 1
                xvalue.append(count)
                yvalue.append(r)
                xvarlst.append([i,j])
                donedic[idx]=True
        except:
            mess='Model:ComputeBondDistance: running python code'
            self.model.ConsoleMessage(mess)
            count=-1
            for i in range(natm):
                if self.model.mol.atm[i].elm == 'XX': continue
                cci=self.model.mol.atm[i].cc[:]
                for j in self.model.mol.atm[i].conect:
                    idx=BondIdx(i,j)
                    if idx in donedic: continue
                    #itemj=AtomItem(j); 
                    ccj=self.model.mol.atm[j].cc[:]
                    r=lib.Distance(cci,ccj)                
                    count += 1
                    xvalue.append(count)
                    yvalue.append(r)
                    xvarlst.append([i,j])
                    donedic[idx]=True  
        return xvalue,yvalue,xvarlst

    def OnExtract(self,item,xvarlst):
        extracted=[]
        if item == 'by element(s)':
            tiptext='Input element(s), e.g., "C","H",...'
            text=wx.GetTextFromUser(tiptext,'GeometryInspect(OnEctract)')
            text=text.strip()
            if len(text) <= 0: return
            items=lib.SplitStringAtSpacesOrCommas(text)
            elmlst=[]; sellst=[]
            for s in items:
                elm=lib.ElementNameFromString(s)
                elmlst.append(elm)
            #if len(elmlst) > 0:
            if self.gparam == 'Bond length' or self.gparam == 'Hydrogen bond':
                for i in range(len(xvarlst)):
                    j=xvarlst[i][0]; k=xvarlst[i][1]
                    elmj=self.model.mol.atm[j].elm
                    elmk=self.model.mol.atm[k].elm
                    if len(elmlst) == 1:
                        if elmj == elmlst[0] or elmk == elmlst[0]:
                            extracted.append(i)
                    elif len(elmlst) >= 2:
                        if (elmj == elmlst[0] and elmk == elmlst[1]) or \
                                (elmj == elmlst[1] and elmk == elmlst[0]): 
                            extracted.append(i)
            elif self.gparam == 'Bond angle':
                for i in range(len(xvarlst)):
                    j=xvarlst[i][0]; k=xvarlst[i][1]; l=xvarlst[i][2]
                    elmj=self.model.mol.atm[j].elm
                    elmk=self.model.mol.atm[k].elm
                    elml=self.model.mol.atm[l].elm
                    if len(elmlst) == 1:
                        if elmj == elmlst[0] or elmk == elmlst[0] or \
                                   elml == elmlst[0]:
                            extracted.append(i)
                    elif len(elmlst) >= 2:
                        elmtmp=elmlst[:]
                        if elmj in elmtmp:
                            elmtmp.remove(elmj)
                            if elmk in elmtmp:
                                elmtmp.remove(elmk)
                            if len(elmlst) == 2:
                                extracted.append(i); continue
                            if elml in elmtmp: extracted.append(i)                        
            return extracted
        else:
            mess='Wrong menu item='+item
            lib.MessageBoxOK(mess,'GeometryInspection(OnExtract)')
            return []
        
    def OnReset(self,event):
        const.CONSOLEMESSAGE('OnReset')

#!/bin/sh
# -*- coding: utf-8 -*- 
#
# -----------------
# Script: fu-qeq.py
# -----------------
# function: run the charge equibration(QEq) method
# usage: This script is executed in the PyShell consolel of fu.
#        >>> fum.ExecuteAddOnScript('fu-qeq.py',False)
#
# change history
# 2015/12/01 - the first version
# 2020/12/16 - refactored

import sys
sys.path.insert(0,'../src')
import os
import time

import numpy
from scipy import linalg

import fumodel
import rwfile
import lib
try: import fortlib
except: pass 

class QEq():
    """ Charge equilibration method:
        A. K. Pappe and W. A. Goddard III, J.Phys.Chem.,3358(1991).
        modified to use NM-gamma for electron-electron repulsion:
        T.Nakano,T.Kaminuma,M.Uebayasi,Y.Nakata, Chem-Bio Info.J.,1,35(2001).

    Example usage:
        qeq=QEq(xyzfile='h2o.xyz',title='title',charge=0,prmfile=None,chgfile=None,messmethod=None)

    :param str title: title
    :param float charge: total charge of molecule. default:0
    :param lst xyzfile: Cartesian coordinate file, e.g. h2o.xyz
    :param str prmfile: parameter file to add/replace internal parameters
    :param str chgfile: output file name of atom charges.
    :param obj messmethod: method of output message with one arg, message(str).

    Example of files:
        prmfile='C://FUDATASET-0.5.3//FUdata//qeq.prm'  <--- same as internal parameters
        xyzfile='C://FUDATASET-0.5.3//FUdocs//data//h2o.xyz'
        chgfile='C://FUDATASET-0.5.3//FUdocs//data//h2o.chg'
    """
    def __init__(self, xyzfile=None, title='QEq calculations', charge=0, prmfile=None, chgfile=None, messmethod=None):
        #
        self.prgnam='fu-qeq ver.0.1'
        self.title=title
        self.messmethod=messmethod
        if not os.path.exists(xyzfile):
            mess='the xyzfile file "'+xyzfile+'" does not exists.'
            self.Message('rwfile.ReadQEqParams: '+mess)
            self.Quit()

        self.xyzfile=xyzfile
        self.coordfile=xyzfile
        self.chgfile=chgfile
        
        self.charge=charge
        self.scale=1.0
        self.prmdic=self.QEqParams()
        if prmfile is not None:
            errmess, prmdic = rwfile.ReadQEqParams(prmfile)
            self.prmdic.update(prmdic)
            if len(errmess) > 0:
                self.Message('rwfile.ReadQEqParams: '+errmess)
                self.Quit()

        self.xyzatm,bonds,resfrg=rwfile.ReadXYZMol(xyzfile)
        self.natm=len(self.xyzatm)
        self.elm=self.CheckParams()       
        self.resnam=lib.MakeMolNamFromFileName(self.coordfile)
        self.resnam=self.resnam.upper()
        
        self.time1=time.clock()
        self.distlst=self.ComputeDistance()
        self.q=self.SolveQEqEq()
        self.time2=time.clock()

        self.PrintResults()

        if chgfile is not None:
            self.WriteAtomCharges(self.chgfile,title=self.title)
            self.Message('partial charges were saved on file='+self.chgfile)

    def CheckParams(self):
        """ Check for QEq parameters

        :return: an(lst) - list of paramters for atomic number
        """
        an=[]
        for i in range(self.natm):
            elm=self.xyzatm[i][0]
            if elm not in self.prmdic:
                mess='Not found QEq parameter for element='+elm+'\n'
                mess=mess+'Define the parameter in the "FUDATASET//FUdata//qeq.prm" file.'
                self.Message('QEq.CheckParams: '+mess)
                self.Quit()
            an.append(elm)
        return an

    def Message(self,mess):
        """ Print out message

        :param str mess: message
        """
        if self.messmethod is not None:
            self.messmethod(mess)
        else:
            print(mess)

    def SolveQEqEq(self):
        """ Solve the QEq eqation

        :return: q(lst) - list of atom charges
        """
        f=0.529917724*27.2113845 # =14.42 bohr*au2ev
        #
        b=self.natm*[0.0]
        b[0]=self.charge
        an0=self.elm[0]
        chi0=self.prmdic[an0][0]
        for i in range(1,self.natm):
            ani=self.elm[i]
            b[i]=self.prmdic[ani][0]-chi0
        #
        a=[]
        a.append(self.natm*[1.0])
        lst=self.natm*[0.0]
        for i in range(1,self.natm): a.append(lst[:])
        j0=self.prmdic[an0][1]
        for i in range(1,self.natm):
            ani=self.elm[i]; ji=self.prmdic[ani][1]
            for j in range(self.natm):
                anj=self.elm[j]
                jj=self.prmdic[anj][1]
                r0j=self.distlst[0][j]
                rij=self.distlst[j][i]
                # g: NM-gamma
                d0j=2.0*f/(j0+jj); g0j=f/(r0j+d0j)
                dij=2.0*f/(ji+jj); gij=f/(rij+dij)
                a[i][j]=g0j-gij
        # solve simultaneous linear equation 
        a=numpy.array(a);
        b=numpy.array(b)
        #q=numpy.linalg.solve(a,b)
        q=linalg.solve(a,b)
        return q
        
    def ComputeDistance(self):
        """ Compute distances

        :return: distlst(lst) - list of distances, distlst[i][j] : distance between i- and j-atom
        """
        distlst=[]; lst=self.natm*[0.0]
        for i in range(self.natm): distlst.append(lst[:])
        #
        try:
            cc=[]; k=-1
            for i in range(self.natm): 
                cc.append([self.xyzatm[i][1],self.xyzatm[i][2],self.xyzatm[i][3]])
            cc=numpy.array(cc)
            rij=fortlib.distance(cc,0)
            for i in range(self.natm-1):
                for j in range(i+1,self.natm):
                    k += 1
                    distlst[i][j]=rij[k]; distlst[j][i]=rij[k]
        except:
            self.Message('Running Python code ...')
            for i in range(1,self.natm):
                xi=self.xyzatm[i][1]; yi=self.xyzatm[i][2]; zi=self.xyzatm[i][3]
                for j in range(i):
                    xj=self.xyzatm[j][1]; yj=self.xyzatm[j][2]; zj=self.xyzatm[j][3]
                    r=numpy.sqrt((xi-xj)**2+(yi-yj)**2+(zi-zj)**2)
                    distlst[i][j]=r; distlst[j][i]=r
        return distlst
    
    def DipoleMoment(self):
        """ Calculate dipole moment

        :return: d(float) - total dipole moment(debye)
                 mu(lst) -  components of dipole moment(debye)
        """
        debbohr=2.541747761/0.529917724 # debye/bohr
        mu=[0.0,0.0,0.0]
        cntr=[0.0,0.0,0.0]
        chg=self.charge
        if self.charge != 0.0:
            for i in range(3):
                for j in range(self.natm):
                    cntr[i] += self.q[j]*self.xyzatm[j][i+1]
            cntr=[x/chg for x in cntr]
        # dipole moment
        for i in range(3):
            for j in range(self.natm):
                mu[i] += self.q[j]*(self.xyzatm[j][i+1]-cntr[i])
        mu=[x * debbohr for x in mu]
        d=numpy.sqrt(mu[0]**2+mu[1]**2+mu[2]**2)
        return d,mu

    def PrintResults(self,prtchg=True):
        """ Print results

        :param bool prtchg: True to print atom partial charges False otherwise
        """
        ff83='%8.3f'
        qt=0.0
        for i in range(self.natm): qt=qt+self.q[i]
        #self.Message('atom charges='+str(self.q))
        if abs(qt-self.charge) > 0.001:
            mess='QEq calculation failed. input charge='+str(self.charge)+'and computed total charge='+str(qt)
            self.Message('Qeq.WriteAtomCharges: '+mess)
        else:
            if prtchg:
                self.Message('Partial charges obtained by the modified QEq method(NM-Gamma is used):')
                self.Message('xyzfile='+self.xyzfile)
                for i in range(self.natm):
                    self.Message(str(i+1)+', '+self.xyzatm[i][0]+', '+str(self.q[i]))
        self.Message('Total Charge='+str(qt))

        # compute dipole moment
        d,mu=self.DipoleMoment()
        self.Message('Dipole moment(Debye)='+ff83 % d+' ('+ff83 % mu[0]+','+ff83 % mu[1]+','+ff83 % mu[2]+')')
        if self.charge != 0.0:
            self.Message('The molecule is charged! So, the dipole moment is calculated at center-of-charge')
        etime=self.time2-self.time1
        self.Message('Elapsed time(sec.): '+ff83 % etime)
    
    def WriteAtomCharges(self,chgfile,title=''):
        """ write QEq charges to file

        :param str chgfile: output file name
        :param str title: comment
        """
        ff8='%10.6f'; fi4='%4d'; fi2='%2d'; blk5=5*' '
        text='# Atomic partial charges created by fu at '+lib.DateTimeText()+'\n'
        text=text+'# Program: '+self.prgnam+'\n'
        if len(title) >= 0: text=text+'# '+title+'\n'
        text=text+'# coordinate file='+self.coordfile+'\n'
        text=text+'# number of atoms='+str(self.natm)+'\n'
        text=text+'NAME   = '+self.resnam+'\n'
        text=text+'CHARGE = '+ff8 % self.charge+'\n'
        text=text+'SCALE  = '+ff8 % self.scale+'\n'
        text=text+'#\n'
        text=text+'# format: sequence number,element, partial charge\n'
        text=text+'#\n'
        chgtext=''
        for i in range(len(self.xyzatm)):
            chgtext=chgtext+fi4 % (i+1)+blk5
            chgtext=chgtext+self.xyzatm[i][0]+blk5
            chgtext=chgtext+ff8 % self.q[i]+'\n'
        text=text+chgtext
        #
        with open(chgfile,'w') as f:
            f.write(text)

    def Quit(self):
        #self.Destroy()
        exit()

    def QEqParams(self):
        """ Default QEq parameters

        :return: paramdic(dic) - dictionary of parameters, {elment_symbol:[chi,j],...}
                                 chi and J are in eV.

        Reference: A.K.Rappe, W.A.Goddard III,J.Phys.Chem.95,3358(1991).
        """
        paramdic={
        " H": [4.5280, 13.8904],
        # H 4.7174  13.4725   # H for comparering Hartree-Fock ESP charges
        "LI": [ 3.006,  4.772],
        " C": [ 5.343, 10.126],
        " N": [ 6.899, 11.760],
        " O": [ 8.741, 13.364],
        " F": [10.874, 14.948],
        "NA": [ 2.843,  4.592],
        "SI": [ 4.168,  6.974],
        " P": [ 5.463,  8.000],
        " S": [ 6.928,  8.972],
        "CL": [ 8.564,  9.892],
        " K": [ 2.421,  3.84],
        "BR": [ 7.790,  8.850],
        "RB": [ 2.331,  3.692],
        " I": [ 6.822,  7.524],
        "CS": [ 2.183,  3.422]
        }
        return paramdic

#---- test run ----
prmfile = 'C://FUDATASET-0.5.3//FUdata//qeq.prm'
xyzfile = 'C://FUDATASET-0.5.3//FUdocs//data//h2o.xyz'
chgfile='e://ATEST//h2o-qeq.out'

qeq=QEq(xyzfile=xyzfile,prmfile=None,chgfile=chgfile,messmethod=None)
# The result will be,
#Partial charges obtained by the modified QEq method(NM-Gamma is used):
#xyzfile=C://FUDATASET-0.5.3//FUdocs//data//h2o.xyz
#1,  O, -0.466927678167354
#2,  H, 0.23350124831941577
#3,  H, 0.23342642984793813
#Total Charge=-8.326672684688674e-17
#Dipole moment(Debye)=   1.406 (  -1.222,  -0.544,  -0.434)
#Elapsed time(sec.):    0.000

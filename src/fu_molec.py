#!/bin/sh
# -*- coding: utf-8



import numpy
import os
import datetime
import copy
import wx
import networkx

from lib2to3.fixer_util import Number
from scipy.constants.constants import atm

import sys
sys.path.insert(0,'.')
# fu modules
import const
import rwfile
import lib
#import fu_crystal
import build
try: import fortlib
except: pass

###import draw
###import frag

class Molecule(object):
    def __init__(self,parent,messout1=None,messout2=None):
        """

        param obj messout1: Status message method object
        param obj messout2: Console message method object
        """

        classnam = 'Molecule'
        self.parent = parent
        self.model  = parent
        #self.setctrl = self.model.setctrl
        self.messout1 = messout1 # output method object
        self.messout2 = messout2 # output method object
        #r# self.parent=parent
        #r# try: self.frame=parent.frame
        #r# except: pass
        self.name = '' # name of molecule, made from input file name
        self.inpfile = '' # input file name
        self.outfile = '' # save file name
        self.inpform = '' # pdb,xyz,fmoinp,gmsinp,zmt
        self.mergedfile = ''
        self.mergedmolname = ''
        self.remark = '' # comment
        # atoms
        self.atm = [] # list of atom instance
        # change default draw parameters of atom
        # The default params are defined in the Atom class

        #2020/11/07/ self.elmcolordic = None #self.model.setctrl.elmcolordic #None
        self.elmcolordic = self.model.setctrl.elmcolordic #None
        self.vdwraddic   = self.model.setctrl.vdwraddic #None
        self.atomradius  = self.model.setctrl.atomradius #None
        self.bondthick   = self.model.setctrl.bondthick #None
        self.bondthickbs = self.model.setctrl.bondthickbs #None
        self.molmodel    = self.model.setctrl.molmodel #None
        self.envatmcolor = [0.68,0.02,0.64,1.0]

        #
        self.zmtpnt = []
        self.zvardic = {}
        self.zactivedic = {}
        #self.zmtdic={} # for symbolic z-matrix
        #
        self.nter = 0
        #
        self.bdadic = {} # for fragmentation
        self.frgattribdic = None #{} # {frgnam:[charge,layer,active,spin],..}
        #XX
        self.sdfdata  = {}
        self.mol2data = {}
        ###self.frgobj=frag.Fragment(self.model)
        #self.cifdata = {}
        self.boxpnts    = None # 4 * [a-vec,bvec,c-vec]
        self.crystalobj = None
        #
        self.cubeobj = None
        #
        self.mdlgrpdic = {} # group data for modeling, {grpnam:[atmlst,charge,??,..},}
        # attribute dictonary for extension for use in external script
        self.attribdic = {} # reserved for future
        # draw paramters
        self.drwdumpitems = {}
        self.drwdumpitems['viewpos'] = True
        #
        self.fogscale = 5.0 # fog strength. 0-20.
        # parameters for view
        self.drwobjs = {}
        self.viewitems = {}
        self.showdic = {}

        self.showmenulst=["Selected only",
                          "Side chain only",
                           "Backbone only",
                           "All atom ",
                           "Hide selected",
                           "Hide hydrogen",
                           "Hide water",
                           "Hide AA side chains",
                           "Hide all atoms"]

    def ShowAtomItem(self,item):
        """  'Show' menu item status
         item:'Backbone only' 
        """
        if item in self.showdic: return self.showdic[item]        
        else: return False

    def SetShowAtomDict(self):
        for item in self.showmenulst:
            if self.model.menuctrl.IsChecked(item):
                self.showdic[item]=self.model.menuctrl.IsChecked(item)

    def GetShowAtomDict(self):
        return self.showdic

    def SetDefaultElementColor(self,elmcolordic):
        """ Set default element color

        :param dic elmcolordic: dictionary of element color in [r,g,b,a],
                                {' H' : [0.8,0.8,0.8,1.0],...}
        """
        self.elmcolordic = elmcolordic

    def SetDefatultVdwRadius(self,vdwraddic):
        """ Set defatult Vdw radius

        :param dic vdwraddic: dictionary of Vdw radius, {' H' : 1.20,...}
        """
        self.vdwraddic = vdwraddic

    def SetDefaultBondThick(self,bondthick):
        """ Set default bond thickness

        :param int bondthick: bond thickness
        """
        self.bondthick = bondthick

    def SetDefaultBondThickBS(self,bondthickbs):
        """ Set default bond thickness

        :param float bondthickb: bond thickness
        """
        self.bondthickbs = bondthickbs

    def SetDefaultMolModel(self,molmodel):
        """ Set default molecule model

        :param int molmodel: 0: line, 1:stick, 2:ball-and-stick, 3:CPK
        """
        self.molmodel = molmodel

    def SetDefaltAtomRadius(self,atmrad):
        """ Set defalt atom radius

        :param float atmrad: atom radius
        """
        self.atomradius = atmrad

    def SetEnvironmentAtomColor(self,envatmcolor):
        """ Set environment atom color

        :param lst envatmcolor: color list [r,g,b,a]
        """
        self.envatmcolor = envatmcolor

    def SetResidueName(self,resatmlst,resnamlst):
        ist=0
        for i in range(len(resatmlst)):
            ied=resatmlst[i]
            resdat=resnamlst[i]
            resnam,resnmb,chain=lib.UnpackResDat(resdat)
            for j in range(ist,ied):
                self.atm[j].resnam=resnam
                self.atm[j].resnmb=resnmb
                self.atm[j].chainnam=chain
            ist=ied

    def SetAtomName(self,atmnamlst):
        """
        :param lst atmnamlst: [nam1(str),nam2(str),...], nam1=' CA ' with quort
        """
        for i in range(len(self.atm)):
            atmnam=atmnamlst[i]
            atmnam=atmnam[1:]; atmnam=atmnam[:-1]
            self.atm[i].atmnam=atmnam

    def IsAttribute(self,attrib):
        if attrib in self.fragattribdic: return True
        else: return False

    def SetFragAttribute(self,frglst,attrib,value):
        if 'FRGNAM' not in self.fragattribdic:
            return

        nfrag=len(self.fragattribdic['FRGNAM'])
        if attrib not in self.fragattribdic:
            self.fragattribdic[attrib]=nfrag*['']
        for frgnam in frglst:
            try:
                idx=self.fragattribdic['FRGNAM'].index(frgnam)
                self.fragattribdic[attrib][idx]=value
            except: pass

    def SetFragmentAttributeList(self,attrib,attriblst):
        self.fragattribdic[attrib]=attriblst

    def DelFragAttribute(self,attrib):
        if attrib in self.fragattribdic:
            del self.fragattribdic[attrib]

    def GetFragmentAttributeList(self,attrib):
        attriblst=[]
        if attrib in self.fragattribdic: attriblst=self.fragattribdic[attrib]
        return attriblst

    def ClearFragmentAttribute(self):
        self.fragattribdic={}

    def DrawItemsList(self):
        drwitemlst=['viewpos','Fog','fogscale','stereo','labels','Distance','Distance:data',
                     'Tube','BDA points','extrabond','sphere','arrow','cube','xyz-axis','axis']

        return drwitemlst

    def SaveDrawObjs(self,drwobjs,add):
        if not add: self.drwobjs={}
        for label,val in list(drwobjs.items()):
            self.drwobjs[label]=val
        #self.drwitems=drwitems

    def GetBGColor(self):
        if 'bgcolor' in self.viewitems: bgcolor = self.viewitems['bgcolor']
        else:
            bgcolor = None #bgcolor = self.setctrl.GetParam('win-color')
        return bgcolor

    def GetDrawObjs(self):
        return self.drwobjs

    def GetViewItems(self):
        return self.viewitems

    def SetDrwDumpItems(self,lst):
        # set draw item dump list
        # lst (lst): item list
        self.drwdumpitems=lst

    def SetViewItems(self,viewitems):
        self.viewitems=viewitems

    def SetDrawItem(self,label,value):
        return
        self.drwitems[label]=value

    def SetDrawObjs(self,drwobjs):
        self.drwobjs=drwobjs

    def Rename(self,newname):
        # newname(str): new mole name
        self.name=newname

    def RenameResDat(self,atmlst,newlst):
        for i in range(len(atmlst)):
            resnam,resnmb,chain=lib.UnpackResDat(newlst[i])
            iatm=atmlst[i]
            self.atm[iatm].resnam=resnam
            self.atm[iatm].resnmb=resnmb
            self.atm[iatm].chainnam=chain

    def RenameAtmNam(self,atmlst,newlst):
        for i in range(len(atmlst)):
            iatm=atmlst[i]
            self.atm[iatm].atmnam=newlst[i]

    def SetRemark(self,remark):
        # remaek(str): remark
        self.remark=remark

    def GetRemark(self):
        # ret remark(str): remark
        return self.remark

    def SetViewPos(self,eyepos,center,upward,ratio):
        #self.eyepos=eyepos; self.center=center; self.upward=upward; self.ratio=ratio
        #self.drawitemdic['viewpos']=[eyepos,center,upward,ratio]
        self.drw.Set('viewpos',[eyepos,center,upward,ratio])

    def GetViewPos(self):
        #[eyepos,center,upward,ratio]=self.drw.Get('viewpos') #drawitemdic['viewpos']
        if 'viewpos' not in self.drwitems:
            eyepos = [0.0, 0.0, 300.0]
            center = [0.0, 0.0, 0.0]
            upward = [0.0, 1.0, 0.0]
            ratio = 1.0
            return [eyepos,center,upward,ratio]
        return self.drwitems['viewpos']

    def SetAtomsFromText(self,form,string):
        """ Set coordinates and other structure data in string

        :param str form: data format,'sdf'('mol'),'xyz','pdb'('ent'),'zmt',
                         'mol2'
        :param str string: a formatted structure string
        """
        support = ['sdf','mol','pdb','ent','xyz','zmt']

        if   form == 'sdf' or form == 'mol': self.SetAtomsFromSDFText(string)
        elif form == 'pdb' or form == 'ent': self.SetAtomsFromPDBText(string)
        elif form == 'xyz' : self.SetAtomsFromXYZText(string)
        elif form == 'zmt' : self.SetAtomsFromZMTText(string)
        elif form == 'mol2': self.SetAtomsFromMOL2Text(string)
        elif form == 'cif': self.SetAtomsFromCIFText(string)
        else:
            mess = 'Molecule: Not supported format = ' + form +'\n'
            mess += '   supported formats are: ' + str(support)
            self.messout2(mess)

    def SetAtomsFromXYZText(self,string):
        """ Set coordinates and other structure data in xyz formatted string

        :param str string: a atring in xyz format
        """
        info,atomcc,xyzdata = lib.AtomCCFromXYZText(string)
        if 'err' in info:
            mess  = 'molec.SetAtomsFromXYZText: Error occured in AtomCCFromXYZ'
            mess += 'Text\n' + '   ' + info['err']
            self.messout2(mess)
            return
        blk3 = 3 * ' '
        self.name = xyzdata['title']
        natm = len(atomcc)
        for i in range(natm):
            # Atom class instance
            atm = Atom(self)
            # set attributes
            atm.seqnmb   = i # sequence number of atoms begin with 0
            atm.elm      = atomcc[i][0]
            atm.cc       = atomcc[i][1:] # coord list, [x,y,z]
            atm.conect   = []
            atm.bndmulti = []
            atm.atmnam   = atm.elm + '  ' # %02d' % i
            atm.resnam   = blk3
            atm.resnmb   = 1
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

    def SetAtomsFromSDFText(self,string):
        """ Set coordinates and other structure data in sdf formatted string

        :param lst string: a atring in sdf format
        """
        info,atomcc,conlst,typlst,sdfdata = lib.AtomCCFromSDFText(string)
        if 'err' in info:
            if info["err"] == "end data":
                mess = 'found blank line (end of data)'
            elif info["err"] == "wrong format":
                mess = info["err"]
            else:
                mess  = 'molec.SetAtomsFromSDFText: Error occured in AtomCCFromSDF'
                mess += 'Text\n' + '    info: ' + info['err']
            self.messout2(mess)
            return

        blk3 = 3 * ' '
        name = sdfdata['title_1']
        self.name = lib.SuppressBlanks(name)
        self.sdfdata = sdfdata
        natm = len(atomcc)
        for i in range(natm):
            # Atom class instance
            atm = Atom(self)
            # set attributes
            atm.seqnmb   = i # sequence number of atoms begin with 0
            atm.elm      = atomcc[i][0]
            atm.cc       = atomcc[i][1:] # coord list, [x,y,z]
            atm.conect   = conlst[i]
            atm.bndmulti = typlst[i]
            atm.atmnam   = atm.elm + '  ' # %02d' % i
            atm.resnam   = 'MOL' #blk3
            atm.resnmb   = 1
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

        if len(self.sdfdata) > 0:
            self.SetPackData(sdfdata)
            self.SetBoxPntsData(sdfdata)

    def SetBoxPntsData(self,sdfdic):
        labels = ['000','100','010','001','110','011','101','111']
        boxdat = ''
        if len(sdfdic) > 0:
            for item,vallst in list(sdfdic.items()):
                if item == '<box_vertexes>': boxdat = vallst
        if len(boxdat) > 0:
            ndat = len(boxdat)
            pntdic = {}
            for dat in boxdat:
                items = lib.SplitStringAtSeparator(dat,',')
                lab = items[0]
                if lab not in pntdic: pntdic[lab] = []
                pntdic[lab].append(float(items[1]))
                pntdic[lab].append(float(items[2]))
                pntdic[lab].append(float(items[3]))
            boxpnts = []
            for lab in labels: boxpnts.append(pntdic[lab])
            self.boxpnts = boxpnts

    def GetBoxPnts(self):
        return self.boxpnts

    def SetPackData(self,datadic):
        """ Create pack object

        :param dic datadic: sdfdata or mol2data
        """
        symequpos  = ''
        cellparams = ''
        if len(datadic) > 0:
            for item,vallst in list(datadic.items()):
                if item == '<symmetry_equiv_pos_as_xyz>':
                    symequpos = vallst[0]
                elif item == '<a,b,c,alpha,beta,gamma>':
                    cellparams = vallst[0]

        if len(cellparams) > 0 and len(symequpos) > 0:
            ###crystalobj = build.Crystal(self.parent)
            crystalobj = Crystal(self.parent)
            crystalobj.SetCellParams(cellparams)
            crystalobj.SetSymEquPos(symequpos)
            crystalobj.ComputeAttribs(unitmol=False)
            xyz_mol = []
            conlst = []
            typlst = []
            for atom in self.atm:
                xyz_mol.append([atom.atmnam,atom.elm,atom.cc[0],atom.cc[1],
                                atom.cc[2]])
                conlst.append(atom.conect)
                typlst.append(atom.bndmulti)
            #crystalobj.SetUnitMolecule(xyz_mol)
            crystalobj.SetUnitMoleculeInXYZ(xyz_mol)
            bndlst = lib.BondListFromConAndTypList(conlst,typlst)
            crystalobj.SetUnitMolBonds(bndlst)
            crystalobj.inpfile = 'unkown' #self.inpfile
            self.crystalobj = crystalobj

    def SetAtomsFromPDBText(self,string):
        """ Set coordinates and other structure data in pdb formatted string

        :param lst string: a atring in pdb format
        """
        # atomattr: [label,atmnum,atmnam,alt,resnam,chain,resnmb,focc,fbfc,chg]
        #              0      1      2    3    4      5     6      7    8   9
        info,atomcc,atomattr,conlst,pdbdata = lib.AtomCCFromPDBText(string)
        #
        if 'err' in info:
            mess = 'molec.SetAtomsFromPDBText: error occured in '
            mess += 'lib>AtomCCFromPDBText'
            self.message2(mess)
            return

        self.atm = []; self.nter = 0
        natm = len(atomcc)
        for i in range(natm):
            # Atom class instance
            atm = Atom(self)
            # set attributes
            atm.seqnmb  = i # sequence number of atoms begin with 0
            atm.cc      = atomcc[i][1:] # coord list, [x,y,z]
            atm.conect  = conlst[i][:] # connect list, [j1,j2,...] where ji is partner if i
            atm.elm      = atomcc[i][0]   # element symbol(right justified)
            if atm.elm == "XX": self.nter += 1
            atm.atmnam   = atomattr[i][2] # atom name
            atm.atmnmb   = atomattr[i][1] # atom number
            atm.resnam   = atomattr[i][4] # residue name
            atm.resnmb   = atomattr[i][6] # residue number
            atm.chainnam = atomattr[i][5] # chain name
            atm.altloc   = atomattr[i][3] # alternate locaton
            atm.focc     = atomattr[i][7] # occupancy
            atm.bfc      = atomattr[i][8] # B factor
            atm.charge   = atomattr[i][9] # charge
            # bond multiplicity
            bndtyp = []
            nbnd = len(conlst[i])
            if nbnd > 0:
                 for j in range(nbnd): bndtyp.append(1) # default: single bond
            atm.bndmulti = bndtyp # bond multiplicy list
            # Set parameters defined in const module
            atm.SetAtomParams(atm.elm)
            self.atm.append(atm)

    def SetAtomsFromMOL2Text(self,string):
        """ Set coordinates and other structure data in pdb formatted string

        :param lst string: a atring in pdb format
        """
        # atomattr: [label,atmnum,atmnam,alt,resnam,chain,resnmb,focc,fbfc,chg]
        #              0      1      2    3    4      5     6      7    8   9
        info,atomcc,atomattr,conlst,typlst,mol2data \
                                   = lib.AtomCCFromMOL2Text(string)
        #
        if 'err' in info:
            mess = 'molec.SetAtomsFromMOL2Text: error occured in '
            mess += 'lib>AtomCCFromMOL2Text'
            self.message2(mess)
            return

        self.name = info['name']
        self.mol2data = mol2data
        self.atm = []; self.nter = 0
        natm = len(atomcc)
        for i in range(natm):
            # Atom class instance
            atm = Atom(self)
            # set attributes
            atm.seqnmb   = i # sequence number of atoms begin with 0
            atm.cc       = atomcc[i][1:] # coord list, [x,y,z]
            atm.conect   = conlst[i][:] # connect list, [j1,j2,...] where ji is partner if i
            atm.elm      = atomcc[i][0]   # element symbol(right justified)
            atm.atmnam   = atomattr[i][1] # atom name
            atm.atmnmb   = atomattr[i][0] # atom number
            atm.resnam   = atomattr[i][4] # residue name
            atm.resnmb   = atomattr[i][3] # residue number
            atm.chainnam = "A" # chain name
            atm.altloc   = 0 # alternate locaton
            atm.focc     = 0 # occupancy
            atm.bfc      = 0 # B factor
            atm.charge   = 0 # charge

            atm.ffatmchg = atomattr[i][5]
            atm.ffatmtyp = atomattr[i][2]
            # bond multiplicity
            atm.bndmulti = typlst[i]
            # Set parameters defined in const module
            atm.SetAtomParams(atm.elm)
            self.atm.append(atm)

        if len(self.mol2data) > 0:
            self.SetPackData(self.mol2data)
            self.SetBoxPntsData(self.mol2data)


    def SetAtomsCIF(self,umol_coords):
        """ Set coordinates and other structure data in cif formatted string

        :param lst string: a CIF molecule object, [[label,elm,x,y,z],...]
        """
        blk3 = 3 * ' '
        natm = len(umol_coords)
        for i in range(natm):
            # Atom class instance
            atm = Atom(self)
            # set attributes
            atm.seqnmb   = i # sequence number of atoms begin with 0
            atm.elm      = lib.ElementNameFromString(umol_coords[i][1])
            atm.cc       = umol_coords[i][2:] # coord list, [x,y,z]
            atm.conect   = []
            atm.bndmulti = []
            atm.atmnam   = umol_coords[i][0]
            if len(atm.atmnam) > 4: atm.atmnam[:4]
            atm.resnam   = blk3
            atm.resnmb   = 1
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

    def SetAtomsFromZMTText(self,string):
        """ Set coordinates and other structure data in zmt formatted string

        :param lst string: a atring in zmt format
        """


    def BuildFromMolFile(self,molfile):
        natoms,nbonds,resnam,molatm=rwfile.ReadMolFile(molfile)
        self.SetMolAtoms(molatm,resnam)

    def SetMolAtoms(self,molatm,resnam='',resnmb=1):
        # create mol data
        elm=molatm[0]
        cc=molatm[1]
        bonds=molatm[2]
        multi=molatm[3]
        natm=len(cc)
        # conect data
        condic={}; muldic={}
        if len(bonds) > 0:
            for i in range(len(bonds)):
                ia=bonds[i][0]; ib=bonds[i][1]
                m=multi[i]
                if ib not in condic:
                    condic[ib]=[]; muldic[ib]=[]
                condic[ib].append(ia); muldic[ib].append(m)
                if ia not in condic:
                    condic[ia]=[]; muldic[ia]=[]
                if ia != ib: condic[ia].append(ib); muldic[ia].append(m)
        #
        for i in range(natm):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            atm.cc=list(cc[i]) # coord list, [x,y,z]
            con=[]; bndmulti=[]
            if i in condic: con=list(condic[i])
            if i in muldic: bndmulti=list(muldic[i])
            else: pass
            if len(con) > 0: atm.conect=con # connect list, [j1,j2,...] where ji is partner if i
            if len(bndmulti) > 0: atm.bndmulti=bndmulti
            atm.atmnam=elm[i]+'  ' # %02d' % i
            atm.elm=elm[i] # element symbol(right justified)
            atm.resnam=resnam
            atm.resnmb=resnmb
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

    def SetZMTAtoms(self,zmtatm,resnam='',resnmb=1,active={},extdat=[]):
        # create mol data
        # actice(dic): {iatm:[prm1,prm2..],...}
        natm     = len(zmtatm)
        self.atm = []
        for i in range(len(zmtatm)): #elm,x,y,z in zmtatm:
            # Atom class instance
            atm = Atom(self)
            #i += 1
            # set attributes
            atm.seqnmb = i # sequence number of atoms begin with 0
            atm.cc     = [zmtatm[i][1],zmtatm[i][2],zmtatm[i][3]] #[x,y,z] # coord list, [x,y,z]
            elm        = zmtatm[i][0]
            atm.elm    = elm
            atm.atmnam = elm + '  ' # %02d' % i
            atm.resnam = resnam
            atm.resnmb = resnmb
            atm.SetAtomParams(atm.elm)
            act = [False,False,False]
            for j in range(3):
                varnam = str(i) + ':' + str(j)
                if varnam in active: act[j] = True
                    #if zmtdic[varnam][1]: active[j]=True
            atm.activezmt = act
            #if active.has_key(i): atm.activezmt=active[i][:]
            #if len(pnts) == natm: atm.zmtpnts=pnts[i][:]
            # append to mol data
            self.atm.append(atm)
        # symbilic z-matrix
        #self.zmtpnt=pnts
        ###self.zmtdic=zmtdic
        #
        if len(extdat) > 0:
            atmnam = extdat[0]; resdat   = extdat[1]
            conect = extdat[2]; bndmulti = extdat[3]
            for i in range(len(self.atm)):
                self.atm[i].atmnam   = atmnam[i]
                resnam,resnmb,chain  = lib.UnpackResDat(resdat[i])
                self.atm[i].resnam   = resnam;
                self.atm[i].resnmb   = resnmb
                self.atm[i].chainnam = chain
                self.atm[i].conect   = conect[i]
                self.atm[i].bndmulti = bndmulti[i]

    def BuildFromPDBFile(self,pdbfile):
        pdbmol,fuoptdic=rwfile.ReadPDBMol(pdbfile)
        self.SetPDBMol(pdbmol,fuoptdic=fuoptdic)

    def SetPDBMol(self,pdbmol,fuoptdic={}):
        # make mol from pdb data
        # pdbmol(lst): [coord,connect,atmname,atmnumber,resname,resnumber,
        #                chaname,altnate,elment,occupation,bfactor,charge]]
        # coord(lst): [cc([x,y,z],...]
        # conect(lst): [conect(lst),...]
        # atmname(lst): [atmnam(str),...]
        # atmnumber, ... : lists. the same as above
        # evironment
        env=False; corereslst=[]
        if 'CORERES' in fuoptdic:
            env=True
            corereslst=fuoptdic['CORERES']
        #
        self.atm=[]; self.nter=0
        # create mol data
        cc=pdbmol[0]; conect=pdbmol[1]; atmnam=pdbmol[2]; atmnmb=pdbmol[3]
        resnam=pdbmol[4]; resnmb=pdbmol[5]; chain=pdbmol[6]; alt=pdbmol[7]
        elm=pdbmol[8]; focc=pdbmol[9]; bfc=pdbmol[10]; charge=pdbmol[11]
        natm=len(cc)
        #
        for i in range(natm):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            atm.cc=list(cc[i]) # coord list, [x,y,z]
            con=list(conect[i])
            del con[0]
            #for j in range(len(con)): con[j] -= 1 # reduce atom number by one
            atm.conect=con # connect list, [j1,j2,...] where ji is partner if i
            atm.atmnam=atmnam[i]
            if isinstance(atmnam[i],int):
                atm.atmnam="    "; elm[i]="XX"
            atm.atmnmb=atmnmb[i]
            atm.resnam=resnam[i] # residue name
            atm.resnmb=resnmb[i] # residue number
            atm.chainnam=chain[i] # chain name
            atm.altloc=alt[i]
            atm.elm=elm[i] # element symbol(right justified)
            if atm.elm == "XX": self.nter += 1
            atm.focc=focc[i] # occupancy
            atm.bfc=bfc[i] # B factor
            atm.charge=charge[i] # charge
            # bond multiplicity, it is not in pdb data
            bndmulti=[]
            nbnd=len(conect[i])-1
            if nbnd > 0:
                for j in range(nbnd): bndmulti.append(1) # default: single bond
            atm.bndmulti=bndmulti # bond multiplicy list
            # Set atom parameters elm color,vdw radius, atom radius, bond thickness,model
            # defined in const module
            atm.SetAtomParams(atm.elm)
            # environment atoms
            if env:
                resdat=lib.ResDat(atm)
                if not resdat in corereslst:
                    atm.envflag=True
                    atm.grpnam='envgrp'
                    atm.color = self.envatmcolor #self.model.setctrl.GetParam('env-atom-color')[:]
            # append to mol data
            self.atm.append(atm)

    def SetPDBAtoms(self,pdbatm):
        # set pdb atom data to mol
        # pdbatm(lst): [[coord,connect,atmname,atmnumber,resname,resnumber,
        #                chaname,altnate,elment,occupation,bfactor,charge],...]
        self.atm=[]; self.nter=0
        # create mol list
        for i in range(len(pdbatm)):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            atm.cc=list(pdbatm[i][0]) # coord list, [x,y,z]
            con=list(pdbatm[i][1])
            del con[0]
            #for j in range(len(con)): con[j] -= 1 # reduce atom number by one
            atm.conect=con # connect list, [j1,j2,...] where ji is partner if i
            atm.atmnam=pdbatm[i][2][0] # atom name
            atm.atmnmb=pdbatm[i][2][1] # atom number
            atm.resnam=pdbatm[i][2][2] # residue name
            atm.resnmb=pdbatm[i][2][3] # residue number
            atm.chainnam=pdbatm[i][2][4] # chain name
            atm.altloc=pdbatm[i][2][5]
            atm.elm=pdbatm[i][3][0] # element symbol(right justified)
            if atm.elm == "XX": self.nter += 1
            atm.focc=pdbatm[i][3][1] # occupancy
            atm.bfc=pdbatm[i][3][2] # B factor
            atm.charge=pdbatm[i][3][3] # charge
            # bond multiplicity
            bndmulti=[]
            nbnd=len(pdbatm[i][1])-1
            if nbnd > 0:
                for j in range(nbnd): bndmulti.append(1) # default: single bond
            atm.bndmulti=bndmulti # bond multiplicy list
            # Set parameters defined in const module
            atm.SetAtomParams(atm.elm)
            #atm.SetDefaultColor() # element color
            #atm.SetDefaultVdwRad() # vdw radius
            #atm.SetDefaultAtmRad() # atom radius
            #atm.SetDefaultBondThick() # bond thickness
            # append to mol data
            self.atm.append(atm)

    def SetFMOXYZAtoms(self,inpfile):
        # make mol from pdb file
        self.inpfile=inpfile
        # read pdb file
        err,fmomol=Molecule.ReadFMOXYZ(inpfile)
        if err:
            print(('ReadFMOXYZ: error in reading file. file='+inpfile))
            return
        #self.molname=molnam
        self.atm=[]
        # create mol data
        for i in range(len(fmomol)):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            atm.atmnam=fmomol[i][0] # atom name
            atm.atmnmb=atm.seqnmb+1 # atom number
            elm=fmomol[i][1]
            if elm.isdigit(): elm=const.ElmSbl[int(elm)]
            atm.elm=fmomol[i][1] # element symbol(right justified)
            atm.cc[0]=fmomol[i][2] # x
            atm.cc[1]=fmomol[i][3] # y
            atm.cc[2]=fmomol[i][4] # z
            # bond multiplicity
            #atm.SetDefaultColor() # element color
            #atm.SetDefaultVdwRad() # vdw radius
            #atm.SetDefaultAtmRad() # atom radius
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

    def SetAtoms(self,atmcc,elm=True,angs=True):
        """ Set atom instance 'atm' to 'mol' instance
        :param lst atmcc: atmcc:[[an(int),x(float),y(float),z(float)],...]
        """
        # atmcc=[[an(int),x(float),y(float),z(float)],...]
        if len(atmcc) <= 0: return []
        self.atm=[]
        toangs = 0.529917724
        fc = 1.0
        if not angs: fc = toangs
        # create mol data
        for i in range(len(atmcc)):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            atm.atmnmb=atm.seqnmb+1 # atom number
            elmdat = atmcc[i][0]
            if elm: atm.elm = lib.ElementNameFromString(elmdat)
            else:   atm.elm = const.ElmSbl[elmdat] # atomic number
            atm.atmnam=atm.elm+str(atm.seqnmb)
            atm.cc=[fc*atmcc[i][1],fc*atmcc[i][2],fc*atmcc[i][3]]
            atm.SetAtomParams(atm.elm)
            # append to mol data
            self.atm.append(atm)

    def InterAtomDistance(self,a,b):
        r=-1.0
        cca=self.atm[a].cc; ccb=self.atm[b].cc
        r=lib.Distance(cca,ccb)
        return r


    def AddAtomAt(self,at,elm,coord,atmdatdic):
        # insert an atom after 'at'-th atom.
        # elm: element name, like ' H' (rigth justfied)
        # coord: [x,y,z]
        # atmdatdic: dictonary of atom parameters. see ATOM() class
        atatm=self.atm[at]
        for i in range(len(self.atm)):
            if i > at:  #self.atm[i].seqnmb >= at:
                self.atm[i].seqnmb += 1
            for j in range(len(self.atm[i].conect)):
                if self.atm[i].conect[j] > at:
                    self.atm[i].conect[j] += 1
        self.atm[at].conect.append(at+1)

        self.atm[at].bndmulti.append(1)


        atm=Atom(self)
        atm.seqnmb=at
        atm.elm=elm
        atm.SetAtomDataByDic(atmdatdic) # atomdata of at atom
        atm.seqnmb=at+1; atm.cc=coord; atm.conect=[at]
        atm.atmnmb=-atatm.atmnmb
        atm.color=const.ElmCol[elm]
        atm.atmrad=const.DefaultAtomParam['AtmRad'] #const.AtmRad # added at 29, May 2013 (kk)
        atm.select=True
        # insert atm before after at
        self.atm.insert(at+1,atm) #+1,atm)

    def AddAtomAt1(self,at,elm,coord,atmdatdic,bndorder=1):
        # insert an atom after 'at'-th atom.
        # elm: element name, like ' H' (rigth justfied)
        # coord: [x,y,z]
        # atmdatdic: dictonary of atom parameters. see ATOM() class
        atatm=self.atm[at]
        #for i in range(len(self.atm)):
        #    if i > at:  #self.atm[i].seqnmb >= at:
        #        self.atm[i].seqnmb += 1
        #    for j in range(len(self.atm[i].conect)):
        #        if self.atm[i].conect[j] > at:
        #            self.atm[i].conect[j] += 1
        #self.atm[at].conect.append(-1) #at+1)

        #self.atm[at].bndmulti.append(1)

        iatm = len(self.atm)
        atm=Atom(self)
        #atm.seqnmb=at
        atm.SetAtomDataByDic(atmdatdic) # atomdata of at atom
        atm.seqnmb=iatm #-1 #at+1
        atm.cc=coord
        atm.conect=[at]
        atm.bndmulti=[bndorder]
        atm.elm=elm
        atm.atmnmb=iatm + 1 #-atatm.atmnmb
        atm.color=const.ElmCol[elm]
        atm.atmrad=const.DefaultAtomParam['AtmRad'] #const.AtmRad # added at 29, May 2013 (kk)
        atm.SetAtomParams(elm)
        self.atm[at].conect.append(atm.seqnmb)
        self.atm[at].bndmulti.append(bndorder)

        atm.select=True
        # insert atm before after at
        ####self.atm.insert(at+1,atm) #+1,atm)
        self.atm.append(atm)

    def AddHydrogen(self,at,nh,coord,hnam):
        # Add nh hydrogens after at-th atom
        # coord: [[x0,y0,z0],[x1,y1,z1],...]
        # hnam: ['H0 name','H1 name',...]
        atatm=self.atm[at]
        grpdatdic=atatm.GetGrpDataDic()
        atmdatdic=atatm.GetResDataDic()
        atmdatdic.update(grpdatdic) # resdatdic+grpdatdic
        atmdatdic['thick'] = atatm.thick
        atmdatdic['model'] = atatm.model
        elm=' H'
        for i in range(nh):
            atmdatdic["atmnam"]=hnam[nh-i-1]
            atmdatdic["atmrad"]=const.DefaultAtomParam['AtmRad'] #const.AtmRad
            self.AddAtomAt(at,elm,coord[nh-i-1],atmdatdic)

    def AddHydrogen1(self,at,nh,coord,hnam):
        # at: inert h after atom at
        # Add nh hydrogens after at-th atom
        # coord: [[x0,y0,z0],[x1,y1,z1],...]
        # hnam: ['H0 name','H1 name',...]
        #for lst in hlst:
        #    at=lst[0]; nh=lst[1]; coord=lst[2]; hnam=lst[3]
        atatm=self.atm[at]
        grpdatdic=atatm.GetGrpDataDic()
        atmdatdic=atatm.GetResDataDic()
        atmdatdic.update(grpdatdic) # resdatdic+grpdatdic
        atmdatdic['thick'] = atatm.thick
        atmdatdic['model'] = atatm.model
        elm=' H'
        for i in range(nh):
            atmdatdic["atmnam"]=hnam[nh-i-1]
            atmdatdic["atmrad"]=const.DefaultAtomParam['AtmRad'] #const.AtmRad
            self.AddAtomAt1(at,elm,coord[nh-i-1],atmdatdic)

    def GetCCAddAtmType1A1(self,atmlst,r):
        # calculate coordinate of 1A1 type atom added to x1.
        # atmlst: [x1,x2,x3,x4], xi: sequence number of atom in Molecule() instance
        # r: bond length between add atom and x1
        #ex. H atom added at C in -CH3 results in HCH3 (CH4).
        #           |-x2
        # add atom-x1-x3
        #           |-x4
        at=atmlst[0]
        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        x3=numpy.array(self.atm[atmlst[2]].cc)
        x4=numpy.array(self.atm[atmlst[3]].cc)
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
        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        x3=numpy.array(self.atm[atmlst[2]].cc)

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
        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        x3=numpy.array(self.atm[atmlst[2]].cc)
        rad=bang
        if abs(bang) < 0:
            if self.atm[x1][2] == ' O': rad=rad61
            if self.atm[x1][2] == ' S': rad=rad70

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
        """ add two H's AT C(SP3) atom for x2-x1(C)H2-x3 """

        u=numpy.identity(3); xr=numpy.zeros(3); xn=numpy.zeros(3)
        x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
        xh1t=numpy.zeros(3); xh2t=numpy.zeros(3)
        rad54=0.955314692
        #at=atmlst[0]
        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        x3=numpy.array(self.atm[atmlst[2]].cc)
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
        """
        x3-x2-x1(H2) where x1 is SP2 atom, all atoms are in a plane.
        """
        u=numpy.identity(3); xr=numpy.zeros(3); xn=numpy.zeros(3)
        x1t=numpy.zeros(3); x2t=numpy.zeros(3); x3t=numpy.zeros(3)
        xh1t=numpy.zeros(3); xh2t=numpy.zeros(3)
        rad59=1.05068821
        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        x3=numpy.array(self.atm[atmlst[2]].cc)
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

        x1=numpy.array(self.atm[atmlst[0]].cc)
        x2=numpy.array(self.atm[atmlst[1]].cc)
        #x3=list(self.atm[atmlst[2]][0])
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

    def AddAtomLast(self,at,coord,elm,atmcol,shwatm,selatm,orgnam,orgnmb,lbl,rem,bndmulti):
        # attach an atom at 'at' and add the atom data at the end.
        # Note! not tested as of 28 Aug 2012.
        con=[]
        #ix=at
        #ix=self.FindAtmSeqNmb(at)
        natm=len(self.atm)
        con.append(natm); con.append(at)
        tmp=[]
        tmp.append(coord); tmp.append(con); tmp.append(elm); tmp.append(atmcol)
        tmp.append(shwatm); tmp.append(selatm); tmp.append(orgnam); tmp.append(orgnmb)
        tmp.append(lbl); tmp.append(rem); tmp.append(bndmulti)
        self.atm.append(tmp)
        self.atm[at][1].append(con[0])

    def ExtractAARes(self,resnam,resnmb,start):
        resdat=[]; nresatm=0; resatmdic={}
        found=False
        for i in range(start,len(self.atm)):
            res=self.atm[i].resnam
            nmb=self.atm[i].resnmb
            if res == resnam and nmb == resnmb:
                nresatm += 1; found=True

                resdat.append(self.atm[i])

                atmnam=self.atm[i].atmnam
                resatmdic[atmnam]=nresatm
            if found and (res != resnam or nmb != resnmb):
                break

        return nresatm,resdat,resatmdic

    def ExtractAARes1(self,resnam,resnmb,chain):
        resatm=[]; nresatm=0; resatmdic={}
        found=False
        for i in range(len(self.atm)):
            res=self.atm[i].resnam
            nmb=self.atm[i].resnmb
            cha=self.atm[i].chainnam
            if res == resnam and nmb == resnmb and cha == chain:
                nresatm += 1; found=True

                resatm.append(self.atm[i])

                atmnam=self.atm[i].atmnam
                resatmdic[atmnam]=nresatm
            if found and (res != resnam or nmb != resnmb or cha != chain):
                break

        return nresatm,resatm,resatmdic


    def OldAddHydrogenToProtein(self,lst):
        # add hydrogens
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        nss=self.MakeSSBond(lst,True)
        self.AddBondUseBL(lst)

        natm=len(lst) #; atm=[' H  ',' H  ',' H  ']
        i=0; na=0; nht=0; nh=0; nhr=0; nres=0; ic=-1; nresatm=0
        prvchain=self.atm[lst[0]].chainnam
        while na < natm:
            i += nresatm
            ia=lst[i]+nht
            nh=0
            resnam=self.atm[ia].resnam
            resnmb=self.atm[ia].resnmb
            #chain=self.atm[ia].chainnam
            nres += 1
            #
            nresatm,resdat,atmnamdic=self.ExtractAARes1(resnam,resnmb,ia)
            #
            if resnam in const.AmiRes3: #.has_key(resnam):
                #self.AddBondInAARes(resnam,resdat)
                nh=self.AddHydrogenToAARes(resnam,resdat,ic)
                #if chain != prvchain: ic=-1
                ic=self.FindCOCarbonInRes(resnam,resnmb)
            else: ic=-1
            #prvchain=chain

            nht=nht+nh
            na += nresatm

        self.AddHydrogenToNterm(lst,True)

    def AddHydrogenToPeptideNC(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))
        natm=len(lst)
        if natm <= 0: return
        bndlst=[]; nh=0
        i=-1; na=0; nht=0
        while na < natm:
            i += 1; na += 1
            ia=lst[i]+nht
            atom=self.atm[ia]
            nb=len(atom.conect)
            elm=atom.elm
            htype='non'
            bndlst=[]
            atm=atom.atmnam
            nb=len(self.atm[ia].conect)
            addh=False
            if atm == ' N  ' and nb == 2:
                addh=True
            if atm == ' C  ' and nb == 2:
                addh=True
            if addh:
                btype=''
                if elm == ' C':
                    btype=' H C'
                    htype = '2A1'
                if elm == ' N':
                    btype=' H N'
                    htype = '1A2'
                if btype != '':
                    rhx=const.CovBndLen[btype][0]
                    ib=atom.conect[0]
                    bndlst.append(ib)
                    ib=atom.conect[1]
                    bndlst.append(ib)
            #
            if htype != 'non':
                nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                nht += nh

    def AddHydrogenToNterm(self,lst,removeh):
        # add hydrogen to N-terminus
        # lst(lst): target atom list. if [], all atoms are targetted.
        # remove: =True,remove existing hydrogens, =False: do nothing
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        nht=0; natm=len(lst); atm=[' H1 ',' H2 ',' H3 ']
        for i in lst:
            atom=self.atm[i]
            bndlst=[]
            if atom.atmnam == ' N  ':
                #if removeh:
                #    dellst=[]
                #    for j in atom.conect:
                #        if self.atm[j].elm == " H": dellst.append(j)
                #    if len(dellst) > 0: self.DelAtoms(dellst)
                if len(atom.conect) <= 2:
                    nterm=i
                    ib=atom.conect[0]
                    bndlst.append(ib) #atom.conect[0])
                    #iib=self.atm[ib].conect[0]
                    htype='3A1'
                    if len(atom.conect) == 2 and self.atm[i].resnmb != 1:
                        htype="1A2"
                        bndlst.append(atom.conect[1]) #self.atm[ib].conect[0])
                    #    bndlst.append(self.atm[ib].conect[0])
                    rhx=const.CovBndLen[' H N'][0]
                    nh=self.AddHydrogenToMol(i,atm,htype,bndlst,rhx)
                    nht += nh
                    #
                    if nh > 0:
                        resnam=atom.resnam
                        resnmb=atom.resnmb
                        chain=atom.chainnam
                        for j in range(nh):
                            ii=nterm+j+1
                            self.atm[ii].resnam=resnam
                            self.atm[ii].resnmb=resnmb
                            self.atm[ii].chainnam=chain
                        mess='AddHydorgenToProtein: '+str(nh)+' Hydrogens were attached at N-terminus, res='+resnam+str(resnmb)+'.'
                        self.Message(mess,True)
                        #self.ConsoleMessage(mess)
        return nht

    def AddHydrogenToProtein(self,lst,addbond=True):
        # add hydrogens
        err=0
        if len(lst) <= 0: lst = list(range(len(self.atm)))
        # add ss bond first
        nss=self.MakeSSBond(lst,True)
        if nss > 0:
            mess="Number of SS bonds created= "+str(nss)
            #self.ConsoleMessage(mess)
            self.Message(mess,True)
        # add bonds
        ###if addbond:
        ###    self.AddBondUseBL(lst)
        # copy org conect
        orgcon=[]
        for i in range(len(self.atm)):
            orgcon.append(copy.deepcopy(self.atm[i].conect))
        #
        start=0; nhchainlst=[]
        for i in lst:
            if self.atm[i].resnam in const.AmiRes3:
                start=i; break
        #print 'start',start
        prvchain="non"
        natm=len(lst)
        i=start; na=0; nht=0; nh=0; ic=-1; nresatm=0; nres=0#; nhr=0
        newchain=False; nhchain=0; nterm=False
        hlst=[]
        while na < natm:
            i += nresatm
            # progress bar
            #try:
            #    if self.model.shwprogbar:
            #        gage=100*float(i-start)/float(natm-start)
            #        self.frame.ProgressBar("SetValue",gage)
            #except: pass
            #if i >= natm:
            #    print 'break i exceeded natm',i,natm
            #    break

            try:
                ia=lst[i]+nht
                #print 'natm,i',natm,i
            except:
                pass
                #print 'i exceeded len(lst),natm',i,len(lst),natm

            if self.atm[ia].chainnam != prvchain:
                newchain=True; prvchain=self.atm[ia].chainnam
                if i != start: nhchainlst.append(nhchain)
                nterm=True; nhchain=0
                #print 'prvchain',prvchain
            else: newchain=False
            resnam=self.atm[ia].resnam
            resnmb=self.atm[ia].resnmb
            nres += 1
            #
            nresatm,resdat,atmnamdic=self.ExtractAARes(resnam,resnmb,ia)  #(resnam,resnmb,ia)
            #print 'i,nresatm,resnam,resnmb',i,nresatm,resnam,resnmb
            #
            nh=0
            #if const.AmiRes3.has_key(resnam):
            if nresatm > 0:
                self.AddBondInAARes(resnam,resdat)
                nh=self.AddHydrogenToAARes(resnam,resdat,ic) #1(ia,nht,resnam,resdat,ic)
                #nh=self.AddHydrogenToAARes1(ia,orgcon,resnam,resdat,ic)
                ic=self.FindCOCarbonInRes(resnam,resnmb)
                #hlst.append(addlst)
                if nterm: ic=-1

                #print 'nh,resnam,resnmb,nresatm',nh,resnam,resnmb,nresatm
            if newchain and nterm and resnam in const.AmiRes3: #.has_key(resnam):
                #print 'new chain, resnam,resnmb',prvchain,resnam,resnmb
                mess="Three hydrogens are added at the first N in chain: "
                mess=mess+prvchain
                mess=mess+", residue: "+resnam+":"+str(resnmb)
                #self.ConsoleMessage(mess)
                self.Message(mess,True)
                reslst=self.MakeResAtomList(resnam,resnmb,ia)
                nhatn=self.AddHydrogenToNterm(reslst,True) #[])
                nterm=False
                nh += nhatn

            else: ic=-1
            nht += nh
            na += nresatm
            nhchain += nh
            #
        ###if nht > 0: self.ConectAddAtom(self)
        self.AddHydrogenToPeptideNC([])

        if nhchain > 0:
            nhchainlst.append(nhchain)

        return nht,nhchainlst

    def ConectAddAtom(self):
        #seq0=self.atm[hlst[0]].seqnmb
        seqdic={}
        for i in range(len(self.atm)):
            print(('i,mol',i,self.atm[i].seqnmb,self.atm[i].atmnam,self.atm[i].resnam))
        #k=-1
        for i in range(len(self.atm)):
            if self.atm[i].seqnmb == -1: continue
            k=self.atm[i].seqnmb; seqdic[k]=i
        #print 'seqdic',seqdic

        k=-1; nh=0; seq0=0
        for i in range(len(self.atm)):
            k += 1; seq=seq0+k; ip=0
            if self.atm[i].seqnmb == -1:
                nh += 1

                ip=self.atm[i].conect[0]
                if ip not in seqdic:
                    print(('program error',ip))
                    break
                #iseq=seqdic[ip]
                # renumber sequence numbers in conect
                iip=seqdic[ip]
                for j in range(len(self.atm[ip].conect)):
                    if self.atm[ip].conect[j] in seqdic:

                        jj=seqdic[self.atm[ip].conect[j]]
                        self.atm[iip].conect[j]=jj
                self.atm[iip].conect.append(i) #[seq]
                self.atm[iip].bndmulti.append(1)
                self.atm[i].conect[0]=iip
            else:
                for j in range(len(self.atm[i].conect)):
                    self.atm[i].conect[j]=seqdic[self.atm[i].conect[j]]
            self.atm[i].seqnmb=i # seq

            #print 'i,mol[i].atmnam,conect',i,self.atm[i].atmnam,self.atm[i].conect
            #print 'i,ip,seqdic', i,ip,seqdic[ip]

    def MakeResAtomList(self,resnam,resnmb,start):
        resatmlst=[]
        nresatm,resdat,resatmdic=self.ExtractAARes(resnam,resnmb,start)
        for ratom in resdat:
            resatmlst.append(ratom.seqnmb)
        return resatmlst

    def MakeAAResAtomList(self,resnam,resnmb,chain):
        resatmlst=[]
        resdic=self.MakeAAResDic1()
        for resdat,value in list(resdic.items()):
            item=resdat.split(':')
            resnam=item[0]; resnmb=int(item[1]); chain=item[2]
        nresatm,resatmlst,resatmdic=self.ExtractAARes1(resnam,resnmb,chain)

        return resatmlst

    def AddHydrogenToCTerm(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        natm=len(lst)
        if natm <= 0: return
        bndlst=[]; nh=0
        i=-1; na=0; nht=0
        while na < natm:
            i += 1; na += 1
            ia=lst[i]+nht
            atom=self.atm[ia]
            nb=len(atom.conect)
            elm=atom.elm
            htype='non'; bndlst=[]
            atm=atom.atmnam
            nb=len(self.atm[ia].conect)
            addh=False
            #if atm == ' N  ' and nb == 2: addh=True
            if atm == ' C  ' and nb == 2: addh=True
            if addh:
                btype=''
                if elm == ' C': btype=' H C'
                #if elm == ' N': btype=' H N'
                if btype != '':
                    rhx=const.CovBndLen[btype][0]
                    ib=atom.conect[0]; bndlst.append(ib)
                    ib=atom.conect[1]; bndlst.append(ib)
                    htype='1A2'
            #
            if htype != 'non':
                nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                nht += nh

    def AddHydrogenToAARes(self,resnam,resdat,ic):
        # add hydrogen atoms to amino acid residues
        nh=0; nht=0 #; addlst=[]
        if not resnam in const.AmiRes3: # .has_key(resnam):
            #if not resnam in const.WaterRes:
            #    mess=resnam+' is not amino acid residue. Skipped.'
            #    self.Message(mess,True) #,0,'blue')
            return nh
        if len(resdat) <= 0:
            mess='No atoms in '+resnam+'. Skipped.'
            self.Message(mess,True) #,0,'blue')
            return nh
        natm=len(resdat); iat=resdat[natm-1].seqnmb #; isn=-1
        for i in range(len(resdat)):
            atm=resdat[i].atmnam; nmb=resdat[i].atmnmb; con=resdat[i].conect
            iatm=resdat[i].seqnmb
            nh=0; resnmb=resdat[i].resnmb
            if atm not in const.AmiResH[resnam]: continue
            nhatm=self.CountHydrogenOfAtom(iatm)
            if nhatm > 0:
                mess=str(nhatm)+'AddHydrogenToAARes: Hydrogen is already attached at '+str(iatm)+'. Skipped.'
                #self.Message(mess,0,'blue')
                #self.ConsoleMessage(mess)
                self.Message(mess,True)
                continue
            #if atm == ' N  ':
            #    isn=iatm
            #    print 'n found,isn',isn
            htype=const.AmiResH[resnam][atm][0]
            hnam=const.AmiResH[resnam][atm][1]
            hcon=const.AmiResH[resnam][atm][2]
            rbnd=const.AmiResH[resnam][atm][3]
            # skip S-S bond
            if (resnam == 'CYS' or resnam == 'CYX') and atm == ' SG ':
                #
                if len(resdat[i].conect) >= 2: continue
            atmlst=[]; atmlst.append(iatm)
            for j in range(len(hcon)):
                coord=[]; lbl=[]
                conatm=hcon[j]
                if conatm == '-C  ':
                    if ic >= 0:
                        #if isn >= 0:
                        #    r=self.InterAtomDistance(ic,isn)
                        #    print 'isn,ic,r',isn,ic,r
                        #    if r < 1.6:
                        #        jatm=ic; atmlst.append(jatm)
                        #    else: htype='non' #jatm=ic; atmlst.append(jatm)
                        jatm=ic; atmlst.append(jatm)
                    else:
                        htype='non'
                else:
                    jatm=self.FindResAtmSeqNmb(resdat,conatm)
                    if jatm >= 0:
                        atmlst.append(jatm)
                    else:
                        htype='non'
            if htype == '1A1':
                nh,coord=self.GetCCAddAtmType1A1(atmlst,rbnd)
            if htype == '1A2':
                nh,coord=self.GetCCAddAtmType1A2(atmlst,rbnd)
            if htype == '1A3':
                nh,coord=self.GetCCAddAtmType1A3(atmlst,rbnd,-1,True)
            if htype == '2A1':
                nh,coord=self.GetCCAddAtmType2A1(atmlst,rbnd)
            if htype == '2A2':
                nh,coord=self.GetCCAddAtmType2A2(atmlst,rbnd)
            if htype == '3A1':
                nh,coord=self.GetCCAddAtmType3A1(atmlst,rbnd)
            if htype == 'non': pass
            if htype != 'non':
                at=iat+nht
                self.AddHydrogen(iatm,nh,coord,hnam)
                #addlst.append([iatm,nh,coord,hnam])
                nht += nh
        #self.AddHydrogens(addlst)

        return nht

    def AddHydrogenToAARes1(self,iatm,orgcon,resnam,resdat,ic):
        # add hydrogen atoms to amino acid residues
        nh=0; nht=0
        if resnam not in const.AmiRes3:
            #mess=resnam+' is not amino acid residue. Skipped.'
            #self.Message(mess,True) #,0,'blue')
            return nh
        if len(resdat) <= 0:
            mess='No atoms in '+resnam+'. Skipped.'
            self.Message(mess,True) #,0,'blue')
            return nh

        #resdat=copy.deepcopy(resdat)

        natm=len(resdat); iat=resdat[natm-1].seqnmb #; isn=-1
        for i in range(len(resdat)):
            atm=resdat[i].atmnam; nmb=resdat[i].atmnmb#; con=resdat[i].conect

            #iatm += nh
            iatm=resdat[i].seqnmb
            iiatm=resdat[i].seqnmb
            #print "iiatm",iiatm
            if iiatm >= len(orgcon): break

            con=orgcon[iiatm]


            nh=0; resnmb=resdat[i].resnmb
            if atm not in const.AmiResH[resnam]: continue
            #nhatm=self.CountHydrogenOfAtom(iatm)
            nhatm=0
            if nhatm > 0:
                mess=str(nhatm)+'AddHydrogenToAARes: Hydrogen is already attached at '+str(iatm)+'. Skipped.'
                #self.Message(mess,0,'blue')
                #self.ConsoleMessage(mess)
                self.Message(mess,True)
                continue
            #if atm == ' N  ':
            #    isn=iatm
            #    print 'n found,isn',isn
            htype=const.AmiResH[resnam][atm][0]
            hnam=const.AmiResH[resnam][atm][1]
            hcon=const.AmiResH[resnam][atm][2]
            rbnd=const.AmiResH[resnam][atm][3]
            # skip S-S bond
            if (resnam == 'CYS' or resnam == 'CYX') and atm == ' SG ':
                #
                if len(resdat[i].conect) >= 2: continue
            atmlst=[]; atmlst.append(iatm)
            for j in range(len(hcon)):
                coord=[]; lbl=[]
                conatm=hcon[j]
                if conatm == '-C  ':
                    if ic >= 0:
                        #if isn >= 0:
                        #    r=self.InterAtomDistance(ic,isn)
                        #    print 'isn,ic,r',isn,ic,r
                        #    if r < 1.6:
                        #        jatm=ic; atmlst.append(jatm)
                        #    else: htype='non' #jatm=ic; atmlst.append(jatm)
                        #try:
                        jatm=ic; atmlst.append(jatm)
                        #except: print 'ic',ic
                    else:
                        htype='non'
                else:
                    jatm=self.FindResAtmSeqNmb(resdat,conatm)
                    jatm += nht+iatm
                    if jatm >= 0:
                        atmlst.append(jatm)
                    else:
                        htype='non'
            if htype == '1A1':
                nh,coord=self.GetCCAddAtmType1A1(atmlst,rbnd)
            if htype == '1A2':
                nh,coord=self.GetCCAddAtmType1A2(atmlst,rbnd)
            if htype == '1A3':
                nh,coord=self.GetCCAddAtmType1A3(atmlst,rbnd,-1,True)
            if htype == '2A1':
                nh,coord=self.GetCCAddAtmType2A1(atmlst,rbnd)
            if htype == '2A2':
                nh,coord=self.GetCCAddAtmType2A2(atmlst,rbnd)
            if htype == '3A1':
                nh,coord=self.GetCCAddAtmType3A1(atmlst,rbnd)
            if htype == 'non': pass
            if htype != 'non':
                at=iat+nht
                self.AddHydrogen1(iatm,nh,coord,hnam) #(iatm,nh,coord,hnam)
                nht += nh
        #self.AddHydrogens(addlst)

        return nht

    def AddBondInAARes(self,resnam,resdat):
        # NOTE! this routine is not tested.
        # add bond to amino acid residue
        if not resnam in const.AmiRes3: # .has_key(resnam):
            #mess=resnam+' is not amino acid residue. Skipped.'
            #self.Message(mess,True) #,0,'blue')
            #self.ConsoleMessage(mess)
            return
        if len(resdat) <= 0:
            mess='No atoms in '+resnam+'. Skipped.'
            self.Message(mess,True) #,0,'blue')
            #self.ConsoleMessage(mess)
            return
        for i in range(len(resdat)):
            elm=resdat[i].elm
            if elm == 'XX': continue
            atm=resdat[i].atmnam; nmb=resdat[i].seqnmb; con=resdat[i].conect
            ###ia=resdat[i].seqnmb #con[0]
            ia = self.FindResAtmSeqNmb(resdat, atm)
            if atm == ' OXT':
                ja=self.FindPrevAtom(ia,' C  ')
                if ja >= 0:
                    self.AddBond(ia,ja,1)
                    continue
            if not atm in const.AmiResBnd[resnam]: #.has_key(atm):
                continue
            hcon=const.AmiResBnd[resnam][atm] # [[atmnam,mbnd],...]
            #
            for j in range(len(hcon)):
                conatm=hcon[j][0]
                mbnd=hcon[j][1]
                if conatm == '-C  ':
                    ja=self.FindPrevAtom(ia,' C  ')
                    if ja < 0: continue
                elif conatm == '+N  ':
                    continue
                else:
                    ja=self.FindResAtmSeqNmb(resdat,conatm)
                #
                if ja >=0:
                    #self.AddBond(ia,ja,mbnd)
                    try:
                        idx=self.atm[ia].conect.index(ja)
                    except:
                        idx=-1
                    if idx >= 0:
                        self.atm[ia].bndmulti[idx] = mbnd
                    else:
                        self.atm[ia].conect.append(ja)
                        self.atm[ia].bndmulti.append(mbnd)

    def FindResAtmSeqNmb(self,resdat,conatm):
        iatm=-1
        for i in range(len(resdat)):
            if resdat[i].atmnam == conatm:
                iatm=resdat[i].seqnmb
                break
        return iatm

    def FindPrevAtom(self,ia,atmnam):
        ja=-1
        for i in range(ia):
            if self.atm[i].atmnam == atmnam:
                ja=self.atm[i].seqnmb
            else: continue
        return ja

    def FindNextAtom(self,ia,atmnam):
        ja=-1
        if ia+1 > len(self.atm):
            print((' Program error(FindNextCatm): wrong sequential number.',ia))
            return ja
        for i in range(ia+1,len(self.atm)):
            if self.atm[i].atmnam == atmnam:
                ja=self.atm[i].seqnmb; break
        return ja

    def FindCOCarbonInRes(self,resnam,resnmb):
        ic=-1; i=0
        for atom in self.atm:
            res=atom.resnam
            nmb=atom.resnmb
            atm=atom.atmnam
            i += 1
            if res == resnam and nmb == resnmb and atm ==' C  ':
                    ic=i; break
        return ic

    def MakeSSBond(self,lst,cyx):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        nss=0; sulf=' S'; coord=[]; elmlst=[]; bndlst=[]; seqnmb=[]
        for i in lst:
            atom=self.atm[i]
            if atom.elm == sulf:
                seqnmb.append(i)
                coord.append(atom.cc)
                elmlst.append(sulf)
        numpy.array(coord)
        if len(elmlst) > 0:
            bndlst=self.FindCovalentBondedAtom(elmlst,coord)
        nss=0; resdic={}
        if len(bndlst) > 0:
            for i,j,rij in bndlst:
                ia=seqnmb[i]; ja=seqnmb[j]
                for k in range(len(self.atm[ia].conect)):
                    elm=self.atm[ia].elm
                    if elm == ' H': self.DelBond(ia,k)
                for k in range(len(self.atm[ja].conect)):
                    elm=self.atm[ja].elm
                    if elm == ' H': self.DelBond(ja,k)
                self.AddBond(ia,ja,1) # 1:single bond
                nami=self.atm[ia].resnam; nmbi=self.atm[ia].resnmb
                namj=self.atm[ja].resnam; nmbj=self.atm[ja].resnmb
                resi=nami+':'+str(nmbi); resj=namj+':'+str(nmbj)
                resdic[resi]=1; resdic[resj]=1
                nss += 1
                #
        if cyx and len(resdic) > 0:
            for atom in self.atm:
                res=atom.resnam+':'+str(atom.resnmb)
                if res in resdic: atom.resnam="CYX"

        return nss

    def AddHydrogenToWaterMol(self,lst):
        # add hydrogen to water molecules
        # lst(lst): target atom list. if [], all atoms are targetted.
        #
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        #else: lst.sort()
        nw=self.CountWater(lst)
        if nw <= 0:
            mess="No water molecule selected."
            self.Message(mess,True) #,0,"")
            return
        nh=2; hnam=[' H1 ',' H2 ']
        nwat=0 #; nsel=len(lst);
        natm=len(lst)
        i=-1; na=0; nht=0
        while na < natm:
            i += 1; na += 1
            #ii=i+nht
            #if nsel > 0:
            ii=lst[i]+nht
            res=self.atm[ii].resnam; elm=self.atm[ii].elm
            #wat=(res == "HOH" or res == 'DOD' or res == "WAT")
            #if not wat: continue
            if not res in const.WaterRes: continue
            if elm != ' O': continue
            if len(self.atm[ii].conect) >= 2: continue
            if len(self.atm[ii].conect) == 1:
                #mess='Skipped, becouse one hydrogen is already attached.'
                #self.Message(mess+' on OW atom='+str(ii),True) #,0,'blue')
                #self.ConsoleMessage(mess)
                continue
            cow=self.atm[ii].cc
            chw=self.GetCCOfWaterHydrogen(cow)
            self.AddHydrogen(ii,nh,chw,hnam)
            nht += nh; nwat += 1
        if nht > 0:
            mess='AddHydrogenToWater: Hydrogens are attached to '+str(nwat)+' waters.'
            #self.Message(mess,0,'black')
            #self.ConsoleMessage(mess)
            self.Message(mess,True)
        else:
            mess='AddHydrogenToWater: No hydrogen is attached to water.'
            #self.Message(mess,0,'black')
            #self.ConsoleMessage(mess)
            self.Message(mess,True)

    def AddGroup1Hydrogen(self,lst,atmnamslt=None):
        # add one hydrogen
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        if len(lst) > 0:
            natm=len(lst)
            i=-1; na=0; nht=0
            while na < natm:
                i += 1; na += 1
                ia=lst[i]+nht
                atom=self.atm[ia]
                nb=len(atom.conect)
                elm=atom.elm
                if elm == ' H': continue
                htype='non'; bndlst=[]; done=False
                btype='    '
                if elm == ' C': btype=' H C'
                elif elm == ' N': btype=' H N'
                elif elm == ' O': btype=' H O'
                elif elm == ' S': btype=' H S'
                if btype not in const.CovBndLen:
                    mess='Covalent bond length for "'+elm+' H"'
                    mess=mess+' is not defined in fufnc.CovBndLen.'
                    self.Message(mess,True) #,0,'red')
                    #self.ConsoleMessage(mess)
                    continue
                rhx=const.CovBndLen[btype][0]
                #
                nhatm=self.CountHydrogenOfAtom(ia)
                if nb == 1: # O and S atom
                    if nhatm > 0:
                        mess='Hydrogens are already attached at '+str(ia)+'. Skipped.'
                        self.Message(mess,True) #,0,'blue')
                        #self.ConsoleMessage(mess)
                        continue
                    if elm == ' O' or elm == ' S':
                        ib=atom.seqnmb; bndlst.append(ib)
                        if len(self.atm[ib].conect) >=1:
                            ic=self.atm[ib].seqnmb; bndlst.append(ic)
                            htype='1A3'
                elif nb == 2: # sp2 is assumed
                    if nhatm > 1:
                        mess='Hydrogens are already attached at '+str(ia)+'. Skipped.'
                        self.Message(mess,True) #,0,'blue')
                        #self.ConsoleMessage(mess)
                        continue
                    if elm == ' C' or elm == ' N':
                        bndlst.append(atom.conect[0])
                        if len(atom.conect) >=2:
                            ib=atom.conect[1]; bndlst.append(ib)
                            htype='1A2'
                elif nb == 3: # sp3 is assumed
                    if nhatm > 2:
                        mess='Hydrogens are already attached at '+str(ia)+'. Skipped.'
                        self.Message(mess,True) #,0,'blue')
                        #self.ConsoleMessage(mess)
                        continue
                    if elm == ' C' or elm == ' N':
                        bndlst.append(atom.conect[0])
                        if len(atom.conect) >=3:
                            ib=atom.conect[1]; bndlst.append(ib)
                            ib=atom.conect[2]; bndlst.append(ib)
                            htype='1A1'
                if htype != 'non':
                    nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                    nht += nh
                    done=True
                    #print 'nh',nh
                if not done or nh == 0:
                    mess='Unable to attach H atom at '+str(ia)+'. Skipped.'
                    mess=mess+' Nmber of bonds= '+str(nb)
                    self.Message(mess,True) #,0,'bule')
                    #self.ConsoleMessage(mess)
        else:
            mess='No selected atoms.'
            self.Message(mess,True) #,0,'blue')

    def AddGroup2Hydrogen(self,lst):
        # add two hydrogens
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        if len(lst) > 0:
            natm=len(lst)
            i=-1; na=0; nht=0
            while na < natm:
                i += 1; na += 1
                ia=lst[i]+nht
                atoma=self.atm[ia]
                nb=len(atoma.conect)
                elm=atoma.elm

                htype='non'; bndlst=[]; done=False
                btype='    '
                if elm == ' C': btype=' H C'
                elif elm == ' N': btype=' H N'
                elif elm == ' O': btype=' H O'
                elif elm == ' S': btype=' H S'
                if btype not in const.CovBndLen:
                    mess='Covalent bond length for '+btype
                    mess=mess+' is not defined in fufnc.CovBndLen.'
                    self.Message(mess,True) #,0,'red')
                    #self.ConsoleMessage(mess)
                    continue
                rhx=const.CovBndLen[btype][0]

                nhatm=self.CountHydrogenOfAtom(ia)
                if nhatm > 1:
                    mess='Hydrogens are already attached at '+str(ia)+'. Skipped.'
                    self.Message(mess,True) #,0,'blue')
                    #self.ConsoleMessage(mess)
                    continue
                if nb == 1: # C and N
                    if elm == ' C' or elm == ' N':
                        ib=atoma.conect[0]; bndlst.append(ib)
                        if len(self.atm[ib].conect) >=1:
                            ic=self.atm[ib].conect[1]
                            if ic == ia:
                                if len(self.atm[ib].conect) >= 3:
                                    ic=self.atm[ib].conect[2]
                                    bndlst.append(ic)
                                    htype='2A2'
                                else: htye='non'
                elif nb == 2: # sp3 is assumed
                    if elm == ' C' or elm == ' N':
                        bndlst.append(atoma.conect[0])
                        if len(atoma.conect) >=1:
                            ic=atoma.conect[1]; bndlst.append(ic)
                            htype='2A1'
                if htype != 'non':
                    nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                    nht += nh
                    done=True
                if not done or nh == 0:
                    mess='Unable to attach H atom at '+str(ia)+'. Skipped.'
                    mess=mess+' Nmber of bonds= '+str(nb)
                    self.Message(mess,True) #,0,'bule')
                    #self.ConsoleMessage(mess)
        else:
            self.Message('No selected atoms. Nothing done.',True) #,0,'blue')

    def AddGroup3Hydrogen(self,lst):
        # add three hydrogens
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        bndlst=[]; nh=0
        rhx=1.090
        if len(lst) > 0:
            natm=len(lst)
            i=-1; na=0; nht=0
            while na < natm:
                i += 1; na += 1
                ia=lst[i]+nht
                atom=self.atm[ia]
                bndlst=[]
                nhatm=self.CountHydrogenOfAtom(ia)
                elm=atom.elm
                if nhatm > 0:
                    mess=str(nhatm)+' hydrogens are already attached at '+str(ia)+'. Skipped.'
                    self.Message(mess,True) #,0,'blue')
                    #self.ConsoleMessage(mess)
                    continue
                if elm == ' C' or elm == ' N':
                    if len(atom.conect) <= 1:
                        bndlst.append(atom.conect[0])
                        htype='3A1'
                        nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                        nht += nh
                else:
                    mess='Unable to attach three H atoms at '+str(ia)+'. Skipped.'
                    self.Message(mess,True) #,0,'bule')
                    #self.ConsoleMessage(mess)
                    continue
        else:
            self.Message('No atoms are selected.',True) #,0,'blue')

    def AddHydrogenToMol(self,at,hname,htype,bndlst,rhx,atend=False):
        # add hydrogen atom at 'at' atom using 'htype','bndlst' and 'rhx'.
        hnam=hname
        if len(hname) <= 0: hnam=[' H1 ',' H2 ',' H3 ']
        atmlst=[]; nh=0
        natm=len(self.atm)
        atoma=self.atm[at]
        elm=atoma.elm
        # find bond multiplicity
        if htype == 'non': return
        #
        atmlst.append(at)
        if htype == '1A1': atmlst=atmlst+bndlst
        elif htype == '1A2': atmlst=atmlst+bndlst
        elif htype == '1A3':
            ib=bndlst[1]
            atomb=self.atm[ib]
            if len(atomb.conect) <= 0:
                atmnam=atoma.atmnam+':'+str(atoma.atmnmb)
                mess='AddHydrogenToMol: unable to attach hydrogen at ',atmnam
                self.Message(mess,True) #,0,'blue')
                #self.ConsoleMessage(mess)
            else:
                ic=atomb.conect[0]
                atmlst=atmlst+bndlst; atmlst.append(ic)
        elif htype == '2A1': atmlst=atmlst+bndlst
        elif htype == '2A2':
            ib=bndlst[1]
            atomb=self.atm[ib]
            if len(atomb.conect) < 1:
                atmnam=atoma.atmnam+':'+str(atoma.atmnmb)
                mess='AddHydrogenToMol: unable to attach hydrogen at ',atmnam
                self.Message(mess,True) #,0,'blue')
                #self.ConsoleMessage(mess)
            else:
                ic=atomb.conect[0]
                if ic == at: ic=atomb.conect[1]
                atmlst=atmlst+bndlst; atmlst.append(ic)
        elif htype == '3A1':
            atmlst=atmlst+bndlst

        else:
            mess='AddHydrogenToMol: failed to Add hydrogen at '+str(at)+'.'
            self.Message(mess,True) #,0,'blue')
            #self.ConsoleMessage(mess)
        if htype == '1A1':
            #print '1A1,atmlst,rhx',atmlst,rhx
            nh,coord=self.GetCCAddAtmType1A1(atmlst,rhx)
        if htype == '1A2': nh,coord=self.GetCCAddAtmType1A2(atmlst,rhx)
        if htype == '1A3': nh,coord=self.GetCCAddAtmType1A3(atmlst,rhx,-1,True) # trans
        if htype == '2A1': nh,coord=self.GetCCAddAtmType2A1(atmlst,rhx)
        if htype == '2A2': nh,coord=self.GetCCAddAtmType2A2(atmlst,rhx)
        if htype == '3A1': nh,coord=self.GetCCAddAtmType3A1(atmlst,rhx)
        #
        if nh < 0: nh=0
        if nh > 0:
            #self.AddHydrogen(at,nh,coord,hnam)
            if atend: self.AddHydrogen1(at,nh,coord,hnam)
            else:     self.AddHydrogen(at,nh,coord,hnam)
        return nh

    def AddHydrogenUseBL(self,lst):
        # Add hydrogen atoms using bond length data.
        # C, N, O and S are supporeted as attached atom.
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        natm=len(lst)
        #
        i=-1; na=0; nht=0
        while na < natm:
            i += 1; na += 1
            ia=lst[i]+nht
            nhatm=self.CountHydrogenOfAtom(ia)
            if nhatm > 0:
                mess=str(nhatm)+' hydrogens are already attached at '+str(ia)+'. Skipped.'
                self.Message(mess,True) #,0,'blue')
                #self.ConsoleMessage(mess)
                continue
            nh,htype,bndlst,rhx=self.FindAddHTypeBL(ia)
            if htype == 'non': continue
            nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
            nht += nh
            #i += nh
    def FindAddHTypeBL(self,a):
        # return bond multiplicity bndmul of atom 'a'(sorted seq number).
        # bond multiplicity is estimated based on bond length
        atoma=self.atm[a]
        elm=atoma.elm
        nh=0; htype='non'; bndlst=[]; rhx=0.0
        if elm != ' C' and elm != ' N' and elm != ' O' and elm != ' S':
            return nh,htype,bndlst,rhx
        dxy=0.10; dss=0.22 # margin of bond length
        ccmul=[1.60,1.50,1.38,1.28,1.18] # max, single,aromatic,double,triple bond, respectively
        ccnv=[1,1.51,2,3]
        natm=len(self.atm)
        lbl=atoma.atmnam+':'+str(atoma.atmnmb)
        atmnam=atoma.atmnam
        elma=atoma.elm
        # detrmine bond multiplicity relying on bond length
        bndlst=list(atoma.conect)
        nb=len(bndlst); nv=0; nbc=0; ccc=[]
        # try fortran codes
        fort=False
        try:
            cc0=[]; cc1=[]
            cc0.append(self.atm[a])
            for i in bndlst:
                cc1.append(self.atm[i].cc)
            #if len(cc0) <= 0 or len(cc1) <= 0:
            rmin=0.0; rmax=3.0; iopt=0
            npair,iatm,jatm,dislst=fortlib.find_contact_atoms0(cc0,cc1,rmin,rmax,iopt)
            if npair > 0: fort=True
        except: fort=False
        #
        for i in range(len(bndlst)): #j in bndlst:
            j=bndlst[i]
            if fort: dist=dislst[i]
            else: dist=self.InterAtomDistance(a,j)
            elmb=self.atm[j].elm
            bnd=elma+elmb
            if const.ElmNmb[elmb] < const.ElmNmb[elma]: bnd=elmb+elma
            #
            d=dxy
            if bnd == ' S  S': d=dss
            nvt=0
            if bnd == ' C C':
                nbc += 1
                ccc.append(self.atm[j].cc)
                for k in range(4):
                    if dist < ccmul[k] and dist >= ccmul[k+1] : nvt=ccnv[k]
            elif bnd in const.CovBndLen:
                bl=const.CovBndLen[bnd]
                #
                for k in bl: #range(nm):
                    if abs(dist-k) < d:
                        nvt=k+1; break
                if nvt == 0: nvt=1
            else:
                nvt=1
                mess='FindAddHTypeBL: No covalent bond length is defined for '+elma+'-'+elmb
                mess=mess+'. Single bond is assumed.'
                self.Message(mess,True) #,0,'blue')
                #self.ConsoleMessage(mess)
            nv=nv+nvt
        nv=int(nv)
        # additional special code for three 'C C ' bonded C atom
        if nbc == 3 and nb ==3:
            c0=atoma.cc; ca=ccc[0]; cb=ccc[1]; cc=ccc[2]
            ca=numpy.subtract(ca,c0); cb=numpy.subtract(cb,c0)
            cc=numpy.subtract(cc,c0)
            ang=lib.AngleT(ca,cb)+lib.AngleT(cb,cc)+lib.AngleT(cc,ca)
            #
            if numpy.degrees(ang) < 340.0: nv=3
        #
        if elma == ' C':
            if nb == 3 and nv == 3:
                htype='1A1'; rhx=const.CovBndLen[' H C'][1]; nh=1
            if nb == 2 and nv == 3:
                htype='1A2'; rhx=const.CovBndLen[' H C'][1]; nh=1
            if nb == 2 and nv == 2:
                htype='2A1'; rhx=const.CovBndLen[' H C'][0]; nh=2
            if nb == 1 and nv == 2:
                htype='2A2'; rhx=const.CovBndLen[' H C'][1]; nh=2
            if nb == 1 and nv == 1:
                htype='3A1'; rhx=const.CovBndLen[' H C'][0]; nh=3
        elif elma == ' N':
            if nb == 2 and nv == 1:
                htype='1A2'; rhx=const.CovBndLen[' H N'][1]; nh=1
            if nb == 1 and nv == 1:
                htype='2A2'; rhx=const.CovBndLen[' H N'][0]; nh=2
        elif elma == 'O ':
            if nb == 1 and nv == 1:
                htype='1A3'; rhx=const.CovBndLen[' H O'][0]; nh=1
        elif elma == 'S ':
            if nb == 1 and nv == 1:
                htype='1A3'; rhx=const.CovBndLen[' H S'][0]; nh=1
        if htype == '1A3' or htype =='2A2':
            # add next neighbor bond atom to bndlst
            ic=-1
            for k in bndlst:
                atomk=self.atm[k]
                if len(atomk.conect) >= 1:
                    jx=atomk.conect[0]
                    bndlst.append(jx); ic=0; break
            if ic < 0: htype='non'

        return nh,htype,bndlst,rhx

    def FindAddHTypeBM(self,a): #AN,nb,nh,bndlst,li_atoms,li_connect):
        """ Find 'AddHType' based on number of bonds and number of H's to be attached

        'AddHType's are 1A0,1A1,1A2,1A4,2A0,2A1,2A2,3A1,and 4A0. the first number
        in the code shows the number of hydrogens to be added and the last number
        just the sequence number in each type.
        """
        # X-H bond length (X=C,N,O,P,S,Se)
        rhc = [1.09, 1.08, 1.07]
        rhn = [1.01, 1.01]
        rho = [0.96, 0.96]
        rhp = [1.38]  # PH2
        rhs = [1.33]  # SH2
        rhse = [1.46] # SeH2
        # X-H (X=F,Cl,Br,I)
        rhf  = [0.92]
        rhcl = [1.31]
        rhbr = [1.46]
        rhi  = [1.65]
        elmlst = [' C',' N',' O',' P',' S','SE']
        #
        htype = ''
        rhx = 1.0

        atoma=self.atm[a]
        elma=atoma.elm
        nh=0; htype='non'; bndlst=[]; rhx=0.0
        #if elm != ' C' and elm != ' N' and elm != ' O' and elm != ' S':
        if not elma in elmlst:
            return nh,htype,bndlst,rhx
        dxy=0.10; dss=0.22 # margin of bond length
        ccmul=[1.60,1.50,1.38,1.28,1.18] # max, single,aromatic,double,triple bond, respectively
        ccnv=[1,1.51,2,3]
        natm=len(self.atm)
        lbl=atoma.atmnam+':'+str(atoma.atmnmb)
        atmnam=atoma.atmnam
        #elma=atoma.elm
        # detrmine bond multiplicity relying on bond length
        bndlst=list(atoma.conect)
        nb = len(bndlst)
        nval = 0
        for m in atoma.bndmulti: nval += m
        nv=0; nbc=0; ccc=[]
        AN = const.ElmNmb[elma]
        nh = const.ElmValence[elma]- nval
        if nb <= 0:
            mess = 'molec.FindAddHTypeBM: Number of bond of the atom ' + str(a)
            mess += '. Unable to add hydrogens '
            self.messout2(mess)
            return nh,htype,bndlst,rhx
        if nh <= 0:
            #mess = 'molec.FindAddHTypeBM: The hydrogens are already attached. '
            #mess += ' nh = ' + str(nh) + ' at the atom ' + str(a) + '.'
            #self.messout2(mess)
            return nh,htype,bndlst,rhx

        if AN == 6:
            if nb == 3 and nh == 1:
                htype = '1A1'; rhx = rhc[0]
            if nb == 2 and nh == 1:
                htype = '1A2'; rhx = rhc[1]
            if nb == 1 and nh == 2:
                htype = '2A2'; rhx = rhc[1]
            if nb == 2 and nh == 2:
                htype = '2A1'; rhx = rhc[0]
            if nb == 1 and nh == 3:
                htype = '3A1'; rhx = rhc[0]
            if nb == 1 and nh == 1:
                htype = '1A4'; rhx = rhc[2]
        elif AN == 7:
            if nb == 2 and nh == 1:
                htype = '1A2'; rhx = rhn[0]
            if nb == 1 and nh == 2:
                htype = '2A2'; rhx = rhn[1]
            if nb == 1 and nh == 1:
                htype = '1A3'; rhx = rhn[0]
                #htype = '1A4'; rhx = rhn[0]
            #if nb == 0 and nh == 3:
            #    htype = '3A1'; rhx = rhn[0]
            if nb == 1 and nh == 3:
                htype = '3A1'; rhx = rhn[0]
        elif AN == 8: # O
            if nb == 1 and nh == 1:
                htype = '1A3'; rhx = rho[0]
            #if nb == 0 and nh == 2:
            #    htype = '2A0'; rhx = rho[0]
        elif AN == 15: # P
            if nb == 2 and nh == 1:
                htype = '1A2'; rhx = rhp[0]
            if nb == 1 and nh == 2:
                htype = '2A2'; rhx = rhp[0]
            if nb == 1 and nh == 1:
                htype = '1A3'; rhx = rhp[0]
            #if nb == 0 and nh == 3:
            #    htype = '3A1'; rhx = rhp[0]
        elif AN == 16: # S
            if nb == 1 and nh == 1:
                htype = '1A3'; rhx = rhs[0]
            #if nb == 0 and nh == 2:
            #    htype = '2A0'; rhx = rhs[0]
        elif AN == 34: # Se
            if nb == 1 and nh == 1:
                htype = '1A3'; rhx = rhse[0]
            #if nb == 0 and nh == 2:
            #    htype = '2A0'; rhx = rhse[0]
        else:
            mess = 'Sorry, atomic number:' + str(AN) + ' is not supported.'
            self.messout2(mess)
            return nh,htype,bndlst,rhx
        #
        if nh > 0 and htype == '':
            mess  ='Program error(FindAddHtype): No addhtype is found. AN,nb,nh '
            mess += str(AN) + ', ' + str(nb) +', ' + str(nh)
            self.messout2(mess)
        if htype == '1A3' or htype =='2A2':
            # add next neighbor bond atom to bndlst
            ic = -1
            for k in bndlst:
                if len(self.atm[k].conect) >= 1:
                    jx = self.atm[k].conect[0]
                    bndlst.append(jx)
                    ic = 0
                    break
            if ic < 0: htype = 'non'
        #
        return nh,htype,bndlst,rhx

    def AddBondUseBL(self,lst):
        # add bonds between atoms in lst based on bond length
        if len(lst) <= 0:
            for i in range(len(self.atm)):
                if self.atm[i].elm == "XX": continue
                if self.atm[i].elm == " X": continue
                lst.append(i)
        try:
            # fortlib Fortran code
            #print 'AddbondUseBL:fortran code is use.'
            cc=[]; rad=[]
            #for i in xrange(len(self.atm)):
            for i in lst:
                atom=self.atm[i]
                cc.append(atom.cc)
                rad.append(const.ElmCov[atom.elm])
            if len(cc) <= 0: return
            margin=1.2 #1.1
            ndat,iatm,jatm=fortlib.find_contact_atoms1(cc,rad,margin)
            for i in range(ndat): #(len(iatm)):
                ia=lst[iatm[i]]; ja=lst[jatm[i]]
                if self.atm[ia].elm == ' X' or self.atm[ja].elm == ' X': continue
                #ia=iatm[i]; ja=jatm[i]
                self.AddBond(ia,ja,1)
        except:
            if len(lst) <= 0:
                for i in range(len(self.atm)):
                    if self.atm[i].elm == "XX": continue
                    lst.append(i)

            elm=[]; coord=[]
            numpy.array(coord)
            for i in lst:
                atom=self.atm[i]
                if atom.elm == 'XX' or atom.elm == ' X': continue
                coord.append(atom.cc)
                elm.append(atom.elm)
            if len(coord) <= 0: return
            bndlst=lib.CovalentBondedAtomList(elm,coord)
            #coni=[]; conj=[]; list(coni); list(conj)
            if len(bndlst) > 0:
                for i,j,r in bndlst:
                    ia=lst[i]; ja=lst[j]
                    if self.atm[ia].elm == ' X' or self.atm[ja].elm == ' X': continue
                    self.AddBond(ia,ja,1)

    def AddHydrogenUseBM(self,lst,atend=True):
        # Not completed yet
        # Add hydrogen atoms using bond multiplicity
        # C, N, O and S are suppoeted as attached atom.
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))
        #lsttmp = lst[:]
        nadd = 0
        for ia in lst: #range(len(self.wrk.mol)):
            elma = self.atm[ia].elm
            if elma == ' H': continue
            #AN = const.ElmNmb[elma]
            nb = 0
            for m in self.atm[ia].bndmulti: nb += m
            try: nh = const.ElmValence[elma]- nb
            except:
                mess = 'Sorry, the valence of ' + elma + ' is not defined.'
                wx.MessageBox(mess,'fu_molec.AddHydrogenUseBM')
                return
            if nh <= 0: continue
            naddedh,htype,bndlst,rhx=self.FindAddHTypeBM(ia)
            if htype == 'non': continue
            self.AddHydrogenToMol(ia,[],htype,bndlst,rhx,atend=atend)
            nadd += nh
        return nadd

    def AddBondUseFrame(self,lst,framedatdic):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        # add bonds between heavy atoms using mht data.
        mhtres=list(framedatdic.keys())
        for res in mhtres:
            nresatm,mhtdat=framedatdic[res]
            prvres=''; firstatm=True
            for i in lst:
                atom=self.atm[i]
                resnam=atom.resnam; resnmb=atom.resnmb; chain=atom.chainnam
                if resnam != res: continue
                curres=resnam+':'+str(resnmb)+':'+chain
                if firstatm:
                    mess='attach hydrogens to '+curres
                    #self.ConsoleMessage(mess)
                    self.Message(mess,True)
                    firstatm=False
                if curres != prvres:
                    ist=i
                    for j in range(len(mhtdat)):
                        s1=mhtdat[j][0]
                        if s1[0:1] == 'H': continue
                        s1=' '+s1; s1=s1[0:4]
                        ia=self.FindAtmNamInRes(s1,ist,resnam,resnmb)
                        if ia < 0:
                            mess='Atom name '+s1+' is not found. Skipped'
                            self.Message(mess,True) #,0,'blue')
                            #self.ConsoleMessage(mess)
                            #
                            continue
                        for k in range(1,len(mhtdat[j])):
                            s2=mhtdat[j][k]
                            if s2[0] == 'H': continue
                            s2=' '+s2; s2=s2[0:4]
                            #    s2=sx[0:2]+s2[2:4]
                            ib=self.FindAtmNamInRes(s2,ist,resnam,resnmb)

                            if ib < 0:
                                mess='Atom name '+s2+' is not found. Skipped'
                                self.Message(mess,True) #,0,'blue')
                                #self.ConsoleMessage(mess)
                                continue
                            if ia >= 0 and ib >= 0: self.AddBond(ia,ib,1)
                    prvres=curres; firstatm=True

    def FindAtmNamInRes(self,atmnam,ist,resnam,resnmb):
        # find sequence number of atomnam atom in residue
        ia=-1
        for i in range(ist,len(self.atm)):
            atom=self.atm[i]
            res=atom.resnam; nmb=atom.resnmb
            if res != resnam or nmb != resnmb: break
            if atom.elm == ' H': continue
            if atom.atmnam == atmnam:
                ia=i; break
        return ia

    def AddHydrogenUseFrame(self,lst,framedatdic):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        donedic={}
        na=0; nht=0
        frameres=list(framedatdic.keys())
        for res in frameres:
            nresatm,framedat=framedatdic[res]
            prvres=''
            for i in lst:
                ii=i+nht
                atom=self.atm[ii] #[i]
                resnam=atom.resnam; resnmb=atom.resnmb; chainnam=atom.chainnam
                if resnam != res: continue
                curres=resnam+':'+str(resnmb)+':'+chainnam
                if curres in donedic: continue
                if curres != prvres:
                    mess='Attaching hydrogens to '+curres
                    self.Message(mess,True) #,0,'')
                    #self.ConsoleMessage(mess)
                    natm=self.CountAtomsInRes(resnam,resnmb,chainnam)
                    ist=i-1; na=0
                    while na < natm:
                        ist += 1; na += 1
                        ia=ist+nht
                        nhatm=self.CountHydrogenOfAtom(ia)
                        if nhatm > 0:
                            mess=str(nhatm)+' hydrogens are already attached at '+str(ia+1)+'. Skipped.'
                            self.Message(mess,True) #,0,'blue')
                            #self.ConsoleMessage(mess)
                            continue
                        nh,htype,bndlst,rhx=self.FindAddHTypeFrame(ia,framedat)
                        if htype == 'non': continue
                        if len(bndlst) <= 1:
                            mess='Failed to attach hydrogen atoms at '+str(ia+1)+'.'
                            self.Message(mess,True) #,0,'blue')
                            #self.ConsoleMessage(mess)
                            continue
                        nh=self.AddHydrogenToMol(ia,[],htype,bndlst,rhx)
                        nht += nh
                    prvres=curres; donedic[curres]=True
            nht=0; lst=list(range(len(self.atm)))

    def AssignAAResAtmChg(self):
        # assign atomic formal charge to be used in calc. fragment charge
        for atom in self.atm:
            chg=0.0
            res=atom.resnam; nmb=atom.resnmb
            if res not in const.AmiRes3: continue
            atm=atom.atmnam
            i=atom.seqnmb
            #if res == 'HIS':
            #    if self.CountResH(res,nmb) == 7: continue
            if res in const.AmiResAtmChg:
                if atm in const.AmiResAtmChg[res]:
                    if res in const.HisRes:
                        if self.CountResH(res,nmb) == 8:
                            chg=const.AmiResAtmChg[res][atm]
                        else: chg=0.0
                    else: chg=const.AmiResAtmChg[res][atm]
            try:
                self.atm[i].frgchg=chg
            except:
                return False
        #ACE and NME
        for i in range(len(self.atm)):
            if self.atm[i].resnam == 'ACE' or self.atm[i].resnam == 'NME':
                self.atm[i].frgchg=0.0
        # forN terminus
        for atom in self.atm:
            ia=-1; i=atom.seqnmb
            if atom.atmnam == ' N  ': ia=i
            if ia >= 0:
                nh=0
                for j in range(len(self.atm[ia].conect)):
                    it=self.atm[ia].conect[j]
                    if self.atm[it].elm == ' H': nh += 1

                if nh == 3: # NH3+ terminal
                    for j in range(len(self.atm[ia].conect)):
                        it=self.atm[ia].conect[j]
                        if self.atm[it].elm == ' H':
                            self.atm[it].frgchg=0.334
        # for C terminus.
        for atom in self.atm:
            if atom.atmnam == ' OXT':
                nbnd=len(atom.conect)
                if nbnd == 1:
                    ic=atom.conect[0]
                    for j in range(len(self.atm[ic].conect)):
                        ja=self.atm[ic].conect[j]
                        if self.atm[ja].atmnam == ' O  ':
                            atom.frgchg=-0.501
                            self.atm[ja].frgchg=-0.501
        # for HIS
        nhis=0
        """
        for atom in self.atm:
            res=atom.resnam
            nmb=atom.resnmb
            atm=atom.atmnam
            if nhis == 0 and res == 'HIS': prv=nmb
            if res == 'HIS' and nmb != prv:
                nhis=1
                nh=self.wrk.CountResH(res,nmb)
                if nh == 8:
                    if atm == ' ND1' or atm == ' NE2':
                        self.atm[i].frgchg=0.501
                prv=nmb
        """
        return True

    def CountAtomsInRes(self,resnam,resnmb,chain):
        natm=0
        for atom in self.atm:
            if atom.resnam == resnam and atom.resnmb == resnmb and atom.chainnam == chain: natm += 1
        return natm

    def FindAddHTypeFrame(self,a,framedat):
        # find add h type using connect data.
        # only 'C', 'N','O' and 'S' are supported.
        atoma=self.atm[a]
        elm=atoma.elm
        nh=0; htype='non'; bndlst=[]; rhx=0.0
        if elm != ' C' and elm != ' N' and elm != ' O' and elm != ' S':
            return nh,htype,bndlst,rhx
        atmnam=atoma.atmnam
        conlst=[]
        for i in range(len(framedat)):
            s=framedat[i][0]
            if s[0:1] == 'H': continue
            s=' '+s
            if s[0:4] == atmnam:
                conlst=framedat[i]; break
        atmnam=atoma.atmnam.ljust(4)

        nb=0; nh=0
        for i in range(1,len(conlst)):
            s=conlst[i]; blsti=atoma.conect
            if s[0:1] == 'H': nh += 1
            else:
                nb += 1
                atm=' '+s[0:4] # note: atmnam in condic is shifted left by one.
                for j in blsti:
                    if self.atm[j].atmnam == atm[0:4]:
                        bndlst.append(j)
                        break
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
        if htype == '1A3' or htype =='2A2'or htype == '3A1':  # add next neighbor bond atom to bndlst
            ic=-1
            for k in bndlst:
                atomk=self.atm[k]
                if len(atomk.conect) >= 1:
                    jx=atomk.conect[0]
                    bndlst.append(jx); ic=0; break
            if ic < 0: htype='non'
        if nh > 0 and htype == 'non':
            #mess='Program error(FindHtypeCon): No H added to '+atmnam+'.'
            #self.Message(mess,True) #,0,'red')
            pass
            #self.ConsoleMessage(mess)
        #
        return nh,htype,bndlst,rhx

    def GetCCOfWaterHydrogen(self,cow):
        #chw=[]
        h1=[0.585892,0.75669,0.0]; h2=[0.585892,-0.75669,0.0] # r(oh)=0.957 angstrom and hoh angle=104.5 degrees
        cnt=[0.0,0.0,0.0]
        nh=2; hnam=[' HW ',' HW ']
        x=numpy.random.random()-0.5
        y=numpy.random.random()-0.5
        z=numpy.random.random()-0.5
        v=[x,y,z]
        t=numpy.random.random()*numpy.pi
        u=lib.RotMatAxis(v,t)
        c=[]; c.append(h1[:]); c.append(h2[:])
        chw=lib.RotMol(u,cnt,c)
        for j in range(2):
            chw[j][0] += cow[0]; chw[j][1] += cow[1]; chw[j][2] += cow[2]

        return chw

    def FindCovalentBondedAtom(self,elmlst,coordlst):
        # return covalen bonded atom pairs i,j and distance r in cbndatm list[i,j,r]
        # elm:{' H','NA',...], coord:[[x1,y1,z1],[x2,y2,z2],...]
        nat=len(coordlst); bndlst=[]
        try: # fortran code(distance is dummy)
            #print 'running frotan code.'
            cc=[]; rad=[]
            for i in range(nat):
                cc.append(coordlst[i])
                rad.append(const.ElmCov[elmlst])
            margin=1.1025 # scale**2=(1.05)**2
            ndat,iatm,jatm=fortlib.find_contact_atoms1(cc,rad,margin)
            for i in range(ndat): #len(iatm)):
                tmp=[]; tmp.append(iatm[i]); tmp.append(jatm[i])
                tmp.append(0.0)
                bndlst.append(tmp)
        except: # python code
            for i in range(nat):
                vi=coordlst[i]
                cri=const.ElmCov[elmlst[i]]
                for j in range(i+1,nat):
                    #xj=coord[j][0]; yj=coord[j][1]; zj=coord[j][2]
                    vj=coordlst[j]
                    crj=const.ElmCov[elmlst[j]]
                    #rij=numpy.sqrt((xi-xj)**2+(yi-yj)**2+(zi-zj)**2)
                    rij=lib.Distance(vi,vj)
                    crij=cri+crj
                    if rij < crij*1.05:
                        tmp=[]
                        tmp.append(i); tmp.append(j); tmp.append(rij)
                        bndlst.append(tmp)
        return bndlst

    def AddBond(self,a,b,multi=1):
        # make bond between a and b atoms (mol data is assumed in original order)
        # multi: =1 single bond, =2 double bond, =3 triple bond, =4 aromatic bond
        bndlst=self.atm[a].conect
        ib=self.FindItemNmb(bndlst,b)
        if ib < 0:
            self.atm[a].conect.append(b)
            self.atm[a].bndmulti.append(multi)
        bndlst=self.atm[b].conect
        ia=self.FindItemNmb(bndlst,a)
        if ia < 0:
            self.atm[b].conect.append(a)
            self.atm[b].bndmulti.append(multi)

    def DeleteAllTers(self):
        nter=0; lstdel=[]
        for i in range(len(self.atm)):
            if self.atm[i].elm == 'XX':
                nter += 1; lstdel.append(i)

        if nter > 0:
            self.DelAtoms(lstdel)
        #
        """
        if nter > 0:
            mess=str(nter)+" TERs are deleted."
            self.Message(mess) #,0,"black")
            self.model.DrawMol(True)
        else:
            mess=str(nter)+" no TER were found."
            self.Message(mess) #,0,"black")
        """

    def DelAtoms(self,lst):
        if len(lst) <= 0:
            self.Message("No selected atoms to delete.") #,0,"")
            return
        deldic={}; k=0

        # delete atom
        lst.reverse()
        for i in lst: del self.atm[i]
        natm=len(self.atm)
        if natm <= 0: return

        atmseqlst=[]
        for atom in self.atm: atmseqlst.append(atom.seqnmb)
        for i in range(len(self.atm)):
            atom=self.atm[i]
            self.atm[i].seqnmb=i
            bnd=[]; bml=[]
            for j in range(len(atom.conect)):
                jj=atom.conect[j]
                try: jm=atom.bndmulti[j]
                except: jm = 1
                try:
                    idx=atmseqlst.index(jj)
                    if not idx in bnd:
                        bnd.append(idx)
                        #    idxjm=atmseqlst.index(jm)
                        bml.append(jm)
                except: pass
            atom.conect=bnd
            atom.bndmulti=bml
            if atom.frgbaa >= 0 and not atom.frgbaa in atmseqlst: atom.frgbaa=-1

    def DelHydrogen(self,lst):
        # delet hydrogens
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        lstdel=[]
        for i in lst:
            if self.atm[i].elm == ' H': lstdel.append(self.atm[i].seqnmb)
        if len(lstdel) > 0:
            self.DelAtoms(lstdel)
            # bellow are old codes which are very slow! (05 Oct 2013 (kk)
            #nd=0
            #for i in lstdel:
            #    ia=i-nd
            #    self.DelAtom(ia)
            #    nd += 1

    def DelWater(self,lst):
        # delete waters
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        lstdel=[]
        for i in lst:
            atom=self.atm[i]
            resnam=atom.resnam
            wat=(resnam == 'HOH' or resnam == 'WAT' or resnam == 'DOD')
            if wat: lstdel.append(atom.seqnmb)
        if len(lstdel) > 0:
            self.DelAtoms(lstdel)

    def DelNonBonded(self,lst):
        # delete non-bonded atoms
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        natm=len(lst); lstdel=[]
        if natm > 0:
            for i in lst:
                if len(self.atm[i].conect) < 1: lstdel.append(i)
        if len(lstdel) > 0:
            self.DelAtoms(lstdel)
        #nd=0
        #for i in lstdel:
        #    ia=i-nd
        #    self.DelAtom(ia)
        #    nd += 1

    def DelBond(self,a,b):
        # delete bond between a and b atoms
        #lst=self.atm[a].conect
        #ib=self.FindItemNmb(lst,b)
        #if ib >= 0:
            #del self.atm[a].conect[ib]
            #del self.atm[a].bndmulti[ib]
        self.atm[a].conect.remove(b)
        try: self.atm[a].bndmulti.remove(b)
        except: pass
        #lst=self.atm[b].conect
        #ia=self.FindItemNmb(lst,a)
        #if ia >= 0:
            #del self.atm[b].conect[ia]
            #del self.atm[a].bndmulti[ia]
        self.atm[b].conect.remove(a)
        try: self.atm[b].bndmulti.remove(a)
        except: pass

    def DelAllKindBonds(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        if len(lst) > 0:
            for i in lst:
                self.atm[i].conect   = []
                self.atm[i].bndmulti = []

    def DelExtraBond(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            self.atm[i].extraconect=[]
            self.atm[i].extrabnd=[]

    def DelVdwBond(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            self.atm[i].extraconect=[]
            self.atm[i].extrabnd=[]

    def DelHydrogenBond(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            self.atm[i].extraconect=[]
            self.atm[i].extrabnd=[]

    def MakeVdwBond(self,lst,pos13,pos14,pos15):
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0:
            selall = True
        else:
            selall = False
        sellst = list(range(len(self.atm)))
        nvdw=0
        self.DelExtraBond(sellst)
        atmdic={}; cc=[]; rad=[]; margin=1.2*1.2 # 1.0 # scaling
        #

        k=-1
        for i in range(len(self.atm)):
            atom=self.atm[i]
            k += 1
            atmdic[k]=i
            cc.append(atom.cc)
            rad.append(const.VdwRad[atom.elm])

        try:
            npair,iatm,jatm=fortlib.find_contact_atoms1(cc,rad,margin)
            print('fortran codes are used\n')
        except:

        #test = True
        #if test:
            npair = 0; iatm = []; jatm = []
            for i in range(1,len(self.atm)): #sellst)):
                #ia = lst[i]
                ia = i
                ci = self.atm[ia].cc #cc[i]
                radi = const.VdwRad[self.atm[ia].elm]
                for j in range(i): #len(self.atm)):
                    ja = j #lst[j]
                    if ja in self.atm[ia].conect: continue
                    cj = self.atm[ja].cc #cc[j]
                    radj = const.VdwRad[self.atm[ja].elm]
                    r2 = (ci[0]-cj[0])**2 + (ci[1]-cj[1])**2 +(ci[2]-cj[2])**2
                    #if r2 > 4.0 and r2 < margin*(radi+radj)**2:
                    if r2 < margin*(radi+radj)**2:
                        npair += 1
                        iatm.append(i)
                        jatm.append(j)
            print('python codes are used\n')
        #
        for i in range(npair):
            #iia=iatm[i]; jja=jatm[i]
            #ia=atmdic[iia]; ja=atmdic[jja]
            ia=iatm[i]; ja=jatm[i]
            if not self.atm[ia].show: continue
            if not self.atm[ja].show: continue
            if ja in self.atm[ia].conect: continue
            elmi=self.atm[ia].elm
            chai=self.atm[ia].chainnam
            nami=self.atm[ia].resnam
            nmbi=self.atm[ia].resnmb
            elmj=self.atm[ja].elm
            chaj=self.atm[ja].chainnam
            namj=self.atm[ja].resnam
            nmbj=self.atm[ja].resnmb
            if chai == chaj and nami == namj and nmbi == nmbj:
                continue
            # check if ia and ja are 1-3 or 1-4 position
            if self.AreThey13Position(ia,ja): continue
            if self.AreThey14Position(ia,ja): continue
            #if self.AreThey15Position(ia,ja): continue
            if not selall:
                if ia in lst or ja in lst:
                    self.atm[ia].extraconect.append(ja)
                    self.atm[ja].extraconect.append(ia)
                    self.atm[ia].extrabnd.append(2)
                    self.atm[ja].extrabnd.append(2)
                    nvdw += 1
            else:
                self.atm[ia].extraconect.append(ja)
                self.atm[ja].extraconect.append(ia)
                self.atm[ia].extrabnd.append(2)
                self.atm[ja].extrabnd.append(2)
                nvdw += 1

        return nvdw

    def AreThey13Position(self,ia,ja):
        pos13=False
        for i in self.atm[ia].conect:
            for j in self.atm[i].conect:
                if j == ja:
                    pos13=True; break
        return pos13

    def AreThey14Position(self,ia,ja):
        pos14=False
        for i in self.atm[ia].conect:
            for j in self.atm[i].conect:
                for k in self.atm[j].conect:
                    if k == ja:
                        pos14=True; break
        return pos14

    def AreThey15Position(self,ia,ja):
        pos15=False
        for i in self.atm[ia].conect:
            for j in self.atm[i].conect:
                for k in self.atm[j].conect:
                    for l in self.atm[k].conect:
                        if l == ja:
                            pos15=True; break
        return pos15

    def MakeHydrogenBond(self,lst):
        """ Make hydrogen bonds. See the parameters HBndElm,HBndLen,
            and HBndAng in the const module.

        :param lst lst: list of selected atoms
        :return: nbnd(int) - the number of hydrogen bonds
                 bnddic(dic) - {#:[ia,ja,r,a],...] , ia and ja are seq.# of
                            atoms, r length in ANGS, and a angle in DEGS
        note: this routine does not wrork beyond 100,000 atoms
        """
        def HBondLenMinMax(elm1,elm2):
            elmp = elm1 + elm2
            if elmp not in const.HBndLen: elmp = elm2 + elm1
            rhmin = 0; rhmax = 0
            try:
                rhbmin = const.HBndLen[elmp][1]
                rhbmax = const.HBndLen[elmp][2]
            except: pass
            return rhbmin,rhbmax

        if len(self.atm) > 100000:
            mess='Sorry, max number of atoms is set 100000 in'
            mess=mess+' molec.MakeHydrogen bond.'
            self.ConsoleMessage(mess)
            return
        #
        todeg = const.PysCon['rd2dg']
        natm = len(self.atm)
        if len(lst) <= 0: lst = list(range(len(self.atm)))
        # clear extra bonds
        self.DelExtraBond(lst)
        #
        atmlst  = []
        cc      = []
        hbndelm = const.HbndElm  # [' O',' N',' S']
        for i in range(natm):
            atom=self.atm[i]
            if atom.elm in hbndelm:
                atmlst.append(i)
                cc.append(atom.cc)
        rmin=2.2; rmax=3.6
        rmin2=rmin**2; rmax2=rmax**2

        try:
            iopt = 0 # return r not r*r(iopt!=0)
            npair,iatm,jatm,rijlst=fortlib.find_contact_atoms2(cc,rmin,rmax,iopt)
            print('fortran codes are used\n')
        except:
            npair = 0; iatm = []; jatm = []; rijlst = []
            for i in range(1,len(atmlst)):
                ia = atmlst[i]
                ci = cc[i]
                for j in range(i):
                    ja = atmlst[j]
                    if ja in self.atm[ia].conect: continue
                    cj = cc[j]
                    r2 = (ci[0]-cj[0])**2 + (ci[1]-cj[1])**2 +(ci[2]-cj[2])**2
                    if r2 > rmin2 and r2 <= rmax2:
                        npair += 1
                        iatm.append(i)
                        jatm.append(j)
                        rijlst.append(numpy.sqrt(r2))
            print('python codes are used\n')

        itmp=[]; jtmp=[]
        bnddic={}
        hangmin=numpy.pi*(const.HBndAng[0]/180.0) # 180.0 degrees
        #
        count=-1
        for i in range(npair): #len(iatm)):
            ii=iatm[i] #-1
            iii=atmlst[ii]
            # if iii not in lst: contine
            hi=[]; atomi=self.atm[iii]
            for ih in atomi.conect:
                if self.atm[ih].elm == ' H': hi.append(ih)
            nhi=len(hi)
            jj=jatm[i]
            jjj=atmlst[jj]

            if iii not in lst and jjj not in lst: continue

            hj=[]; atomj=self.atm[jjj]
            #
            elmi = atomi.elm
            elmj = atomj.elm
            rhbmin,rhbmax = HBondLenMinMax(elmi,elmj)
            if rhbmax == 0: continue
            if rijlst[i] < rhbmin and rijlst[i] > rhbmax: continue
            for jh in atomj.conect:
                if self.atm[jh].elm == ' H': hj.append(jh)
            nhj=len(hj)
            if nhi <= 0 and nhj <= 0: continue # not h-bond
            for j in self.atm[iii].conect:
                for k in self.atm[j].conect:
                    if k == jjj: continue
            # check angle
            cci=self.atm[iii].cc[:]; ccj=self.atm[jjj].cc[:]
            rmin=1000.0
            im=-1; rmini=rmin
            for ih in hi:
                cch=self.atm[ih].cc[:]
                rij=lib.Distance(cch,ccj)
                if rij < rmini:
                    im=ih; rmini=rij
            jm=-1; rminj=rmin
            for jh in hj:
                cch=self.atm[jh].cc[:]
                rij=lib.Distance(cch,cci)
                if rij < rminj:
                    jm=jh; rminj=rij
            if rmini < rminj:
                cch=self.atm[im].cc[:]
                r1=numpy.subtract(cci,cch); r2=numpy.subtract(ccj,cch)
                ang=lib.AngleT(r1,r2)
                if ang < hangmin: continue
            else:
                cch=self.atm[jm].cc[:]
                r1=numpy.subtract(cci,cch); r2=numpy.subtract(ccj,cch)
                ang=lib.AngleT(r1,r2)
                if ang < hangmin: continue
            count += 1
            itmp.append(iii); jtmp.append(jjj)
            if rmini < rminj:
                bnddic[count]=[iii,jjj,rijlst[i],ang*todeg]
            else:
                bnddic[count]=[jjj,iii,rijlst[i],ang*todeg]
        nbnd=len(bnddic)
        for i in range(nbnd):
            ii=bnddic[i][0]; jj=bnddic[i][1]
            self.atm[ii].extraconect.append(jj)
            self.atm[ii].extrabnd.append(1) # hydrogenbond code
            self.atm[jj].extraconect.append(ii)
            self.atm[jj].extrabnd.append(1) # hydrogen bond code
        return nbnd,bnddic

    def FindItemNmb(self,lst,b):
        # find data number of b in lst. return -1 if not found.
        found=-1
        for i in range(len(lst)):
            if lst[i] == b:
                found=i; break
        return found

    def CountElement(self):
        elmlst=[]; elmdic={}
        for atom in self.atm:
            elm=atom.elm
            if elm == '': continue
            if elm == 'XX': continue
            elmlst.append(elm)
        elmlst,chem=lib.ChemFormula(elmlst)
        return elmlst,chem

    def CountAtoms(self):
        nhev=0; nhyd=0; nter=0
        for atom in self.atm:
            if atom.elm == 'XX': nter += 1
            elif atom.elm == ' H': nhyd +=1
            else: nhev += 1
        return nhev+nhyd,nhev,nhyd,nter

    def CountIonCharge(self,lst):
        charge=0
        for i in lst: charge += self.atm[i].charge
        return charge

    def CountChargeOfAARes(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        self.AssignAAResAtmChg()
        #
        chg=0
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            if self.atm[i].frgchg is not None:
                chg += self.atm[i].frgchg
        return int(chg)

    def CountHydrogenOfAtom(self,a):
        # count number of hydrogen atoms attaced at atom a.
        nh=0
        for i in range(len(self.atm[a].conect)):
            ix=self.atm[a].conect[i]
            if self.atm[ix].elm == ' H':
                nh += 1
        return nh

    def CountWater(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        nw=0
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            atom=self.atm[i]
            if atom.resnam in const.WaterRes and atom.elm == ' O': nw += 1
        return nw

    def CountTer(self,lst):
        # lst(lst): target atom list. if [], all atoms are targetted.
        nt=0
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        for i in lst:
            atom=self.atm[i]
            if atom.elm == 'XX': nt += 1
        return nt

    def CountAAResAtoms(self):
        nres=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            if res in const.AmiRes3: nres += 1
        return nres

    def CountResH(self,resnam,resnmb):
        nh=0
        for atom in self.atm:
            res=atom.resnam; nmb=atom.resnmb
            if res == resnam and nmb == resnmb:
                elm=atom.elm
                if elm == ' H': nh += 1
        return nh

    def CountNonAARes(self,water):
        nres=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            if not water and (res == "WAT" or res == "HOH"): continue
            if res not in const.AmiRes3: nres += 1
        return nres

    def PrintAtomInPDBForm(self):
        print('PrintAtomInPDBForm: the sequence number is internal one.')
        for atom in self.atm:
            print((atom.MakePDBAtomText()))

    def MakeChainDic(self):
        chaindic={}; nchain=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            cha=atom.chainnam
            if cha in chaindic:
                chaindic[cha] += 1
            else:
                chaindic[cha]=1
        return chaindic

    def MakeElmDic(self):
        elmdic={}; nwat=0
        for atom in self.atm:
            res=atom.resnam
            elm=atom.elm
            if elm == 'XX': continue
            if res == 'HOH' or res == 'WAT':
                nwat += 1
            else:
                if elm in elmdic:
                    elmdic[elm] += 1
                else:
                    elmdic[elm]=1
        nwat /= 3
        return elmdic

    def MakeAAResDic(self):
        resdic={}; ini=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            nmb=atom.resnmb
            cha=atom.chainnam
            if res not in const.AmiRes3: continue
            if ini == 0:
                resdic[res]=1
                ini=1; prvnmb=nmb; prvres=res; prvcha=cha
            if res == prvres and nmb == prvnmb and cha == prvcha: continue
            if res in resdic:
                resdic[res] += 1
            else:
                resdic[res]=1
            prvres=res; prvnmb=nmb; prvcha=cha

        return resdic

    def MakeAAResDic1(self):
        resdic={}; ini=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            if res not in const.AmiRes3: continue
            resdat=atom.resnam+':'+str(atom.resnmb)+':'+atom.chainnam
            resdic[resdat]=True
        return resdic

    def ListResidues(self):
        """ Return list of residues in resdat names"""
        resdatlst=[]; donedic={}
        for atom in self.atm:
            resdat=lib.ResDat(atom)
            if resdat in donedic: continue
            resdatlst.append(resdat)
            donedic[resdat]=True
        return resdatlst

    def ListResidueAtoms(self,resdat):
        """ Return list of resdiue atom objects """
        atmobjlst=[]
        for i in range(len(self.atm)):
            atom=self.atm[i]
            res=lib.ResDat(atom)
            if res == resdat: atmobjlst.append(self.CopyIthAtom(i))
        return atmobjlst

    def ListAAResSeq(self,resdat=False):
        resdic={}; aaseqlst=[]
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            if res not in const.AmiRes3: continue
            if resdat: res=atom.resnam+':'+str(atom.resnmb)+':'+atom.chainnam
            if res in resdic: continue
            aaseqlst.append(res); resdic[res]=True
        return aaseqlst

    def MakeNonAAResDic(self):
        resdic={}; ini=0
        for atom in self.atm:
            elm=atom.elm
            if elm == 'XX': continue
            res=atom.resnam
            nmb=atom.resnmb
            cha=atom.chainnam
            if res in const.AmiRes3: continue
            if ini == 0:
                resdic[res]=1
                ini=1; prvnmb=nmb; prvres=res; prvcha=cha
            if res == prvres and nmb == prvnmb and cha == prvcha: continue
            if res in resdic:
                resdic[res] += 1
            else:
                resdic[res]=1
            prvres=res; prvnmb=nmb; prvcha=cha

        return resdic

    def MakeBondedAtomGroupList(self,condat):
        # make list of covalent bonded atom group.
        # condat: [[cc,conect,elm],..]
        grplst=[]; ngrp=-1
        for i in range(len(condat)):

            elm=condat[i][2]

            if elm == 'XX': continue

            ia=i
            iga=self.FindGrpNmb(ia,grplst)
            if iga < 0:
                ngrp += 1
                lst=[]; lst.append(ia)
                grplst.append(lst)
            for j in range(len(condat[i][1])):
                ###ib=moldat[i][1][j]
                ib=j
                iga=self.FindGrpNmb(ia,grplst)
                igb=self.FindGrpNmb(ib,grplst)
                if igb < 0: grplst[iga]=grplst[iga]+[ib]
                else:
                    if igb != iga:
                        grplst[iga]=grplst[iga]+grplst[igb]
                        #
                        del grplst[igb]; ngrp -= 1
        return grplst

    def CenterOfMass(self):
        cc=[]; mass=[]
        for atom in self.atm:
            if atom.elm == 'XX': continue
            cc.append(atom.cc); mass.append(const.ElmMas[atom.elm])
        com,eig,vec=lib.CenterOfMassAndPMI(mass,cc)

        return com,eig,vec

    def IsBAAAtom(self,ia):
        isbaa=False
        for i in self.bdadic:
            if self.bdadic[i][0] == ia:
                isbaa=True; break
        return isbaa

    def SetToBDADic(self,ia,ib):
        atoma=self.atm[ia]; atomb=self.atm[ib]
        atmanam=atoma.atmnam; atmanmb=atoma.atmnmb
        resanam=atoma.resnam; resanmb=atoma.resnmb
        atmbnam=atomb.atmnam; atmbnmb=atomb.atmnmb
        resbnam=atomb.resnam; resbnmb=atomb.resnmb
        bda=[]; bda.append(ib)
        bda.append(atmanam); bda.append(atmanmb)
        bda.append(resanam); bda.append(resanmb)
        bda.append(atmbnam); bda.append(atmbnmb)
        bda.append(resbnam); bda.append(resbnmb)
        self.bdadic[ia]=bda

    def RenumberFragment(self,ini):
        """ not fully tested, 27Feb2014"""
        ifg=ini-1; frgdic={}
        for atom in self.atm:
            frgnam=atom.frgnam
            if atom.frgnam == '': continue
            if frgnam not in frgdic:
                ifg += 1; frgdic[frgnam]=ifg
        for atom in self.atm:
            if atom.frgnam in frgdic:
                name=frgnam[0:3]+('%03d' % frgdic[frgnam])
                atom.frgnam=frgdic[frgnam]

    def SetFragmentCharge(self,chglst):


        if len(chglst) < 0: return
        if len(self.atm) <= 0: return
        ic=-1
        for atom in self.atm:
            if atom.elm == 'XX': continue
            ic += 1; atom.frgchg=chglst[ic]
            #if abs(atom.frgchg) > 0.01:
            #    print 'ic,frgchg',ic,atom.frgchg
        return
        """
        chgdic={}; done={}
        for i in xrange(len(chglst)):
            #if chgdic.has_key(i): continue
            chgdic[i+1]=chglst[i]
        print 'chgdic',chgdic
        for atom in self.atm:
            atom.frgchg=0.0
            #print 'atom.frgnam',atom.frgnam
            frgnam=atom.frgnam
            #if frgnam == '': continue
            frgnmb=int(atom.frgnam[3:])
            if chgdic.has_key(frgnmb) and not done.has_key(frgnmb):
                atom.frgchg=chgdic[frgnmb]; done[frgnmb]=True
                print 'frgnmb,chgdic',frgnmb,chgdic[frgnmb]
        """

    def SetActives(self,activelst):
        if len(activelst) <= 0: return
        for i in activelst: self.atm[i].active=True

    def FindAtmSeqNmb(self,nam,nmb):
        iseq=-1
        for i in range(len(self.atm)):
            atmnam=self.atm[i].atmnam; atmnmb=self.atm[i].atmnmb
            if atmnam == nam and atmnmb == nmb:
                iseq=i; break
        return iseq

    def FindAtmSeqNmb1(self,nam):
        iseq=-1
        for i in range(len(self.atm)):
            atmnam=self.atm[i].atmnam
            if atmnam == nam:
                iseq=self.atm[i].seqnmb; break
        return iseq

    def IsConnected(self,ia,ib):
        ret=False
        for i in range(len(self.atm[ia].conect)):
            if self.atm[ia].conect[i] == ib:
                ret=True; break
        return ret

    def SetFragmentUseFMOIndat(self,frgnam,indat,bdabaa):
        # set fragment data according to GAMESS-FMO input data
        # frgnam: [frgnam1,frgnam2,...]
        # indat: [[i,j,k..],[l,m,n,...],,,] # indat in FMOinput data
        # bdabaa: [[atom seq number of bda+1, atom seq number of baa +1],[,,,],...]
        if len(self.atm) <= 0:
            mess='No molecule data.'
            print(mess)
            #self.Message(mess,1,'black')
            return

        bdadic={}
        for i,j in bdabaa:
            bdadic[i-1]=j-1

        for i in range(len(indat)):
            for j in indat[i]:
                jj=j-1
                self.atm[jj].frgnam=frgnam[i]
                if jj in bdadic:
                    self.atm[jj].frgbaa=bdadic[jj]

    def FindSSBond(self,idx):
        # 2013.2 KK
        ssblst=[]
        for i in range(len(self.atm)):
            res=self.atm[i].resnam; atm=self.atm[i].atmnam
            if (res == 'CYS' or res == 'CYX') and atm == ' SG ':
                ia=self.atm[i].seqnmb
                for j in range(len(self.atm[i].conect)):
                    ib=self.atm[i].conect[j]
                    resb=self.atm[ib].resnam
                    if (resb == 'CYS' or resb == 'CYX') and self.atm[ib].atmnam == ' SG ':
                        tmp=[]; tmp.append(idx[ia]); tmp.append(idx[ib])
                        ssblst.append(tmp)
        return ssblst

    def FindMinMaxXYZ(self):
        # find mix/max coordinates
        x=[]; y=[]; z=[]
        for atom in self.atm:
            x.append(atom.cc[0]); y.append(atom.cc[1]); z.append(atom.cc[2])
        xmin=min(x); xmax=max(x); ymin=min(y); ymax=max(y); zmin=min(z); zmax=max(z)

        return xmin,xmax,ymin,ymax,zmin,zmax

    def ChangeToCenterOfMassCC(self):
        cc=[]; mass=[]
        for atom in self.atm:
            cc.append(atom.cc); mass.append(const.ElmMas[atom.elm])
        cc=lib.CenterOfMassCC(mass,cc)
        for i in range(len(self.atm)): self.atm[i].cc=cc[i]

    def IsCOOTerm(self,resdat):
        ans=False; resatmlst=[]
        for atom in self.atm:
            res=lib.PackResDat(atom.resnam,atom.resnmb,atom.chainnam)
            if res != resdat: continue
            resatmlst.append(atom.atmnam)
        if len(resatmlst) > 0:
            for atmnam in resatmlst:
                if atmnam == ' OXT':
                    ans=True; break
        return ans

    def IsNH3Term(self,resdat):
        ans=False; resatmlst=[]
        for atom in self.atm:
            res=lib.PackResDat(atom.resnam,atom.resnmb,atom.chainnam)
            if res != resdat: continue
            resatmlst.append(atom.atmnam)
        if len(resatmlst) > 0:
            for atmnam in resatmlst:
                if atmnam == ' N ' and len(self.atm[i].conect) >= 4:
                    ans=True; break
        return ans

    def IsCaAtCterminal(self,ia):
        ret=False
        count=0
        for i in range(len(self.atm[ia].conect)):
            ib=self.atm[ia].conect[i]
            atm=self.atm[ib].atmnam
            elm=self.atm[ib].elm
            if elm == ' O': count += 1
            if atm == ' OXT': ret=True
        if count == 2: ret=True
        return ret

    def MakeFullAtomName(self,iatm,chainnam,resnam,resnmb):
        # fullatonmame: chain:resnam:resnmb:atmnam
        name=""
        atom=self.atm[iatm]
        if chainnam: name=name+atom.chainnam+":"
        if resnam: name=name+atom.resnam+":"
        if resnmb: name=name+str(atom.resnmb)+":"
        name=name+atom.atmnam
        return name

    def IsBackBoneAtom(self,ia):
        ret=False
        atom=self.atm[ia]; atmnam=atom.atmnam
        if atom.resnam not in const.AmiRes3: return ret
        if atmnam == ' CA ' or atmnam == ' N  ' or atmnam == ' C  ': ret=True
        return ret

    def DelBDABond(self,ia,ib):
        atoma=self.atm[ia]
        for i in range(len(atoma.frgcondat[1])):
            if atoma.frgcondat[1][i] == ib:
                del atoma.frgcondat[1][i]
                break
        atomb=self.atm[ib]
        for i in range(len(atomb.frgcondat[1])):
            if atomb.frgcondat[1][i] == ia:
                del atomb.frgcondat[1][i]
                break

    def ClearBDABAA(self,lst):
        # clear bdas
        # lst(lst): target atom list. if [], all atoms are targetted.
        if len(lst) <= 0: lst=list(range(len(self.atm)))

        if len(lst) <= 0: return
        for i in lst:
            atom=self.atm[i]
            if atom.frgbaa >= 0:
                ia=atom.seqnmb; ib=atom.frgbaa
                self.RemoveBDA(ia,ib)

    def ClearFormalCharge(self,lst):
        # clear charges for counting fragment charge
        for i in lst:
            atom=self.atm[i]; atom.frgchg=0.0; atom.charge=0

    def CreateBDA(self,ia,ib):
        self.SetToBDADic(ia,ib)
        self.DelBDABond(ia,ib)
        self.atm[ia].frgbaa=ib

    def AddBDABond(self,ia,ib):
        self.atm[ia].frgcondat[1].append(ib)
        self.atm[ib].frgcondat[1].append(ia)

    def CheckBDADup(self,ia,ib):
        dup=-1
        bdalst=list(self.bdadic.keys())
        if len(self.bdalst) < 0: return dup
        for i in range(len(self.bdalst)):
            ja=self.bdalst[i][0]; jb=self.bdalst[i][1]
            if ia == ja and ib == jb: dup=i
            if ia == jb and ib == ja: dup=i
        return dup

    def ListFragmentCharge(self):
        # return total charge and fragment charge list, totalchg,frgchglst
        frgchglst=[]
        frgnamdic=self.DictFragmentName(0.0)
        for atom in self.atm:
            frgnam=atom.frgnam
            frgnamdic[frgnam] += atom.frgchg
        done={}; totalchg=0.0
        for atom in self.atm:
            frgnam=atom.frgnam
            if frgnam in done: continue
            done[frgnam]=True
            chg=round(frgnamdic[frgnam],0)
            frgchglst.append([frgnam,chg])
            totalchg += chg

        return totalchg,frgchglst


        # frgchg:[0,1,2,...]
        frgchg=[]; frgdic={}
        #
        prvnam='dummy'; nfrg=-1
        for atom in self.atm:
            if atom.elm == 'XX': continue
            i=atom.seqnmb
            frg=atom.frgnam
            if frg == prvnam: continue
            if frg in frgdic: continue
            else:
                nfrg += 1; frgdic[frg]=nfrg; prvnam=frg
                frgchg.append(0)
        for atom in self.atm:
            if atom.elm == 'XX': continue
            ifrg=frgdic[atom.frgnam]
            frgchg[ifrg] += atom.frgchg
        for i in range(len(frgchg)): frgchg[i]=int(frgchg[i])

        return frgchg

    def FindMaxResNmb(self):
        maxresnmb=0
        for atom in self.atm:
            if atom.resnmb > maxresnmb: maxresnmb=atom.resnmb
        return maxresnmb

    def FindMaxAtmNmb(self):
        maxatmnmb=0
        for atom in self.atm:
            if atom.atmnmb > maxatmnmb: maxatmnmb=atom.atmnmb
        return maxatmnmb

    def ChangeAtomName(self,a,atmnam,atmnmb):
        self.atm[a].atmnam=atmnam
        self.atm[a].atmnmb=atmnmb

    def RenumberAtmNmbAndConDat(self):
        old2newdic={}
        for i in range(len(self.atm)):
            old2newdic[self.atm[i].atmnmb]=i+1
            self.atm[i].atmnmb=i
        for i in range(len(self.atm)):
            dellst=[]
            for j in range(len(self.atm[i].conect)):
                jj=self.atm[i].conect[j]
                try: self.atm[i].conect[j]=old2newdic[jj]
                except: dellst.append(jj)
            if len(dellst) > 0:
                for jj in dellst: self.atm[i].conect.remove(jj)
        const.CONSOLEMESSAGE('old2newdic='+str(old2newdic))

    def RenumberConDat(self):
        # renumber pdb CON data in mol
        # i.e. subtract by one to atom number if pdb2bld=True, and back to original if False.
        for atom in self.atm:
            atom.seqnmb += 1
            for j in range(len(atom.conect)):
                atom.conect[j] += 1

    def SetBondMultiplicity(self,atom1,atom2,bndmulti):
        # change bond kind
        print('change bond kind')

    def SetExtraBond(self,bndlst,on):
        # bndlst: extra bond data [[i,j],...]
        # on(Treu/False): True:set, False:reset
        if on:
            if len(bndlst) <= 0: return
            for i,j in bndlst:
                self.atm[i].extrabnd.append(j)
                self.atm[j].extrabnd.append(i)
        else:
            if len(bndlst) > 0:
                for i,j in bndlst:
                    self.atm[i].extrabnd=[]
                    self.atm[j].extrabnd=[]
            else:
                for atom in self.atm: atom.extrabnd=[]

    def RenumberAtmNmb(self):
        i=0
        for atom in self.atm:
            i += 1; atom.atmnmb=i

    def CopyMolecule(self,parent=None):
        if parent is None: parent = self.parent
        cpymol=Molecule(parent)
        atm=self.CopyAtom()
        cpymol.atm=atm
        cpymol.name=self.name
        return cpymol

    def CopyIthAtom(self,i):
        atm=Atom(self)
        atm.seqnmb=i
        atm.cc=self.atm[i].cc[:]
        atm.elm=self.atm[i].elm
        atm.atmnam=self.atm[i].atmnam
        atm.resnam=self.atm[i].resnam
        atm.resnmb=self.atm[i].resnmb
        atm.chainnam=self.atm[i].chainnam
        atm.charge=self.atm[i].charge
        atm.conect=self.atm[i].conect[:]
        atm.color=self.atm[i].color[:]
        atm.show=self.atm[i].show
        atm.select=self.atm[i].select
        atm.model=self.atm[i].model
        atm.atmrad=self.atm[i].atmrad
        atm.vdwrad=self.atm[i].vdwrad
        atm.vdwradsc=self.atm[i].vdwradsc
        atm.thick=self.atm[i].thick
        atm.thicksc=self.atm[i].thicksc
        atm.active=self.atm[i].active
        # group data
        atm.group=self.atm[i].group
        atm.grpnam=self.atm[i].grpnam # group name
        atm.grpchg=self.atm[i].grpchg # gropu charg
        atm.envflag=self.atm[i].envflag # environment (special group) flag
        atm.parnam=self.atm[i].parnam # name of parent molecule
        #
        atm.frgnmb=self.atm[i].frgnmb
        atm.frgnam=self.atm[i].frgnam
        atm.frgbaa=self.atm[i].frgbaa
        atm.frgchg=self.atm[i].frgchg
        atm.layer=self.atm[i].layer
        #
        #if self.atm[i].bndmulti is not None:
        atm.bndmulti=self.atm[i].bndmulti[:]
        #else: atm.bndmulti=self.atm[i].bndmulti
        #if self.atm[i].extraconect is not None:
        atm.extraconect=self.atm[i].extraconect[:]
        #else: atm.extraconect=self.atm[i].extraconect
        #if self.atm[i].extrabnd is not None:
        atm.extrabnd=self.atm[i].extrabnd[:]
        #else: atm.extrabnd=self.atm[i].extrabnd
        #if self.atm[i].color is not None:
        atm.color=self.atm[i].color[:]
        #else: atm.color=self.atm[i].color
        #if self.atm[i].frgcondat is not None:
        atm.frgcondat=self.atm[i].frgcondat[:]
        #else: atm.frgcondat=self.atm[i].frgcondat
        return atm

    def CopyAtom(self):
        atm=[]
        #for i in range(len(self.atm)): atm.append(Atom(self))
        #for atom in self.atm: atm.append(atom)
        for i in range(len(self.atm)):
            atom=self.CopyIthAtom(i)
            atm.append(atom)
        return atm

    def Write(self,form,filename=None,title=None,
                 sdfcomm=None,sdfdic=None,xyzlabel=True):
        """ Write strcuture data on file

        :param str form: output format, 'sdf','xyz','pdb','zmt', 'tin'
                                        or 'xyzstd'
        :param str filename: True for writing on file, False for output string
        :param str sdfcomm:  the 2nd and 3rd line data in sdf
        :param dic sdfdic:  dictionary of sdf data
        :param bool xyzlabel: add label to coordinates data in xyz format
        :return: gstring(str) - formatted structure data string
        """
        gstring = ''
        nl = '\n'
        formlst = ['sdf','mol','xyz','pdb','zmt', 'tin','xyzstd']
        #
        if title is None:   name = self.name
        else:               name = title
        #
        if form == 'sdf' or form == 'mol':
            gstring = lib.SDFText(self,name,sdfcomm=sdfcomm,sdfdic=sdfdic)
        elif form == 'xyz':
            gstring  = name + nl
            gstring += nl
            gstring += lib.XYZText(self,label=xyzlabel)
        elif form == 'pdb' or form == 'ent':
            comment  = 'REMARK Created by fu at ' + lib.DateTimeText() + nl
            comment += 'REMARK parent file: ' + self.inpfile + nl
            gstring += lib.PDBText(self,name=name,comment=comment)
        elif form == 'zmt':
            pass
        elif form == 'tin':
            pass
        elif form == 'xyzstd':
            gstring  = str(len(self.atm)) + nl
            gstring += name + nl
            gstring += lib.XYZText(self,label=xyzlabel)
        else:
            meth = 'Molecule.WriteMol: '
            mess += 'Wrong format =' + form +'.\n'
            mess += 'supported formats are ' + str(formlst)
            lib.MessageBoxOK(mess,meth)
            return
        #
        if filename is None: return gstring
        else:
            f = open(filename,'w')
            f.write(gstring)
            f.close()

    def WritePDBMol(self,filename,parnam,parfilnam,con):
        #rwfile.WritePDBMolFile(filename,parnam,parfilnam,self.atm,con)
        name = self.name
        pdbstring = lib.PDBTextFromMol(self,name=name,comment=None,
                                       condat=True)
        if filename is None: return pdbstring

        f = open(filename,'w')
        f.write(pdbstring)
        f.close()

    def WriteSDFMol(self,filename,resnam='',title='',comment=''):
        #rwfile.WriteMolFile(filename,self,resnam=resnam,title=title,comment=comment)
        name = self.name
        sdfdic = self.SetSDFAndMOL2DataDic()
        sdfstring = lib.SDFTextFromMol(self,name=name,sdfcomm=None,
                                       sdfdic=sdfdic)
        if filename is None: return sdfstring
        #
        f = open(filename,'w')
        f.write(sdfstring)
        f.close()

    def WriteCIFMol(self,filename,title='',comment=''):
        name = self.name
        cifstring = lib.CIFTextFromMol(self,name=name,cifcomm=None)
        if filename is None: return cifstring
        #
        f = open(filename,'w')
        f.write(cifstring)
        f.close()

    def CountIsolatedResidures(self):
        grpdic = {}
        netx,G = lib.NetXGraphObject(self)
        con    = netx.connected_components(G)
        conlst = [x for x in con]
        for i in range(len(conlst)): grpdic[i] = list(conlst[i])
        for i in range(len(grpdic)): grpdic[i].sort()
        ngrp = len(grpdic)
        return ngrp

    def BoxVertexesString(self):
        labels = ['000','100','010','001','110','011','101','111']
        ff12 = '%12.6f'
        boxvertlst = [] #''
        pnts = len(self.boxpnts)
        for i in range(pnts):
            s = labels[i] + ', '
            for j in range(3):
                s += (ff12 % self.boxpnts[i][j]) +', '
            s = s[:-2] + '\n'
            boxvertlst.append(s.strip())
        return boxvertlst

    def CellParamString(self):
        todeg = 180.0/numpy.pi
        cellparam = self.crystalobj.cell_params[:]
        for i in range(3): cellparam[i+3] *= todeg
        cellparam = str(cellparam).strip()
        cellparam = cellparam[1:-1]
        return cellparam

    def SymEquPosString(self):
        symequpos = str(self.crystalobj.sym_equ_pos)
        if symequpos[0]  == '[': symequpos = symequpos[1:-1]
        return symequpos

    def SetSDFAndMOL2DataDic(self):
        datadic = None
        if self.crystalobj is not None:
            datadic = {}
            datadic['cif_file']                  = [self.crystalobj.inpfile]
            datadic['a,b,c,alpha,beta,gamma']    = [self.CellParamString()]
            datadic['symmetry_equiv_pos_as_xyz'] = [self.SymEquPosString()]
        if self.boxpnts is not None:
            if datadic is None: datadic = {}
            boxvertx = self.BoxVertexesString()
            nmol = self.CountIsolatedResidures()
            natm = len(self.atm)
            natm_in_unit = natm / nmol
            natm_itemname = 'natm_in_unit(average)'
            if (natm % nmol) == 0: natm_itemname = 'natm_in_unit'
            if len(boxvertx) > 0:
                datadic['box_vertexes']  = boxvertx
                datadic[natm_itemname]   = [str(natm_in_unit)]
                datadic['nmol_isolated'] = [str(nmol)]
        return datadic

    def WriteMOL2Mol(self,filename,resnam='',title='',comment=''):
        #rwfile.WriteMolFile(filename,self,resnam=resnam,title=title,comment=comment)
        name = self.name
        mol2dic = self.SetSDFAndMOL2DataDic()
        #
        mol2string = lib.MOL2TextFromMol(self,name=name,mol2dic=mol2dic)

        if filename is None: return mol2string

        f = open(filename,'w')
        f.write(mol2string)
        f.close()


    def WriteZMTMol(self,filename,title,zelm,zpnt,zprm,extdat=[],active={}):
        #self.messout.ConsoleMessage('Extered in mol.Write')
        rwfile.WriteZMTFile(filename,title,zelm,zpnt,zprm,extdat=extdat,active=active)
        #self.messout.ConsoleMessage('Exit from mol.Write')

    def WriteTinkerXYZ(self,xyzfile):
        #   642 crambin
        #     1  N3    17.047000   14.099000    3.625000   124     2     5     6     7
        #
        rwfile.WriteTinkerXYZFile(xyzfile,self.atm)

    def WriteXYZMol(self,filename,bond=None,resfrg=None,name=None,
                    label=False):
        rwfile.WriteXYZMolFile(filename,self.atm,bond=None,resfrg=None,
                               name=name,label=label)
    @staticmethod
    def MakeMolName(filename):
        # 2013.2 KK
        #pick up base name as molnam
        root,ext=os.path.splitext(filename)
        basenam=os.path.basename(filename)
        molnam=basenam.replace(ext,"")
        return molnam

    @staticmethod
    def MakeMolNameWithExt(filename):
        # 2013.2 KK
        #pick up base name as molnam
        root,ext=os.path.splitext(filename)
        molnam=os.path.basename(filename)
        return molnam

    @staticmethod
    def GetOrgSeqNmb(ith,idx):
        # 2013.2 KK
        seq=-1
        for i in range(len(idx)):
            if idx[i] == ith:
                seq=i; break
        return seq

    @staticmethod
    def BondAtmGrp(condat,ssblst):
    # 2013.2 KK
    # make list of bonded atom group.
        # grpdic[i]=group number (i=atom number)
        grplst=[]; ngrp=-1
        for i in range(len(condat)):
            ia=condat[i][0]
            if ia < 0: continue
            iga=Molecule.FindNmbInGrpLst(ia,grplst)
            if iga < 0:
                ngrp += 1
                lst=[]; lst.append(ia)
                grplst.append(lst)
            for j in range(1,len(condat[i])):
                ib=condat[i][j]
                iga=Molecule.FindNmbInGrpLst(ia,grplst)
                igb=Molecule.FindNmbInGrpLst(ib,grplst)
                if igb < 0:
                    grplst[iga]=grplst[iga]+[ib]
                else:
                    if igb != iga:
                        grplst[iga]=grplst[iga]+grplst[igb]
                        del grplst[igb]; ngrp -= 1
        # merge S-S bonded groups
        if len(ssblst) > 0:
            for ia,ib in ssblst:
                iga=Molecule.FindNmbInGrpLst(ia,grplst)
                igb=Molecule.FindNmbInGrpLst(ib,grplst)
                if iga != igb:
                    grplst[iga]=grplst[iga]+grplst[igb]
                    del grplst[igb]; ngrp -= 1

        grplst.sort(key=lambda x:x[0])
        for i in range(len(grplst)): grplst[i].sort()
        return grplst

    @staticmethod
    def FindNmbInGrpLst(ia,grplst):
        # 2013.2 KK
        ig=-1
        if len(grplst) <= 0: return ig
        for i in range(len(grplst)):
            for j in grplst[i]:
                if j == ia:
                    ig=i; break
        return ig

    def SetFMOAtoms(self,xyzmol,frgnam,indat,bdalst):
        self.atm=[]
        # create mol data
        for i in range(len(xyzmol)):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            cc=[]
            cc.append(xyzmol[i][1])
            cc.append(xyzmol[i][2])
            cc.append(xyzmol[i][3])
            atm.cc=cc # coord list, [x,y,z]
            elm=xyzmol[i][0]
            if len(elm) == 1: elm=' '+elm
            atm.elm=elm
            atm.atmnam=elm+'  '
            atm.SetAtomParams(atm.elm)
            self.atm.append(atm)
        # fragment
        if len(frgnam) > 0:
            for i in range(len(indat)):
                for j in indat[i]:
                    jj=j-1; self.atm[jj].frgnam=frgnam[i]
                    self.atm[jj].frgnmb=i
        # indat
        if len(indat) > 0:
            pass
        # bda-baa
        if len(bdalst) > 0:
            for i,j in bdalst:
                ii=i-1; jj=j-1
                self.atm[ii].frgbaa=jj

    def SetXYZAtoms(self,xyzmol,bond,resfrg):
        self.atm=[]
        # create mol data
        for i in range(len(xyzmol)):
            # Atom class instance
            atm=Atom(self)
            # set attributes
            atm.seqnmb=i # sequence number of atoms begin with 0
            cc=[]
            cc.append(xyzmol[i][1])
            cc.append(xyzmol[i][2])
            cc.append(xyzmol[i][3])
            atm.cc=cc # coord list, [x,y,z]
            elm=xyzmol[i][0]
            if len(elm) == 1: elm=' '+elm
            atm.elm=elm
            atm.atmnam=elm+'  '
            atm.atmnmb=i
            self.atm.append(atm)
            atm.SetAtomParams(atm.elm)
        # bond data
        for i in range(len(bond)):
            if len(bond[i]) == 0: continue
            bnddic={}
            for i in range(len(bond)):
                ii=bond[i][0]; jj=bond[i][1]; kk=bond[i][2]
                if ii in bnddic:
                    bnddic[ii].append(jj); bnddic[ii].append(kk)
                else:
                    bnddic[ii]=[]
                    bnddic[ii].append(jj)
                    bnddic[ii].append(kk)
            bnd=list(bnddic.keys())
            bnd.sort()
            for i in bnd:
                atm=self.atm[i]
                tmp=bnddic[i]; con=[]; knd=[]
                for j in range(0,len(tmp),2):
                    con.append(tmp[j])
                    knd.append(tmp[j+1])
                atm.conect=con
                atm.bndmulti=knd
        # residue and fragment data
        if len(resfrg) > 0:
            self.ResetBDADic()
            for i in range(len(resfrg)):
                atm=self.atm[i]
                s0=resfrg[i][0]
                s1=resfrg[i][1]
                s2=resfrg[i][2]
                s3=resfrg[i][3]
                s4=resfrg[i][4]
                s5=resfrg[i][5]
                s6=resfrg[i][6]
                s7=resfrg[i][7]
                s8=resfrg[i][8]
                s9=resfrg[i][9]
                #s10=resfrg[i][10]
                #s11=resfrg[i][11]
                atm.atmnam=s0 # atom name
                atm.atmnmb=int(s1) # atom number
                atm.resnam=s2 # residue name
                atm.resnmb=int(s3) # residue number
                atm.chainnam=s4 # chain name
                atm.charge=float(s5) # charge
                #if s6 != 'None':
                atm.grpnam=s6 # group name
                #if s7 != 'None':
                atm.frgnam=s7
                atm.frgchg=float(s8)
                atm.frgbaa=int(s9) # ! not treatedd in ReadXYZMol()
                if atm.frgbaa >=0: self.SetToBDADic(i,atm.frgbaa)
                #if s6 != 'None':
                #    atm.ffatmnam=s10
                #    atm.ffatmtyp=int(s11)
            self.CreateFrgConDat()

    def SetTinkerAtoms(self,tinatm): #,atyp):
        # atyp: True=set, False* do't set
        if len(tinatm) <= 0:
            lib.MessageBoxOK('No atoms in tinatm list',"")
            return
        self.atm=[]
        for i, atmnam,cc,atmtyp,con in tinatm:
            atm=Atom(self)
            atm.seqnmb=i
            atm.cc=cc #tinatm[i][2]
            atm.atmnam=atmnam #tinatm[i][1]
            atm.ffatmnam=atmnam
            if atmtyp == 0:
                tmp=atmnam #tinatm[i][1]
                atm.elm=lib.AtmNamToElm(tmp)
            else: atm.elm=' '+atmnam[0:1]
            atm.ffatmtyp=atmtyp #tinatm[i][3]
            atm.conect=con #tinatm[i][4]
            #atm.bndmulti=1
            bndmulti=[]
            nbnd=len(con)
            if nbnd > 0:
                for j in range(nbnd): bndmulti.append(1) # default: single bond
            atm.bndmulti=bndmulti # bond multiplicy list

            self.atm.append(atm)
            # Set parameters defined in const module
            #atm.SetDefaultElmColor() # element color
            #atm.SetDefaultVdwRad() # vdw radius
            #atm.SetDefaultAtmRad() # atom radius
            atm.SetAtomParams(atm.elm)

    def ConsoleMessage(self,mess):
        # mess(str): message
        if self.messout2 is not None:
            try: self.messout2(mess)
            except: print(mess)

    def Message(self,mess,outlog=False): #,loc,color):
        if self.messout1 is not None:
            try: self.messout1(mess,outlog=outlog) #,loc,color)
            except: print(mess)

class Atom(object):
    def __init__(self,parent):
        self.parent = parent # the 'Molecule' object
        # pdb data. See PDB manual for each items
        self.seqnmb   = -1 # seq number of atoms 0,1,..,natom-1
        self.cc       = [] # cartesian coordinate [x,y,z] in Angstrom
        self.conect   = [] # connect data
        self.atmnam   = '' # atom name
        self.atmnmb   = -1 # atom number
        self.resnam   = 'UNK' # residue name
        self.resnmb   = -1 # residue number
        self.chainnam = '' # chain name
        self.altloc   = ' '
        self.elm      = '' # element name
        self.focc     = 0 # occupancy
        self.bfc      = 0 # thermal factor
        self.charge   = 0 # atom charge
        # additional to pdb data
        self.bndmulti      = [] # {'single':1,'double':2,'triple':3,'aromatic':4}
        self.extraconect   = [] # connect data for extrabond
        self.extrabnd      = [] # extra bonds, 1:H-bond,2:vdW,3:salt-bridge,4:CH/pi,...
        self.extrabndthick = 1 # bond thickness
        self.extrabndcolor = [0.0,1.0,1.0,1.0] # cyan
        # draw parameters
        self.color    = [] # const.ElmCol['ZZ'] # atom color. defaul:unknown elm
        #self.opacity=1.0 # opacity. 0.0-1.0
        self.show     = True # show flag
        self.select   = False # select flag
        self.model    = 0 #1 # draw model, 0:line model; 1:stick, 2:ball-and-stick,3.CPK
        self.atmrad   = 0.4 # default value defined in const is set
        self.vdwrad   = 1.0 # default value defined in const is set
        self.atmradsc = 1.0 # scale factor of atom radius for ball and stick model
        self.vdwradsc = 1.0 # scale factor of van der Waals radius
        self.thick    = 1.0 # 0.5  # bond thicknes. default balue in const is set
        self.thickbs  = 0.5
        self.thicksc  = 1.0 #1.0 # scale factor of bond thickness
        # for geo opt
        self.activexyz = [] # True or False for [x,y,z](cartesian)
        #self.zmtpnts=[] # z-matrix point data
        self.activezmt = [] # True or False for [length,angle,tosion](zmt)
        # for move
        self.active  = False # for geo opt
        # group data
        self.group   = 0 # group number
        self.grpnam  = 'base' # group name
        self.grpchg  = 0 # gropu charg
        self.envflag = False # environment (special group) flag
        self.parnam  = '' # name of parent molecule
        # fragement data
        self.frgnmb  = -1
        self.frgnam  = '' # fragment name, three characters+seqence number
        self.frgchg  = None # fragment atom formal charge used to calulate fragment charge.
        self.frgknd  = -1 # kind 0:peptide, 1:non-peptide, 2:water
        #self.frgspin=0 # fragment spin
        self.frgmulti = 1
        self.frgbaa   = -1 # atom seq numbe of baa. atom with non zero frgbaa is a bda atom.
        self.layer    = 1 # FMO layer. 1:1st, n: n-th layer and 11:MM in IMOMM, 12:EFP
        self.frgcondat = []
        # force field data
        self.ffatmtyp = '' # ff atom type
        self.ffatmcls = '' # ff atom class
        self.ffatmnam = '' # ff atom name
        self.ffatmchg = 0.0 # ff partial charge
        self.ffLJprm  = [] # LJ potential parameters
        self.ffname   = '' # ff name
        #
        self.atmprp = 0.0 # temporal value
        self.atmtxt = ""   # temporal text data
        # undefined
        self.undefinedelmcolor = [1.0,0.75,0.8,1.0]
        self.undefinedvdwrad = 1.8
        # attribute dictonary for extension for use in external script
        self.attribdic = {}
        #
    def GetDefaultElementColor(self,elm):
        colordic = {' H' : [0.8,0.8,0.8,1.0],
                    ' C' : [0.5,0.5,0.5,1.0],
                    ' N' : [0.0,0.47,0.94,1.0], #[0.5,0.5,1.0,1.0],
                    ' O' : [1.0,0.0,0.0,1.0],
                    ' S' : [0.94,0.73,0.0,1.0], #[1.0,1.0,0.0,1.0], # yellow
                    ' P' : [0.5,0.5,0.5,1.0], # unknown element color
                    'CL' : [0.0,1.0,1.0,1.0], # cyan ... anion color
                    'NA' : [1.0,1.0,0.0,1.0], # yellow ... cation color
                    'MG' : [1.0,1.0,0.0,1.0], # yellow
                    'MN' : [1.0,1.0,0.0,1.0], # yellow
                    'FE' : [1.0,1.0,0.0,1.0], # yellow
                    'CA' : [0.5,0.0,0.0,1.0], # brown,[1.0,1.0,0.0,1.0], # yellow
                    ' X' : [0.0,0.5,1.0,1.0], # dummy atom
                    'ZZ' : [0.5,0.5,0.5,1.0], # unkown element
                    'XX' : [0.0,0.0,0.0,1.0], # black, TER atom
                    'SL' : [0.0,1.0,0.0,1.0], # green, selected atom
                    'EV' : [1.0,0.0,0.6,1.0], # magenta,environment atoms
                    'EX' : [0.0,1.0,1.0,1.0], # cyan, extra bond
                    '??' : [1.0,0.0,0.6,1.0]  # unidentified atom
                 }
        if elm in colordic: color = colordic[elm]
        else: color = colordic['ZZ']
        return color

    def GetDefaultVdwRadius(self,elm):
        raddic={' H' : 1.20, 'HE' : 1.20, 'LI' : 1.37, 'BE' : 1.45, ' B' : 1.45,
                ' C' : 1.50, ' N' : 1.50, ' O' : 1.40, ' F' : 1.35, 'NE' : 1.30,
                'NA' : 1.57, 'MG' : 1.36, 'AL' : 1.25, 'SI' : 1.17, ' P' : 1.80,
                ' S' : 1.75, 'CL' : 1.70, 'AR' : 1.80, ' K' : 1.80, 'CA' : 1.80,
                'SC' : 1.80, 'TI' : 1.80, 'V ' : 1.80, 'CR' : 1.80, 'MN' : 1.80,
                'FE' : 1.80, 'CO' : 1.80, 'NI' : 1.80, 'CU' : 1.80, 'ZN' : 1.80,
                'GA' : 1.80, 'GE' : 1.80, 'AS' : 1.80, 'SE' : 1.80, 'BR' : 1.80,
                'KR' : 1.80, 'RB' : 1.80, 'SR' : 1.80, ' Y' : 1.80, 'ZR' : 1.80,
                'NB' : 1.80, 'MO' : 1.80, 'TC' : 1.80, 'RU' : 1.80, 'RH' : 1.80,
                'PD' : 1.80, 'AG' : 1.80, 'CD' : 1.80, 'IN' : 1.80, 'SN' : 1.80,
                'SB' : 1.80, 'TE' : 1.80, ' I' : 1.80, 'XE' : 1.80, 'CS' : 1.80,
                'BA' : 1.80, 'LA' : 1.80, 'CE' : 1.80, 'PR' : 1.80, 'ND' : 1.80,
                'ZZ' : 1.80, 'XX':0.0} # 'ZZ': unkown, 'XX': TER Atom

        if elm in raddic: rad = raddic[elm]
        else: rad = raddic['ZZ']
        return rad

    def SetAtomParams(self,elm):
        self.SetElmColor(elm)
        self.SetVdwRad(elm)
        self.SetAtmRad(elm)
        self.SetBondThick()
        self.SetBondThickBS()
        self.SetModel()

    def SetElmColor(self,elm):
        """ Set color to element

        :param str elm: element symbol in right adjusted two characters
                        (upper case)
        :return: color(lst) - color list of [r,g,b,a]
        """
        if self.parent.elmcolordic is not None:
            if elm in self.parent.elmcolordic:
                self.color = self.parent.elmcolordic[elm][:]
            else:
                if 'ZZ' in self.parent.elmcolordic:
                    self.color = self.parent.elmcolordic['ZZ'][:]
                else: self.color = self.DefaultElementColor()['ZZ'][:]
        else:
            self.color = self.GetDefaultElementColor(elm)

    def SetVdwRad(self,elm):
        if self.parent.vdwraddic is not None:
            if elm in self.parent.vdwraddic:
                self.vdwrad = self.parent.vdwraddic[elm]
            else: self.vdwrad = self.undefinedvdwrad
        else:
            self.vdwrad = self.GetDefaultVdwRadius(elm)

    def SetAtmRad(self,elm):
        if self.parent.atomradius is not None:
            fact = 1.0
            #if elm == ' X': fact=0.2
            self.atmrad = fact * self.parent.atomradius

    def SetBondThick(self):
        if self.parent.bondthick is not None:
            self.thick = self.parent.bondthick

    def SetBondThickBS(self):
        if self.parent.bondthickbs is not None:
            self.thickbs = self.parent.bondthickbs

    def SetModel(self):
        #self.model=self.setctrl.GetParam('mol-model')
        if self.parent.molmodel is not None:
            self.model = self.parent.molmodel

    def SetAtomDataByDic(self,atmdatdic):
        for prm, value in list(atmdatdic.items()):
            # pdb data
            if prm == "seqnmb": self.seqnmb = value
            if prm == "cc":     self.cc = value
            if prm == "conect": self.conect = value
            if prm == "atmnam": self.atmnam = value
            if prm == "atmnmb": self.atmnmb = value
            if prm == "resnam": self.resnam = value
            if prm == "resnmb": self.resnmb = value
            if prm == "chainnam": self.chainnam = value
            if prm == "altloc":    self.elm = value
            if prm == "elm":    self.elm = value
            if prm == "focc":   self.focc = value
            if prm == "bfc":    self.bfc = value
            if prm == "charge": self.charge = value
            # extra bond data
            if prm == "bndmulti": self.bndmulti = value
            if prm == "extrabnd": self.extrabnd = value
            # draw parameters
            if prm == "color":   self.color = value
            if prm == "show":    self.show = value
            if prm == "select":  self.select = value
            if prm == "model":   self.model = value
            if prm == "atmrad":  self.atmrad = value
            if prm == "atmradsc":  self.atmradsc = value
            if prm == "vdwrad":  self.vdwrad = value
            if prm == "vdwradsc":  self.vdwrad = value
            if prm == "thick":   self.thick = value
            # group data
            if prm == "grpnam":  self.grpnam = value
            if prm == "grpchg":  self.grpchg = value
            if prm == "envflag": self.envflag = value
            if prm == "parnam":  self.parnam = value
            # fragement data
            if prm == "frgnam":  self.frgnam = value
            if prm == "frgchg":  self.frgchg = value
            if prm == "frgbaa":  self.frgbaa = value
            if prm == "layer":  self.frgbaa = value
            # force field data
            if prm == "ffatmtyp": self.ffatmtyp = value # ff atom type
            if prm == "ffatmcls": self.ffatmcls = value # ff atom class
            if prm == "ffatmnam": self.ffatmnam = value # ff atom name
            if prm == "ffcharge": self.ffcharge = value# ff partial charge
            if prm == "ffname": self.ffname = value # ff name

    def MakePDBAtomString(self):
        # ret s(str): string of PDB ATOM record format
        blk = ' '; fi4 = '%4d'; fi3 = '%3d'; fi2 = '%2d'; fi5 = '%5d'
        ff8 = '%8.3f'; ff6 = '%6.2f'
        #s = blk * 80;
        ires = 0
        if self.elm == 'XX':
            s = 'TER' + 3*blk
            st = (fi5 % (self.seqnmb + 1))
            s += st[0:5] # s[6:11], atom seq number
            s += blk
            st = 4 * blk
            s += st[0:4] # s[12:16] atmnam
            st = self.altloc
            s += blk  #s=s+st[0:1] # s[16:17], alt location
            st = self.resnam
            s += st[0:3] # s[17:20], resnam
            s += blk + self.chainnam
            s += '\n'
        else:
            rec = 'HETATM'
            if self.resnam in const.AmiRes3:
                ires += 1; rec='ATOM  '
            s = rec[0:6] # s[0:6], rec name
            st = fi5 % (self.seqnmb+1)
            s += st[0:5] # s[6:11], atom seq number
            s += blk
            st = self.atmnam + 4 * blk
            s += st[0:4] # s[12:16] atmnam
            st = self.altloc
            s += blk  #s=s+st[0:1] # s[16:17], alt location
            st = self.resnam + 3 * blk
            s += st[0:3] # s[17:20], resnam
            s += blk + self.chainnam
            st = fi4 % self.resnmb + 4 * blk
            s += st[0:4] #s[22:26] resnumb
            s += blk # s[26:27], anchar
            s += 3 * blk
            s += ff8 % self.cc[0] ##s[30:38] x coord
            s += ff8 % self.cc[1] #s[38:46] y coord
            s += ff8 % self.cc[2] #s[46:54] z coord
            s += ff6 % self.focc #s[54:60] occupancy
            s += ff6 % self.bfc #s[60:66] temperature factor
            s += 10 * blk
            st = self.elm
            st = st.strip(); st = st.rjust(2) + 2 * blk
            s += st[0:2] #s[76:78] element
            if self.charge == 0: s += '  '
            else: s += fi2 % self.charge #s[78:80] charge
            s += '\n'
            #
        return s

    def GetPDBDataDic(self):
        pdbdatdic = {}
        pdbdatdic["seqnmb"]   = self.seqnmb
        pdbdatdic["cc"]       = self.cc
        pdbdatdic["conect"]   = self.conect
        pdbdatdic["atmnam"]   = self.atmnam
        pdbdatdic["atmnmb"]   = self.atmnmb
        pdbdatdic["resnam"]   = self.resnam
        pdbdatdic["resnmb"]   = self.resnmb
        pdbdatdic["chainnam"] = self.chainnam
        pdbdatdic["altloc"]   = self.elm
        pdbdatdic["elm"]      = self.elm
        pdbdatdic["focc"]     = self.focc
        pdbdatdic["bfc"]      = self.bfc
        pdbdatdic["charge"]   = self.charge
        return pdbdatdic

    def MakeMol2AtomString(self):
        ff10 = '%10.4f'; fi4 = '%4d'; fi6  = '%6d'; nl = '\n'; blk  = ' '

        atomstring += (fi6 % (self.seqnmb+1))+ blk
        atomstring += self.atmnam + blk
        atomstring += (ff10 % self.cc[0]) + blk
        atomstring += (ff10 % self.cc[1]) + blk
        atomstring += (ff10 % self.cc[2]) + blk
        atmtyp = self.ffatmtyp
        if len(atmtyp) < 4: atmtyp += (4-len(atmtyp)) * blk
        atomstring += atmtyp + blk
        atomstring += (fi4 % self.resnmb) + blk
        atomstring += self.resnam + str(self.resnmb)
        atomstring += (4-len(str(atom.resnmb))) * blk
        atomstring += (ff10 % self.ffatmchg) + nl
        return atomstring

    def MakeSDFAtomString(self):
        ff10 = '%10.4f'
        atmblock   = '  0  0  0  0  0  0  0  0  0  0  0  0\n'

        atomstring = ''
        elm = self.elm.strip()
        if len(elm) == 1: elm = elm + ' '
        atomstring += ff10 % self.cc[0] + ff10 % self.cc[1]
        atomstring += ff10 % self.cc[2] + ' ' + elm + atmblock
        return atomstring

    def MakeXYZAtomString(self,label=False):
        ff10 = '%10.4f'; blk = ' '; nl = '\n'
        atomstring = 2 * blk
        if label: atomstring += (fi6 % (self.seqnmb+1)) + 2 * blk
        atomstring += elm
        atomstring += ff10 % self.cc[0] + ff10 % self.cc[1]
        atomstring += ff10 % self.cc[2] + nl
        return atomstring

    def GetGrpDataDic(self):
        grpdatdic = {}
        grpdatdic["grpnam"]  = self.grpnam
        grpdatdic["grpchg"]  = self.grpchg
        grpdatdic["envflag"] = self.envflag
        grpdatdic["parnam"]  = self.parnam
        return grpdatdic

    def GetResDataDic(self):
        resdatdic = {}
        resdatdic["resnam"]   = self.resnam
        resdatdic["resnmb"]   = self.resnmb
        resdatdic["chainnam"] = self.chainnam
        return resdatdic

    def GetAtmDataDic(self):
        atmdatdic = {}
        atmdatdic["atmnam"] = self.resnam
        atmdatdic["atmnmb"] = self.resnmb
        return atmdatdic

    def GetDrwParamDic(self):
        drwprmdic = {}
        drwprmdic["color"]    = self.color
        drwprmdic["show"]     = self.show
        drwprmdic["select"]   = self.select
        drwprmdic["model"]    = self.model
        drwprmdic["atmrad"]   = self.atmrad
        drwprmdic["atmradsc"] = self.atmradsc
        drwprmdic["vdwrad"]   = self.vdwrad
        drwprmdic["vdwradsc"] = self.vdwradsc
        drwprmdic["thick"]    = self.thick
        drwprmdic["thicksc"]  = self.thicksc
        return drwprmdic

    def SetDrwParams(self,drwprmdic):
        if "color" in drwprmdic:    self.color    = drwprmdic["color"]
        if "show" in drwprmdic:     self.show     = drwprmdic["show"]
        if "select" in drwprmdic:   self.select   = drwprmdic["select"]
        if "model" in drwprmdic:    self.model    = drwprmdic["model"]
        if "atmrad" in drwprmdic:   self.atmrad   = drwprmdic["atmrad"]
        if "atmradsc" in drwprmdic: self.atmradsc = drwprmdic["atmradsc"]
        if "vdwrad" in drwprmdic:   self.vdwrad   = drwprmdic["vdwrad"]
        if "vdwradsc" in drwprmdic: self.vdwradsc = drwprmdic["vdwradsc"]
        if "thick" in drwprmdic:    self.thick    = drwprmdic["thick"]
        if "thicksc" in drwprmdic:  self.thicksc  = drwprmdic["thicksc"]

    def GetFrgDataDic(self):
        frgdatdic = {}
        frgdatdic["frgnam"] = self.frgnam
        frgdatdic["frgchg"] = self.frgchg
        frgdatdic["frgbaa"] = self.frgbda
        frgdatdic["layer"]  = self.layer
        return frgdatdic


class Crystal(object):
    def __init__(self,parent=None,ciffile=None,messout1=None,messout2=None):
        """

        param obj messout1: Status message method object
        param obj messout2: Console message method object
        """
        print('Crystal class in fu_molec')

        classnam = 'Packing'
        self.parent = parent
        self.model  = parent
        self.messout1 = messout1 # output method object
        self.messout2 = messout2 # output method object
        self.warning  = True
        #
        self.inpfile        = None # usually cif file
        # data in cif file
        self.database_code  = None
        self.chem_form      = None
        self.chem_name_sys  = None
        self.chem_name_com  = None
        self.weight         = None
        self.cell_setting   = None
        self.space_group    = None
        self.unit_Z         = None
        self.temperature    = None
        self.cell_params    = None
        self.sym_equ_pos    = None
        self.fract_coords   = None
        self.bond_atomnams  = None
        #
        self.natm_unit_mol  = None
        self.box_vertexes   = None # xyz coordinates of cell box bertexes
        self.unit_molecule  = None # fract coords of unit molecule
        self.mat_fract2xyz  = None # tf matrix from fract to xyz coords
        self.top            = None # tr vecs of sym_equ_pos operations
        self.sop            = None # rot matrices of sym_equ_pos operations
        self.cell_volume    = None
        self.unit_mol_bonds = None # [[ia,ja,order],...]
        #
        self.margin = 1.1

        if ciffile is not None:
            if os.path.exists(ciffile):
                cifdata = self.ReadCIFFile(ciffile)
            self.SetCIFData(cifdata)
            self.ComputeAttribs()

    def Warning(self):
        if not self.warning: return
        mess  = 'This program is designed to work on organic molecules\n'
        mess += ' and may not work on inorganic molecules'
        wx.MessageBox(mess,'CrystalBuilder_Frm.Warning')

    def WarningOnOff(self,on):
        """ on = True or False """
        self.warning = on

    def ReadCIFFile(self,filename):
        cifdata = rwfile.ReadCIFFile(filename)
        return cifdata

    def SetCIFData(self,cifdata):
        self.inpfile       = cifdata["input_ciffile"]
        #
        self.database_code = cifdata["database_code"]
        self.chem_form     = cifdata["chemical_formula"]
        self.chem_name_sys = cifdata["chemical_name_sys"]
        self.chem_name_com = cifdata["chemical_name_com"]
        self.weight        = cifdata["mol_weight"]
        self.cell_setting  = cifdata["cell_setting"]
        self.space_group   = cifdata["space_group"]
        self.unit_Z        = cifdata["units_Z"]
        self.temperature   = cifdata["temperature"]
        self.cell_params   = cifdata["cell_params"]
        self.sym_equ_pos   = cifdata["sym_equ_pos"]
        self.fract_coords  = cifdata["fract_coords"]
        self.bond_atomnams = cifdata["bond_atomnams"]

    def GetCIFData(self):
        cifdata = {}
        cifdata["input_ciffile"]     = self.inpfile
        cifdata["database_code"]     = self.database_code
        cifdata["chemical_formula"]  = self.chem_form
        cifdata["chemical_name_sys"] = self.chem_name_sys
        cifdata["chemical_name_com"] = self.chem_name_com
        cifdata["mol_weight"]        = self.weight
        cifdata["cell_setting"]      = self.cell_setting
        cifdata["space_group"]       = self.space_group
        cifdata["units_Z"]           = self.unit_Z
        cifdata["temperature"]       = self.temperature
        cifdata["cell_params"]       = self.cell_params
        cifdata["sym_equ_pos"]       = self.sym_equ_pos
        cifdata["fract_coords"]      = self.fract_coords
        cifdata["bond_atomnams"]     = self.bond_atomnams
        return cifdata

    def ComputeAttribs(self,unitmol=True):
        """

        :param bool unitmol: True for generate unit molecule, False do not
        """
        self.mat_fract2xyz  = self.TFMatrixFromCellToXYZCoords()
        self.top,self.sop   = self.GetSymEquPosOps()
        #
        self.box_vertexes   = self.BoxVertexXYZ()
        if unitmol:
            self.unit_molecule  = self.GenUnitMolecule()
            self.natm_unit_mol  = len(self.unit_molecule)
        self.cell_volume    = self.CellVolume()

    def SetCellParams(self,paramstring):
        """ Set cell parameters

        :param str paramstring: string data, '5.522, 5.4396, 7.6726, ...'
        """
        torad = 2.0 * numpy.pi / 360.0
        params = lib.SplitStringAtSeparator(paramstring,',')
        nprm   = len(params)
        if nprm != 6:
            print('Error: input cell params are less than 6.')
            return
        self.cell_params = 6 * [0.0]
        for i in range(6):
            self.cell_params[i] = float(params[i])
            if i > 2: self.cell_params[i] = torad * float(params[i])

    def SetSymEquPos(self,symstring):
        """ Set symmetry equivalent positon

        :param str symstring: 'x, y, z', '-x, y+1/2, -z+1/2',...
        """
        self.sym_equ_pos =lib.GetStringBetweenQuotation(symstring)

    def SetUnitMoleculeInXYZ(self,umol_xyz):
        """ Set unit molecule in fractional coordinates

        :param lst umol_xyz: [[label,el,x,y,z],...]
        """
        self.natm_unit_mol = len(umol_xyz)
        self.unit_molecule  = self.XYZCoordsToFracts(umol_xyz)

    def XYZCoordsToFracts(self,xyz_coords):
        umol_fract_coords = []
        """ Convert xyz coordinates to fractiobal coordinates

        :param str xyz_coords: [[label,elm,fx,fy,fz],...]
        :return: fract_coords(lst) - list of Cartesian coordinates,
                 [[label(str),elm(str),x(float),y(float),z(float)],..]
        """
        if len(self.mat_fract2xyz) <= 0:
            mess = 'Please set matrix converting from fractional to xyz '
            mess += ' coordinates'
            lib.MessageBoxOK(mess,'fu_crystal.XYZCoordsToFracts')
            return

        fract_coords = []
        natm = len(xyz_coords)
        uinv = numpy.linalg.inv(self.mat_fract2xyz)
        for i in range(natm):
            xyz = numpy.array([xyz_coords[i][2],xyz_coords[i][3],
                                xyz_coords[i][4]])
            fxyz = numpy.dot(uinv,xyz)
            fract_coords.append([xyz_coords[i][0],xyz_coords[i][1],
                               fxyz[0],fxyz[1],fxyz[2]])
        return fract_coords

    def SetFractCoords(self, fract_coords):
        """ Set fractional coordinates of asymmetric unit

        :param lst fract_coords: [[label,el,fx,fy,fz],..]
        """
        self.fract_coords = fract_coords

    def SetUnitMolBonds(self,umol_bonds):
        """ Set bonds in unit molecule

        :param lst umol_bonds: [[a1,a2,bond type],...]
        """
        self.unit_mol_bonds = umol_bonds

    def GetUnitMolecule(self):
        """ Return unit molecule in fractional coordinates """
        return self.unit_molecule[:]

    def GetSymEquOps(self):
        """ Return symmetry equvalent position operators """
        return self.top[:],self.sop[:]

    def GetMatFractToXYZ(self):
        """ Return transformation matrix from fractional to xyz coordinates """
        return self.mat_fract2xyz[:]

    def GetInputCIFFileName(self):
        """ Return flename of input cif file """
        return self.inpfile

    def GetCellVolume(self):
        """ Return cell volume """
        return self.cell_volume

    def GetCellParams(self):
        """ Return cell params """
        return self.cell_params

    def GetBoxVertexs(self):
        """ Return vertexes of cell box """
        return self.box_vertexes[:]

    def CellVolume(self):
        """ Compute cell volume

        return: cell_volume(float)
        """
        half_pi = 0.5 * numpy.pi
        eps     = 1.0e-5
        #
        [a,b,c,alpha,beta,gamma] = self.cell_params
        #
        if abs(alpha - half_pi) > eps: ca = numpy.cos(alpha)
        else: ca = 0.0
        if abs(beta - half_pi)  > eps: cb = numpy.cos(beta)
        else: cb = 0.0
        if abs(gamma - half_pi) > eps: cg = numpy.cos(gamma)
        else: cg = 0.0
        #
        cell_volume = a * b * c * numpy.sqrt(1.0 - ca * ca - cb * cb
                                             - cg * cg + 2.0 * ca * cb * cg)
        return cell_volume


    def TFMatrixFromCellToXYZCoords(self):
        """ Compute transformation matrix from fractional to Cartesian coordinates

        return: u(lst) - transformation matrix
        """
        [a,b,c,alpha,beta,gamma] = self.cell_params
        #
        ca = numpy.cos(alpha)
        cb = numpy.cos(beta)
        cg = numpy.cos(gamma)
        sg = numpy.sin(gamma)
        t1 = (cb - ca * cg) / sg
        t2 = numpy.sqrt(1.0 - ca * ca - cb * t1 - cg * ( cg - ca * cb))
        #
        u  = numpy.zeros((3,3))
        u[0][0] = a * sg
        u[0][2] = c * t1
        u[1][0] = a * cg
        u[1][1] = b
        u[1][2] = c * ca
        u[2][2] = c * t2 / sg
        #
        return u

    def GetSymEquPosOps(self):
        """ Resolve symmetry equivalent position data

        :return: toplst(lst) - translation matrices
                 soplst(lst) - symmetry operation matrices
        """
        def GetValues(symstr):
            top = 0.0
            sop = [0.0,0.0,0.0]
            #
            varlst = [['-x','+x','x'],['-y','+y','y'],['-z','+z','z']]
            valdic = {'-x': [0,-1.0],'+x': [0,1.0],'x': [0,1.0],
                      '-y': [1,-1.0],'+y': [1,1.0],'y': [1,1.0],
                      '-z': [2,-1.0],'+z': [2,1.0],'z': [2,1.0] }
            # sop
            for i in range(3):
                vars = varlst[i]
                for j in range(3):
                    var = vars[j]
                    nc = symstr.find(var)
                    if nc >= 0:
                        sop[valdic[var][0]] = valdic[var][1]
                        symstr = symstr.replace(var,'')
                        if len(symstr) <= 0: break
            # top
            if len(symstr) > 0:
                nc = symstr.find('/')
                if nc >= 0:
                    top = float(symstr[:nc]) / float(symstr[nc+1:])
                else: top = float(symstr)
            return top,sop
        #
        nop = len(self.sym_equ_pos)
        toplst = []
        soplst = []
        for i in range(nop):
            str = self.sym_equ_pos[i]
            items = lib.SplitStringAtSpaces(str)
            if len(items) == 1: symstr = str
            else: symstr = items[1]
            items = lib.SplitStringAtSeparator(symstr,',')
            sop = []
            top = []
            for i in range(3):
                topi,sopi = GetValues(items[i])
                sop.append(sopi)
                top.append(topi)
            toplst.append(top)
            soplst.append(sop)

        return toplst,soplst

    def FindAsymUnitFromUnitMol(self,umol_fract_coords):
        """ Return fractional coodinates of asymmetric unit

        :param lst umol_fracto_coords: fractional coordinates of unit molecule
        :return: fract_coods(lst) - fractional coodinates of asymmetric unit
        """
        eps  = 1e-4
        fract_coords = []
        ufc  = umol_fract_coords[:]
        skip = []
        nop = len(self.top)
        natm = len(ufc)
        for i in range(natm):
            if i in skip: continue
            pfc = numpy.array(ufc[i][2:])
            for iop in range(nop):
                to    = self.top[iop]
                so    = self.sop[iop]
                spfc  = numpy.dot(so,pfc)
                spfc += to
                for j in range(natm):
                    if j == i: continue
                    if j in skip: continue
                    if abs(ufc[j][2]-spfc[0])+abs(ufc[j][3]-spfc[1])\
                                  +abs(ufc[j][4]-spfc[2]) < eps:
                        skip.append(j)
        for i in range(natm):
            if not i in skip: fract_coords.append(ufc[i])
        return fract_coords

    def GenUnitMolecule(self,margin=None):
        """ Return fractional coordinates of asymmetric unit molecules

        :return: mol_fract_coords(lst9 - fractional coordinates of unit molecule
        """
        if margin is None: margin = self.margin
        #
        mol_fract_coords = []
        nop     = len(self.sop)
        natm    = len(self.fract_coords)
        cclst   = []
        elmlst  = []
        asymlst = []
        iatm = -1
        for iop in range(nop):
            tsym = self.top[iop]
            us   = self.sop[iop]
            cc = []
            for i in range(natm):
                iatm += 1
                fxyz = [self.fract_coords[i][2],self.fract_coords[i][3],self.fract_coords[i][4]]
                elm = lib.ToElementSymbol(self.fract_coords[i][1])
                fxyz = numpy.dot(us,fxyz)
                fxyz += tsym
                xyz = numpy.dot(self.mat_fract2xyz,fxyz)
                if self.AreMolsOverlap([xyz],cclst,formxyz=True): continue
                asymlst.append([i,iop])
                cclst.append([xyz[0],xyz[1],xyz[2]])
                elmlst.append(elm)
        #
        bndlst = lib.CovalentBondedAtomList(elmlst,cclst) #,margin=margin)
        ntatm = len(elmlst)
        grplst = self.FindBondedGroups(ntatm,bndlst)
        ngrp = len(grplst)
        if ngrp <= 0:
            mess  = 'Failed to generate aymmetric molecule.'
            mess += ' Unable to continue.'
            wx.MessageBox(mess,"CrystalBuilder_Frm.GenUnitMolecule")
            return []
        #
        maxatm = 0
        maxgrp = 0
        for i in range(ngrp):
            if len(grplst[i]) > maxatm:
                maxatm = len(grplst[i])
                maxgrp = i

        for i in grplst[maxgrp]:
            fract = self.fract_coords[asymlst[i][0]]
            iop   = asymlst[i][1]
            fxyz  = [fract[2],fract[3],fract[4]]
            fxyz  = numpy.dot(self.sop[iop],fxyz)
            fxyz += self.top[iop]
            mol_fract_coords.append([fract[0],fract[1],fxyz[0],fxyz[1],fxyz[2]])
        return mol_fract_coords

    def FindBondedGroups(self,natm,bndlst):
        """ Return bonded atom groups(using networkx)

        :param int natm: number of atoms
        :param lst bndlst: list of bonded atom pair, [[ia,ja,r],...]
        :return: grplst(lst) - group list, e.g., [[1,2,..],[8,..],..(ngroups)]
        """
        grplst  = []
        edgelst = []
        atmlst  = list(range(natm))
        for i,j,rij in bndlst: edgelst.append([i,j])
        G = networkx.Graph()
        G.add_edges_from(edgelst)
        congrp = networkx.connected_components(G)
        grplst = [list(x) for x in congrp]
        return grplst

    def FractCoordsToXYZs(self,fract_coords):
        """ Convert fractional coordinates to xyz coordinates

        :param str fact_coords: [[label,elm,fx,fy,fz],...]
        :return: xyz_coords(lst) - list of Cartesian coordinates,
                 [[label(str),elm(str),x(float),y(float),z(float)],..]
        """
        xyz_coords = []
        natm = len(fract_coords)
        u = self.mat_fract2xyz
        for i in range(natm):
            fxyz = [fract_coords[i][2],fract_coords[i][3],fract_coords[i][4]]
            xyz = numpy.dot(u,fxyz)
            xyz_coords.append([fract_coords[i][0],fract_coords[i][1],
                               xyz[0],xyz[1],xyz[2]])
        return xyz_coords

    def GenMolsIn000Cell(self,surface=True): #,umol_fract_coords,top,sop):
        """ Generate molecules in 000 cells and at the boundary

        :return: mols_fract_coords(lst) - fractional coordinates of generated
                 molecules,[[label,symbol,fx,fy,fz],...]
        """
        mols_fract_coords = []
        natm = len(self.unit_molecule)
        nop  = len(self.top)
        nmol = 0
        for iop in range(nop):
            nmol += 1
            tsym = numpy.zeros(3)
            tsym[0] = self.top[iop][0]
            tsym[1] = self.top[iop][1]
            tsym[2] = self.top[iop][2]
            mol_coords = []
            for i in range(natm):
                fcoords = [self.unit_molecule[i][2],self.unit_molecule[i][3],
                           self.unit_molecule[i][4]]
                fcoords  = numpy.dot(self.sop[iop],fcoords)
                fcoords += tsym
                mol_coords.append([self.unit_molecule[i][0],
                                   self.unit_molecule[i][1],
                                   fcoords[0],fcoords[1],fcoords[2]])
            #
            count = 0
            ans = False
            com = self.CenterCoordsOfMolecule(mol_coords)
            while ans == False:
                mol_coords = self.MoveMolInCell(com,mol_coords)
                com = self.CenterCoordsOfMolecule(mol_coords)
                ans = self.IsInCell(com)
                count += 1
                if count > 3:
                    print('Warninng: some molecules are not in cell.')
                    break
            if not self.AreMolsOverlap(mol_coords,mols_fract_coords):
                com = self.CenterCoordsOfMolecule(mol_coords)
                mols_fract_coords += mol_coords
                if surface:
                    # add boundary molecules
                    add_coords = self.AddBoundaryMols(com,mol_coords)
                    if len(add_coords) > 0: mols_fract_coords += add_coords

        return mols_fract_coords

    def GenMolsInKLMCells(self,klm,cmol_fract_coords):
        """ Generate molecules in klm cells and at the boundary

        :param lst klm: [k,l,m], lattice indeces k,l,m (>= 0).
        :param lst cmol_fract_coords: list of fractional coordinates in cell
                                      molecules
        :return: mols_fract_coords(lst) - fractional coordinates of generated
                 molecules,[[label,symbol,fx,fy,fz],...]
        """
        def AddCellMols(icmp,cmol_fract_coords,mols_fract_coords):
            ncatm = len(cmol_fract_coords)
            for i in range(ncatm):
                fract = cmol_fract_coords[i][:]
                fract[icmp+2] += 1
                if self.AreMolsOverlap([fract],mols_fract_coords): continue
                mols_fract_coords.append(fract[:])
            return mols_fract_coords
        #
        mols_fract_coords = cmol_fract_coords[:]
        cell_fract_coords = cmol_fract_coords[:]
        for icmp in range(3):
            for cidx in range(klm[icmp]+1):
                if cidx == 0: continue
                mols_fract_coords = AddCellMols(icmp,cell_fract_coords,
                                                    mols_fract_coords)
                cell_fract_coords = mols_fract_coords[:]
        return mols_fract_coords


    def AddBoundaryMols(self,com,mol_coords):
        """ Return coordinates of molecules at cell boundary

        :param lst com: fractional coordinates of center-of-molecule
        :param lst mol_coords: coordinates of asymmetric unit molecule
        :return: add_coords(lst) - list of coordinates at boundary
        """
        add_coords = []
        atorigin   = self.AtOrigin(com)
        onedge     = self.OnEdge(com)
        onwall     = self.OnWall(com)
        if atorigin: add_coords = self.AddOriginMol(mol_coords) # at origin
        elif onedge: add_coords = self.AddEdgeMol(onedge,mol_coords) # on edge
        elif onwall: add_coords = self.AddWallMol(onwall,mol_coords) # on wall]
        return add_coords

    def AddOriginMol(self,mol_coords):
        """ Retrun coordinates of molecules at cell vertexes

        :param lst mol_coords: fractional coordinates of unit molecule
        :return: add_coords(lst) - list of coordinates at boundary
        """
        add_coords = []
        trsvec = [[1,0,0],[0,1,0],[0,0,1],
                  [1,1,0],[1,0,1],[0,1,1],
                  [1,1,1]]
        natm = len(mol_coords)
        for i in range(7):
            coords = []
            for j in range(natm):
                coords.append(mol_coords[j][:])
                coords[j][2] += trsvec[i][0]
                coords[j][3] += trsvec[i][1]
                coords[j][4] += trsvec[i][2]
            add_coords += coords[:]
        return add_coords

    def AddWallMol(self,onwall,mol_coords):
        """ Retrun coordinates of molecules on cell wall

        :param str onwall: side wall index, 'yz0','xz0' or 'xy0'
        :param lst mol_coords: fractional coordinates of unit molecule
        :return: add_coords(lst) - list of coordinates at boundary
        """
        add_coords = []
        natm = len(mol_coords)
        coords = []
        for j in range(natm):
            if   onwall == 'yz0': vec = [1,0,0]
            elif onwall == 'xz0': vec = [0,1,0]
            elif onwall == 'xy0': vec = [0,0,1]
            coords.append(mol_coords[j][:])
            coords[j][2] += vec[0]
            coords[j][3] += vec[1]
            coords[j][4] += vec[2]
        add_coords = coords[:]
        return add_coords

    def AddEdgeMol(self,onedge,mol_coords):
        """ Retrun coordinates of molecules at cell edges

        :param str onedge: edge index, 'x0','y0' or 'z0'
        :param lst com: fractional coordinates of center-of-molecule
        :return: add_coords(lst) - list of coordinates at boundary
        """
        add_coords = []
        natm = len(mol_coords)
        if   onedge == 'x0': trsvec = [[0,0,1],[0,1,0],[0,1,1]]
        elif onedge == 'y0': trsvec = [[1,0,0],[0,0,1],[1,0,1]]
        elif onedge == 'z0': trsvec = [[1,0,0],[0,1,0],[1,1,0]]
        for i in range(3):
            coords = []
            for j in range(natm):
                coords.append(mol_coords[j][:])
                coords[j][2] += trsvec[i][0]
                coords[j][3] += trsvec[i][1]
                coords[j][4] += trsvec[i][2]
            add_coords += coords[:]
        return add_coords

    def IsInCell(self,com):
        """ Check if a point is in cell 000

        :params lst com: fractional coordinates of a point, [fx,fy,fz]
        :reeturn: ans(bool) - True or False
        """
        ans = True
        eps = 1e-4
        for i in range(3):
            if abs(com[i]) < eps: com[i] = 0.0
            if com[i] < - eps:
                ans = False
                break
            if com[i] > 1.0 + eps:
                ans = False
                break
        return ans

    def MoveMolInCell(self,com,mol_coords):
        """ Move molecule into cell 000

        :param str com: factiona cordinates of center-of-molecule
        :param str mol_coords: fractional coodinates of atoms
        :return: new_coords(lst) - list of fractional coordinates of moved molecule
        """
        new_coords = mol_coords[:]
        eps = 1e-4
        natm = len(mol_coords)
        for i in range(natm):
            for j in range(3):
                if abs(com[j]) < eps: com[j] = 0.0
                elif abs(com[j]-1.0) < eps: com[j] = 1.0
            if com[0] < 0.0:    new_coords[i][2] += 1.0
            elif com[0] >= 1.0: new_coords[i][2] -= 1.0
            if com[1] < 0.0:    new_coords[i][3] += 1.0
            elif com[1] >= 1.0: new_coords[i][3] -= 1.0
            if com[2] < 0.0:    new_coords[i][4] += 1.0
            elif com[2] >= 1.0: new_coords[i][4] -= 1.0
        return new_coords

    def AtOrigin(self,com):
        """ Is molecule at origin of 000 cell box

        :param str com: fractional coordinates of center-of-mass
        :return: ans(bool) - True or False
        """
        eps = 1e-4
        ans = False
        if abs(com[0]) < eps and abs(com[1]) < eps and abs(com[2]) < eps:
             ans = True
        return ans

    def OnWall(self,com):
        """ Is molecule on wall of 000 cell box

        :param str com: fractional coordinates of center-of-mass
        :return: onwall(str) - wall index, 'yz0','xz0', or 'xy0'
        """
        eps = 1e-4
        onwall = False
        if   abs(com[0]) < eps:        onwall = 'yz0'
        elif abs(com[1]) < eps:        onwall = 'xz0'
        elif abs(com[2]) < eps:        onwall = 'xy0'
        return onwall


    def OnEdge(self,com):
        """ Is molecule on edge of 000 cell box

        :param str com: fractional coordinates of center-of-mass
        :return: onedge(str) - edge index, 'x0','y0', or 'z0'
        """
        eps = 1e-4
        # edge
        onedge = False
        if   abs(com[1]) < eps and abs(com[2]) < eps: onedge = 'x0'
        elif   abs(com[0]) < eps and abs(com[2]) < eps: onedge = 'y0'
        elif   abs(com[0]) < eps and abs(com[1]) < eps: onedge = 'z0'
        return onedge

    def AreMolsOverlap(self,coords1,coords2,formxyz=False):
        """ Check overlap of two molecules

        :param lst coords1: coordinates of a molecule
        :param lst coords2: coordinates of the other molecule
        :param bool formxyz: True for xyz list([[x,y,z],.. )
                             False for coords lsit([[label,elm,x,y,z],..]
        :return: ans(bool) - True in overlap, False in non-overlap
        """
        eps2  = 1e-4
        ans = False
        if len(coords1) <= 0 or len(coords2) <= 0: return ans
        #
        if formxyz:
            ix = 0; iy = 1; iz = 2
        else:
            ix = 2; iy = 3; iz = 4
        natm1 = len(coords1)
        natm2 = len(coords2)
        #
        for i in range(natm1):
            x1 = coords1[i][ix]
            y1 = coords1[i][iy]
            z1 = coords1[i][iz]
            for j in range(natm2):
                x2 = coords2[j][ix]
                y2 = coords2[j][iy]
                z2 = coords2[j][iz]
                r2 = (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2
                if r2 < eps2:
                    ans = True
                    break
        return ans

    def CenterCoordsOfMolecule(self,coords):
        """ return center-of-coordinates

        :param lst coords: coordinate list, [[label,elm,x,y,z],...]
        :return: [x,y,z] - list of center-of-mass coodinates
        """

        natm   = len(coords)
        elmlst = []
        for i in range(natm): elmlst.append(lib.ElementNameFromString(coords[i][1]))
        atmass = []
        for i in range(natm): atmass.append(const.ElmMas[elmlst[i]])
        #
        mx = my = mz = sm = 0.0
        for i in range(natm):
            ms = atmass[i]
            x = coords[i][2]; y = coords[i][3]; z = coords[i][4]
            mx += ms*x; my += ms*y; mz += ms*z
            sm += ms
        # center of mass
        sm = 1.0 / sm
        return [mx*sm,my*sm,mz*sm]

    def BoxVertexXYZ(self):
        """ Return Cartesiann coordinates of vertexes of cell box

        :return: boxpnts(lst)- coordinates of 8 box vertexes
        """
        pntlst = [[0,0,0],[1,0,0],[0,1,0],[0,0,1],
                  [1,1,0],[0,1,1],[1,0,1],[1,1,1]]
        boxpnts = [numpy.array(lst) for lst in pntlst]
        #
        u = self.TFMatrixFromCellToXYZCoords()
        for i in range(7): boxpnts[i+1] = numpy.dot(u,boxpnts[i+1])
        return boxpnts

    def MoleculesInKLMCells(self,klm):
        """ Return XYZ cordinates of molecules in KLM cells and its surface

        :return: mols_xyz_coords(lst) - [[label,,elm,x,y,z],...]
        """
        if min(klm) < 0:
            mess = 'Negative k,l,m is not accepted'
            self.messout1(mess)
            return

        if klm == 'unit':
              klm = [0,0,0]
              cmol_fract_coords = self.GenMolsIn000Cell(surface=False)
        else: cmol_fract_coords = self.GenMolsIn000Cell()

        if max(klm) == 0: mols_fract_coords = cmol_fract_coords
        else: mols_fract_coords = self.GenMolsInKLMCells(klm,cmol_fract_coords)


        mols_xyz_coords = self.FractCoordsToXYZs(mols_fract_coords)
        return mols_xyz_coords

    def UnitMolecule(self):
        """ Return XYZ cordinates of unit molecule

        :return: umol_xyz_coords(lst) - [[label,,elm,x,y,z],...]
        """
        umol_fract_coords = self.GenUnitMolecule()
        if len(umol_fract_coords) <= 0: return []

        umol_xyz_coords   = self.FractCoordsToXYZs(umol_fract_coords)
        return umol_xyz_coords

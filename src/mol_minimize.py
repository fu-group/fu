#!/bin/sh
# -*- coding: utf-8 -*-
#



import os
import wx
import sys
import io
import time
#import rdkit
#from rdkit import Chem

#sys.path.insert(0,'..//')
import lib
import const
import subwin
import rwfile
import fu_molec as molec

try:
    from openbabel import *
    import openbabel
    const.OPENBABEL=True
except: pass

try:
    import pybel
    const.PYBEL=True
except: pass


try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import AllChem
    const.RDKIT=True
except: pass



def SplitSDFFile(sdffile,dirnam,overwrite=True):
    """ Split multiple data sdf file into single ones

    :param str sdffile: sdf filename
    :param str dirnam: directory name in which separated files are created
                       output file are given by molecule name, mol.titl
    """
    for mol in pybel.readfile("sdf", sdffile):
        file = dirnam + '//' + mol.title + '.sdf'
        mol.write("sdf",file,overwrite=overwrite)

def SplitMOL2File(mol2file,dirnam,overwrite=True):
    """ Split multiple data mol2 file into single ones

    :param str mol2file: mol2 filename
    :param str dirnam: directory name in which separated files are created
                       output file are given by molecule name, mol.titl
    """
    for mol in pybel.readfile("mol2", mol2file):
        file = dirnam + '//' + mol.title + '.mol2'
        mol.write("mol2",file,overwrite=overwrite)

def UpdateFUMolCoords(fumol,atomcc,conect=None):
    natm = len(atomcc)
    if len(fumol.atm) != natm:
        print(('The number of atoms in fumol object ', len(fumol.atm)))
        print(('   is not equal to that of AtomCC',natm))
        print ('   Unable to update coordinates!')
        return
    for i in range(natm):
        fumol.atm[i].cc  = atomcc[i][1:]
        fumol.atm[i].elm = atomcc[i][0]
        if conect is not None: fumol.conect = conect
    return fumol

def GetOBAtomCC(obmol,type='OBMol'):
    """ type = 'pybel' or 'OBMol' """
    if type == 'pybel': mol = obmol.OBMol
    else: mol = obmol
    natm = mol.NumAtoms()
    atomcc = []
    for i in range(natm):
        Atom = mol.GetAtom(i+1)
        an = Atom.GetAtomicNum()
        elm = const.ElmSbl[an]
        x = Atom.GetX()
        y = Atom.GetY()
        z = Atom.GetZ()
        atomcc.append([elm,x,y,z])
    return atomcc

def GetFUAtomCC(fumol):
    natm = len(fumol.atm)
    atomcc = []
    for atom in fumol.atm:
        atomcc.append([atom.elm,atom.cc[0],atom.cc[1],atom.cc[2]])
    return atomcc

def FUToOBMol(fumol,viaform=None):
    natm = len(fumol.atm)
    #print 'FUToOBMol: the mumber of atoms =',natm
    name = fumol.name
    frmlst = ['sdf','mol2','pdb']
    if viaform is None:
        if natm > 999: viaform = 'pdb'
        else:          viaform = 'sdf'
    #
    if not viaform in frmlst:
        mess = 'Wrong via form' + viaform
        wx.MessageBox(mess,'mol_minimize.FuToOBMol')
        return None

    if viaform == 'mol2':
        mol2string = lib.MOL2TextFromMol(fumol)
        obmol = pybel.readstring("mol2",mol2string)
    elif viaform == 'sdf':
        sdfstring = lib.SDFTextFromMol(fumol)
        obmol = pybel.readstring("sdf",sdfstring)
    elif viaform == 'pdb':
        pdbstring = lib.PDBTextFromMol(fumol)
        obmol = pybel.readstring("pdb",pdbstring)
    return obmol

""" pybel function """
def make3D(obmol,forcefield='UFF',steps=500,crit=0.0001):
    forcefield = forcefield.lower()
    openbabel.OBBuilderBuild(obmol)
    obmol.AddHydrogens()
    ff = openbabel.OBForceField.FindForceField(forcefield)
    success = ff.Setup(obmol)
    if not success:
        print(('Failed to assign forcefield = ',forcefield))
        return
    #print 'retcod from ',forcefield
    ff.SteepestDescent(steps,crit)
    ff.GetCoordinates(molobj)
    print((ff.Energy()))
    return molobj

""" pybel function """
def localopt(molobj=None,forcefield='UFF',method='sd',steps=500,crit=0.01,
             logfile=None,filed=None):
    ###print 'logfile in localopt',logfile
        #sys.stdout = open(logfile,'w',1)
    forcefield = forcefield.lower()
    ff = openbabel.OBForceField.FindForceField(forcefield)
    ff.SetLogToStdOut()
    ff.SetLogLevel(openbabel.OBFF_LOGLVL_LOW)
    success = ff.Setup(molobj.OBMol)
    inienergy = ff.Energy()

    if logfile is not None and filed is None: #sys.stdout = open(logfile,'w')
        if os.path.exists(logfile):
            fd = os.open(logfile, os.O_WRONLY|os.O_APPEND) #os.O_CREAT)
            #f = open(logfile,"a",0)
            os.lseek(fd,0,2)
        else:
            ff.OBFFLog('test message text')
            fd = os.open(logfile, os.O_WRONLY|os.O_CREAT)
            #f = open(logfile,"w",0)
        os.dup2(fd, 1) #sys.stdout.fileno())=1 , stderr=2
        ###print 'fd',fd
        ####sys.stdout.flush()

    if success: pass # print 'localopt succeeded'
    else:
        print ('localopt failed')
        return None

    if filed is not None: os.lseek(filed,0,2)
    #print 'localopt: retcod from ',forcefield,success
    if   method== 'sd': ff.SteepestDescent(steps,crit)
    elif method== 'cg': ff.ConjugateGradients(steps,crit)

    ff.GetCoordinates(molobj.OBMol)
    ffenergy = ff.Energy()
    """
    e_elec = ff.E_Electrostatic()
    print 'eelec',e_elec
    e_bond = ff.E_Bond()
    print 'ebond',e_bond
    """
    #sys.stdout.flush()
    #print ff.Energy()
    return molobj,ffenergy,inienergy,fd

class FFParamOption_Frm(wx.Frame):
    def __init__(self,parent,retmethod):
        self.title='FF Parameters'
        winpos=[-1,-1]; winsize=lib.WinSize((190,155)) #((275,355))
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
        # message method
        self.retmethod = retmethod

        self.chargelst = ['FF charges','QEq charges','xxx','from file']
        self.charge = 'FF charges'

        self.dielec=1.0     # for amber
        self.vdw14scale=2.0 # for amber
        self.chg14scale=1.2 # for amber


        self.CreatePanel()

        self.Show()


    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        xsize=w; ysize=h
        hcb = 22
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(xsize,ysize)) #ysize))
        self.panel.SetBackgroundColour("light gray")
        #
        yloc = 10
        wx.StaticText(self.panel,-1,"Partial charge:",pos=(10,yloc),
                      size=(90,18))
        self.cmbchg=wx.ComboBox(self.panel,-1,'',choices=self.chargelst, \
                            pos=(100,yloc-2),size=(90,hcb),style=wx.CB_READONLY)
        self.cmbchg.SetStringSelection(self.charge)
        #self.cmbchg.Bind(wx.EVT_COMBOBOX,self.OnPartialCharge)
        yloc += 25
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        wx.StaticText(self.panel,-1,"charge 1-4 scale:",pos=(10,yloc),
                      size=(100,18))
        self.tclchg14=wx.TextCtrl(self.panel,-1,str(self.chg14scale),
                                  pos=(120,yloc),size=(50,18))
        yloc += 25
        wx.StaticText(self.panel,-1,"vdW 1-4 scale:",pos=(10,yloc),
                      size=(100,18))
        self.tclvdw14=wx.TextCtrl(self.panel,-1,str(self.vdw14scale),
                                  pos=(120,yloc),size=(50,18))
        yloc += 25
        wx.StaticText(self.panel,-1,"dielectric:",pos=(10,yloc),
                      size=(100,18))
        self.tcldielec=wx.TextCtrl(self.panel,-1,str(self.dielec),
                                   pos=(120,yloc),size=(50,18))
        #
        yloc += 25
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        btnapl=wx.Button(self.panel,-1,"Apply",pos=(40,yloc),
                         size=(50,22))
        btnapl.Bind(wx.EVT_BUTTON,self.OnApply)
        btncls=wx.Button(self.panel,-1,"Close",pos=(120,yloc),
                         size=(50,22))
        btncls.Bind(wx.EVT_BUTTON,self.OnClose)

    def OnApply(self,event):
        self.chg14scale = self.tclchg14.GetValue()
        self.vdw14scale = self.tclvdw14.GetValue()
        self.dielec     = self.tcldielec.GetValue()
        self.charge     = self.cmbchg.GetValue()
        self.retmethod(self.chg14scale,self.vdw14scale,self.dielec,self.charge)
        self.OnClose(1)

    def OnPartialCharge(self,event):
        self.charge = self.cmbchg.GetValue()

    def OnClose(self,event):
        self.Destroy()

""" execute 'obabel' in command shell
cmd='obabel e://TEST//fk506.mol -O e://TEST//obabel-opt.mol --minimize --steps 500 --sd'
retcod=subprocess.call(cmd,shell=True)


--log        output a log of the minimization process (default= no log)
--crit <converge>     set convergence criteria (default=1e-6)
--sd         use steepest descent algorithm (default = conjugate gradient)
--newton     use Newton2Num linesearch (default = Simple)
--ff <forcefield-id>       select a forcefield (default = Ghemical)
--steps <number>    specify the maximum number of steps (default = 2500)
--cut        use cut-off (default = don't use cut-off)
--rvdw <cutoff>     specify the VDW cut-off distance (default = 6.0)
--rele <cutoff>     specify the Electrostatic cut-off distance (default = 10.0)
--freq <steps>     specify the frequency to update the non-bonded pairs (default

def run(cmd, logfile):
    p = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=logfile)
    ret_code = p.wait()
    logfile.flush()
    return ret_code

"""

class OBMinimizer(object):
    def __init__(self,parent,model):

        self.parent = parent
        self.model  = model

        self.targetlst   = None
        self.forcefield  = None
        self.method      = None
        self.ene_conv    = None
        self.max_steps   = None
        self.coords_form = 'atomcc' # 'sdf' ot 'mol2'

        self.opt_coordslst  = []
        self.opt_sdftextlst = []
        self.opt_mol2textlst = []
        self.ffenergylst    = []
        self.inienergylst   = []
        self.convergelst    = []
        self.stepslst       = []
        self.timelst        = []
        self.logfile        = None
        self.filed = None

    def SetCoordsFrom(self,form):
        formlst = ['sdf','mol2','atomcc']
        if not form in formlst:
            mess = 'Wrong coordinates format. "sdf" is assumed.'
            wx.MessageBox(mess,'mol_minimize.OBMinimizer.SetCoordsForm')
            return
        self.coords_form = form

    def SetLogFile(self,logfile):
        self.logfile = logfile

    def SetTargetMols(self,targetlst):
        self.targetlst = targetlst

    def SetForceField(self,forcefield):
        self.forcefield = forcefield

    def SetMethod(self,method):
        self.method = method

    def SetEneConv(self,ene_conv):
        self.ene_conv = ene_conv

    def SetMaxSteps(self,max_steps):
        self.max_steps = max_steps

    def Minimize(self,update=True):
        mess = 'failed'
        for molnam in self.targetlst:
            start_time = time.clock()
            fumol = self.model.molctrl.GetMolByName(molnam)
            obmol = FUToOBMol(fumol)
            obmol,ffenergy,inienergy,filed = localopt(molobj=obmol,
                             forcefield=self.forcefield,
                             method=self.method,
                             steps=self.max_steps,crit=self.ene_conv,
                             logfile=self.logfile,filed=self.filed)
            self.filed = filed
            if self.coords_form == 'sdf':
                if obmol is None: self.opt_sdftextlst.append(mess)
                else: self.opt_sdftextlst.append(obmol.write('sdf'))
            elif self.coords_form == 'mol2':
                if obmol is None: self.opt_mol2textlst.append(mess)
                else: self.opt_mol2textlst.append(obmol.write('mol2'))
            else: # 'atomcc':
                if obmol is None: self.opt_coordslst.append(mess)
                else: self.opt_coordslst.append(GetOBAtomCC(obmol,type='pybel'))

            self.inienergylst.append(inienergy)
            self.ffenergylst.append(ffenergy)
            #
            end_time = time.clock()
            self.timelst.append(end_time-start_time)

    def GetOptCoords(self):
        if self.coords_form == 'sdf':
            return self.opt_sdftextlst
        elif self.coords_form == 'mol2':
            return self.opt_mol2textlst
        else: return self.opt_coordslst

    def GetFFEnergy(self):
        return self.ffenergylst

    def GetIniEnergy(self):
        return self.inienergylst

    def GetTimes(self):
        return self.timelst


class MMMinimizer_Frm(wx.Frame):
    """ Uses pybel/openbabel """
    def __init__(self,parent):
        self.prgnam = 'mol-minimize'
        self.winlabel = 'MMMinimizer'
        self.title = self.winlabel
        try:
            [x,y]  = parent.mdlwin.GetPosition()
            [w,h]  = parent.mdlwin.GetSize()
            winpos = [x+w,y+20]
        except: winpos=[-1,-1]
        winpos  = lib.SetWinPos(winpos)
        winsize=lib.WinSize((290,270))
        wx.Frame.__init__(self,parent,-1,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)

        self.model  = parent
        self.mdlwin = self.model.mdlwin
        self.setctrl = self.model.setctrl
        # attach FU icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        # check openbabbel is aveilable
        if not const.OPENBABEL or not const.PYBEL:
            mess = 'Need pybel and openbabel.\n'
            mess += 'Install "Open Babel 2.4.1"'
            wx.MessageBox(mess,'mol_minimizer.__init__')
            self.model.winctrl.CloseWin(self.winlabel)
            self.OnClose(1)
        #
        if not self.model.mol:
            mess='No molecule data in fumodel.'
            wx.MessageBox(mess,"mol_minimize",wx.OK)
            self.model.winctrl.CloseWin(self.winlabel)
            self.OnClose(1)
        # Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[MMMinimizer]')
        self.Bind(wx.EVT_MENU,self.OnMenu)
        # molecule object from fumodel
        self.fumol      = self.model.mol
        self.molnam     = self.fumol.name
        self.curmolname = self.fumol.name
        # ff params
        self.ffname     = "uff"
        self.ffnamelst  = ['uff','mmff94','gaff','ghemical']
        self.optmethod  = "cg"
        self.methodlst  = ['cg','sd']
        self.ene_conv   = 0.1 # for rough optimization!
        self.max_steps  = 100
        self.logfile    = None
        self.filed      = None
        # save data
        self.save_atomcc  = []
        self.coords_form     = 'atomcc'
        self.opt_atomcc   = None
        self.rms_atomcc   = []
        self.opt_atoms    = []
        self.rmsd         = None
        self.natm_org  = None
        self.opt_sdftext  = None
        self.opt_mol2text = None
        # flags
        self.execute = False
        self.rmsfit  = False
        self.update  = False
        self.undo    = False

        """ logout does not work, use >python -u fu.py """
        #try: sys.stdout = os.fdopen(1,'w',0)
        #except: pass

        """
        self.sysoutopen = False
        if not self.sysoutopen:
            fd = 1 #sys.stdout.fileno()
            sys.stdout = os.fdopen(fd, 'w', 0)
            self.sysoutopen = True
        """
        #
        """
        try:
            import pybel, openbabel
            self.openbabel = True
        except: self.openbabel = False
        if not self.openbabel:
            mess  = 'Please install "pybel" and "openbabel"'
            wx.MessageBox(mess,'mol_minimize',wx.OK)
            sys.exit()
        if self.openbabel: self.curtool = 'openbabel'
        """
        #
        self.rbtformobj = [] # for keeping radio button objects

        self.CreatePanel()

        self.SetButtonStat()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        # Event handler to receive message when child thread ends
        subwin.ExecProg_Frm.EVT_THREADNOTIFY(self,self.OnNotify)

        self.Show()

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        xsize=w; ysize=h
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(xsize,ysize)) #ysize))
        self.panel.SetBackgroundColour("light gray")
        hcb=25 #const.HCBOX
        yloc=10
        wx.StaticText(self.panel,-1,"target mol:",pos=(10,yloc),
                      size=(75,18))
        self.tcltrg = wx.TextCtrl(self.panel,-1,self.curmolname, \
                               pos=(90,yloc-2),size=(150,hcb))
        self.SetTargetMols()
        # Reset mol button
        subwin.Reset_Button(self.panel,-1,retmethod=self.OnResetCurMol,
                                         winpos=[250,yloc-2])
        yloc += 25
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        wx.StaticText(self.panel,-1,"Forcefield:",pos=(10,yloc),size=(60,18))
        self.cmbff=wx.ComboBox(self.panel,-1,'',choices=self.ffnamelst, \
                               pos=(110,yloc-2),size=(100,hcb),
                               style=wx.CB_READONLY)
        self.cmbff.SetStringSelection(self.ffname)
        yloc += 30
        wx.StaticText(self.panel,-1,"opt. method:",pos=(10,yloc),size=(85,18))
        self.cmbmet=wx.ComboBox(self.panel,-1,'',choices=self.methodlst, \
                               pos=(110,yloc-2),size=(100,hcb),
                               style=wx.CB_READONLY)
        self.cmbmet.SetStringSelection(self.optmethod)
        yloc += 25
        wx.StaticText(self.panel,-1,"energy conv:",pos=(10,yloc),
                      size=(80,18))
        self.tclcnv=wx.TextCtrl(self.panel,-1,str(self.ene_conv),pos=(110,yloc),
                                size=(50,20))
        yloc += 25
        wx.StaticText(self.panel,-1,"max. steps:",pos=(10,yloc),
                      size=(80,18))
        self.tclstp=wx.TextCtrl(self.panel,-1,str(self.max_steps),
                                pos=(110,yloc),size=(50,20))
        yloc += 25
        wx.StaticText(self.panel,-1,"opt. atoms:",pos=(10,yloc),
                      size=(80,18))
        self.optall=wx.RadioButton(self.panel,-1,'all',pos=(110,yloc),
                                    style=wx.RB_GROUP)
        self.optsel=wx.RadioButton(self.panel,-1,'selected',pos=(160,yloc))
        self.optsel.SetValue(True)
        yloc += 25
        self.ckbrms=wx.CheckBox(self.panel,-1,
                                "RMS fit of optimized and original coords",
                                pos=(10,yloc),size=(230,20))
        self.ckbrms.SetValue(False)
        lib.SetTipString(self.ckbrms,'RMS fit of optimized and original mols')
        yloc = h - 40
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 10
        self.btnexe=wx.Button(self.panel,-1,"Exec",pos=(15,yloc),size=(45,22))
        lib.SetTipString(self.btnexe,'Execute minimization')
        self.btnexe.Bind(wx.EVT_BUTTON,self.OnExec)
        wx.StaticLine(self.panel,pos=(70,yloc-10),size=(2,45),
                      style=wx.LI_VERTICAL)
        xpos = 85
        self.btncan=wx.Button(self.panel,-1,"Cancel",pos=(xpos,yloc),
                              size=(60,22))
        lib.SetTipString(self.btncan,'Cancel optimization')
        self.btncan.Bind(wx.EVT_BUTTON,self.OnCancel)
        self.btncod=wx.Button(self.panel,-1,"Update",pos=(xpos+70,yloc),
                         size=(60,22))
        self.btncod.Bind(wx.EVT_BUTTON,self.OnUpdateCoords)
        lib.SetTipString(self.btncod,'Update coordinates')
        self.btnund=wx.Button(self.panel,-1,"Undo",pos=(xpos+140,yloc),
                         size=(50,22))
        self.btnund.Bind(wx.EVT_BUTTON,self.OnUndo)
        lib.SetTipString(self.btnund,'Undo update coordinates')

    def OnOptionPanel(self,event):
        retmethod = self.ReturnFromOptionPanel
        optwin = FFParamOption_Frm(self,retmethod)

    def ReturnFromOptionPanel(self,chg14scale,vdw14scale,dielec,
                              chargemodel):
        self.chargemodel = chargemodel
        self.chg14scale = float(chg14scale)
        self.vdw14scale = float(vdw14scale)
        self.dielec     = float(dielec)

        if self.chargemodel == 'from file':
            filename = 'c://charge//test_partial_chages.chg'
            self.partialchg = []

        nl = '\n'
        mess = nl + 'parameters used are,' + nl
        mess += '  charge model     = ' + chargemodel
        if self.chargemodel == 'from file':
            mess += '(' + filename + ')' + nl
        else: mess += nl
        mess += '  charge 1-4 scale = ' + str(self.chg14scale) + nl
        mess += '  vdW 1-4 scale    = ' + str(self.vdw14scale) + nl
        mess += '  dielectric       = ' + str(self.dielec)

        self.model.ConsoleMessage(mess)

    def OnResetCurMol(self,event):
        self.SetTargetMols()
        self.execute = False
        self.rmsfit  = False
        self.update  = False
        self.undo    = False
        self.SetButtonStat()

        self.save_atomcc  = []
        self.opt_atomcc   = None
        self.rms_atomcc   = []
        self.opt_sdftext  = None
        self.opt_mol2text = None

    def SetTargetMols(self):
        self.fumol = self.model.mol
        self.curmolname = self.fumol.name
        #self.targmols   = self.model.molctrl.GetMolNameList()
        #####self.curmolname = self.model.molctrl.GetCurrentMolName()
        self.tcltrg.SetValue(self.curmolname)

    def OnUndo(self,event):
        if not self.update:
            mess = 'Not updated. Can not undo.'
            self.Message(mess)
            return
        self.RecoverCoords()

    def RecoverCoords(self):
        molnam = self.curmolname
        self.fumol.atm = self.fumol.atm[:self.natm_org]
        for i in range(len(self.opt_atoms)):
            ii = self.opt_atoms[i]
            self.fumol.atm[ii].cc = self.save_atomcc[i]

        mess = '\nUndo: Original coordinates were recovered.'
        self.Message(mess)

        self.model.DrawMol(True)

        self.rms_atomcc   = []
        self.undo = True
        self.update = False
        self.execute = False
        self.SetButtonStat()

    def OnUpdateCoords(self,even):
        nopt = len(self.opt_atoms)
        if len(self.opt_atomcc) > 0:
            self.fumol.atm = self.fumol.atm[:self.natm_org]
            for i in range(nopt):
                ii = self.opt_atoms[i]
                self.fumol.atm[ii].cc = self.opt_atomcc[i][1:]
        self.model.DrawMol(True)
        mess = 'Coordinates were updated.'
        self.Message(mess)
        self.update = True
        self.execute = False
        self.SetButtonStat()
        self.btnund.Enable()

    def OnCancel(self,event):
        self.RecoverCoords()
        self.btnund.Enable()

    def RMSFit(self):
        def CCListFromAtomCC(atomcc):
            cclst = []
            for i in range(len(atomcc)):
                cclst.append([atomcc[i][1],atomcc[i][2],atomcc[i][3]])
            return cclst

        cc0 = self.save_atomcc[:]
        cc1 = CCListFromAtomCC(self.opt_atomcc)
        rmsfit = lib.RMSFitCC(self)
        rmsfit.SetCCAndMass(cc0,cc1)
        #
        err,etime,ndat,rmsd,chisq,dcnt,cnt,rot = rmsfit.PerformRMSFit()
        fitcc = lib.ComputeRMSFitCoords(cc1,dcnt,cnt,rot,r2t=True)
        natm = len(fitcc)
        self.rms_atomcc = fitcc[:]
        if err:
            print(('Error in RMS fit: ' + self.curmolname))
            print(('    err',err))
            print(('    rmsd',rmsd))
            print(('    etime',etime))
            return
        #
        self.opt_atomcc = []
        for i in range(len(self.opt_atoms)):
            elm = self.fumol.atm[self.opt_atoms[i]].elm
            elmcc  = [elm,self.rms_atomcc[i][0],self.rms_atomcc[i][1],
                      self.rms_atomcc[i][2]]
            self.opt_atomcc.append(elmcc)

        self.MergeOptAtomsToMol()
        #
        self.rmsfit = True
        self.rmsd = rmsd
        mess  = 'Optimized(yellow) and original coordinates are RMS fitted,\n'
        mess += '    The RMSD(Angstroms) = ' + ('%8.3f' % rmsd)
        self.Message(mess)

    def MergeOptAtomsToMol(self):

        molnam = self.curmolname
        norg = len(self.fumol.atm)
        ngrp,grpdic = self.model.MakeGroupDic(self.fumol.atm)
        newatmdic = {}

        print(('len(opt_atoms)',len(self.opt_atoms)))
        print(('len(fumol.atm)',len(self.fumol.atm)))
        for i in range(len(self.opt_atoms)):
            newatmdic[self.opt_atoms[i]] = i+norg
        cc1  = []
        cc0 = []
        for i in range(len(self.opt_atoms)):
            ii = self.opt_atoms[i]
            atom = molec.Atom(self.fumol)
            atom.seqnmb = norg + i
            atom.elm    = self.fumol.atm[ii].elm
            atom.cc     = self.opt_atomcc[i][1:]
            cc1.append(atom.cc)
            cc0.append(self.fumol.atm[ii].cc)
            atom.atmnmb = atom.seqnmb
            atom.grpnam = 'mrg' + str(ngrp+1)
            atom.SetAtomParams(atom.elm)
            atom.color = [1.0,1.0,0.0,1.0] # yellow
            atom.conect = []
            atom.bndmulti = []
            conect = self.fumol.atm[ii].conect[:]
            # renumber conect data
            ncon = len(conect)
            for j in range(ncon):
                if conect[j] in newatmdic:
                    jj = newatmdic[conect[j]]
                    atom.conect.append(jj)
                    try: atom.bndmulti.append(self.fumol.atm[ii].bndmulti[j])
                    except: atom.bndmulti.append(1)
            self.fumol.atm.append(atom)

        rmsd = lib.ComputeRMSD(cc0,cc1)
        #
        self.model.DrawMol(True)
        return rmsd

    def OnExec(self,event):
        self.btnund.Enable()
        ff = self.cmbff.GetStringSelection()
        method = self.cmbmet.GetStringSelection()
        try:
            ene_conv  = float(self.tclcnv.GetValue())
            max_steps = int(self.tclstp.GetValue())
        except:
            mess = 'Wrong input in "energy conv:" or "max. steps:"'
            return
        natm = len(self.fumol.atm)
        self.natm_org = natm
        optall = self.optall.GetValue()
        if not optall:
            #mess = 'Sorry, partial minimization is under development'
            #wx.MessageBox(mess,'MMMinimizer.OnExec')
            #return
            nsel,self.opt_atoms = self.model.ListSelectedAtom()
            if nsel <= 0:
                mess = 'No atoms are selected for optmization'
                wx.MessageBox(mess,'MMMinimizer.OnExec')
                return
        else: self.opt_atoms = list(range(natm))

        self.model.mdlwin.BusyIndicator('On','MMMinimization ...')

        coords_form = self.coords_form
        targetlst = [self.curmolname]  # restriced to one target in MolMinimize

        if optall:
            self.OBMinimizer0(targetlst,ff,method,ene_conv,
                             max_steps,coords_form)
        else:
            #mess = 'Sorry, not implemented. 30OCT2017'
            #wx.MessageBox(mess,'MMMinimizer.OnExec')
            #return
            self.OBMinimizer1(targetlst,ff,method,ene_conv,
                             max_steps,coords_form)
        """
        # RDkit minimizer needs tests
        self.RDMinimizer(targetlst,ff,method,ene_conv,
                         max_steps,coords_form)
        """
        if self.ckbrms.GetValue(): self.RMSFit()
        else:
            self.rmsd = self.MergeOptAtomsToMol()
            mess  = 'Optimized(yellow) and original structures are overlayed.\n'
            mess += '    The RMSD(Angstroms) = ' + ('%8.3f' % self.rmsd)
            self.Message(mess)

        self.model.mdlwin.BusyIndicator('Off','MMMinimization ...')

        self.execute = True
        self.SetButtonStat()
        boxname='messbox_MMMinimizer'
        if self.model.setctrl.GetParam(boxname):
            mess  = 'The minimized structure is overwritten in yellow.'
            mess += ' Please hit the "Update"(accept) or "Cancel"(not accept)'
            mess += ' button.'
            title='MMMinimizer.OnExec'
            subwin.MessageBox_Frm(self,title='MMMinimizer.OnExec',message=mess,
                                  boxname=boxname,boxkind='Info')
            #wx.MessageBox(mess,title)

    def SetButtonStat(self):
        if self.execute:
           self.btncan.Enable()
           self.btncod.Enable()
           self.btnund.Disable()
           self.btnexe.Disable()
        else:
           self.btncan.Disable()
           self.btncod.Disable()
           self.btnund.Disable()
           self.btnexe.Enable()

    def RDMolFromFUMol(self,fumol,sanitize=False,removeHs=False):
        sdfstring = fumol.WriteSDFMol(None)
        rdmol = Chem.MolFromMolBlock(sdfstring,sanitize=sanitize,
                                     removeHs=removeHs)
        return rdmol

    def RDMinimizer(self,targetlst,ffield,method,ene_conv=0.1,max_steps=100,
                    coords_form='atomcc',prtopt=True,prtcc=False):
        """ not used

        :param str coords_form: 'atomcc','sdf' or 'mol2'
        """
        # save atomcc for undo
        name = self.fumol.name
        self.save_atomcc = []
        for atom in self.fumol.atm: self.save_atomcc.append(atom.cc)
        #
        rdmol = self.RDMolFromFUMol(self.fumol)
        AllChem.EmbedMolecule(rdmol)
        if ffield == 'UFF' or ffield == 'uff':
            ff = AllChem.UFFGetMoleculeForceField(rdmol)
        elif ffield == 'MMFF94' or ffield == 'mmff94':
            ff = AllChem.MMFFGetMoleculeForceField(rdmol)
        else:
            mess = 'Unknown forcefiled in RDkit =' + ffiled

        ff.Initialize()
        inienergy = ff.CalcEnergy()
        print(('inienerg=',inienergy))
        print(('maxsteps=',max_steps))
        print(('conv=',ene_conv))
        retcode = ff.Minimize(maxIts=max_steps,energyTol=ene_conv)

        ffenergy = ff.CalcEnergy()

        if retcode == 0:
            mess='Molecule "'+name+'" is optimized by '+ ffield +'\n'
        else:
            mess='Molecule "'+name+'" is not fully optimized by '
            mess=mess+ffield+'\n'
        mess=mess+'final energy(kcal/mol)='+str(ffenergy)+'\n'
        mess=mess+'energy decrease(kcal/mol)='+str(ffenergy-inienerg)
        self.ConsoleMessage(mess)

        opt_sdfstring = Chem.MolToMolBlock(rdmol)
        info,atomcc,conlst,typlst,sdfdata = \
                      lib.AtomCCFromSDFText(opt_sdfstring)

        self.opt_atomcc = atomcc[:]

        etime = 0
        #
        #if retcode != 0:
        #    ff10 = '%12.6f'
        #    mess += ': minimization failed \n'
        #    mess += '    elapsed time(sec) = ' + (ff10 % etime).strip() + '\n'
        #    self.Message(mess)
        #else:
        if prtcc: atomcoord = self.opt_atomcc
        else:     atomcoord = None
        if prtopt: self.PrintMinimize('RDKit',method,ffield,ene_conv,
                                      max_steps,
                                      self.curmolname,inienrgy,ffenergy,
                                      etime,atomcoord=atomcoord)

    """ needs tests and generalization """
    def OBMinimizer1(self,targetlst,ff,method,ene_conv=0.1,max_steps=100,
                    coords_form='atomcc',prtopt=True,prtcc=False):
        """

        :param str coords_form: 'atomcc','sdf' or 'mol2'
        """
        # save atomcc for undo
        self.save_atomcc = []
        molname = self.fumol.name
        natm = len(self.fumol.atm)
        nopt = len(self.opt_atoms)
        for i in range(nopt): #atom in self.fumol.atm:
            ii = self.opt_atoms[i]
            self.save_atomcc.append(self.fumol.atm[ii].cc)
        # fumol to obmol
        obmol = FUToOBMol(self.fumol)
        obmol = obmol.OBMol
        #
        obff=openbabel.OBForceField.FindForceField("UFF")
        obff.SetLogLevel(openbabel.OBFF_LOGLVL_LOW)
        scrpath = self.model.setctrl.GetDir('Scratch')
        logfile = molname + '-' + ff + '-opt.log'
        self.logfile = os.path.join(scrpath,logfile)
        if self.filed is None:
            if os.path.exists(self.logfile):
                fd = os.open(self.logfile, os.O_WRONLY|os.O_APPEND) #os.O_CREAT)
                os.lseek(fd,0,2)
            else: fd = os.open(self.logfile, os.O_WRONLY|os.O_CREAT)
            os.dup2(fd, 1) #sys.stdout.fileno())
            self.filed = fd
        ###print 'filed',self.filed
        if self.filed is not None: os.lseek(self.filed,0,2)
        #ys.stdout = open(self.logfile,'w')
        obff.SetLogToStdOut()
        # set atom group
        start_time = time.clock()
        constrains=openbabel.OBFFConstraints()
        optgroup = openbabel.OBBitVec()
        fixgroup = openbabel.OBBitVec()
        for i in range(natm):
            if i in self.opt_atoms: optgroup.SetBitOn(i+1)
            else:
                fixgroup.SetBitOn(i+1)
                constrains.AddAtomConstraint(i+1)
        firstcc = self.fumol.atm[self.opt_atoms[0]].cc
        # set interaction
        obff.AddIntraGroup(optgroup)
        obff.AddInterGroup(optgroup)
        obff.AddInterGroups(optgroup,fixgroup)
        #
        obff.Setup(obmol,constrains)
        #####obff.UpdateCoordinates(obmol)
        inienergy = obff.Energy()
        #
        obff.ConjugateGradients(500)
        obff.UpdateCoordinates(obmol)

        # obmol to fumol
        atomcc = GetOBAtomCC(obmol,type='OBMol')
        self.opt_atomcc = []
        for i in range(len(self.opt_atoms)):
            ii = self.opt_atoms[i]
            self.opt_atomcc.append(atomcc[ii])
        ###self.fumol = UpdateFUMolCoords(self.fumol,self.opt_atomcc,conect=None)
        #
        ffenergy = obff.Energy()
        end_time = time.clock()
        etime = end_time - start_time
        #
        optout = False
        if optout == 'failed':
            ff12 = '%12.6f'
            mess += ': minimization failed \n'
            mess += '    elapsed time(sec) = ' + (ff12 % etime).strip() + '\n'
            self.Message(mess)
        else:
            if prtcc: atomcoord = self.opt_atomcc
            else:     atomcoord = None
            if prtopt: self.PrintMinimize('OpenBabel partial',method,
                                          ff,ene_conv,max_steps,
                                          self.curmolname,inienergy,ffenergy,
                                          etime,opt_atoms=[self.opt_atoms,natm],
                                          atomcoord=atomcoord)


    def OBMinimizer0(self,targetlst,ff,method,ene_conv=0.1,max_steps=100,
                    coords_form='atomcc',prtopt=True,prtcc=False):
        """

        :param str coords_form: 'atomcc','sdf' or 'mol2'
        """
        # save atomcc for undo
        self.save_atomcc = []
        for atom in self.fumol.atm: self.save_atomcc.append(atom.cc)
        molname = self.fumol.name

        #
        natm = len(self.fumol.atm)
        self.opt_atoms = list(range(natm))
        obmin = OBMinimizer(self,self.model)
        obmin.SetCoordsFrom(coords_form)
        obmin.SetTargetMols(targetlst)
        obmin.SetForceField(ff)
        obmin.SetMethod(method)
        obmin.SetEneConv(ene_conv)
        obmin.SetMaxSteps(max_steps)
        scrpath = self.model.setctrl.GetDir('Scratch')
        logfile = molname +'-' + ff + '-opt.log'
        self.logfile = os.path.join(scrpath,logfile)
        ###print 'logfile',self.logfile
        obmin.SetLogFile(self.logfile)
        # perform minimization
        obmin.Minimize()
        # get results. taget mols are always one in Mol_minimize
        if coords_form == 'atomcc':
            atomcc = obmin.GetOptCoords()[0]
            optout = atomcc
            #if prtopt:
            #    molnam = targetlst[i]
            #    PrintAtomCC(opt_atomcc,self.curmolname)
        elif coords_form == 'sdf':
            self.opt_sdftext = obmin.GetOptCoords()[0]
            optout = self.opt_sdftext
            info,atomcc,conlst,typlst,sdfdata = \
                          lib.AtomCCFromSDFText(self.opt_sdftext)
            if prt: print((self.opt_sdftext))
        elif coords_form == 'mol2':
            self.opt_mol2text = obmin.GetOptCoords()[0]
            optout = self.opt_mol2text
            info,atomcc,atomattr,conlst,typlst,mol2data = \
                        lib.AtomCCFromMOL2Text(self.opt_mol2text)
            if prt: print((self.opt_mol2text))
        self.opt_atomcc = atomcc[:]
        #
        ffenergy = obmin.GetFFEnergy()[0]
        inienergy = obmin.GetIniEnergy()[0]

        etime = obmin.GetTimes()[0]
        #
        if optout == 'failed':
            ff12 = '%12.6f'
            mess += ': minimization failed \n'
            mess += '    elapsed time(sec) = ' + (ff12 % etime).strip() + '\n'
            self.Message(mess)
        else:
            if prtcc: atomcoord = self.opt_atomcc
            else:     atomcoord = None
            if prtopt: self.PrintMinimize('OpenBabel',method,ff,ene_conv,
                                          max_steps,
                                          self.curmolname,inienergy,ffenergy,
                                          etime,opt_atoms=[self.opt_atoms,natm],
                                          atomcoord=atomcoord)
        #sys.stdout = os.fdopen(fd, 'w', 1)


    def PrintMinimize(self,prog,method,ff,ene_conv,max_steps,molname,
                      inienergy,ffenergy,etime,opt_atoms=None,atomcoord=None):
        """

        param lst opt_atoms: [opt_atoms list,number of total atoms]
        """
        ff12 = '%12.6f'; ff10 = '%10.3f'
        if opt_atoms is not None:
            optatoms = opt_atoms[0]
            optatoms = [x+1 for x in optatoms]
            tatoms   = str(opt_atoms[1])
            soptatoms = str(len(optatoms)) + '/' + tatoms + ' ('
            soptatoms += lib.IntegersToString(optatoms) + ')'
        mess = '\n' + prog + ' Minimizer:\n'
        #self.Message(mess)
        mess += '    method         = ' + method + '\n'
        mess += '    forcefield     = ' + ff + '\n'
        mess += '    energy conv    = ' + str(ene_conv) + '\n'
        mess += '    max.steps      = ' + str(max_steps) + '\n'
        ttime = 0
        mess += '    molecule       = '  + molname + '\n'
        if opt_atoms is not None:
            mess += '    optimize atoms = '  + soptatoms + '\n'
        mess += '    initial energy = ' + (ff12 % inienergy).strip() + '\n'
        mess += '    final energy   = ' + (ff12 % ffenergy).strip() + '\n'
        mess += '    elapsed time(sec) = ' + (ff12 % etime).strip() + '\n'
        #self.Message(mess)
        #etime = elapsed_timelst[0]
        if atomcoord is not None:
            atomcc = atomcoord
            mess += '\nOptimized coordinates(Angs.)\n'
            for i in range(len(atomcc)):
                mess += '%6d' % (i+1) + ' ' + str(atomcc[i][0])
                mess += ff10 % atomcc[i][1]
                mess += ff10 % atomcc[i][2]
                mess += ff10 % atomcc[i][3] +'\n'
        self.Message(mess)

    def Message(self,mess):
        self.model.ConsoleMessage(mess)

    def OnNotify(self,event):
        try: item=event.message
        except: return
        if item == 'SwitchMol' or item == 'OpenFiles':
            self.SetTargetMols()
            mess = 'MMMinimizer: Current molecule is reset'
            self.Message(mess)

    def OnClose(self,event):
        try: sys.stdout = sys.__stdout__
        except: pass

        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        #
        try: self.Destroy()
        except: pass

    def HelpDocument(self):
        helpname = 'MMMinimizer'
        self.model.helpctrl.Help(helpname)

    def HelpNote(self):
        text = ''
        text += '1. To disable the "Update MessageBox" as default,\n'
        text += '   add "fum.setctrl.SetParam("messbox_MMMinimizer",False)"\n'
        text += '   in "FUDATASET/fumodelset.py"'
        title='MMMinimizer note'
        win=subwin.TextViewer_Frm(self,winsize=[450,120],
                                  title=title,text=text)

    def ViewLog(self):
        winpos = self.GetPosition()
        winsize = [600,400]
        title = 'MMMinimizer log'

        ###print 'logfile',self.logfile

        f = open(self.logfile,'r')
        text = f.read()
        f.close()
        subwin.TextEditor_Frm(self,-1,winpos,winsize,title,text,mode='View')

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        #submenu.Append(-1,"Recover coords", "Delete merged atoms")
        submenu.Append(-1,'Enable/disable MessageBox', "Enabel MessageBox")

        submenu.Append(-1,"Close", "Close mol minimizer")

        menubar.Append(submenu,"File")
        #submenu=wx.Menu()
        #submenu.Append(-1,"View log", "View log")
        #menubar.Append(submenu,"Edit")
        # Params
        #submenu=wx.Menu()
        #submenu.Append(-1,"Change params","change params")
        #menubar.Append(submenu,"Option")
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Note','Note')
        submenu.Append(-1,'Document','Help document')
        menubar.Append(submenu,'Help')

        return menubar

    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        menuitem=self.menubar.FindItemById(menuid)
        item=menuitem.GetItemLabel()

        if item == "Close": self.OnClose(1)
        elif item == 'Enable/disable MessageBox':
            if self.model.setctrl.GetParam("messbox_MMMinimizer"):
                value = False
                mess = '\n"messbox_MMMinimizer" is disabled'
            else:
                value = True
                mess = '\n"messbox_MMMinimizer" is enabled'
            self.model.setctrl.SetParam("messbox_MMMinimizer",value)
            self.ConsoleMessage(mess)
        #elif item == "Recover coords": self.RecoverCoords()
        #elif item == "Change params":
        #    self.ConsoleMessage('Entered in menu')
        #    self.ChangeOpenBabelParams()
        # Edit
        elif item == "View log": self.ViewLog()

        elif item == "Note":     self.HelpNote()
        elif item == "Document": self.HelpDocument()

    def ConsoleMessage(self,mess):
        self.model.ConsoleMessage(mess)

    def ChangeOpenBabelParams(self):
        # default values
        mess = 'Enter param_name = value, separated by a comma.\n'
        mess += 'current values are,\n'
        mess += '   ffname=' + self.ffname + ', '
        mess += 'method=' + self.optmethod + ', '
        mess += 'max_steps=' + str(self.max_steps) + ', '
        mess += 'ene_conv=' + str(self.ene_conv)
        #
        title = 'Change OpenBabel params for minimization'
        text = wx.GetTextFromUser(mess,title)
        if len(text.strip()) <= 0: return
        #
        textlst = lib.SplitStringAtSeparator(text,',')
        for s in textlst:
            var,value = lib.GetKeyAndValue(s)
            #print 'var,value',var,value
            if var == 'ffname':
                self.cmbff.SetStringSelection(value)
            elif var == 'method':
                self.cmbmet.SetStringSelection(value)
            elif var == 'max_steps':
                try:
                    self.tclstp.SetValue(int(value))
                except:
                    mess = 'Wrong input for max_steps(int)\n. Unchaged the value.'
                    self.ConsoleMessage(mess)
            elif var == 'ene_conv':
                try:
                    self.tclcnv.SetValue(float(value))
                except:
                    mess = 'Wrong input for crit(float)\n. Unchaged the value.'
                    self.ConsoleMessage(mess)
            else:
                mess = 'Unknown param name = ' + var + '\n'
                mess += 'Ignored'
                self.ConsoleMessage(mess)
        mess  = 'Params of OpenBabel minimization have changed to \n'
        mess += text + ' (except input errors)'
        self.ConsoleMessage(mess)
        #

    def XXChangeOpenBabelParams(self):
        self.ready = True
        forcefield = self.setctrl.GetParam('ob_forcefield')
        method     = self.setctrl.GetParam('ob_opt_method')
        max_steps  = self.setctrl.GetParam('ob_opt_max_steps')
        crit       = self.setctrl.GetParam('ob_opt_crit')
        # default values
        mess = 'Enter param_name = value, separated by a comma.\n'
        mess += 'current values are,\n'
        mess += '   forcefield=' + forcefield + ', '
        mess += 'method=' + method + ', '
        mess += 'max_steps=' + str(max_steps) + ', '
        mess += 'crit=' + str(crit)
        #
        title = 'Change OpenBabel params for minimization'
        text = wx.GetTextFromUser(mess,title)
        if len(text.strip()) <= 0: return
        #
        textlst = lib.SplitStringAtSeparator(text,',')
        for s in textlst:
            var,value = lib.GetKeyAndValue(s)
            #print 'var,value',var,value
            if var == 'forcefiled':
                self.setctrl.SetParam('ob_forcefield',value)
                self.ffname = value
            elif var == 'method':
                self.setctrl.SetParam('ob_opt_method',value)
                self.optmethod = value
            elif var == 'max_steps':
                try:
                    self.setctrl.SetParam('ob_opt_max_steps',int(value))
                    self.max_steps = int(value)
                except:
                    mess = 'Wrong input for max_steps(int)\n. Unchaged the value.'
                    self.ConsoleMessage(mess)
            elif var == 'crit':
                try:
                    self.setctrl.SetParam('ob_opt_crit',float(value))
                    self.ene_conv   = float(value)
                except:
                    mess = 'Wrong input for crit(float)\n. Unchaged the value.'
                    self.ConsoleMessage(mess)
            else:
                mess = 'Unknown param name = ' + var + '\n'
                mess += 'Ignored'
                self.ConsoleMessage(mess)
        mess  = 'Params of OpenBabel minimization have changed to \n'
        mess += text + ' (except input errors)'
        self.ConsoleMessage(mess)
        #


""" test main """
"""
filename = "e://ATEST//mono_results//opv_mols.mol2"
dirnam   = "e://ATEST//scratch"
SplitMOL2File(filename,dirnam)

filename = "e://ATEST//mono_results//opv_mols.sdf"
dirnam   = "e://ATEST//scratch"
SplitSDFFile(filename,dirnam)
"""

#!/bin/sh
# -*- coding: utf-8 -*-
#
#!/bin/sh
# -*- coding: utf-8 -*-



import os
import sys
import time
import wx

import subprocess

sys.path.insert(0,'..//')
import fumodel
import fu_molec as molec
import const
import lib

import PIL

try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    from rdkit.Chem import AllChem
    rdkit_ready = True
except: rdkit_ready = False

try:
    import openbabel
    openbabel_ready = True
except: pass

try:
    import pybel
    pybel_ready = True
except: 
    pass

def ReadyPybel():
    return pybel_ready

def ReadyRDKit():
    return rdkit_ready

def OBAddHsAndMinimize(inpfile,FF='UFF',max_steps=200,crit=0.01):
    """ inpfile should be the output file of GenTautomers """
    ff = openbabel.OBForceField.FindForceField(FF)
    mols = []
    enelst = []
    imol = 0
    for mol in pybel.readfile('sdf',inpfile):
        imol += 1
        mol.addh()
        success = ff.Setup(mol.OBMol)
        if not success:
            mess ='OBAddHsAndMinimize: Failed to set up forcefield for mol = '
            mess += str(imol)
            print (mess)
            continue
        ff.SteepestDescent(max_steps,crit)
        ff.GetCoordinates(mol.OBMol)
        ffenergy = ff.Energy()
        enelst.append(ffenergy)
        mols.append(mol)
    return mols,enelst

def RDAddHsAndMinimize(inpfile,FF='uff',max_steps=200):
    """ inpfile should be the output file of GenTautomers """
    mols = [Chem.AddHs(m,addCoords=True) for m in Chem.SDMolSupplier(inpfile)]
    enelst = []
    #FF='UFF'
    #max_steps = 200
    if FF.lower() == 'mmff94': prop = AllChem.MMFFGetMoleculeProperties(mols[0])
    for m in mols:
        if FF.lower() == 'uff': ff = AllChem.UFFGetMoleculeForceField(m)
        else:                   ff = AllChem.MMFFGetMoleculeForceField(m,prop)
        ff.Minimize(maxIts=max_steps)
        e = ff.CalcEnergy()
        enelst.append(e)
    return mols,enelst

def AtomDataFromRDMol(rdmol):
    def AtomCC():
        """ Make atom data """
        atomcc = []
        atoms  = rdmol.GetAtoms()
        natm   = rdmol.GetNumAtoms()
        atoms  = rdmol.GetAtoms()
        confs  = rdmol.GetConformers()
        for i in range(natm):
            pos = rdmol.GetConformer(0).GetAtomPosition(i)
            elm = atoms[i].GetSymbol()
            elm = elm.strip()
            if len(elm) <= 1: elm = ' ' + elm
            elm = elm.upper()
            atomcc.append([elm,pos.x,pos.y,pos.z])
        return atomcc

    def SetBonds():
        """ Make bond data """
        bndlst  = []
        bndtype = {'SINGLE':1,'DOUBLE':2,'TRIPLE':3,'AROMATIC':4}
        bonds   = rdmol.GetBonds()
        nbnd    = rdmol.GetNumBonds()
        for i in range(nbnd):
            iat   = bonds[i].GetBeginAtomIdx()
            jat   = bonds[i].GetEndAtomIdx()
            btype = str(bonds[i].GetBondType())
            bndlst.append([iat,jat,btype])
        return bndlst

    name = rdmol.GetProp("_Name")
    #
    atomcc = AtomCC()
    #
    bndlst = BondList()
    #
    return name,atomcc,bndlst


def OBWriteSDF(mols,outfile,overwrite=True):
    """ """
    # write SD file
    f = pybel.Outputfile('sdf',outfile,overwrite=overwrite)
    for m in mols: f.write(m)
    f.close()

def RDWriteSDF(mols,outfile):
    """ """
    # write SD file
    f = Chem.SDWriter(outfile)
    for m in mols: f.write(m)

def OBWritePNG(mols,pngfile,overwrite=True):
    #f = pybel.Outputfile('svg',pngfile,overwrite=overwrite)
    for mol in mols:
        moltmp = pybel.readstring('smi',mol.write('smi'))
        moltmp.write('bmp',pngfile,overwrite=overwrite)
    #f.close()

def RDWritePNG(mols,pngfile,perRow=4,imgSize=(200,200),legends=None):
    p = mols[0]
    subms = [x for x in mols if x.HasSubstructMatch(p)]
    AllChem.Compute2DCoords(p)
    for m in subms: AllChem.GenerateDepictionMatching2DStructure(m,p)
    drwmols = subms
    if len(mols) != len(subms): drwmols = mols
    if legends is None: titles = legends
    else: titles = [x.GetProp("_Name") for x in drwmols]
    img=Draw.MolsToGridImage(drwmols,molsPerRow=perRow,subImgSize=imgSize,
                             legends=titles)
    img.save(pngfile)

def OBMolToFUMol(obmol,i):
    form = 'sdf' # 'mol2'
    sdfstring = obmol.write(form)
    print(('sdfstring',sdfstring))
    propdic = obmol.data

    print(('procdic',propdic))

    fumol = molec.Molecule(None,None,None) #Message,Message)
    fumol.SetAtomsFromText(form,sdfstring)
    fumol.name = propdic['TAUTOMER_RANK']
    fumol.name = 'tautomer-'+str(i) #rdmol.title
    fumol.inpfile = 'gen_tautomers'
    return fumol

def RDMolToFUMol(rdmol,i):
    """

    :param int i: isomer number, when no isomers generated, this is 0
    """
    form = 'sdf' # 'mol2'
    writer = Chem.SDWriter(outfile)

    print(('mol.GetPropsAsDict',rdmol.GetPropsAsDict()))
    propdic = rdmol.GetPropsAsDict()

    sdfstring = writer.GetText(rdmol)

    print(('sdfstring',sdfstring))

    fumol = molec.Molecule(None,None,None) #Message,Message)
    fumol.SetAtomsFromText(form,sdfstring)
    fumol.name = propdic['TAUTOMER_RANK']
    fumol.name = 'tautomer-'+str(i) #rdmol.title
    fumol.inpfile = 'gen_tautomers'
    return fumol

def RDMolFromFUMol(fumol,sanitize=False,removeHs=False):
    sdfstring = fumol.WriteSDFMol(None)
    rdmol = Chem.MolFromMolBlock(sdfstring,sanitize=sanitize,
                                 removeHs=removeHs)
    return rdmol

class ChemInfoTools_Frm(wx.Frame):
    def __init__(self,parent,id,winpos=[50,30],winlabel='ChemInfoTools'):
        self.title = 'ChemInfoTools'
        self.parent = parent
        if len(winpos) <= 0: winpos=(-1,-1)
        winsize = (100,240)
        self.winsize=winsize
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.STAY_ON_TOP)

        self.model = parent
        self.winlabel = winlabel

        self.SetBackgroundColour([185,125,85]) #[64,128,128])

        self.winlabel = winlabel
        self.helpname = winlabel

        # Create Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        self.Bind(wx.EVT_MENU,self.OnMenu)

        # Panel layout
        self.cmdbutton_names = ['Modeling','Frag/React','Analysis',
                                'Compute','DBSearch','DBAccess','Misc',]
        self.cmdwindic = {'Modeling'   : [Modeling_Pan,[560,220]],
                          'Frag/React' : [Reaction_Pan,[560,300]],
                          'Analysis'   : [Analysis_Pan,[640,220]],
                          'Compute'    : [Compute_Pan,[640,250]],
                          'DBSearch'   : [DBSearch_Pan,[640,250]],
                          'DBAccess'   : [DBAccess_Pan,[640,250]],
                          'Misc'       : [Misc_Pan,[640,220]]   }

         # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 25
        # work objects
        #self.frm = None
        self.drw = None
        self.mdl = None
        self.frg = None
        self.anl = None
        self.tol = None
        self.cmp = None
        self.dbs = None
        self.dba = None


        self.CreateButtons()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.Show()

    def CreateButtons(self):
        [w,h] = self.GetClientSize()
        # command buttoms
        xloc = 20
        yloc = 10
        xsize = 90
        hbtn = 20
        for i in range(len(self.cmdbutton_names)):
            label = self.cmdbutton_names[i]
            btn = wx.ToggleButton(self,-1,self.cmdbutton_names[i],
                                  pos=(xloc,yloc),size=(xsize,hbtn))
            btn.Bind(wx.EVT_TOGGLEBUTTON,self.OnCmdButton)
            mess = 'Toggle button to open ' + self.cmdbutton_names[i]
            mess += ' panel.'
            #btn.SetToolTipString(mess)
            lib.SetTipString(btn,mess)
            yloc += 25

    def OnCmdButton(self,event):
        obj = event.GetEventObject()
        label = obj.GetLabel()

        parpos = self.parent.GetPosition()
        parsize = self.parent.GetSize()
        #if self.panpos is None:
            #xpos = parpos[0]; ypos = parpos[1] + parsize[1]
        xpos = parpos[0] + parsize[0]; ypos = parpos[1]
        panpos = [xpos,ypos]
        pansize = [560,220]
        #else: panpos = self.panpos
        #pansize = self.pansize # self.panel.GetClientSize()
        pansize = self.cmdwindic[label][1]
        win = self.cmdwindic[label][0](self,panpos=panpos,pansize=pansize)
        self.model.winctrl.SetOpenWin(label,win)

    def OnClose(self,event):
        """ make ini file before exit"""
        try: self.model.winctrl.Close(self.winlabel)
        except: self.Destroy()

    def HelpDocument(self):
        mess = 'Sorry, not implemented'
        wx.MessageBox(mess,'HelpDocument')

    def ConsoleMessage(self,mess):
        self.model.ConsoleMessage(mess)

    def CloseAllPanels(self):
        mess = 'Sorry, not implemented'
        wx.MessageBox(mess,'CloseAllPanels')


    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)

        if item == "Close":
            self.OnClose(1)
        elif item == 'Close all panels':
            self.CloseAllPanels()
        elif item == 'Document':
            self.HelpDocument()
        elif item == "RDkit API documents":
            webpage = "http://rdkit.org/docs/api/module-tree.html"
            moldev_lib.ViewHtmlFile(webpage)
        elif item == "RDkit documentation":
            webpage = "http://www.rdkit.org/docs/index.html"
            lib.ViewHtmlFile(webpage)

        elif item == "OB Python documentation":
            webpage = "http://openbabel.org/docs/current/UseTheLibrary/Python.html"
            lib.ViewHtmlFile(webpage)
        elif item == "Pybel":
            webpage = "http://openbabel.org/docs/current/UseTheLibrary/Python_Pybel.html#pybel-module"
            lib.ViewHtmlFile(webpage)
        elif item == "Openbabel":
            webpage = "http://openbabel.org/docs/current/UseTheLibrary/PythonDoc.html#openbabel-python-module"
            lib.ViewHtmlFile(webpage)

        #
        #elif item == "SQLite document":
        #    #webpage = "http://www.sqlite.org/docs.html"
        #    webpage = "http://www.sqlite.org/lang.html"
        #    moldev_lib.ViewHtmlFile(webpage)
        #elif item == "Python2.7.13/library/sqlite3":
        #    webpage = "https://docs.python.org/2/library/sqlite3.html"
        #    moldev_lib.ViewHtmlFile(webpage)

        elif item == "SMART theory":
            webpage = "http://www.daylight.com/dayhtml/doc/theory/theory.smarts.html"
            lib.ViewHtmlFile(webpage)
        elif item == "SMILE theory":
            webpage = "http://www.daylight.com/dayhtml/doc/theory/theory.smiles.html"
            lib.ViewHtmlFile(webpage)


    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        #File
        submenu=wx.Menu()
        submenu.Append(-1,'Close all panels','Close all panels')
        submenu.AppendSeparator()
        submenu.Append(-1,'Close','Close')
        menubar.Append(submenu,'File')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Document')
        submenu.AppendSeparator()
        """http://www.rdkit.org/docs/Cookbook.html"""
        submenu.Append(-1,'RDkit documentation','RDkit documentation')
        """http://rdkit.org/docs/api/module-tree.html"""
        submenu.Append(-1,'RDkit API documents','RDKit python APIs')
        submenu.AppendSeparator()

        submenu.Append(-1,'OB Python documentation','OB python documents')
        """ http://openbabel.org/docs/current/UseTheLibrary/Python_Pybel.html#pybel-module"""
        submenu.Append(-1,'Pybel','Pybel')
        """ http://openbabel.org/docs/current/UseTheLibrary/PythonDoc.html#openbabel-python-module"""
        submenu.Append(-1,'Openbabel','Openbabel')
        submenu.AppendSeparator()
        submenu.Append(-1,"SMILE theory","DAYLIGHT SMART theory")
        submenu.Append(-1,"SMART theory","DAYLIGHT SMART theory")

        menubar.Append(submenu,'Help')

        return menubar

class Modeling_Pan(wx.Frame):
    def __init__(self,parent,panpos=(-1,-1),pansize=(100,100)):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize) #,
        #       style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|\
        #       wx.RESIZE_BORDER|wx.FRAME_FLOAT_ON_PARENT)

        self.SetBackgroundColour('light gray')
        #
        self.parent = parent # Modeling
        self.modelmgr = parent
        #self.frm = parent.parent

        self.SetTitle('Modeling')
        # icon
        #paramobj = params.MolDevParams()
        #self.help_icon = paramobj.Icon_BMP('help')
        # Create Menu
        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)

        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20

        #self.targetlst = ['','Selecteded mol in viewer','']
        ###self.molnamlst = self.frm.datamgr.molnam + ['---','Read file']
        self.molnamlst = ['dummy']
        self.cmdlst=['Create conformers',
                     '---',
                     'MM minimize',
                     'MOPAC minimize'
                     ] #'Make2D model']
        self.viewlst = ['','summary','output file','input file']

        self.target = self.molnamlst[0]
        self.command = self.cmdlst[0]
        self.args = ''



        #
        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()

    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        self.panel = wx.Panel(self,-1,(0,0),(w,h))
        self.panel.SetBackgroundColour('light gray')

        #self.helpbtn = wx.BitmapButton(self.panel,-1,
        #            bitmap=self.modelmgr.help_icon,pos=(w-20,0),size=(20,20))
        #self.helpbtn.Bind(wx.EVT_BUTTON,self.OnHelp)

        hcb = 30; hbt = 25
        # modeling panel
        xloc = 10; yloc = 10

        wx.StaticText(self.panel,-1,"Target molecule",pos=(xloc,yloc+3),
                          size=(100,18))
        xloc += 110

        self.trgcmb = wx.ComboBox(self.panel,-1,'',choices=self.molnamlst, \
                           pos=(xloc,yloc), size=(120,hcb),style=wx.CB_READONLY)
        self.trgcmb.Bind(wx.EVT_COMBOBOX,self.OnTarget) #ControlPanMdl)
        self.trgcmb.SetValue(self.target)
        xloc += 150
        resetbtn = wx.Button(self.panel,-1,"Reset",pos=(xloc,yloc),
                         size=(60,hbt))
        resetbtn.Bind(wx.EVT_BUTTON,self.OnReset)
        #resetbtn.SetToolTipString('Restore input data list for targtes')
        lib.SetTipString(resetbtn,'Restore input data list for targtes')
        """
        trgbtn = wx.Button(self.panel,-1,"Set",pos=(xloc,yloc),
                         size=(40,hbt))
        trgbtn.Bind(wx.EVT_BUTTON,self.OnSetTargetMolecule)
        #trgbtn.SetToolTipString('Get selected molecule in viewer')
        lib.SetTipString(trgbtn,'Get selected molecule in viewer')
        xloc += 50
        wx.StaticText(self.panel,-1,"=",pos=(xloc,yloc+3),
                          size=(10,18))
        """
        """
        xloc += 20
        self.trgtext = wx.StaticText(self.panel,-1,'',pos=(xloc,yloc+3),
                          size=(w-20,18))
        self.trgtext.SetLabel(self.target)
        #self.trgtext.SetBackgroundColour('white')
        """
        yloc += 30
        xloc = 10
        wx.StaticText(self.panel,-1,"Command:",pos=(10,yloc+3),
                          size=(70,18))
        xloc += 70

        self.cmdcmb = wx.ComboBox(self.panel,-1,'',choices=self.cmdlst, \
                           pos=(xloc,yloc), size=(150,hcb),style=wx.CB_READONLY)
        self.cmdcmb.Bind(wx.EVT_COMBOBOX,self.OnOperation) #ControlPanMdl)
        self.cmdcmb.SetValue(self.command)
        xloc += 170
        exebtn = wx.Button(self.panel,-1,"Exec",pos=(xloc,yloc),
                         size=(50,hbt))
        exebtn.Bind(wx.EVT_BUTTON,self.OnCommand)
        #exebtn.SetToolTipString('Execute command')
        lib.SetTipString(exebtn,'Execute command')
        xloc += 80
        st1 = wx.StaticText(self.panel,-1,"View:",pos=(xloc,yloc+3),
                          size=(50,18))
        #st1.SetToolTipString('View input file, output file,... after Exec')
        lib.SetTipString(st1,'View input file, output file,... after Exec')
        xloc += 50
        #logbtn = wx.Button(self.panel,-1,"View log",pos=(xloc,yloc),
        #                 size=(70,hbt))
        #logbtn.Bind(wx.EVT_BUTTON,self.OnViewLog)
        ##logbtn.SetToolTipString('View log')
        #lib.SetTipString(logbtn,'View log')
        viewcmb = wx.ComboBox(self.panel,-1,'',choices=self.viewlst, \
                           pos=(xloc,yloc), size=(90,hcb),style=wx.CB_READONLY)
        viewcmb.Bind(wx.EVT_COMBOBOX,self.OnView) #ControlPanMdl)
        viewcmb.SetValue(self.viewlst[0])

        yloc += 30
        xloc = 80 ; harg = h - yloc - 45; warg = w - 80 - 80 #320
        wx.StaticText(self.panel,-1,"ARGS:",pos=(xloc-50,yloc+3),size=(40,18))
        self.argtcl = wx.TextCtrl(self.panel,-1,'',pos=(xloc,yloc),
                     size=(warg,harg),style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
        self.argtcl.Bind(wx.EVT_RIGHT_DOWN,self.OnArgsPopup)
        self.argtcl.Bind(wx.EVT_TEXT_ENTER ,self.OnARGS)
        if self.args == '': self.SetArgs()
        else: self.argtcl.SetValue(self.args)
        edtbtn = wx.Button(self.panel,-1,"Edit",pos=(xloc+warg+10,yloc+8),
                         size=(50,hbt))
        edtbtn.Bind(wx.EVT_BUTTON,self.OnEditArgs)
        #edtbtn.SetToolTipString('Edit args')
        lib.SetTipString(edtbtn,'Edit args')
        yloc += (harg+10); xloc = 10
        wx.StaticText(self.panel,-1,"Update with MOPAC coords:",
                      pos=(xloc,yloc+3),size=(180,18))
        xloc += 190
        updatebtn = wx.Button(self.panel,-1,"Update",pos=(xloc,yloc),
                         size=(60,hbt))
        updatebtn.Bind(wx.EVT_BUTTON,self.OnUpdateStructure)
        mess ='Update coordinates with optimized one by MOPAC'
        #updatebtn.SetToolTipString(mess)
        lib.SetTipString(updatebtn,mess)
        xloc += 80
        undbtn = wx.Button(self.panel,-1,"Undo",pos=(xloc,yloc),
                         size=(60,hbt))
        undbtn.Bind(wx.EVT_BUTTON,self.OnUndoUpdate)
        #undbtn.SetToolTipString('Undo update')
        lib.SetTipString(undbtn,'Undo update')

    def OnView(self,event):
        obj = event.GetEventObject()
        item = obj.GetStringSelection()
        print(('OnView. item=',item))
        if item == '': return
        elif item == 'input file':
            pass
        elif item == 'output file':
            pass
        elif item == 'summary':
            pass

    def OnReset(self,event):
        self.molnamlst = self.frm.datamgr.molnam + ['---','Read file']
        self.trgcmb.SetItems(self.molnamlst)
        self.target = self.molnamlst[0]
        self.trgcmb.SetStringSelection(self.target)

        self.modelmgr.molconfdic = self.frm.datamgr.GetMolConfDic()

    def OnModelingHelp(self,event):
        print ('OnModelingHelp')

    def XXOnTarget(self,event):
        obj = event.GetEventObject()
        value = obj.GetValue()
        print(('target value',value))
        if value == 'Selecteded mol in viewer':
            selectedmol = self.GetSelectedMoleculeInViewer()
            if selectedmol is None:
                mess = 'Please select(double click) a molecule in Viewer'
                wx.MessageBox(mess,'GetSelectedMoleculeInViewer',
                              wx.OK | wx.ICON_INFORMATION)
                return

            text = str(len(selectedmol))
            self.trgnumtext.SetLabel(text)

    def XXOnSetTargetMolecule(self,event):
        print ('OnSetTargetMolecule')
        self.modelmgr.SetTargetMolecule()

    def OnTarget(self,event):
        print ('OnTarget')
        self.target = self.trgcmb.GetStringSelection()

    def TextTargetMolecule(self,targetmol):
        print ('TextTargetMolecule')
        if targetmol is None: text = ''
        else: text = 2*' ' + targetmol + 2*' '
        self.trgtext.SetLabel(text)


    def OnEditArgs(self,event):
        mess='Sorry, not implemented yet'
        wx.MessageBox(mess)

    def OnArgsPopup(self,event):
        obj=event.GetEventObject()
        cmd_method=self.cmdcmb.GetStringSelection()
        mopac=False
        if cmd_method[:5] == 'MOPAC': mopac=True
        rdkvarvaldic={'FF':['UFF    ','MMFF94  '],
                      'optmethod':['SD   ','CG   '],
                      'outdir':['none','scratch']}
        mopgrvarvaldic={'ham':['AM1','PM3','MINDO/3'],
                        'calctype':['minimize','energy'],
                        'precise':['.t.','.f.'],
                        'geo-ok':['.t.','.f.'],
                        'vectors':['.t.','.f.'],
                        'elepo':['.t.','.f.'],
                        'mulk':['.t.','.f.'],
                        'xyz':['.t.','.f.'] }
        mopexvarvaldic={}

        if cmd_method == 'MOPAC minimize':
            varvaldic=mopgrvarvaldic
        elif cmd_method == 'MOPAC gr.input':
            varvaldic=mopgrvarvaldic
        elif cmd_method == 'MOPAC ex.input':
            varvaldic=mopexvarvaldic

        else:
            varvaldic=rdkvarvaldic

        # print 'OnArgsPopup'
        argstxt=self.argtcl.GetValue()
        self.argvaldic=self.GetArgAndValue(argstxt)
        #print 'argstxt=',argstxt
        #print 'argvaldic',self.argvaldic
        #argpos=self.argtcl.GetPosition()
        pos=wx.GetMousePosition()
        #print 'argpos',argpos
        #print 'pos',pos
        #inspos=self.argtcl.GetInsertionPoint()
        #print 'inspos',inspos
        selpos=self.argtcl.GetSelection()
        #print 'selpos',selpos
        selvar=argstxt[selpos[0]:selpos[1]].strip()

        #print 'selvar',selvar
        #print 'selval[:-1]',selvar[:-1]

        if selvar.endswith('='): selvar=selvar[:-1].strip()
        #print 'selvar',selvar
        vallst=[]
        if selvar in varvaldic:
            vallst=varvaldic[selvar]

        if len(vallst) <= 0: return
        #print 'vallst',vallst
        retmethod=self.ArgsPopupMenu
        label=selvar
        menulst=vallst
        tiplst=[]
        try: self.lbmenu=subwin.ListBoxMenu_Frm(self,-1,[],[],retmethod,
                                               menulst,tiplst,menulabel=label)
        except: pass

    def ArgsPopupMenu(self,item,label):
        #print 'item,label',item,label
        #print 'argvaldic',self.argvaldic
        self.selvar=label.strip()
        self.newval=item.strip()
        if len(self.selvar) > 0 and len(self.newval) > 0:
            self.argvaldic[self.selvar]=self.newval
            text=''
            for var, val in list(self.argvaldic.items()):
                text=text+var.strip()+'='+val.strip()+', '
            text=text[:-2]
            #print 'text',text
            self.argtcl.Clear()
            self.argtcl.SetValue(text)

    def SetArgs(self):
        #cmdlst=['MM minimize','Create conformers','make2D']
        cmd_method=self.cmdcmb.GetStringSelection()
        ###mopac=False
        ###if cmd_method[:5] == 'MOPAC': mopac=True
        text=''
        if cmd_method == 'MM minimize':
            text='FF=UFF, conv=1.0e-3, maxsteps=200'
        elif cmd_method == 'Create conformers':
            text='nconfs=10, FF=UFF, outdir=scratch, outfile=none'
        elif cmd_method == 'Make2D model':
            text=''
        elif cmd_method == 'Save all':
            text="outfile=''"
            mess='Sorry, not implemented yet'
            wx.MessageBox(mess)
        elif cmd_method == 'Save selected':
            selected=self.iconctrl.GetSelectedMols()
            text="outfile=''"
            mess='Sorry, not implemented yet'
            wx.MessageBox(mess)
        # MOPAC7
        elif cmd_method == 'MOPAC minimize':
            text='ham=AM1, calctype=minimize, charge=0, precise=.t.'
            text=text+' geo-ok=.t., vectors=.t., conv=1.0e-2, maxsteps=500'

        elif cmd_method == 'MOPAC gr.input':
            pass

        elif cmd_method == 'MOPAC ex.input':
            pass


        self.argtcl.SetValue(text)

    def OnARGS(self,event):
        self.SetArgs()


    def OnOperation(self,event):
        cmd_method = self.cmdcmb.GetStringSelection()
        if cmd_method[:3] == '---':
            self.command = self.cmdlst[0]
            self.cmdcmb.SetStringSelection(self.command)
            return

        self.SetArgs()


    def OnCommand(self,event):
        #targetmol = self.modelmgr.targetmol
        targetmol = self.trgcmb.GetStringSelection()
        #print 'selected mols',mols
        if targetmol is None or targetmol[:3] == '---':
            mess='No target molecule is selected. Please select a target '
            mess=mess + 'molecule'
            #self.ConSoleMessage(mess)
            wx.MessageBox(mess,'OnCommand')
            return

        mols = [targetmol]
        obj = event.GetEventObject()
        cmd_method = self.cmdcmb.GetStringSelection()
        #print 'cmd_method=',cmd_method
        args = self.argtcl.GetValue()
        #print 'args=',args
        mess='Execute ' + cmd_method + ' args:' + args
        self.modelmgr.ConsoleMessage(mess)
        argdic = self.ArgStringToDic(args)
        #print 'argdic',argdic
        if cmd_method[:3] == '---':
            self.command = self.cmdlst[0]
            self.cmdcmb.SetStringSelection(self.command)
            return
        elif cmd_method == 'MM minimize':
            self.modelmgr.FFMinimize(mols,argdic)
        elif cmd_method == "Create conformers":
            out = 'none'
            if 'outdir' in argdic:
                outdir = argdic['outdir']
                if outdir != 'none':
                    out = 'dir'
            if 'outfile' in argdic:
                outfile = argdic['outfile']
                if outfile != 'none': out = 'file'
            """ does not work! if out != 'none': sdw=Chem.SDWriter(outfile) """
                    #print 'sdwriter',sdw
            ffeneg = self.modelmgr.GenerateConformers(mols,argdic,out,outdir,outfile)


            #self.iconview.UpdateMolDic(self.molnam,self.moldic)



            """
            mess = 'energy=' + str(ffeneg)
            self.modelmgr.ConsoleMessage(mess)
            """
            #if out:
                #sdw.flush()
                #sdw.close()



            #self.iconview.UpdateMolDic(self.molnam,self.moldic)

        elif cmd_method == 'MOPAC minimize':
            #mess='Sorry, not inplemented yet.'
            #wx.MessageBox(mess)
            print(('mols',mols))
            #print 'self.molconfdic',self.molconfdic

            self.modelmgr.MOPACMinimize(mols,argdic)

        elif cmd_method == 'MOPAC gr.input':
            mess='Sorry, not inplemented yet.'
            wx.MessageBox(mess)

        elif cmd_method == 'MOPAC ex.input':
            mess='Sorry, not inplemented yet.'
            wx.MessageBox(mess)
    """
    def MOPACMinimize(self,mols,argdic):
        prg='h://mopac7//MOPAC_7.1.exe'
        dirname='h://mopac7'

        argtext=self.MakeArgsOfMOPAC(argdic)
        argtext='pm3 CHARGE=0 PRECISE GNORM=0.01 XYZ MULLIK FLEPO GEO-OK VECTORS MMOK'

        for name in mols:
            fumol=self.moldic[name][0].fumol
            coordtext=self.MakeCoordOfMOPAC(fumol,'xyz')
            title=name+' minimization'
            text=argtext+'\n'+title+'\n\n'+coordtext
            inpfile=name+'-mopac-opt.dat'
            inpfile=os.path.join(dirname,inpfile)
            f=open(inpfile,'w')
            f.write(text)
            f.close()
            cmd_method='h://mopac7//MOPAC_7.1.exe '+inpfile
            subprocess.call(cmd_method,shell=True)

    def MakeArgsOfMOPAC(self,argdic):
        text=''

        return text

    def MakeCoordOfMOPAC(self,fumol,case='xyz'):
        ff128='%12.8f'; one=' 1 '; blk=3*' '
        text=''
        if case == 'xyz':
            for atom in fumol.atm:
                sx=(ff128 % atom.cc[0])
                sy=(ff128 % atom.cc[1])
                sz=(ff128 % atom.cc[2])
                text=text+atom.elm+blk+sx+one+sy+one+sz+one+'\n'
        return text

    def GenerateConformers(self,mols,argdic,out,outdir,outfile):
        messc='Running Conformer optimizations\n'
        messbox=subwin.Message_Frm(self,-1)
        messbox.SetMessage(messc)
        ffeneg=[]
        for name in mols:
            mol=self.moldic[name][0].rdmol
            nconfs=argdic['nconfs']
            molc=Chem.AddHs(mol)
            confs=AllChem.EmbedMultipleConfs(molc,numConfs=nconfs)
            mess='Number of conformations='+str(len(confs))
            #print 'confs',confs
            self.ConsoleMessage(mess)
            for confid in confs:
                #print 'confid',confid
                if argdic['FF'] == 'UFF':
                    ff=AllChem.UFFGetMoleculeForceField(molc,confId=confid)
                elif argdic['FF'] == 'MMFF94':
                    ff=AllChem.MMFFGetMoleculeForceField(molc,confId=confid)
                ff.Minimize()
                energy=ff.CalcEnergy()

                ffeneg.append(energy)

                cf=Confs(self)
                self.moldic[name].append(cf)
                #idx=len(self.moldic[name])-1
                idx=confid+1
                cfname=str(name+'-'+str(idx))
                molc.SetProp("_Name",cfname)

                self.moldic[name][idx].rdmol=molc
                self.moldic[name][idx].energy=energy
                fumol=self.RDMolToFUMol(molc)
                self.moldic[name][idx].fumol=fumol
                mess='Molecule "'+name+'" is optimized by '+argdic['FF']
                self.ConsoleMessage(mess)
                if out != 'none':
                    filename=name+'-confs.sdf'
                    if outdir == 'scratch':
                        outfile=os.path.join(self.scratch,filename)
                    else:
                        outfile=os.path.join(outdir,filename)

                    sd=Chem.MolToMolBlock(molc,confId=confid)
                    f=open(outfile,'a')
                    f.write(sd)
                    f.write('$$$$\n')
                    f.close()
                    #sdw.write(molc,confid)
                    mess='Conformer-'+str(idx)+' is written on '+outfile
                    self.ConsoleMessage(mess)
                mess=messc+'Done '+str(idx)+' of '+str(len(confs))
                messbox.SetMessage(mess)
        messbox.Close()
        return ffeneg

    def FFMinimize(self,mols,argdic):
        for name in mols:
            mol=self.moldic[name][0].rdmol
            AllChem.EmbedMolecule(mol)
            if argdic['FF'] == 'UFF':
                #AllChem.UFFOptimizeMolecule(mol)
                ff=AllChem.UFFGetMoleculeForceField(mol)
            elif argdic['FF'] == 'MMFF94':
                #AllChem.MMFFOptimizeMolecule(mol)
                ff=AllChem.MMFFGetMoleculeForceField(mol)
            ff.Initialize()
            inienerg=ff.CalcEnergy()
            print 'inienerg=',inienerg
            maxsteps=200; conv=1.0e-6
            if argdic.has_key('conv'): conv=float(argdic['conv'])
            if argdic.has_key('maxsteps'):
                maxsteps=int(argdic['maxsteps'])

            print 'maxsteps=',maxsteps
            print 'conv=',conv
            retcode=ff.Minimize(maxIts=maxsteps,energyTol=conv)
            energy=ff.CalcEnergy()
            self.moldic[name][0].rdmol=mol
            self.moldic[name][0].energy=energy
            fumol=self.RDMolToFUMol(mol)
            self.moldic[name][0].fumol=fumol
            if retcode == 0:
                mess='Molecule "'+name+'" is optimized by '+argdic['FF']+'\n'
            else:
                mess='Molecule "'+name+'" is not fully optimized by '
                mess=mess+argdic['FF']+'\n'
            mess=mess+'final energy(kcal/mol)='+str(energy)+'\n'
            mess=mess+'energy decrease(kcal/mol)='+str(energy-inienerg)
            self.ConsoleMessage(mess)
        self.iconview.UpdateMolDic(self.molnam,self.moldic)

    """
    def ArgStringToDic(self,args):
        argdic={}
        items=args.split(',')
        for keyarg in items:
            key,value=lib.GetKeyAndValue(keyarg)
            argdic[key]=value
        return argdic


    def OnUndoUpdate(self,event):
        mess='Sorry, not inplemented yet.'
        wx.MessageBox(mess)

    def OnUpdateStructure(self,event):
        print ('OnUpdateStructure')
        #mess='Sorry, not inplemented yet.'
        #wx.MessageBox(mess)
        targetmol = self.trgcmb.GetStringSelection()

        if targetmol not in self.modelmgr.mopac_resutls:
            mess = 'No Mopac results of molnam '+ targetmol
            self.modelmgr.Message2(mess)
            return
        mols = [targetmol]
        self.modelmgr.SetMopacCoords(mols)

    def OnViewLog(self,event):
        mess='Sorry, not inplemented yet.'
        wx.MessageBox(mess)

    def OnRDkitCmd(self,event):
        pass



    def XXStatusMessage(self,mess):
        self.parent.SetStatusText(mess)

    def XXMessage(self,mess):
        self.parent.SetStatusText(mess)

    def XXOnPageChanged(self,event):
        messlst=['Make/modify/delete "Setting" script','Make/modify/delete general parameters',
                 'Make/modify/delete model parameters','Make/modify/delete "Add-on" menus',
                 'Define/modify/delete shortcut-key','Make/modify/delete projects']
        if not self.gonewpage: newpage=self.notebook.ChangeSelection(self.prvpage)
        else:
            self.curpage=self.notebook.GetSelection()
            self.StatusMessage(messlst[self.curpage])
            self.pageinslst[self.curpage].Initialize()
            #event.Skip() # may need to work properly ?

    def XXOnPageChanging(self,event):
        self.prvpage=self.curpage
        self.gonewpage=True
        if not self.pageinslst[self.prvpage].IsSaved():
            try:
                prvpage=self.pagenamlst[self.prvpage]
                mess='"'+prvpage+'" is not saved. Are you sure to move?'
            except: mess='previou page is not saved. Are you sure to move?'
            dlg=lib.MessageBoxYesNo(mess,"")
            if not dlg: self.gonewpage=False

    def OnClose(self,event):
        #self.frm.SetValueToButton('Model',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        self.OnMove(1)
        event.Skip()

    def OnMove(self,event):

        self.target = self.trgcmb.GetStringSelection()
        self.command = self.cmdcmb.GetStringSelection()
        self.args = self.argtcl.GetValue()

        self.panel.Destroy()
        self.CreateWidgets()

        try: event.Skip()
        except: pass

    def OnHelp(self,event):
        print ('OnHelp')


    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.modelmgrMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.modelmgrMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.modelmgr.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.modelmgr.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.modelmgr.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.modelmgr.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.modelmgr.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()


class Reaction_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.fragmgr = parent

        self.SetTitle('Fragmentation/Reaction')
        # icon
        #paramobj = params.MolDevParams()
        #self.help_icon = paramobj.Icon_BMP('help')

        # Create Menu
        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)


        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20

        self.fragalgolst = ['Recap','BRICS','Generic']
        self.molnamlst = self.frm.datamgr.molnam + ['---','Read file']
        self.fragsavelst = ['Smart file','sdf file'] #,'Subst group']
        #
        self.fragtarget = self.molnamlst[0]
        self.fragalgo = self.fragalgolst[0]
        self.reactcore = ''
        self.reactwith = ''
        self.sanitize = False
        self.rxnsmarts = ''
        #
        self.CreateWidgets()
        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        #
        self.Show()

    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        self.panel = wx.Panel(self,-1,(0,0),(w,h))
        self.panel.SetBackgroundColour('light gray')
        #
        hcb = 30; hbt = 25
        # help button
        xloc = 10; yloc = 10



        # Fragmentation widgets
        wx.StaticText(self.panel,-1,'Fragmentation      target=',
                                 pos=(xloc,yloc),size=(150,self.htext))
        xloc += 160
        self.fragtrgcmb = wx.ComboBox(self.panel,-1,'',choices=self.molnamlst, \
              pos=(xloc,yloc-2), size=(120,self.hcombo),
              style=wx.CB_READONLY|wx.LB_SINGLE)
        self.fragtrgcmb.SetStringSelection(self.fragtarget)
        self.fragtrgcmb.Bind(wx.EVT_COMBOBOX,self.OnFragTarget)
        xloc += 140
        resetbtn = wx.Button(self.panel,-1,"Reset",pos=(xloc,yloc-2),
                         size=(60,hbt))
        resetbtn.Bind(wx.EVT_BUTTON,self.OnReset)
        #resetbtn.SetToolTipString('Restore input data list for targtes')
        lib.SetTipString(resetbtn,'Restore input data list for targtes')
        yloc += 25; xloc = 20
        wx.StaticText(self.panel,-1,'Algorithm:',pos=(xloc,yloc+2),
                      size=(70,self.htext))
        xloc += 70
        self.fragalgocmb = wx.ComboBox(self.panel,-1,'',choices=self.fragalgolst, \
              pos=(xloc,yloc), size=(70,self.hcombo),
              style=wx.CB_READONLY|wx.LB_SINGLE)
        self.fragalgocmb.SetStringSelection(self.fragalgo)
        self.fragalgocmb.Bind(wx.EVT_COMBOBOX,self.OnFragAlgorithm)
        xloc += 80
        fragbtn = wx.Button(self.panel,-1,'Exec',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        fragbtn.Bind(wx.EVT_BUTTON,self.OnFragmentExec)
        xloc += 70
        self.fragdrawbtn = wx.Button(self.panel,-1,'Draw',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        self.fragdrawbtn.Bind(wx.EVT_BUTTON,self.OnFragmentDraw)
        #self.fragdrawbtn.Disable()
        xloc += 70
        wx.StaticText(self.panel,-1,'Save as:',pos=(xloc,yloc+2),
                      size=(60,self.htext))
        xloc += 60
        self.fragsavecmb = wx.ComboBox(self.panel,-1,'',choices=self.fragsavelst, \
              pos=(xloc,yloc), size=(100,self.hcombo),
              style=wx.CB_READONLY|wx.LB_SINGLE)
        self.fragsavecmb.SetStringSelection(self.fragsavelst[0])
        #self.fragsavecmb.Bind(wx.EVT_COMBOBOX,self.OnFragAlgorithm)
        xloc += 110

        self.fragsavebtn = wx.Button(self.panel,-1,'Save',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        self.fragsavebtn.Bind(wx.EVT_BUTTON,self.OnFragmentSave)

        #self.EnableFragSaveWidgets(False)
        # Raction widgets
        yloc += 30
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,4),style=wx.LI_HORIZONTAL)
        yloc += 10; xloc = 10
        wx.StaticText(self.panel,-1,'Reaction of',
                                 pos=(xloc,yloc),size=(70,self.htext))
        xloc += 80
        self.coretcl = wx.TextCtrl(self.panel,-1,'',pos=(xloc,yloc),
                                   size=(30,20))
        self.coretcl.SetValue(self.reactcore)
        xloc += 40
        wx.StaticText(self.panel,-1,'with',
                                 pos=(xloc,yloc),size=(40,self.htext))
        xloc += 40
        self.withtcl = wx.TextCtrl(self.panel,-1,'',pos=(xloc,yloc),
                                    size=(180,20))
        self.withtcl.SetValue(self.reactwith)

        xloc += 200
        self.sanitackb = wx.CheckBox(self.panel,-1,'Sanitize',pos=(xloc,yloc),
                                size=(70,20))
        self.sanitackb.SetValue(self.sanitize)
        xloc += 80
        self.genrxnbtn = wx.Button(self.panel,-1,'Generate',pos=(xloc,yloc),
                           size=(80,self.hbutton))
        self.genrxnbtn.Bind(wx.EVT_BUTTON,self.OnGenerateReactionSmarts)
        #self.genrxnbtn.SetToolTipString('Generate reaction smarts')
        lib.SetTipString(self.genrxnbtn,'Generate reaction smarts')
        yloc += 30; xloc = 20
        wx.StaticText(self.panel,-1,'Reaction smatrs:',
                                 pos=(xloc,yloc),size=(120,self.htext))
        yloc += 20
        htcl = h - yloc - 40; wtcl = w - 30
        self.rxnsmarttcl = wx.TextCtrl(self.panel,-1,'',pos=(xloc,yloc),
                                    size=(wtcl,htcl))
        self.rxnsmarttcl.SetValue(self.rxnsmarts)
        yloc += (htcl+10) ; xloc = 100
        reactbtn = wx.Button(self.panel,-1,'Exec',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        reactbtn.Bind(wx.EVT_BUTTON,self.OnReactionExec)
        xloc += 70
        self.reactdrawbtn = wx.Button(self.panel,-1,'Draw',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        self.reactdrawbtn.Bind(wx.EVT_BUTTON,self.OnReactionDraw)
        #self.fragdrawbtn.Disable()
        xloc += 70
        wx.StaticText(self.panel,-1,'Save as:',pos=(xloc,yloc+2),
                      size=(60,self.htext))
        xloc += 60
        self.reactsavecmb = wx.ComboBox(self.panel,-1,'',choices=self.fragsavelst, \
              pos=(xloc,yloc), size=(100,self.hcombo),
              style=wx.CB_READONLY|wx.LB_SINGLE)
        self.reactsavecmb.SetStringSelection(self.fragsavelst[0])
        xloc += 110

        self.reactsavebtn = wx.Button(self.panel,-1,'Save',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        self.reactsavebtn.Bind(wx.EVT_BUTTON,self.OnReactionSave)


    def EnableFragSaveWidgets(self,value):
        if value:
            self.fragsavebtn.Enable()
            self.fragsavecmb.Enable()
        else:
            self.fragsavebtn.Disable()
            self.fragsavecmb.Disable()

    def OnReset(self,event):
        self.molnamlst = self.frm.datamgr.molnam + ['---','Read file']
        self.fragtrgcmb.SetItems(self.molnamlst)
        self.fragtarget = self.molnamlst[0]
        self.fragtrgcmb.SetStringSelection(self.fragtarget)

    def OnReactionSave(self,event):
        print ('OnReactionSave')

    def OnReactionDraw(self,event):
        print ('OnReactionDraw')

    def OnReactionExec(self,event):
        print ('OnReactionExec')


    def OnGenerateReactionSmarts(self,event):
        core = self.coretcl.GetValue()
        subst = self.substtcl.GetValue()
        sanitize = self.sanitackb.GetValue()
        # Genarate reaction smarts
        print ('OnGenerateReactionSmarts')
        print(('core,subst,sanitize',core,subst,sanitize))


    def OnFragTarget(self,event):
        obj = event.GetEventObject()
        target = obj.GetStringSelection()
        print(('OnFragTarget. fragtarget=',self.fragtarget))
        if target[:3] == '---':
            self.fragtrgcmb.SetStringSelection(self.molnamlst[0])

    def OnFragmentSave(self,event):
        saveform = self.fragsavecmb.GetStringSelection()
        print(('OnFragamentSave. form=',saveform))


    def OnFragAlgorithm(self,event):
        obj = event.GetEventObject()
        self.fragalgo = obj.GetStringSelection()
        print(('OnFragAlgo. fragalgo',self.fragalgo))


    def OnFragmentExec(self,event):
        fragalgo =self.fragalgocmb.GetStringSelection()
        obj = event.GetEventObject()
        print(('OnFragExec. fragalgo',fragalgo))
        target = self.fragtrgcmb.GetStringSelection()
        if target == 'Read file':
            print ('read file')


        else: pass

        self.fragmgr.DecomposeMolecule(fragalgo,target)


    def OnFragmentDraw(self,event):
        obj = event.GetEventObject()
        print ('OnFragDraw.')


    def OnClose(self,event):
        #self.frm.SetValueToButton('Frag/React',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        self.OnMove(1)
        try: event.Skip()
        except: pass

    def OnMove(self,event):
        self.fragtarget = self.fragtrgcmb.GetStringSelection()
        self.fragalgo = self.fragalgocmb.GetStringSelection()
        self.reactcore = self.coretcl.GetValue()
        self.reactwith = self.withtcl.GetValue()
        self.sanitize = self.sanitackb.GetValue()
        self.rxnsmarts = self.rxnsmarttcl.GetValue()

        self.panel.Destroy()
        self.CreateWidgets()

        try: event.Skip()
        except: pass

    def OnFragReactHelp(self,event):
        print ('OnFragHelp')

    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class Analysis_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.analysismgr = parent

        self.SetTitle('Analysis')
        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)



        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20


        self.cmdlst=['MM minimize','Create conformers','---',
                     'MOPAC minimize','MOPAC gr.input','MOPAC ex.input',
                     '---','Save all','Save slected'] #'Make2D model']

        #self.CreateNotebook()

        self.Show()


        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()


    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        hcb = 30; hbt = 25
        # help button

        # modeling panel
        xloc = 10; yloc = 10

    def OnClose(self,event):
        #self.frm.SetValueToButton('Analysis',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        event.Skip()

    def OnMove(self,event):
        event.Skip()

    def OnAnalysisHelp(self,event):
        print ('OnAnalysisHelp')

    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class Compute_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.computemgr = parent
        #
        self.SetTitle('Compute')
        # Create Menu
        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)



        # icon
        paramobj = params.MolDevParams()
        self.programdic, self.serverdic = paramobj.ComputeParams()
        self.programlst = list(self.programdic.keys())
        self.serverlst = list(self.serverdic.keys())
        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20
        #
        self.datasellst = ['selected','all']


        self.curprogram = None
        self.curserver  = None


        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()


    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        print(('computepansize',w,h))
        # other widgets
        yloc = 10; xloc = 10
        wx.StaticText(self,-1,'Program:',
                                 pos=(xloc,yloc),size=(60,self.htext))
        xloc += 70
        self.prgcmb=wx.ComboBox(self,-1,'',choices=self.programlst, \
              pos=(xloc,yloc), size=(100,self.hcombo))
        self.prgcmb.SetStringSelection(self.programlst[0])
        self.prgcmb.Bind(wx.EVT_COMBOBOX,self.OnProgram)
        xloc += 120
        wx.StaticText(self,-1,'Generate input data for',
                                 pos=(xloc,yloc),size=(130,self.htext))
        xloc += 150
        self.datacmb=wx.ComboBox(self,-1,'',choices=self.datasellst, \
              pos=(xloc,yloc), size=(80,self.hcombo))
        self.datacmb.SetStringSelection(self.datasellst[0])
        self.datacmb.Bind(wx.EVT_COMBOBOX,self.OnTargetData)
        #yloc += 30; xloc = 30
        xloc += 110
        makebtn = wx.Button(self,-1,'Make input data',pos=(xloc,yloc),
                           size=(100,self.hbutton))
        makebtn.Bind(wx.EVT_BUTTON,self.OnMakeInput)



        """
        xloc += 140
        savebtn = wx.Button(self,-1,'Save input data',pos=(xloc,yloc),
                           size=(100,self.hbutton))
        savebtn.Bind(wx.EVT_BUTTON,self.OnSaveInput)
        """


        yloc += 30; xloc = 10
        wx.StaticText(self,-1,'Select server:',
                                 pos=(xloc,yloc),size=(80,self.htext))
        xloc += 90
        self.servercmb=wx.ComboBox(self,-1,'',choices=self.serverlst, \
              pos=(xloc,yloc), size=(130,self.hcombo))
        self.servercmb.SetStringSelection(self.serverlst[0])
        self.servercmb.Bind(wx.EVT_COMBOBOX,self.OnServer)
        xloc += 160
        runbtn = wx.Button(self,-1,'Run',pos=(xloc,yloc),
                           size=(50,self.hbutton))
        runbtn.Bind(wx.EVT_BUTTON,self.OnRun)
        yloc += 30
        wx.StaticLine(self,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)


        yloc += 10; xloc = 10
        #wx.StaticText(self,-1,'Job status:',
        #                         pos=(xloc,yloc),size=(70,self.htext))
        width = w-20; height = h - yloc - 30
        self.CreateStatPanel(xloc,yloc,width,height)

    def CreateStatPanel(self,xloc,yloc,width,height):
        wx.StaticText(self,-1,'Job status:',
                                 pos=(xloc,yloc),size=(70,self.htext))

        xloc += 370
        cancelbtn = wx.Button(self,-1,'Cancel',pos=(xloc,yloc-2),
                           size=(80,self.hbutton))
        cancelbtn.Bind(wx.EVT_BUTTON,self.OnCancel)
        xloc += 100
        viewbtn = wx.Button(self,-1,'View log',pos=(xloc,yloc-2),
                           size=(80,self.hbutton))
        viewbtn.Bind(wx.EVT_BUTTON,self.OnViewLog)


        yloc += 20; xloc = 10
        self.statlc = moldev_lib.CheckListCtrl(self,-1,winpos=(xloc,yloc),
                                 winsize=(width,height),oncheckbox=self.OnCheck)
        self.statlc.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnJobStatus)
        #self.statlc.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.OnListTip)
        self.statlc.InsertColumn(0,'job#',width=50,
                                  format=wx.LIST_FORMAT_RIGHT)
        self.statlc.InsertColumn(1,'program',width=80)
        self.statlc.InsertColumn(2,'input data',width=210)
        self.statlc.InsertColumn(3,'server',width=100)
        self.statlc.InsertColumn(4,'status',width=50)
        self.statlc.InsertColumn(5,'date',width=50)
        self.statlc.InsertColumn(6,'owner',width=50)

    def OnProgram(self,event):
        obj = event.GetEventObject()
        self.curprogram = obj.GetStringSelection()
        print(('curprogram = ',self.curprogram))


    def OnTargetData(self,event):
        obj = event.GetEventObject()
        data = obj.GetStringSelection()

        print(('OnTargetData. data=',data))

    def OnServer(self,event):
        obj = event.GetEventObject()
        server = obj.GetStringSelection()

        print(('OnServer.server=',server))

    def OnMakeInput(self,event):
        print ('onMakeInput')

    def OnSaveInput(self,event):
        print ('OnSaveInput')

    def OnRun(self,event):
        print ('OnRun')

    def OnJobStatus(self,event):
        obj = event.GetEventObject()
        job = obj.GetValue()
        print(('OnJobStatus. job =',job))

    def OnCheck(self,event):
        print ('OnCheck')

    def OnCancel(self,event):
        print ('OnCancel')


    def OnViewLog(self,event):
        print ('OnViewLog')

    def OnHelp(self,event):
        print ('OnHelp')


    def OnClose(self,event):
        #self.frm.SetValueToButton('Compute',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        event.Skip()

    def OnMove(self,event):
        event.Skip()


    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class Misc_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.toolsmgr = parent

        self.SetTitle('Misc')
        # Create Menu
        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)



        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20


        self.cmdlst=['MM minimize','Create conformers','---',
                     'MOPAC minimize','MOPAC gr.input','MOPAC ex.input',
                     '---','Save all','Save slected'] #'Make2D model']

        #self.CreateNotebook()

        self.Show()


        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()


    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        hcb = 30; hbt = 25
        # help button

        # modeling panel
        xloc = 10; yloc = 10

    def OnClose(self,event):
        #self.frm.SetValueToButton('Tools',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        event.Skip()

    def OnMove(self,event):
        event.Skip()


    def OnFragReactHelp(self,event):
        print ('OnFragHelp')

    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class DBSearch_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.dbsearchmgr = parent

        self.SetTitle('Database Search')

        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)

        paramobj = params.MolDevParams()
        #self.help_icon = paramobj.Icon_BMP('help')
        self.mydblst = paramobj.PrivateDatabase()
        self.dblst = []
        for [name,file] in self.mydblst: self.dblst.append(name)
        print(('dblst',self.dblst))

        self.hitsetlst = []

        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20

        self.curdb = None
        self.curset = None

        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()


    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        hcb = 30; hbt = 25
        # modeling panel
        xloc = 10; yloc = 10
        wx.StaticText(self,-1,"Search:",pos=(xloc,yloc+3),
                          size=(50,self.htext))
        xloc = 60

        self.databaserbt = wx.RadioButton(self,-1,'',pos=(xloc,yloc+2), \
                               style=wx.RB_GROUP)
        xloc += 20
        wx.StaticText(self,-1,"Database:",pos=(xloc,yloc+3),
                          size=(60,self.htext))
        xloc += 70
        self.dbcmb = wx.ComboBox(self,-1,'',choices=self.dblst, \
                           pos=(xloc,yloc), size=(100,hcb),style=wx.CB_READONLY)
        self.dbcmb.Bind(wx.EVT_COMBOBOX,self.OnSelectDB) #ControlPanMdl)
        self.dbcmb.SetValue(self.dblst[0])
        xloc += 110
        conectbtn = wx.Button(self,-1,"Connect",pos=(xloc,yloc),
                         size=(60,hbt))
        conectbtn.Bind(wx.EVT_BUTTON,self.OnConnect)


        xloc += 80
        self.hitsetrbt = wx.RadioButton(self,-1,'',pos=(xloc,yloc+2))
        xloc += 20
        wx.StaticText(self,-1,"Hit set:",pos=(xloc,yloc+3),
                          size=(50,self.htext))

        xloc += 60
        self.hitsetcmb = wx.ComboBox(self,-1,'',choices=self.hitsetlst, \
                           pos=(xloc,yloc), size=(100,hcb),style=wx.CB_READONLY)
        xloc += 110
        self.hitsetcmb.Bind(wx.EVT_COMBOBOX,self.OnSelectHitSet) #ControlPanMdl)


        # ------ query
        yloc += 30; xloc = 10
        wx.StaticText(self,-1,"Query:",pos=(xloc,yloc+2),size=(50,18))


        xloc += 60
        appendbtn = wx.Button(self,-1,"Append to query with:",pos=(xloc,yloc),
                      size=(150,25))
        appendbtn.Bind(wx.EVT_BUTTON,self.OnAppendQuery)
        #appendbtn.SetToolTipString('Append items to query text')
        lib.SetTipString(appendbtn,'Append items to query text')
        xloc += 160
        self.andrbt = wx.RadioButton(self,-1,'AND',pos=(xloc,yloc+5), \
                               style=wx.RB_GROUP)
        self.orrbt = wx.RadioButton(self,-1,'OR',pos=(xloc+50,yloc+5))


        xloc += 110
        editbtn = wx.Button(self,-1,"Edit",pos=(xloc,yloc),
                         size=(50,hbt))
        editbtn.Bind(wx.EVT_BUTTON,self.OnEditQuery)
        #editbtn.SetToolTipString('Edit query text')
        lib.SetTipString(editbtn,'Edit query text')
        xloc += 70

        restbtn = wx.Button(self,-1,"Restore",pos=(xloc,yloc),
                         size=(60,hbt))
        restbtn.Bind(wx.EVT_BUTTON,self.OnRestoreQuery)
        #restbtn.SetToolTipString('Restore query text')
        lib.SetTipString(restbtn,'Restore query text')
        #searchbtn.SetBackgroundColour([0,128,64])
        #searchbtn.SetForegroundColour('white')



        yloc += 30
        xloc = 20 ; hque = h - yloc - 45; wque = w - 110
        self.argtcl = wx.TextCtrl(self,-1,'',pos=(xloc,yloc),
                     size=(wque,hque),style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE)
        xloc = w - 80; yloc1 = yloc + 10
        searchbtn = wx.Button(self,-1,"SEARCH",pos=(xloc,yloc1),
                         size=(60,hbt))
        searchbtn.Bind(wx.EVT_BUTTON,self.OnSearch)
        #searchbtn.SetToolTipString('Search database')
        lib.SetTipString(searchbtn,'Search database')
        """
        # append buttons
        yloc += (hque+5); xloc =20
        wx.StaticText(self,-1,"Append to query with:",pos=(xloc,yloc),
                      size=(130,18))
        xloc += 140
        self.andrbt = wx.RadioButton(self,-1,'AND',pos=(xloc,yloc+2), \
                               style=wx.RB_GROUP)
        self.orrbt = wx.RadioButton(self,-1,'OR',pos=(xloc+50,yloc+2))
        yloc += 20
        xloc = 40
        namebtn = wx.Button(self,-1,"ID",pos=(xloc,yloc),
                         size=(30,hbt))
        namebtn.Bind(wx.EVT_BUTTON,self.OnName)
        xloc += 40
        idbtn = wx.Button(self,-1,"Name",pos=(xloc,yloc),
                         size=(50,hbt))
        idbtn.Bind(wx.EVT_BUTTON,self.OnID)
        xloc += 60
        smilebtn = wx.Button(self,-1,"Smile",pos=(xloc,yloc),
                         size=(50,hbt))
        smilebtn.Bind(wx.EVT_BUTTON,self.OnSmile)
        xloc += 60
        structbtn = wx.Button(self,-1,"Structure",pos=(xloc,yloc),
                         size=(80,hbt))
        structbtn.Bind(wx.EVT_BUTTON,self.OnStructure)
        xloc += 90
        describtn = wx.Button(self,-1,"Descriptor",pos=(xloc,yloc),
                         size=(80,hbt))
        describtn.Bind(wx.EVT_BUTTON,self.OnDescriptor)
        xloc += 90
        qmpropbtn = wx.Button(self,-1,"QM property",pos=(xloc,yloc),
                         size=(80,hbt))
        qmpropbtn.Bind(wx.EVT_BUTTON,self.OnQMProperty)
        xloc += 90
        qmpropbtn = wx.Button(self,-1,"Keyword",pos=(xloc,yloc),
                         size=(80,hbt))
        qmpropbtn.Bind(wx.EVT_BUTTON,self.OnKeyword)
        """

        yloc += (hque+10); xloc = 10
        wx.StaticText(self,-1,"Input/Save selected hit set:",pos=(xloc,yloc+2),
                      size=(170,18))

        xloc += 180


        self.inputbtn = wx.Button(self,-1,"Add to Input",pos=(xloc,yloc),
                         size=(100,hbt))
        self.inputbtn.Bind(wx.EVT_BUTTON,self.OnInputHitSet)
        xloc += 120
        self.savebtn = wx.Button(self,-1,"Save as",pos=(xloc,yloc),
                         size=(60,hbt))
        self.savebtn.Bind(wx.EVT_BUTTON,self.OnSaveHitSet)
        xloc += 70
        label = 'single molecule files'
        self.chkbox = wx.CheckBox(self,-1,label,pos=(xloc,yloc+5)) #,size=[w-20,28])
        #

        xloc += 150
        self.delbtn = wx.Button(self,-1,"Del",pos=(xloc,yloc),
                         size=(40,hbt))
        self.delbtn.Bind(wx.EVT_BUTTON,self.OnDeleteHitSet)
        #self.delbtn.SetToolTipString('Delete selected hit set')
        lib.SetTipString(self.delbtn,'Delete selected hit set')

        self.DisableFileButtons()

    def OnAppendQuery(self,event):
        print ('OnAppend')

    def OnID(self,event):
        print ('OnID')

    def OnName(self,event):
        print ('OnName')

    def OnStructure(self,event):
        print ('OnStructure')

    def OnSmile(self,event):
        print ('OnSmile')

    def OnDescriptor(self,event):
        print ('OnDescriptor')

    def OnQMProperty(self,event):
        print ('OnQMProperty')

    def OnKeyword(self,event):
        print ('OnKeyword')

    def OnEditQuery(self,event):
        print ('OnEditQuery')

    def OnRestoreQuery(self,event):
        print ('OnRestoreQuery')


    def OnSearch(self,event):
        print ('OnSearch')

    def OnSelectDB(self,event):
        obj = event.GetEventObject()
        self.curdb = obj.GetSelection()
        print(('OnSelectDB curdb',self.curdb))

    def OnSelectHitSet(self,event):
        obj = event.GetEventObject()
        self.curset = obj.GetSelection()
        print(('OnSelectHitSet curset',self.curset))

    def OnInputHitSet(self,event):
        print ('InputHitSet')

    def OnSaveHitSet(self,event):
        singlemolfiles = self.chkbox.GetValue()
        print(('OnSaveHitSet',singlemolfiles))

    def OnDeleteHitSet(self,event):
        print ('OnDeleteHitSet')

    def OnConnect(self,event):
        self.curdb = self.dbcmb.GetSelection()
        dbfile = self.mydblst[self.curdb][1]
        print(('curdb,dbfile',self.curdb,dbfile))

    def EnableFileButtons(self):
        self.inputbtn.Enable()
        self.savebtn.Enable()
        self.chkbox.Enable()
        self.delbtn.Enable()

    def DisableFileButtons(self):
        self.inputbtn.Disable()
        self.savebtn.Disable()
        self.chkbox.Disable()
        self.delbtn.Disable()


    def OnDBSearchHelp(self,event):
        print ('OnDBSearchHelp')

    def OnClose(self,event):
        self.frm.SetValueToButton('DBsearch',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        event.Skip()

    def OnMove(self,event):
        event.Skip()


    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class DBAccess_Pan(wx.Frame):
    def __init__(self,parent,panpos,pansize):
        self.frm = parent.parent
        wx.Frame.__init__(self,self.frm,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.parent = parent
        self.dbaccessmgr = parent

        self.SetTitle('Database Access')

        menu = True
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            self.Bind(wx.EVT_MENU,self.OnMenu)


        paramobj = params.MolDevParams()
        #self.help_icon = paramobj.Icon_BMP('help')
        self.pubdblst = paramobj.PublicDatabase()
        self.dblst = []
        for [name,file] in self.pubdblst: self.dblst.append(name)
        print(('dblst',self.dblst))

        # widget height
        self.htext = 18
        self.hcombo = 20
        self.hbutton = 20

        self.curdb = None
        self.downloadedfile = None

        self.CreateWidgets()

        #self.cmdcls = cmd.Cmd(self)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Show()

    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        hcb = 30; hbt = 25
        # modeling panel
        xloc = 10; yloc = 10

        wx.StaticText(self,-1,"Database:",pos=(xloc,yloc+3),
                          size=(70,self.htext))
        xloc += 80
        self.dbcmb = wx.ComboBox(self,-1,'',choices=self.dblst, \
                           pos=(xloc,yloc), size=(120,hcb),style=wx.CB_READONLY)
        self.dbcmb.Bind(wx.EVT_COMBOBOX,self.OnSelectDB) #ControlPanMdl)
        self.dbcmb.SetValue(self.dblst[0])
        xloc += 140
        conectbtn = wx.Button(self,-1,"Connect",pos=(xloc,yloc),
                         size=(60,hbt))
        conectbtn.Bind(wx.EVT_BUTTON,self.OnConnect)
        yloc += 30; xloc = 10
        wx.StaticText(self,-1,"Downloaded file:",pos=(xloc,yloc+3),
                          size=(100,self.htext))
        xloc += 110

        openbtn = wx.Button(self,-1,"Open",pos=(xloc,yloc),
                         size=(50,hbt))
        openbtn.Bind(wx.EVT_BUTTON,self.OnOpenDownloadedFile)
        xloc += 70
        viewbtn = wx.Button(self,-1,"View",pos=(xloc,yloc),
                         size=(50,hbt))
        viewbtn.Bind(wx.EVT_BUTTON,self.OnViewDownloadedFile)

        yloc += 30; xloc = 20
        self.filetxt = wx.StaticText(self,-1,"",pos=(xloc,yloc+3),
                          size=(w-xloc-10,self.htext))
        yloc += 25; xloc = 20
        self.nummoltxt = wx.StaticText(self,-1,"",pos=(xloc,yloc+3),
                          size=(w-xloc-10,self.htext))
        yloc += 30; xloc = 40
        self.inputbtn = wx.Button(self,-1,"Add to Input",pos=(xloc,yloc),
                         size=(100,hbt))
        self.inputbtn.Bind(wx.EVT_BUTTON,self.OnInputDownloadedFile)
        xloc += 120
        self.savebtn = wx.Button(self,-1,"Save as",pos=(xloc,yloc),
                         size=(60,hbt))
        self.savebtn.Bind(wx.EVT_BUTTON,self.OnSaveDownloadedFile)
        xloc += 70
        label = 'single molecule files'
        self.chkbox = wx.CheckBox(self,-1,label,pos=(xloc,yloc+5)) #,size=[w-20,28])
        #
        self.DisableFileButtons()


    def OnSelectDB(self,event):
        obj = event.GetEventObject()
        self.curdb = obj.GetSelection()
        print(('OnSelectDB curdb',self.curdb))

    def OnConnect(self,event):
        self.curdb = self.dbcmb.GetSelection()
        webaddr = self.pubdblst[self.curdb][1]
        print(('web',webaddr))
        moldev_lib.ViewHtmlFile(webaddr)

    def OnDBSearchHelp(self,event):
        print ('OnDBSearchHelp')

    def OnOpenDownloadedFile(self,event):
        print ('OnOpenDownloadedFile')
        filename = ''
        # wild card
        wcard = 'sdf(*.sdf)|*.sdf|smile(*.smi)|*.smi'
        #filename = fu_lib.GetFileName(None,wcard,'r',check=False,
        #                           defaultname='*.sdf',message='')

        dlg = wx.FileDialog(None,"",os.getcwd(),style=wx.FD_OPEN, #|wx.FD_MULTIPLE,
                          wildcard=wcard)
        if dlg.ShowModal() == wx.ID_OK: filename = dlg.GetPath()

        if len(filename) <= 0: return

        self.filetxt.SetLabel(filename)
        count = self.CountMoleculesInFile(filename)
        countmols = 'Number of molecule data in the file = ' + str(count)
        self.nummoltxt.SetLabel(countmols)
        self.downloadedfile = filename
        # enable save button
        self.EnableFileButtons()

    def EnableFileButtons(self):
        self.inputbtn.Enable()
        self.savebtn.Enable()
        self.chkbox.Enable()

    def DisableFileButtons(self):
        self.inputbtn.Disable()
        self.savebtn.Disable()
        self.chkbox.Disable()

    def OnViewDownloadedFile(self,event):
        self.downloadedfile = None
        self.nummoltxt.SetLabel('')
        self.filetxt.SetLabel('')
        self.DisableFileButtons()

    def OnInputDownloadedFile(self,event):
        print ('OpenDownloadedFile')
        if self.downloadedfile is not None:
            if os.path.exists(self.downloadedfile):
                print(('Input ',self.downloadedfile))

    def CountMoleculesInFile(self,filename):
        count = 10

        return count

    def OnSaveDownloadedFile(self,event):
        singlemolfiles = self.chkbox.GetValue()
        print(('OnSaveDownloadedFile',singlemolfiles))

    def OnClose(self,event):
        #self.frm.SetValueToButton('DBaccess',False)
        #except: pass

        self.Destroy()


    def OnResize(self,event):
        event.Skip()

    def OnMove(self,event):
        event.Skip()


    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Read file','Read file')
        subsubmenu.Append(-1,'Smile text','type Smile text')
        subsubmenu.Append(-1,'Open sketch panel','Open sketch panel')
        submenu.AppendMenu(-1,'Input data',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All','All')
        subsubmenu.Append(-1,'Selected','Selected')
        submenu.AppendMenu(-1,'Remove',subsubmenu)
        #
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'All in a file','All')
        subsubmenu.Append(-1,'All in separated sdfs','')
        subsubmenu.Append(-1,'Selected in a file','')
        subsubmenu.Append(-1,'Selected in separate files','')
        submenu.AppendMenu(-1,'Save as',subsubmenu)
        #
        submenu.Append(-1,"Exit",'Exit')
        #
        menubar.Append(submenu,'File')
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy current",'Copy current molecule')
        submenu.Append(-1,"Copy selected",'Copy selected molecules')
        submenu.Append(-1,"Copy all",'Copy all molecules')
        submenu.AppendSeparator()
        submenu.Append(-1,"Paste(append)",'Paste and append') #kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Paste(replace)",'Paste and replace')
        #submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear",'Clear')
        #submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Edit')
        # Script
        submenu=wx.Menu()
        submenu.Append(-1,'2D<->3D molde','2D/3D model') #kind=wx.ITEM_CHECK)

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,'Small','small size')
        subsubmenu.Append(-1,'Medium','Medium size')
        subsubmenu.Append(-1,'Large','Large size')
        subsubmenu.Append(-1,'Input','Input size')
        submenu.AppendMenu(-1,'Icon size',subsubmenu)

        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Line",'Line model')
        subsubmenu.Append(-1,"Stick",'Stick model')
        submenu.AppendMenu(-1,'Molecular model',subsubmenu)

        submenu.AppendSeparator()
        submenu.Append(-1,"Show/hide hydrogens",'Show/hide hydrogens')
        submenu.Append(-1,"Hide/show all atoms",'Hide/show all atoms(show chain only)')
        submenu.Append(-1,"Show chain",'Show chain')
        submenu.AppendSeparator()
        submenu.Append(-1,'Background color','Open color picker')

        menubar.Append(submenu,'Script')

        # Window
        submenu=wx.Menu()
        id0 = wx.NewId()
        submenu.Append(id0,'Open PyShell','Open pyShell',
                       kind=wx.ITEM_CHECK)
        id1 = wx.NewId()
        submenu.Append(id1,'Open command button panel','command button panel',
                       kind=wx.ITEM_CHECK)
        submenu.Append(-1,'Text viewer','Text viewer')
        menubar.Append(submenu,'Window')
        # Setting
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Setting')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        # check
        #menubar.Check(id0,self.show_pyshell)
        #menubar.Check(id1,self.show_cmdpan)

        return menubar

    def CopyMolToClipboard(self,case='current'):
        molnam=self.iconview.GetCurrentMol()
        print(('currentmol'+molnam))

        cpy=molec.Molecule(self)
        fumol=self.moldic[molnam].fumol
        natm=len(fumol.atm)
        cpy.atm=self.mol.CopyAtom()

        dumpmol=pickel.dumps(cpy.atm)
        cbobj=wx.TextDataObject()
        cbobj.SetText(dumpmol)
        try:
            wx.TheClipboard.Open()
            wx.TheClipboard.Clear() # clear clipboard
            wx.TheClipboard.SetData(cbobj)
            #wx.TheClipboard.Flush()
            wx.TheClipboard.Close()
            mess=molnam+" molecule object is copied to clipboard."
            self.ConsoleMessage2(mess)
        except:
            mess='Faled to copy molecule object to clipboard. name='+molnam
            self.ConsoleMessage2(mess)

    def PasteMolFromClipboard(self,case):
        atm=[]
        if not wx.TheClipboard.IsOpened():
            try:
                cbobj=wx.TextDataObject()
                wx.TheClipboard.Open()
                ok=wx.TheClipboard.GetData(cbobj)
                if ok:
                    dumpmol=cbobj.GetText()
                    atm=dumpmol.encode('utf-8') # needs this!
                    atm=pickel.loads(atm)
                else:
                    mess='No data in clipboard.'
                    self.ConsoleMessage(mess)
                wx.TheClipboard.Close()
                if not ok: return
            except:
                mess='Failed to open clipboard.'
                self.ConsoelMessage(mess)
                return
        if len(atm) <= 0: return
        try:
            for i in range(len(atm)): atm[i].setctrl=self.setctrl
            #
            mess=str(len(atm))+" atoms are merged. total number of atoms="
            self.mdlargs['MergeMolecule']=atm
            self.MergeMolecule(None,True) #(atm,True)

            ntot,nhev,nhyd,nter=self.mol.CountAtoms()
            mess=mess+str(ntot)+" ["+str(nhev)+","+str(nhyd)+","+str(nter)+"]"
            self.ConsoleMessage(mess)
            # clear self.savecc
            self.savcc=[]; self.savcclst=[]

            self.FitToScreen(True,False)
        ###self.DrawMol(True)
        except:
            mess='Failed to paste molecule object, may be wrong data type in '
            mess=mess+'clipbload.'
            self.ConsoleMessage(mess)

    def ClearClipboard(self):
        wx.TheClipboard.Clear()
        self.ConsoleMessage('Clipboard is emptied.')

    def OnMenu(self,event):
        """ Menu event handler """
        menuid = event.GetId()
        item = self.menubar.GetLabel(menuid)
        bChecked = self.menubar.IsChecked(menuid)
        # File menu items
        # File-Input data
        if item == 'Read file':
            # wild card
            wcard = 'smile,sdf(*.smi;*.sdf)|*.smi;*.sdf|'
            wcard = wcard + 'pdb(*.pdb;*.ent)|*.pdb;*.ent|mol(*.mol;*.sdf)|'
            wcard = wcard + '*.mol;*.sdf|all(*.*)|*.*'
            #filenames = fu_lib.GetFileNames(None,wcard,'r',check=False,
            #                           defaultname='*.smi;*.sdf',message='')
            filename = ''
            dlg = wx.FileDialog(None,"",os.getcwd(),wildcard=wcard,
                     style=wx.FD_OPEN|wx.FD_MULTIPLE,defaultFile='*.smi;*.sdf')
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPaths()
            else: filename = ''
            if len(filename) <= 0: return
            self.dat.ReadFiles(filename)
        elif item == "Smile text":
            self.dat.InputSmileString()
        elif item == 'Open sketch panel':
            print ('menu: Open sketch panel')

            self.dat.OpenKetcher()
            #self.dat.OpenBKChem()
        # File-Remove
        elif item == "Remove all":
            self.RemoveMolecules('all')
        elif item == "Remove selected":
            self.RemoveMolecules('selected')

        elif item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # edit
        elif item == "Copy current":
            self.CopyMolToClipboard('current')
        elif item == "Copy selected":
            self.CopyMolToClipboard('selected')
        elif item == "Copy all":
            self.CopyMolToClipboard('all')
        elif item == "Paste(append)":
            self.PasteMolFromClipboard('append')
        elif item == "Paste(replace)":
            self.PasteMolFromClipboard('replace')
        elif item == "Clear":
            self.ClearClipboard()


        # Windows
        elif item == 'Open PyShell':
            print(('Menu: Open PyShell',bChecked))
            if bChecked: self.OpenPyShell()
            else: self.ClosePyShell()
        elif item == 'Open command button panel':
            print(('OnMenu: Open command button panel, bcheked',bChecked))

            if bChecked: self.OpenCommandButtonPanel()
            else: self.CloseCommandButtonPanel()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

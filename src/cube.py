#!/bin/sh
# -*- coding:utf-8



import os
#import psutil # downloaded from http://code.google.com/p/psutil/downloads/detail?name=psutil-1.0.1.win32-py2.7.exe&can=2&q=
import wx
import copy
# import FU modules
import fumodel
import view
import const
import lib
import fu_molec as molec
import rwfile
import subwin
import graph

from numpy import *
import numpy
import math

try: import fucubelib
except: pass

try: import comp_mo
except: pass


class SaveImageParams_Frm(wx.Frame):
    def __init__(self,parent,winpos=[],winsize=[],retmethod=None):
        """
        """
        self.title='SaveImageParams'
        #if norbpanel <= 0: norbpanel=1
        winsize = lib.WinSize([270,310],False)
        winpos  = parent.GetPosition()
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,self.title,pos=winpos,size=winsize,
          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)

        self.parent=parent
        self.retmethod = retmethod

        self.fontlabel = self.FontList()
        self.params = self.DefaultParams()
        self.defaultfont = 6
        self.fontcolor = 'green' # green
        self.colortxt=['red','magenta','yellow','orange','brown','blue','cyan','green','purple',
                       'white','gray','black','---','palette']

        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.Show()

    def CreatePanel(self):
        bgcolor = 'light gray'
        [w,h]   = self.GetClientSize()
        hcb=25 #const.HCBOX
        # upper panel
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(w,h)) #ysize))
        self.panel.SetBackgroundColour(bgcolor)

        yloc = 10
        xloc = 10
        xpos = 95

        wx.StaticText(self.panel,-1,"Save MO images (with white background)" ,
                      pos=(xloc,yloc),size=(270,18))
        yloc += 25
        wx.StaticText(self.panel,-1,"MO numbers:" ,
                      pos=(xloc+10,yloc),size=(80,18))
        monums = str(self.params['molevs'])
        self.molevs=wx.TextCtrl(self.panel,-1,monums,
                               pos=(xloc+xpos,yloc-2),size=(145,22),
                              style=wx.TE_PROCESS_ENTER)
        lib.SetTipString(self.molevs,'MO numbers to be drawn, 1,5-8,20,...')
        yloc += 25
        wx.StaticText(self.panel,-1,"Margin:" ,
                      pos=(xloc+10,yloc),size=(80,18))
        margin = str(self.params['margin'])
        self.margin=wx.TextCtrl(self.panel,-1,margin,
                               pos=(xloc+xpos,yloc-2),size=(40,22),
                              style=wx.TE_PROCESS_ENTER)
        lib.SetTipString(self.margin,'margin in pixels')
        yloc += 25
        wx.StaticText(self.panel,-1,"MO width, height:" ,
                      pos=(xloc+10,yloc),size=(120,18))
        wmo = str(self.params['wmo'])
        self.wmo=wx.TextCtrl(self.panel,-1,wmo,
                               pos=(xloc+130,yloc-2),size=(50,22),
                              style=wx.TE_PROCESS_ENTER)
        lib.SetTipString(self.wmo,'Width of a MO draw')
        hmo = str(self.params['hmo'])
        self.hmo=wx.TextCtrl(self.panel,-1,hmo,
                               pos=(xloc+190,yloc-2),size=(50,22),
                              style=wx.TE_PROCESS_ENTER)
        lib.SetTipString(self.hmo,'Height of a MO draw')
        yloc += 25
        wx.StaticText(self.panel,-1,"MOs per row:" ,
                      pos=(xloc+10,yloc),size=(80,18))
        perrow = str(self.params['perRow'])
        self.perrow=wx.TextCtrl(self.panel,-1,perrow,
                               pos=(xloc+xpos,yloc-2),size=(40,22),
                              style=wx.TE_PROCESS_ENTER)
        lib.SetTipString(self.perrow,'Number of MOs per row')
        yloc += 25

        model = self.params['drawmodel']
        wx.StaticText(self.panel,-1,"Mol. model:" ,
                      pos=(xloc+10,yloc),size=(80,18))
        modelchoice = ['as is','line','stick','ball-and-stick']
        self.model=wx.ComboBox(self.panel,-1,model,
                               choices=modelchoice,
                               pos=(xloc+xpos,yloc), size=(100,hcb),
                               style=wx.CB_READONLY)
        yloc += 25
        wx.StaticText(self.panel,-1,"Font:" ,
                      pos=(xloc+10,yloc),size=(40,18))
        self.fontchoice=wx.ComboBox(self.panel,-1,self.fontlabel[0],
                               choices=self.fontlabel,
                               pos=(xloc+xpos,yloc),size=(145,hcb),
                               style=wx.CB_READONLY)
        self.fontchoice.SetSelection(self.defaultfont)
        """
        yloc += 20
        wx.StaticText(self.panel,-1,"Font color:",pos=(xloc+10,yloc),
                      size=(40,18))
        self.cbcol=wx.ComboBox(self.panel,-1,'',choices=self.colortxt, \
                               pos=(xloc+35,yloc-3), size=(90,hcb),
                               style=wx.CB_READONLY)
        self.cbcol.SetSelection(self.fontcolor)
        self.cbcol.Bind(wx.EVT_COMBOBOX,self.OnFontColor)
        #self.cbcol.SetToolTipString('Choose font color. "---" is dummy')
        lib.SetTipString(self.cbcol,'Choose font color. "---" is dummy')
        """
        yloc += 30
        wx.StaticText(self.panel,-1,"File name:" ,
                      pos=(xloc+10,yloc),size=(80,18))
        btnbrows=wx.Button(self.panel,-1,"Browse",pos=(xloc+xpos,yloc),
                               size=(60,22))
        btnbrows.Bind(wx.EVT_BUTTON,self.OnBrowse)
        yloc += 30
        self.file=wx.TextCtrl(self.panel,-1,'',
                               pos=(xloc+20,yloc-2),size=(220,22),
                              style=wx.TE_PROCESS_ENTER)
        self.file.Bind(wx.EVT_TEXT_ENTER,self.OnApply)
        lib.SetTipString(self.file,'Image file name, e.g., "xxx.png"')

        #self.fontchoice.Bind(wx.EVT_COMBOBOX,self.OnFont)
        yloc += 25
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        #yloc += 25
        yloc += 8
        btncan=wx.Button(self.panel,-1,"Cancel",pos=(xloc+30,yloc),
                               size=(60,22))
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)
        btnapply=wx.Button(self.panel,-1,"Apply",pos=(xloc+100,yloc),
                               size=(60,22))
        btnapply.Bind(wx.EVT_BUTTON,self.OnApply)
        btncls=wx.Button(self.panel,-1,"Close",pos=(xloc+170,yloc),
                               size=(60,22))
        btncls.Bind(wx.EVT_BUTTON,self.OnClose)

    def OnFontColor(self,event):
        color=self.cbcolp.GetValue()
        if color == '---': return
        self.rgbpos=self.GetColor(color,self.cbcolp)
        if len(self.rgbpos) <= 0: return
        #if self.btndraw.GetValue(): self.OnDraw(1)
        if self.ondraw: self.OnDraw(1)

    def DefaultParams(self):
        params = {
            'molevs'    : 'HOMO,LUMO',
            #'wbitmap'   : 700,   # bitmap width
            'margin'    : 100,     # margin for left,right, top,bottom
            'wmo'       : 300,    # mo width
            'hmo'       : 300,    # mo height
            'perRow'    : 2,      # mos per row
            'drawmodel' : 'as is',# stick
            'fontstyle' : 6       # GLUT_BITMAP_HELVETICA_18
             } # save directory
        return params

    def OnBrowse(self,event):
        wcard ="image(*.png;*.bmp)|*.png;*.bmp"
        filename = lib.GetFileName(wcard=wcard,rw='w')
        if len(filename) <= 0: return
        self.file.SetValue(filename)

    def OnFont(self,event):
        pass

    def OnFontCole(self,event):
        pass

    def OnCancel(self,event):
        self.OnClose(1)

    def OnClose(self,event):
        self.Destroy()

    def OnApply(self,event):
        #modeldic = {0:'line',1:'stick',2:'ball-and-stic',3:'CPK'}
        self.params['fontstyle'] = self.fontchoice.GetSelection()
        #self.params['wbitmap'] = 700, # bitmap width
        self.params['margin']    =  int(self.margin.GetValue()) # margin for left,right, top,bottom
        self.params['wmo']       =  int(self.wmo.GetValue()) # mo width
        self.params['hmo']       =  int(self.hmo.GetValue()) # mo height
        self.params['perRow']    =  int(self.perrow.GetValue()) # mos per row
        molmdl=self.parent.cbmdl.GetValue().strip()
        if len(molmdl) <= 0: molmdl='line'
        self.params['drawmodel'] = molmdl
        self.params['molevs']    = self.molevs.GetValue()
        """ 
        fontcolor = self.cbcol.GetValue()
        if fontcolor == '---': fontcolor = self.fontcolor
        rgbcol = lib.GetRGBColor(fontcolor)
        self.params['fontcolor'] = rgbcolor
        self.fontcolor           = rgbcolor
        """
        filename                 = self.file.GetValue()

        if self.retmethod is not None:
            if len(filename) <= 0:
                mess = 'Please input filename'
                wx.MessageBox(mess,'SaveImageParams.OnApply')
                return
            self.retmethod(filename,self.params)

    def FontList(self):
        """ See fu_draw.GetBitmapFont """
        fontlabel = ['BITMAP_8_BY_13',
                     'BITMAP_9_BY_15',
                     'TIMES_ROMAN_10',
                     'TIMES_ROMAN_24',
                     'HELVETICA_10',
                     'HELVETICA_12',
                     'HELVETICA_18' ]
        return fontlabel

class PlotEnergy_Frm(wx.Frame):
    def __init__(self,parent,model,mode=0,winpos=[],winsize=[],
                 norbdat=1,orbtitle=None,erange=None,
                 enableselect=False): #,model,ctrlflag,molnam,winpos):
        """
        :param obj parent: parent object
        :param int id: object id
        :param obj model: an instance of "Model" (model.py)
        :param obj viewer: viewer instance
        :param int mode: 0 for stand alone, 1 for child (no menu)
        """
        self.title='Energy plotter'

        ###self.orbitallst=[[[-20,-15,-10,5,10,15]],[[-50,-20,-15,-10,5,10,15],[-15,-10,-5,8,10,12]]]
        #self.orbitallst=[[[-20,-15,-10,5,10,15]]]
        parsize = parent.GetSize()
        if len(winpos) <= 0:
            parpos = parent.GetPosition()
            winpos = [parpos[0]+parsize[0],parpos[1]]
        if len(winsize) <= 0:
            x0 = 75 # x0 in the graph.EnergyGraph class
            barwidth = 15 # barwidth in in the graph.EnergyGraph class
            winwidth=x0+norbdat*(barwidth+15)+60 #40 #20
            winheight = 425 # the same size as parent win
        winsize=lib.MiniWinSize([winwidth,winheight]) #([100,355])
        self.winwidth = winsize[0]
        self.norbdat=norbdat
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent = parent # may be DrawCubeData_Frm in FU
        self.model  = model # model #parent.model
        # FU icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        # menu
        self.mode = mode
        if self.mode <= 1:
            menud = self.MenuItems()
            self.menubar = self.MenuItems() # create instance of fuMenu class
            self.SetMenuBar(self.menubar) # method of wxFrame class
            lib.InsertTitleMenu(self.menubar,'[PlotEnergy]')
            self.Bind(wx.EVT_MENU,self.OnMenu)
            
        self.bgcolor = [160,180,190]
        self.enableselect = enableselect
        if orbtitle is None: self.orbtitle = 'Orbital energy'
        else: self.orbtitle = orbtitle
        self.orbgraph = None #self.norbdat*[None]
        self.spin = self.norbdat*[''] # not used
        self.widgetiddic={}

        self.curdata=0
        if erange is None:
            self.erangemin = -15.0
            self.erangemax = 5.0
        else:
            self.erangemin = erange[0]
            self.erangemax = erange[1]
        #
        self.eiglstlst = None
        self.eigidxlst = None
        self.homolst   = None
        self.lumolst   = None
        self.datacolorlst = None
        self.graphtitle = None
        self.messagetextlst = None
        self.magnify=False

        self.CreatePanel()

        self.orbgraph.Plot(True)
        #self.OnOrbReset(1)
        #if lib.GetPlatform() == 'MACOSX' and wx.version()[0:2] != '2.':
        #    wx.MessageBox('Please push "Reset" button when resized the panel')
        #
        self.Show()

        # activate event handlers
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def CreatePanel(self):
        idata = 0
        [w,h] = self.GetClientSize()
        ff='%5.0f'
        self.panel=wx.Panel(self,-1,pos=(0,0),size=(w,h)) #ysize))
        self.panel.SetBackgroundColour(self.bgcolor)

        yloc=5; xloc=15
        label=wx.StaticText(self.panel,-1,label=self.orbtitle,
                            pos=(xloc,yloc),size=(w-10,18))
        yloc += 25
        self.wplt=w-25
        self.hplt=h-100
        #id=wx.NewId()
        self.orbgraph=graph.EnergyGraph(self.panel,(xloc,yloc),
                                        (self.wplt,self.hplt),'white',
                                        enableselect=self.enableselect,
                                        retobj=self)
        yloc += self.hplt+15
        xloc = (w-80)/2-10
        id=wx.NewId()
        btnrdc=wx.Button(self.panel,id,"<",pos=(xloc,yloc),size=(22,20))
        btnrdc.Bind(wx.EVT_BUTTON,self.OnOrbReduce)
        lib.SetTipString(btnrdc,'"<" key press also reduces/magnifies')
        btnrdc.Bind(wx.EVT_KEY_DOWN,self.OnOrbKeyDown)
        self.widgetiddic[id]=[idata,'Reduce',btnrdc]
        id=wx.NewId()
        btnmag=wx.Button(self.panel,id,">",pos=(xloc+30,yloc),size=(22,20))
        btnmag.Bind(wx.EVT_BUTTON,self.OnOrbMagnify)
        self.widgetiddic[id]=[idata,'Magnify',btnmag]
        lib.SetTipString(btnmag,'"<"  key press also reduces/magnifies')
        btnmag.Bind(wx.EVT_KEY_DOWN,self.OnOrbKeyDown)
        id=wx.NewId()
        btnset=wx.Button(self.panel,id,"Reset",pos=(xloc+60,yloc),size=(50,20))
        btnset.Bind(wx.EVT_BUTTON,self.OnOrbReset)
        lib.SetTipString(btnset,'Reset draw size')
        self.widgetiddic[id]=[idata,'Reset',btnset]
        yloc += 25
        xloc = (w-45)/2 + 10
        id=wx.NewId()
        btncls=wx.Button(self.panel,id,"Close",pos=(xloc-5,yloc),size=(50,20))
        btncls.Bind(wx.EVT_BUTTON,self.OnClose)
        lib.SetTipString(btncls,'Close this panel')
        #
        self.SetOrbLabelColor(self.curdata)
                
    def SetTitle(self,title):
        self.orbgraph.SetTitle(title)

    def PlotEnergy(self,eiglstlst,eigidxlst,title=None,datacolorlst=None):
        self.eiglstlst = eiglstlst
        self.eigidxlst = eigidxlst
        self.orbgraph.SetYRange(self.erangemin,self.erangemax)
        self.orbgraph.SetData(eiglstlst) # self.orbitallst)
        self.orbgraph.SetDataIndex(eigidxlst)
        if title is not None:
            self.graphtitle = title
            self.orbgraph.SetTitle(self.graphtitle)
        if datacolorlst is not None:
            self.datacolorlst = datacolorlst
            self.orbgraph.SetDataColor(self.datacolorlst)
        
        
        
        #
        self.orbgraph.Plot(True)
        #self.orbgraph.Refresh()
        #self.orbgraph.SetFocus()
        #
        return
    
    
        if lib.IsWxVersion2():
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        else: wx.Cursor(wx.CURSOR_HAND)

    def RefreshGraphPanel(self):
        for id,lst in list(self.widgetiddic.items()):
            if lst[1] == 'Panel':
                lst[2].Refresh(); lst[2].Update()

    def OnOrbKeyDown(self,event):
        # ascii:44:'<',46:'>', unicode: 60:'<',62:'>'
        keycode=event.GetKeyCode()
        if keycode == 46: self.ZoomEnergyGraph(self.curdata,True)
        elif keycode == 44: self.ZoomEnergyGraph(self.curdata,False)

    def OnOrbMagnify(self,event):
        id=event.GetId()
        idata=self.widgetiddic[id][0]
        self.SetOrbLabelColor(idata)
        self.ZoomEnergyGraph(idata,True)

    def OnOrbReduce(self,event):
        id=event.GetId()
        idata=self.widgetiddic[id][0]
        self.SetOrbLabelColor(idata)
        #
        self.ZoomEnergyGraph(idata,False)

    def ZoomEnergyGraph(self,idata,magnify):
        ymin,ymax=self.orbgraph.GetYRange()
        yinc=1.0
        if magnify: ymin += yinc; ymax -= yinc
        else: ymin -= yinc; ymax += yinc
        #
        self.orbgraph.SetYRange(ymin,ymax)
        self.orbgraph.Plot(True)

    def SetFocusOnOrbPanel(self,idata):

        #print(('SetFocuson',idata))
        for id,lst in list(self.widgetiddic.items()):
            if lst[1] == 'Panel' and lst[0] == idata:
                panel=lst[2]; break
        panel.SetFocus()

    def SetGraphMessageText(self,messagetextlst):
        self.messagetextlst = messagetextlst
        self.orbgraph.SetTitleMessageText(messagetextlst)

    def SetOrbLabelColor(self,idata):
        # widgetiddic:{id:[idata,label,obj],...}
        for id,lst in list(self.widgetiddic.items()):
            if lst[1] == 'Label':
                if lst[0] == idata: color='red'
                else: color='black'
                lst[2].SetForegroundColour(color)
                lst[2].Refresh()
                self.curdata=idata

    def OnOrbReset(self,event):
        # reset energy graph color
        #graphobj=self.orbgraph #self.GetGraphObj(self.curdata)
        #
        ymin=self.erangemin
        ymax=self.erangemax
        self.orbgraph.SetYRange(ymin,ymax)
        self.orbgraph.Plot(True)

    def OnOrbClose(self,event):
        id=event.GetId()
        idata=self.curdata #self.widgetiddic[id][0]
        pos=self.GetPosition()

        try: del self.orbitallst[idata]
        except: pass

        self.parent.orbobj.SetOrbitalList(self.orbitallst)

        self.Destroy()

        self.parent.orbobj.OpenDrawOrbitalWin(self.orbitallst)
        self.SetPosition(pos)

    def SaveImage(self):
        wcard = "image data(*.png;*.bmp)|*.png;*.bmp"
        filename = lib.GetFileName(wcard=wcard,rw='w')
        if len(filename) <= 0: return

        wxbmp = self.orbgraph.GetDCBuffer()

        ret = lib.SaveImageOnFile(filename,wxbmp)
        mess = 'Orbital energy image was saved to ' + filename
        self.model.ConsoleMessage(mess)

    def CopyImage(self):
        wxbmp = self.orbgraph.GetDCBuffer()
        lib.CopyBitmapToClipboard(wxbmp)
        mess = 'Orbital energy image was copied to clipboard.'
        self.model.ConsoleMessage(mess)

    def ViewEnergy(self):
        if len(self.eiglstlst) <= 0: return
        winpos  = [self.GetPosition()[0]+10,self.GetPosition()[1]+10]
        winsize = [200,300]
        viewer  = subwin.TextViewer_Frm(self,winpos,winsize)
        fmt='%8.3f'
        mess = '<' + self.orbtitle + '>\n'
        mess += 'Orbital energy(eV):\n'
        ndat = len(self.eiglstlst)
        for i in range(ndat):
            try: title = self.messagetextlst[i]
            except: title = 'data ' + str(i+1)
            mess += title +'\n'
            neig = len(self.eiglstlst[i])
            for j in range(neig):
                mess += '   ' + str(self.eigidxlst[i][j]+1) + ' = '
                ho = ''
                if self.homolst is not None:
                    if self.eigidxlst[i][j] == self.homolst[i]: ho = 'H'
                if self.lumolst is not None:
                    if self.eigidxlst[i][j] == self.lumolst[i]: ho = 'L'

                #if self.eigidmoxlst[i][j] == self.ho
                mess += fmt % self.eiglstlst[i][j] + ho + '\n'
        viewer.SetText(mess)

    def OnClose(self,event):
        try: self.parent.drwene = None
        except: pass
        self.Destroy()

    def OnPaint(self,event):
        self.orbgraph.Plot(True) 
        event.Skip()


    def OnMove(self,event):
        self.orbgraph.Plot(True) 
        #self.OnOrbReset(1)
        event.Skip()

    def OnResize(self,event):
        [w,h] = self.GetSize()
        if w < self.winwidth: self.SetSize([self.winwidth,h])
        ###self.orbgraph.Destroy()
        self.panel.Destroy()
        self.CreatePanel()
        self.orbgraph.SetTitleMessageText(self.messagetextlst)
        self.PlotEnergy(self.eiglstlst,self.eigidxlst,self.graphtitle,self.datacolorlst)
        
        #self.OnOrbReset(1)
        self.orbgraph.Plot(True) 
        
        #event.Skip()

    def OpenFile(self):
        wcard = "GMS output(*.out;*.log)|*.out;*.log|orb file(*.orb)|*.orb|"
        wcard += "all(*.*)|*.*"
        filename = lib.GetFileName(self,wcard,"r",True,"")
        if len(filename) <= 0: return
        head,tail = os.path.split(filename)
        base,ext  = os.path.splitext(tail)
        if ext not in ['.out','.orb']: return
        if ext == '.orb': # orbital file
            orbinfo,atomcclst,eiglstlst,\
                      symlstlst,moslstlst,basdiclst =\
                      rwfile.ReadMOsInOrbFile(filename)
            titlelst   = orbinfo['TITLES']
            nocclst = orbinfo['NOCCA']
        elif ext == '.out':
            natoms,nbasis,atomcc,noccs,eiglst,symlst,moslst,basdic,basoptlst = \
                      rwfile.ReadMOsInGMSOutput(filename)
            titlelst=[base]
            eiglstlst=[eiglst]
            natomslst = [natoms]; nbasislst = [nbasis]; nocclst  = noccs
            atomcclst = [atomcc]; symlstlst = [symlst]; eiglstlst = [eiglst]
            moslstlst = [moslst]; basdiclst = [basdic]

        self.titlelst   = titlelst #orbinfo['TITLES']
        #nocclst = orbinfo['NOCCA']
        #self.messagetextlst = self.titlelst[:]
        self.eiglstlst = eiglstlst
        norbdat = len(self.eiglstlst)

        self.homolst   = []
        self.lumolst   = []
        self.eigidxlst = []
        self.datacolorlst = []
        toev = 27.2113845
        for i in range(norbdat):
            ndat = len(eiglstlst[i])
            self.datacolorlst.append(ndat*['black'])
        for i in range(norbdat):
            ndat = len(eiglstlst[i])
            self.eigidxlst.append(list(range(ndat)))
            self.eiglstlst[i] = [x * toev for x in self.eiglstlst[i]]
            #print(('ig,eiglst=',i,self.eiglstlst[i]))
            self.datacolorlst[i][nocclst[i]-1] = 'cyan' #'blue'
            self.datacolorlst[i][nocclst[i]]   = 'green'
            self.homolst.append(nocclst[i]-1)
            self.lumolst.append(nocclst[i])

        self.Reopen(norbdat)

    def Reopen(self,norbdat):
        try: self.Destroy()
        except: pass
        
        winpos = self.GetPosition()

        self.drwene = PlotEnergy_Frm(self.model.mdlwin,self.model,mode=0,
                                      winpos=winpos,norbdat=norbdat,
                                      enableselect=True)
        self.drwene.messagetextlst = self.titlelst
        self.drwene.homolst = self.homolst
        self.drwene.lumolst = self.lumolst
        self.drwene.datacolorlst = self.datacolorlst
        #self.drwene.SetTitle(self.titlelst)
        title = 'Mols='
        for t in self.titlelst: title += t +',\n'
        self.drwene.PlotEnergy(self.eiglstlst,self.eigidxlst,title,self.datacolorlst)
        self.model.winctrl.Close('Open PlotEnergyWin')

    def HelpDocument(self):
        helpdir=self.model.setctrl.GetDir('FUdocs')

        helpfile='EnergyPlotter//html//EnergyPlotter.html'
        helpfile=os.path.join(helpdir,helpfile)
        title='EnergyPlotter Help'
        #HelpTextWin_Frm(self,title=title,textfile=helpfile,fumodel=self.model)

        [x,y]=self.GetPosition()
        winpos=[x+20,y+20]
        subwin.HelpMessage(helpfile,title=title,winpos=winpos,parent=self)

    def MenuItems(self):
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        if self.mode == 0:
            submenu.Append(-1,"Open","Open...")
            submenu.AppendSeparator()
        submenu.Append(-1,"Save image","Save image...")
        submenu.AppendSeparator()
        submenu.Append(-1,"Replot","Replot...")
        submenu.AppendSeparator()
        submenu.Append(-1,"Quit","Quit...")
        menubar.Append(submenu,'File')
        # View
        submenu=wx.Menu()
        submenu.Append(-1,"View Orbital energy","View energy")
        submenu.AppendSeparator()
        submenu.Append(-1,"Copy image to clipboard","Copy image")
        menubar.Append(submenu,'Edit')

        submenu=wx.Menu()
        submenu.Append(-1,"Document","Document")
        menubar.Append(submenu,'Help')

        return menubar

    def OnMenu(self,event):
        # menu event handler
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        # File menu
        if item == "Open": self.OpenFile()
        elif item == "Save image": self.SaveImage()
        elif item == "Replot": self.OnResize(1)
        elif item == "Quit":
            self.OnClose(1)
        # Edit menu
        elif item == "View Orbital energy": self.ViewEnergy()
        elif item == "Copy image to clipboard": self.CopyImage()
        elif item == "Document": self.HelpDocument()


class DrawCubeData_Frm(wx.Frame):
    def __init__(self,parent,winpos,winsize,model,viewer,mode,
                 winlabel=None,wincount=None): #,model,ctrlflag,molnam,winpos):
        """
        :param obj parent: parent object
        :param int id: object id
        :param obj model: an instance of "Model" (model.py)
        :param obj viewer: viewer instance
        :param int mode: 0 for stand alone, 1 for child (no menu)
                         2 for MO darwer in MDLWIN
        """
        title='Cube Drawer'
        winname,winnum = lib.SplitNumberInString(winlabel)
        if winnum is not None: winnum = '(' + str(winnum) + ')'
        else: winnum = ''
        if mode == 2: title = 'MO Drawer' + winnum
        if len(winsize) <= 0:
            if mode == 2: winsize = [180,450] #380] #360]
            else:         winsize = [180,450] #305]
        winsize = lib.WinSize(winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.mode = mode
        if self.mode == 1: self.viewer=viewer

        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass

        self.model     = model # model #parent.model
        self.mdlwin    = model.mdlwin
        self.draw      = self.mdlwin.draw
        #self.ctrlflag  = model.ctrlflag
        self.winlabel  = winlabel
        self.wincount  = wincount # 0,1,2,...window number
        #
        bgcolorlst     = []
        name,self.winnum = lib.SplitNumberInString(winlabel)
        if self.winnum is not None:
            pass
        #    if num < 5: self.bgcolr = bgcolorlst[num-1]
        if self.mode == 2: self.bgcolor = [160,180,190]
        else: self.bgcolor = 'light gray'
        self.textmessagecolor = \
                         self.model.setctrl.GetParam('text-message-color')
        self.fontstyle = self.model.setctrl.GetParam('text-message-fontstyle')
        self.fontcolorids = None
        self.colorlst = ['Black','White','Green','Yellow','Pickup in palett']
        self.colornum = 3
        # menu
        self.fontmenuids = None
        if self.mode == 0 or self.mode == 2:
            self.menubar = self.MenuItems() # method of MyModel class
            self.SetMenuBar(self.menubar) # method of wxFrame class
            lib.InsertTitleMenu(self.menubar,'[DrawCube]')
            self.Bind(wx.EVT_MENU,self.OnMenu)
            popmenu    = self.PopupMenu
            pophandler = self.OnPopupMenu
            self.model.mdlwin.SetPopupMenu(popmenu,pophandler)
        #
        #self.cubedataname=[]
        nulobj = CubeObj()
        self.cmpord = None # ao components order,0:GAMESS,1:canonical,2:lotus
        #Xself.cubedatalst = []
        self.cubeobjdic  = {} #; self.cubeobjdic[' ']=nulobj
        self.moobjdic    = {} #; self.moobjdic[' ']=nulobj # ?
        self.cubeobjlst  = []
        self.curcube     = ''

        self.gridmo    = None
        self.datlst    = []
        self.curdat    = ''
        self.grplst    = []
        self.curgrp    = ''
        self.grporgdic = {} # {curgrpdat: org name of the group,...}
        self.curgrpdic = {} # {datnam:curgrp,...
        self.curmodic  = {} # {curdatgrp:curitem,...
        self.eigidxlst = None # index to plot energy
        ###self.curmolst  = []
        self.grplstdic = {} # {datnam: grplst,..
        self.gridmodic = {} # {datnam:grpnam: gridmoobj,...}
        ###self.curitemdic = {} # {datgrp: cur mo,...}
        self.grppolygdic = {}  # group polyg {grpnam: [polyg[0],polyg[1],text]
        self.donotshowlst = []
        #
        self.parentbgcolor = self.mdlwin.draw.bgcolor
        #self.cubefile=''
        self.prptxt    = ['DENSITY','MEP','CUBE']
        self.itemlst   = ['']
        self.curitem   = ''
        self.curnum    = -1
        self.property  = 0
        self.style     = 1 # 0:solid, 1:mesh
        self.ondraw     = False
        #
        self.isovalue  = 0.05
        self.interpol  = 1
        self.minipo    = 1
        self.maxipo    = 4 # maximum degree of intepolation for cube data
        self.opacity   = 1.0 #0.5 # 0-1
        self.colortxt=['red','magenta','yellow','orange','brown','blue','cyan','green','purple',
                       'white','gray','black','---','palette']
        self.bgcolorlst = ['black','white','gray','blue',
                           'yellow','orange','brown',
                           'cyan','green','purple',
                           'magenta','red',
                           '---','palette']
        self.colorpos=self.colortxt[0]; self.rgbpos=const.RGBColor[self.colorpos]
        self.colorneg=self.colortxt[6]; self.rgbneg=const.RGBColor[self.colorneg]
        self.opacitylst  = ['0.2','0.3','0.5','0.6','0.8','1.0']
        self.isovaluelst = ['0.1','0.07','0.05','0.03','0.02','0.01']
        self.merge   = False
        #self.overlay = False
        self.molmodellst  = ['line','stick','ball-and-stick']
        self.labelgroup   = True
        self.drawlablegroup = False
        self.drwene = None
        self.drweigmin = -20.0 # eV
        self.drweigmax =  10.0

        # create panel
        self.CreatePanel()

        self.SetParamsToWidgets()
        if winnum == '': self.InfoMessage()
        #
        if self.mode == 1: self.GetCubeFileAndMakeCubeObjDic()
        #
        self.PopupMenu()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        # for synchronize with MDLWIN
        subwin.ExecProg_Frm.EVT_THREADNOTIFY(self,self.OnNotify)

    def CreatePanel(self):
        size=self.GetClientSize()
        w=size[0]; h=size[1]
        hcb=25 #const.HCBOX
        ff='%5.0f'
        # upper panel
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(w,h)) #ysize))
        self.panel.SetBackgroundColour(self.bgcolor)
        # cubedata
        yloc=5
        if self.mode != 2: yloc = 10
        xloc=15
        label = 'Choose Data'
        if self.mode == 2: label = 'Choose MO:'
        self.itemchoice = None
        ###if self.mode == 2:
        btnrset=subwin.Reset_Button(self.panel,-1,self.OnResetMol)
        self.title = wx.StaticText(self.panel,-1,label='Choose data:',
                                   pos=(xloc,yloc),size=(100,18))
        if self.mode == 2:
            yloc += 20
            self.datchoice=wx.ComboBox(self.panel,-1,str(self.curdat),
                                   choices=self.datlst,
                                   pos=(20,yloc), size=(150,hcb), #size=(145,hcb),
                                   style=wx.CB_READONLY)
            self.datchoice.Bind(wx.EVT_COMBOBOX,self.OnDataChoice)
            self.datchoice.Bind(wx.EVT_RIGHT_DOWN,self.OnDataChoiceRightDown)
            mess = 'Choose data. Right click to see long name'
            lib.SetTipString(self.datchoice,mess)

            yloc += 25
            self.title = wx.StaticText(self.panel,-1,label='Choose group:',
                                       pos=(xloc,yloc),size=(100,18))
            yloc += 20
            self.grpchoice=wx.ComboBox(self.panel,-1,str(self.curgrp),
                                   choices=self.grplst,
                                   pos=(20,yloc), size=(120,hcb),
                                   style=wx.CB_READONLY)
            self.grpchoice.Bind(wx.EVT_COMBOBOX,self.OnGroupChoice)
            lib.SetTipString(self.grpchoice,'Choose group')
            self.grpchoice.Bind(wx.EVT_RIGHT_DOWN,self.OnGroupChoiceRightDown)
            rmvbmp =self.model.setctrl.GetIconBmp('remove16',imgfrm='.png')
            btnrmv=wx.BitmapButton(self.panel,-1,bitmap=rmvbmp,
                                         pos=(150,yloc+2),size=(20,20))
            btnrmv.Bind(wx.EVT_BUTTON,self.OnRemoveMO)
            lib.SetTipString(btnrmv,'Remove MO of the group')

            yloc += 30
            upbmp  =self.model.setctrl.GetIconBmp('up-20',imgfrm='.png')
            downbmp=self.model.setctrl.GetIconBmp('down-20',imgfrm='.png')
            ststyle=wx.StaticText(self.panel,-1,label=label,
                                  pos=(xloc,yloc),size=(80,18))
            btnup=wx.BitmapButton(self.panel,-1,bitmap=upbmp,
                                         pos=(xloc+100,yloc-2),size=(20,20))
            btnup.Bind(wx.EVT_BUTTON,self.OnUp)
            lib.SetTipString(btnup,'Choose upper level and draw')

            btndw=wx.BitmapButton(self.panel,-1,bitmap=downbmp,
                                         pos=(xloc+125,yloc-2),size=(20,20))
            btndw.Bind(wx.EVT_BUTTON,self.OnDown)
            lib.SetTipString(btndw,'Choose lower level and draw')

        yloc += 20
        wsize = 150
        if self.mode == 2: wsize = 120
        self.itemchoice=wx.ComboBox(self.panel,-1,str(self.curitem),
                               choices=self.itemlst,
                               pos=(20,yloc), size=(wsize,hcb),
                               style=wx.CB_READONLY)
        self.itemchoice.Bind(wx.EVT_COMBOBOX,self.OnMOChoice)
        mess = label[:-1] + ' and draw.  Right click to see long name'
        lib.SetTipString(self.itemchoice,mess)
        self.itemchoice.Bind(wx.EVT_RIGHT_DOWN,self.OnItemChoiceRightDown)

        if self.mode == 2:
            signbmp  =self.model.setctrl.GetIconBmp('change-sign16',imgfrm='.png')
            btnsgn=wx.BitmapButton(self.panel,-1,bitmap=signbmp,
                                         pos=(150,yloc+2),size=(20,20))
            btnsgn.Bind(wx.EVT_BUTTON,self.OnChangeMOSign)
            lib.SetTipString(btnsgn,'Change sign of the MO')

        yloc += 28
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        # style
        ststyle=wx.StaticText(self.panel,-1,label='Style:',pos=(xloc,yloc),
                              size=(35,18))
        lib.SetTipString(ststyle,'Choose draw style')
        #yloc += 18
        self.rbtwire=wx.RadioButton(self.panel,-1,"wire",pos=(xloc+40,yloc),
                                    size=(50,18),style=wx.RB_GROUP)

        self.rbtwire.Bind(wx.EVT_RADIOBUTTON,self.OnWire)
        #yloc += 18
        self.rbtsold=wx.RadioButton(self.panel,-1,"solid",pos=(xloc+90,yloc),
                                    size=(50,18))
        self.rbtsold.Bind(wx.EVT_RADIOBUTTON,self.OnSolid)
        self.rbtwire.SetValue(True)
        yloc += 25
        wx.StaticText(self.panel,-1,"Opacity:" ,pos=(xloc,yloc),size=(50,18))
        self.cbopa=wx.ComboBox(self.panel,-1,'',choices=self.opacitylst, \
                               pos=(xloc+75,yloc-3), size=(80,hcb),
                               style=wx.TE_PROCESS_ENTER)
        self.cbopa.Bind(wx.EVT_TEXT_ENTER,self.OnOpacity)
        self.cbopa.Bind(wx.EVT_COMBOBOX,self.OnOpacity)
        lib.SetTipString(self.cbopa,'Input value and "ENTER"')
        yloc += 30
        #
        wx.StaticText(self.panel,-1,"Isovalue:" ,pos=(xloc,yloc),
                      size=(60,18))
        self.cbval=wx.ComboBox(self.panel,-1,'',choices=self.isovaluelst, \
                               pos=(xloc+75,yloc-3), size=(80,hcb),
                               style=wx.TE_PROCESS_ENTER)
        self.cbval.Bind(wx.EVT_COMBOBOX,self.OnIsoValue)
        self.cbval.Bind(wx.EVT_TEXT_ENTER,self.OnIsoValue)
        lib.SetTipString(self.cbval,'Input value and "ENTER"')

        yloc += 25
        wx.StaticText(self.panel,-1,"Interpolation:" ,pos=(xloc,yloc),
                      size=(85,18))
        self.spip=wx.SpinCtrl(self.panel,-1,value=str(self.interpol),
                              pos=(xloc+95,yloc),size=(60,22),
                              style=wx.SP_ARROW_KEYS,min=self.minipo,
                              max=self.maxipo)
        self.spip.Bind(wx.EVT_SPINCTRL,self.OnInterpolate)
        lib.SetTipString(self.spip,'Choose interpolation points number.')

        yloc += 20
        wx.StaticText(self.panel,-1,"Color:",pos=(xloc,yloc),size=(55,18))
        yloc += 20
        wx.StaticText(self.panel,-1,"+",pos=(xloc+10,yloc),size=(10,18))
        self.cbcolp=wx.ComboBox(self.panel,-1,'',choices=self.colortxt, \
                               pos=(xloc+45,yloc-3), size=(110,hcb),
                               style=wx.CB_READONLY)
        self.cbcolp.Bind(wx.EVT_COMBOBOX,self.OnColorPos)
        lib.SetTipString(self.cbcolp,'Choose color for positive value. "---" is dummy')

        yloc += 25
        wx.StaticText(self.panel,-1," -" ,pos=(xloc+10,yloc),size=(10,18))
        self.cbcoln=wx.ComboBox(self.panel,-1,'',choices=self.colortxt, \
                               pos=(xloc+45,yloc-3), size=(110,hcb),
                               style=wx.CB_READONLY)
        self.cbcoln.Bind(wx.EVT_COMBOBOX,self.OnColorNeg)
        lib.SetTipString(self.cbcoln,'Choose color for negative value. "---" is dummy')
        yloc += 25
        wx.StaticText(self.panel,-1,"bg" ,pos=(xloc+7,yloc),size=(20,18))
        self.cbcolbg=wx.ComboBox(self.panel,-1,'',choices=self.bgcolorlst, \
                               pos=(xloc+45,yloc-3), size=(110,hcb),
                               style=wx.CB_READONLY)
        self.cbcolbg.Bind(wx.EVT_COMBOBOX,self.OnColorBG)
        lib.SetTipString(self.cbcolbg,'Choose background color. "---" is dummy')
        self.cbcolbg.SetStringSelection('---') #str(self.parentbgcolor))
        yloc += 25
        """
        wx.StaticText(self.panel,-1,"Opacity:" ,pos=(xloc,yloc),size=(45,18))
        self.cbopa=wx.ComboBox(self.panel,-1,'',choices=self.opacitylst, \
                               pos=(xloc+60,yloc-3), size=(50,hcb),
                               style=wx.TE_PROCESS_ENTER)
        self.cbopa.Bind(wx.EVT_TEXT_ENTER,self.OnOpacity)
        self.cbopa.Bind(wx.EVT_COMBOBOX,self.OnOpacity)
        #self.cbopa.SetToolTipString('Input value and "ENTER"')
        lib.SetTipString(self.cbopa,'Input value and "ENTER"')
        yloc += 25
        """
        wx.StaticText(self.panel,-1,"Model:" ,pos=(xloc,yloc),size=(50,18))
        self.cbmdl=wx.ComboBox(self.panel,-1,'',choices=self.molmodellst, \
                               pos=(xloc+60,yloc-3), size=(95,hcb),
                               style=wx.CB_READONLY)
        self.cbmdl.Bind(wx.EVT_COMBOBOX,self.OnMolModel)
        lib.SetTipString(self.cbmdl,'Molecular model')

        yloc += 25
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        #yloc += 25
        yloc += 8
        self.btndel=wx.Button(self.panel,-1,"Del",pos=(xloc+20,yloc),size=(35,22))
        self.btndel.Bind(wx.EVT_BUTTON,self.OnRemove)
        lib.SetTipString(self.btndel,'Remove cube object')
        self.btndraw=wx.Button(self.panel,-1,"Draw",pos=(xloc+90,yloc),size=(50,22))
        self.btndraw.Bind(wx.EVT_BUTTON,self.OnDraw)
        lib.SetTipString(self.btndraw,'Redraw')

    def OnRemoveMO(self,event):
        grp = self.grpchoice.GetStringSelection()
        datgrp = self.curdat + ':' + grp
        self.SwitchDrawAndRemoveGroup(datgrp)
        """
        self.donotshowlst.append(datgrp)
        self.RemoveMO()
        self.RedrawMO(current=None)
        """
    def OnChangeMOSign(self,event):
        dat = self.itemchoice.GetStringSelection()
        if len(dat) <= 0: return
        self.curnum = self.itemchoice.GetSelection()
        ithmo = self.gridmo.morange[1] - self.curnum
        self.gridmo.ChangeSignOfMO(ithmo)
        self.DrawCubeData(ithmo=ithmo) #ithmo-1)
        mess = 'Sign of MO was changed, ithmo= ' + str(ithmo+1)
        self.ConsoleMessage(mess)

    def MergeWithExistingMol(self):
        if self.mode != 2: return
        ###self.winzero = self.model.winctrl.GetWin('Open DrawMOsWin')
        try:
            mol = self.model.mol
            if mol is None:
                mess = 'No current molecule in MDLWIN'
                wx.MessageBox(mess,'DrawMOsWin.MergeWithExistingMol')
                return
        except: pass
        # get filename
        wcard = "GMS output(*.out;*.log)|*.out;*.log|orb file(*.orb)|*.orb|"
        wcard += "all(*.*)|*.*"
        filename = lib.GetFileName(self,wcard,"r",True,"")
        if len(filename) <= 0: return
        #
        self.merge = True
        self.MakeMOCubeData(filename,check=False,merge=True)

    def MakeGridMO(self,nocc,atomcc,eiglst,symlst,moslst,basdic):
        toev = 27.2113845
        gridmo = GridMO(self)
        gridmo.noccs    = nocc[:] # [nocca,noccb]
        gridmo.homo     = nocc[0] - 1
        gridmo.lumo     = nocc[0]
        gridmo.natoms   = len(atomcc) # natoms
        gridmo.nbasis   = len(eiglst) # nbasis
        gridmo.atomcc   = atomcc[:]
        #####gridmo.basoptlst= basoptlst
        #gridmo.coorddic = retcoord
        eiglst = [x * toev for x in eiglst]
        gridmo.eiglst   = eiglst[:]
        gridmo.symlst   = symlst[:]
        gridmo.moslst   = moslst[:]
        gridmo.basdic   = basdic
        size0 = self.model.setctrl.GetParam('cube-mo-grid-size')
        gridmo.SetSize0(size0)
        morange = self.model.setctrl.GetParam('cube-mo-range') # #occ-#vac
        gridmargin = self.model.setctrl.GetParam('cube-mo-grid-margin')
        gridmo.gridmargin = gridmargin
        minmo = gridmo.homo - morange[0] + 1
        if minmo < 0: minmo = 0
        maxmo = gridmo.lumo + morange[1] - 1
        nmos = len(gridmo.eiglst)
        if maxmo > nmos: maxmo = nmos - 1
        gridmo.morange  = [minmo,maxmo] # homo -10, lumo + 8
        morange1 = [minmo+1,maxmo+1]

        return gridmo

    def OnMolModel(self,event):
        modeldic = {'line':0, 'stick':1, 'ball-and-stick':2, 'CPK':3}
        model = self.cbmdl.GetStringSelection()
        modelnum = modeldic[model]
        self.model.ChangeDrawModel(modelnum)

    def OnOverlay(self,event):
        pass

    def OnUp(self,event):
        try:
            curitem = self.itemchoice.GetSelection()
            curitem -= 1
            if curitem < 0:
                mess = 'No more data'
                wx.MessageBox(mess,'DrawCubeData_Frm.OnUp')
                return
            self.curitem = curitem
            self.itemchoice.SetSelection(self.curitem)
            self.Draw()
            # select level in PoltEnergy
            if self.drwene is not None: self.SelectInPlotEnergy()
        except: pass

    def OnDown(self,event):
        try:
            maxmo = self.itemchoice.GetCount()
            curitem = self.itemchoice.GetSelection()
            curitem += 1
            if curitem >= maxmo:
                mess = 'No more data'
                wx.MessageBox(mess,'DrawCubeData_Frm.OnDown')
                return
            self.curitem = curitem
            self.itemchoice.SetSelection(self.curitem)
            self.Draw()
            # select level in PoltEnergy
            if self.drwene is not None: self.SelectInPlotEnergy()
        except: pass

    def OnMOChoice(self,event):
        if self.mode == 2:
            self.curitem = self.itemchoice.GetSelection()
            grp = self.grpchoice.GetStringSelection()
            dat = self.datchoice.GetStringSelection()
            datgrp = dat + ':' + grp
            self.curmodic[datgrp] = self.curitem
            # select level in PoltEnergy
            if self.drwene is not None: self.SelectInPlotEnergy()
        else:
            self.curdat = self.itemchoice.GetStringSelection()
            curmol = self.model.molctrl.GetMolIndex(self.curdat)
            self.model.SwitchMol(curmol,False,False,notify=False)
        self.OnDraw(1)

    def OnGroupChoice(self,event):
        self.curgrp = self.grpchoice.GetStringSelection()
        self.curdat = self.datchoice.GetStringSelection()

        datgrp = self.curdat + ':' + self.curgrp
        self.gridmo   = self.gridmodic[datgrp]
        self.curitem  = self.curmodic[datgrp]
        # set orbital energies to Item choice combo box
        self.SetItemsToMOChoice()
        self.itemchoice.SetSelection(self.curitem)
        ithmo = self.gridmo.morange[1] - self.curitem
        self.DrawCubeData(ithmo=ithmo)
        # select level in PoltEnergy
        if self.drwene is not None: self.SelectInPlotEnergy()

    def SelectInPlotEnergy(self):
        if self.drwene is None: return
        try:
            idx = -1
            curgrpnum = self.grpchoice.GetSelection()
            curorbnum = self.GetCurrentMONumber()
            ndat = len(self.eigidxlst[curgrpnum])
            for i in range(ndat):
                if self.eigidxlst[curgrpnum][i] == curorbnum:
                    idx = i
                    break
            self.drwene.orbgraph.SelectOrbital(curgrpnum,idx)
            if idx < 0:
                mess = 'The current level is out of range in Orbital energy plot'
                self.ConsoleMessage(mess)
        except: pass

    def SaveCurMO(self):
        curdatgrp = self.curdat + ':' + self.curgrp
        self.curmodic[curdatgrp] = self.itemchoice.GetSelection()

    def OnDataChoice(self,event):
        # save current
        self.SaveCurMO()
        self.curdat = self.datchoice.GetStringSelection()
        self.DataChange()

        if self.drwene:
            self.drwene.Destroy()
            self.drwene=None
            self.PlotOrbitalEnergies()
            

    def OnDataChoiceRightDown(self,event):
        data = self.datchoice.GetStringSelection()
        self.DisplayLongName(data)

    def OnGroupChoiceRightDown(self,event):
        dat = self.datchoice.GetStringSelection()
        grp = self.grpchoice.GetStringSelection()
        datgrp = dat + ':' + grp

        #print(('self.grporgdic',self.grporgdic))

        data = self.grporgdic[datgrp]
        title = 'original data name'
        winsize = [300,100]
        subwin.TextBox_Frm(self,title=title,winsize=winsize,text=data,
                  ok=False,cancel=False)

    def OnItemChoiceRightDown(self,event):
        data = self.itemchoice.GetStringSelection()
        self.DisplayLongName(data)

    def DisplayLongName(self,data):
        title = 'Long data name'
        winsize = [300,100]
        subwin.TextBox_Frm(self,title=title,winsize=winsize,text=data,
                  ok=False,cancel=False)

    def DataChange(self):
        """ self.mode == 2 """
        #self.datchoice.SetStringSelection(self.curdat)
        self.curgrp = self.curgrpdic[self.curdat]
        datgrp = self.curdat + ':' + self.curgrp
        self.gridmo = self.gridmodic[datgrp]
        self.curnum = self.curmodic[datgrp]
        # switch  molecule in MDLWIN
        curmol = self.model.molctrl.GetMolIndex(self.curdat)
        self.model.SwitchMol(curmol,False,False,notify=False)
        # change combo box list
        self.SetItemsToMOChoice()

        self.grplst = self.grplstdic[self.curdat]
        self.grpchoice.SetItems(self.grplst)
        self.grpchoice.SetStringSelection(self.curgrp)

        if len(self.grplst) > 1 and self.labelgroup: self.drawlablegroup = True
        else: self.drawlablegroup = False

        self.Draw(redraw=True)

    def OnResetMol(self,event):
        curmol = self.model.mol.name
        if self.mode == 2:
            if curmol not in self.datlst: return
            # save current
            self.SaveCurMO()

            self.model.Message('Restored molecule object',0,'')
            self.curdat = curmol
            self.DataChange()
        else:
            if curmol not in self.itemlst: return
            self.curdat = curmol
            self.itemchoice.SetStringSelection(self.curdat)
            self.DrawCubeData(ithmo=None)

    def OnNotify(self,event):
        #if event.jobid != self.winlabel: return
        try: item=event.message
        except: return
        if item == 'SwitchMol':
            self.model.ConsoleMessage('Reset mol object in "DrawCubeData_Frm"')
            self.OnResetMol(1)

    def GetCubeFileAndMakeCubeObjDic(self):
        filename=self.viewer.GetCubeFile()
        if os.path.exists(filename):
            base,ext=os.path.splitext(filename)
            self.cubefile=filename
            if ext == '.den' or ext == '.mep' or ext == '.cub':
                err=self.AddToCubeObjDic(filename)
            else:
                mess='The file "'+filename+'" is not cube data (ext should be ".mep" or ".den"'
                lib.MessageBoxOK(mess,"")
                self.OnClose(1)
        else:
            mess='Cube file is not found. filename="'+filename+'"'
            lib.MessageBoxOK(mess,"")
            self.OnClose(1)

    def GetDrawPanelParams(self):
        #self.ondraw=self.btndraw.GetValue()
        return [self.style,self.isovalue,self.interpol,self.colorpos,self.colorneg,
                self.opacity,self.ondraw]

    def SetDrawPanelParams(self,params):
        self.style=params[0]; self.isovalue=params[1]; self.interpol=params[2]
        self.colorpos=params[3]; self.colorneg=params[4]; self.opacity=params[5]
        self.ondraw=params[6]
        self.SetParamsToWidgets()

    def SetParamsToWidgets(self):
        self.rbtsold.SetValue(True)
        if self.style == 1: self.rbtwire.SetValue(True)
        self.cbval.SetValue(str(self.isovalue))
        self.spip.SetValue(self.interpol)
        self.cbcolp.SetValue(self.colorpos) #StringSelection(self.colorpos)
        self.cbcoln.SetValue(self.colorneg) #StringSelection(self.colorneg)
        self.cbopa.SetValue(str(self.opacity))

    def OnSolid(self,event):
        self.style=0
        if self.ondraw: self.OnDraw(1)

    def OnWire(self,event):
        self.style=1
        self.opacity = 1.0
        self.cbopa.SetStringSelection('1.0')
        if self.ondraw: self.OnDraw(1)

    def OnIsoValue(self,event):
        value=self.cbval.GetValue()
        try: self.isovalue=float(value)
        except:
            mess="error input for Draw value."
            lib.MessageBoxOK(mess,"")
            return
        #
        if self.ondraw: self.OnDraw(1)

    def OnInterpolate(self,event):
        self.interpol=self.spip.GetValue()
        #
        if self.ondraw: self.OnDraw(1)

    def OnOpacity(self,event):
        value=self.cbopa.GetValue()
        try: self.opacity=float(value)
        except:
            mess="error input for Opacity value (0-1)."
            lib.MessageBoxOK(mess,"")
            return
        #
        if self.ondraw: self.OnDraw(1)

    def OnColorPos(self,event):
        color=self.cbcolp.GetValue()
        if color == '---': return
        self.rgbpos=self.GetColor(color,self.cbcolp)
        if len(self.rgbpos) <= 0: return
        if self.ondraw: self.OnDraw(1)

    def OnColorNeg(self,event):
        color=self.cbcoln.GetValue()
        if color == '---': return
        self.rgbneg=self.GetColor(color,self.cbcoln)
        if len(self.rgbneg) <= 0: return
        if self.ondraw: self.OnDraw(1)

    def OnColorBG(self,event):
        if self.model.mol is None:
            mess = 'No molecule in MDLWIN'
            wx.MessageBox(mess,'DrawCube_Frm.OnColorBG')
            return
        color=self.cbcolbg.GetValue()
        if color == '---': return
        self.parentbgcolor = self.GetColor(color,self.cbcolbg)
        if len(self.parentbgcolor) <= 0: return
        self.model.ChangeBackgroundColor(self.parentbgcolor)
        if self.ondraw: self.OnDraw(1)

    def GetColor(self,color,obj):
        if color == 'palette':
            obj.Disable(); obj.SetValue('---'); obj.Enable()
            rgbcol=lib.ChooseColorOnPalette(self,False,1.0) # parent,rgb255,opacity
            if len(rgbcol) <= 0: return []
            else: return rgbcol
        else: return const.RGBColor[color]

    def OnDensity(self,event):
        self.property=0
        self.cubcmb.SetItems(self.denobjlst)
        self.cubcmb.SetValue(self.curden)

    def OnMEP(self,event):
        self.property=1
        self.cubcmb.SetItems(self.mepobjlst)
        self.cubcmb.SetValue(self.curmep)

    def OnOthers(self,event):
        #print ('property: others. not implemented yet.')
        self.property=2

    def MakePolygonData(self,ithmo=None):
        polys = []
        value = self.isovalue # threshold value
        intp  = self.interpol
        test=True
        if test:
        #try:
            if ithmo is None:
                cubeobj = self.cubeobjdic[self.curdat]
                cubefile=cubeobj.file
                if len(cubefile) <= 0:
                    mess='No cube file for property='+prop
                    lib.MessageBoxOK(mess,"MakePloygonData")
                    return []
                # ex,ey,ez,boxmin are in Angs
                fval,ex,ey,ez,boxmin = rwfile.ReadCubeFile(cubefile)
            else: # MO plot
                fval,ex,ey,ez,boxmin = \
                              self.gridmo.ComputeMOValues(ithmo,value,intp,
                                                          cmpord=self.cmpord)
            #
            polys = MC.CubePolygons(fval,ex,ey,ez,boxmin,value,intp)

        #except:
        #    print ('Failed to create polygons in MakePolygonData.')
        return polys

    def OnInfo(self,event):
        self.DispCubeDataInfo()

    def OnCubeData(self,event):
        if self.property == 0:
            self.curden=self.cubcmb.GetValue() #GetStringSelection()
        if self.property == 1:
            self.curmep=self.cubcmb.GetValue() #GetStringSelection()

    @staticmethod
    def MakeCubeDataInfoText(file,prop,natoms,info):
        f61='%6.1f'; f64='%6.4f'; fi4='%4d'
        #
        txtprop='Property: '+prop+'\n'
        txtfile='Cube file: '+file+'\n'
        txtatm=' Number of atoms='+str(natoms)+'\n'
        txtcnt=' Center: x='+(f61 % info[0][0]).strip()
        txtcnt=txtcnt+',  y='+(f61 % info[0][1]).strip()
        txtcnt=txtcnt+',  z='+(f61 % info[0][2]).strip()+'\n'

        txtx=' x: min='+(f61 % info[1])+', max='+(f61 % info[2])+', nptx='+str(info[3])+'\n'
        txty=' y: min='+(f61 % info[4])+', max='+(f61 % info[5])+', npty='+str(info[6])+'\n'
        txtz=' z: min='+(f61 % info[7])+', max='+(f61 % info[8])+', nptz='+str(info[9])+'\n'

        txtval=' value: min= '+(f64 % info[10])
        txtval=txtval+', max= '+(f64 % info[11])+'\n'

        mess=txtprop+'\n'+txtfile+'\n'+txtatm+txtcnt+txtx+txty+txtz+'\n'+txtval
        return mess

    def CubeDataInfo(self,obj):
        f61='%6.1f'; f64='%6.4f'; fi4='%4d'
        if obj is None: return

        prop=obj.prop
        info=obj.gridinfo
        file=obj.file
        natoms=obj.natoms

        txt=[]
        txtprop='Property: '+prop+'\n'
        txtfile='Cube file: '+file+'\n'
        txtatm=' Number of atoms='+str(natoms)+'\n'
        txtcnt=' Center: x='+(f61 % info[0][0]).strip()
        txtcnt=txtcnt+',  y='+(f61 % info[0][1]).strip()
        txtcnt=txtcnt+',  z='+(f61 % info[0][2]).strip()+'\n'

        txtx=' x: min='+(f61 % info[1])+', max='+(f61 % info[2])+', nptx='+str(info[3])+'\n'
        txty=' y: min='+(f61 % info[4])+', max='+(f61 % info[5])+', npty='+str(info[6])+'\n'
        txtz=' z: min='+(f61 % info[7])+', max='+(f61 % info[8])+', nptz='+str(info[9])+'\n'

        txtval=' value: min= '+(f64 % info[10])
        txtval=txtval+', max= '+(f64 % info[11])+'\n'

        mess=txtprop+'\n'+txtfile+'\n'+txtatm+txtcnt+txtx+txty+txtz+'\n'+txtval

        return mess

    def GetCurrentCubeObj(self):
        if self.property == 3: return 'MO',None
        else:
            curname = self.itemlst[self.curitem]
            return 'Cube',self.cubeobjdic[curname]

    def OnRemove(self,event):
        #try:
        test=True
        if test:
            label = 'cube-data'
            self.mdlwin.draw.DelDrawObj(label)
            self.TextMessage1([],[])
            if self.mode == 2:
                grplst = self.grpchoice.GetItems()
                for i in range(len(grplst)):
                    datgrp = self.curdat + ':' + grplst[i]
                    self.donotshowlst.append(datgrp)

            self.model.DrawMol(True)
        #except: pass
    def RemoveMO(self):
        label = 'cube-data'
        self.mdlwin.draw.DelDrawObj(label)
        self.TextMessage1([],[])
        self.model.DrawMol(True)

    def OnDraw(self,event):
        self.donotshowlst = []
        self.Draw()

    def Draw(self,redraw=False):
        if self.mode == 0 or self.mode == 1:
            dat = self.itemchoice.GetStringSelection()
            if len(dat) <= 0: return
            self.curitem = self.itemchoice.GetStringSelection()
            self.DrawCubeData(ithmo=None)

        elif self.mode == 2:
            dat = self.itemchoice.GetStringSelection()
            if len(dat) <= 0:
                mess = 'No MO is choosen'
                wx.MessageBox(mess,'DrawCubeData_Frm.OnDraw')
                return

            if redraw: self.RedrawMO(current=None)
            else:
                self.curitem = self.itemchoice.GetSelection()
                ithmo = self.gridmo.morange[1] - self.curitem
                self.DrawCubeData(ithmo=ithmo) #ithmo-1)

    def SetPolygonColor(self,polyg,rgbpos,rgbneg,opacity):
        if len(polyg) <= 0: return []
        if len(polyg[0]) <= 0: return []
        n0 = len(polyg[0])
        n1 = len(polyg[1])
        polyg0 = list(polyg[0])
        polyg1 = list(polyg[1])
        for i in range(n0):
            lst = list(polyg0[i])
            lst.append(rgbpos)
            lst.append(opacity)
            polyg0[i] = lst
        for i in range(n1):
            lst = list(polyg1[i])
            lst.append(rgbneg)
            lst.append(opacity)
            polyg1[i] = lst
        return [polyg0,polyg1]


    def DrawCubeData(self,ithmo=None,fontstyle=None):
        f64 = '%6.4f'
        #try:
        # check molecular data in model
        if not self.model.mol:
            prop,obj=self.GetCurrentCubeObj()
            natoms=obj.natoms
            if natoms <= 0:
                mess='No molecule data in MDLWIN. Read structure data.'
                lib.MessageBoxOK(mess,"DrawCubeData_Frm:OnDraw")
                #self.btndraw.SetValue(False)
                self.ondraw=False
                return
            else: pass
        """
        if self.model.mol.cubeobj is None:
            mess = 'The current molecule does not have cube object.'
            wx.MessageBox(mess,'DrawCubeData_Frm.OnDraw')
            return
        """
        label='cube-data'
        # parameters for draw
        thick = self.model.setctrl.GetParam('cube-line-thick')
        if thick is None: thick = 0.5
        pltfrm,release=lib.GetPlatformAndRelease()
        if pltfrm == 'MACOSX': thick *= 2
        ###params=[self.style,self.rgbpos,self.rgbneg,self.opacity,thick]
        params=[self.style,thick]
        # make polygon data
        try: self.mdlwin.BusyIndicator('On','Drawing polygons ...')
        except: pass

        polyg = self.MakePolygonData(ithmo=ithmo)

        if len(polyg) <= 0:
            try: self.mdlwin.BusyIndicator('Off','Drawing polygons ...')
            except: pass
            mess = 'No polygon data to draw'
            wx.MessageBox(mess,'cube.DrawCubeData')
            return

        polyg = self.SetPolygonColor(polyg,self.rgbpos,self.rgbneg,
                                     self.opacity)
        polyg0 = polyg[0][:]
        polyg1 = polyg[1][:]
        #polyg = [polyg[0][:],polyg[1][:]]
        # text message
        if ithmo is None:
            #prop,obj=self.GetCurrentCubeObj()
            obj = self.cubeobjdic[self.curdat]
            name=obj.name; name=name.split('.')[0]
            mess = 'Cube:' + name
            self.draw.SetDrawData(label,'CUBE',[params,polyg])

            self.model.DrawMol(True)
            messlst =[mess]
            self.TextMessage1(messlst) #,  # color=self.textmessagecolor,
                              #fontstyle=fontstyle)

            self.ondraw = True
            return
        else:
            prop = 'MO'
            name = self.gridmo.name + '-mo' + str(ithmo+1)
            mess = prop + ':' + name
            if ithmo == self.gridmo.homo: mess += '(HOMO)'
            if ithmo == self.gridmo.lumo: mess += '(LUMO)'

            self.Message(mess,0,'')


        mess += ',' + 'isovalue=' + (f64 % self.isovalue)

        datgrp = self.curdat + ':' + self.curgrp
        self.grppolygdic[datgrp] = [polyg0,polyg1,mess]

        polyg,messlst = self.MergeGroupPolyg()

        #print 'polyg0',polyg0
        #print 'polyg1',polyg1
        #print 'messlst',messlst

        #print 'len(polyg[0]',len(golyg[0])
        #print 'len(polyg[1]',len(golyg[1])

        #ployg = [polyg0,polyg1]
        """
        [polyg0,polyg1,mess] = self.grppolygdic[self.curgrp]
        polyg = [polyg0,polyg1]
        messlst = [mess]
        """
        if len(polyg[0]) <= 0 and len(polyg[1]) <= 0:
            mess = 'No polygon data to draw'
            wx.MessageBox(mess,'DrawCubeData_Frm.DrawCubeData')
            return

        try: self.mdlwin.BusyIndicator('Off')
        except: pass

        self.draw.SetDrawData(label,'CUBE',[params,polyg])
        self.TextMessage1(messlst)
        self.model.DrawLabelGroup(self.drawlablegroup,drw=False)
        self.model.DrawMol(True)


        self.ondraw = True

        #except:
        #    self.OnRemove(1)
        #    self.ondraw = False

    def BuildCubeMol(self,atomcc,merge=False):
        mol = molec.Molecule(self.model)
        mol.SetAtoms(atomcc,elm=False,angs=False) # coords in BOHR in cube file
        if merge:
            curmol = self.model.molctrl.GetCurrentMolIndex()
            mrgatm = mol.atm
            self.model.MergeMolecule(mrgatm,check=True,drw=False,gname='MOL')
            self.model.mol.AddBondUseBL([])
            mol = self.model.mol
            self.model.RemoveMol()
        else:
            natm = len(atomcc)
            for atom in mol.atm: atom.grpnam = 'MOL1'
            mol.AddBondUseBL([])
        return mol

    def UpdateGroupOrgDict(self,oldname,newname):
        dellst = []
        #print(('grporgdic in UpdateGroupOrgDic',self.grporgdic))
        #print(('oldname,newname in UpdateGroupOrgDic',oldname,newname))
        for key,val in list(self.grporgdic.items()):
            nc = key.find(':')
            if nc >= 0:
                key1 = key[:nc].strip()
                key2 = key[nc+1:].strip()
                #print(('key1,key2',key1,key2))

                if key1 == oldname:
                    dellst.append(key)
                    newkey = key1 + ':' + newname
                    self.grporgdic[newkey] = val
        if len(dellst) > 0: del sel.fgrporgdic[dellst[i]]



    def OnClose(self,event):
        # Reset original PopupMenu in MDLWIN
        try: self.model.mdlwin.ClosePopupMenu()
        except: pass

        try:
            #self.OnRemove(1)
            self.model.RemoveMol(allmol=True)
        except: pass
        #try: # Close all DrawMOsWin windows
        try: self.model.winctrl.Close(self.winlabel)
        except: pass

        if self.winlabel == 'Open DrawMOsWin':
            try:
                winnamlst = self.model.winctrl.GetOpenedName()
                for nam in winnamlst:
                    if nam.find('Open DrawMOsWin') >= 0:
                        self.model.winctrl.Close(nam)
            except: pass
        try:
            #self.OnRemove(1)
            self.Destroy()
        except: pass

    def AddToCubeObjDic(self,filename):
        gridinfo,natoms,atomcc=self.ReadGridDataInCubeFile(filename)
        if len(gridinfo) < 0: return 1
        head,tail = os.path.split(filename)
        name,ext  = os.path.splitext(tail)
        prp = 'Cube'
        # make cube object
        cube = CubeObj()
        cube.file     = filename
        cube.gridinfo = gridinfo
        cube.name     = name
        cube.atomcc   = atomcc
        cube.natoms   = natoms
        if len(self.itemlst) > 0:
            count = 0
            for exname in self.itemlst:
                if exname.find(name) >= 0:
                    count += 1
            if count > 0: name += '(' + str(count) + ')'

        #####self.BuildCubeMol(cube)
        self.curdat = name
        cube.name = name
        self.cubeobjdic[name] = cube
        if '' in self.itemlst: self.itemlst.remove('')
        self.itemlst.append(self.curdat)
        self.itemchoice.SetItems(self.itemlst)
        self.itemchoice.SetStringSelection(self.curdat)
        #Xself.cubedatalst.append(name)

        mol = self.BuildCubeMol(atomcc)
        mol.name    = name
        mol.inpfile = filename
        mol.cubeobj = cube
        self.model.SetUpBuildMol(mol)

        self.DrawCubeData()

        return 0

    def MergeGroupPolyg(self,current=True):
        messlst      = []
        grplst = self.grpchoice.GetItems()
        if current:
            datgrp0 = self.curdat + ':' + self.curgrp
            polyg0 = self.grppolygdic[datgrp0][0][:]
            polyg1 = self.grppolygdic[datgrp0][1][:]
            messlst.append(self.grppolygdic[datgrp0][2])
        else:
            polyg0 = []
            polyg1 = []
        for grp in grplst:
            datgrp = self.curdat + ':' + grp
            if current and datgrp == datgrp0: continue
            if datgrp in self.donotshowlst: continue
            addpolyg0 = self.grppolygdic[datgrp][0]
            addpolyg1 = self.grppolygdic[datgrp][1]
            nadd0 = len(addpolyg0)
            nadd1 = len(addpolyg1)
            for i in range(nadd0): polyg0.append(addpolyg0[i][:])
            for i in range(nadd1): polyg1.append(addpolyg1[i][:])
            messlst.append(self.grppolygdic[datgrp][2])
        return [polyg0,polyg1],messlst

    def MakeMOCubeData(self,filename,check=True,merge=False,messout=True):
        self.property = 3
        self.merge = merge
        #
        name = lib.BaseNameInFileName(filename)
        name1 = self.model.CheckSameMolName(name)
        if check:
            if name1 != name:
                mess = 'Data with the same name exists. \n'
                mess += ' Please rename file and try again.'
                wx.MessageBox(mess,'DrawCubeData_Frm.MakeMOCubeData')
                return
        head,tail = os.path.split(filename)
        base,ext  = os.path.splitext(tail)
        if ext not in ['.out','.orb','log']: return
        self.cmpord = 0
        if ext == '.orb': # orbital file
            if merge:
                mess = '"Merge" supports only from GMS output'
                wx.MessageBox(mess,'DrawCubeData.MakeMOCubeData')
                return
            orbinfo,atomcclst,eiglstlst,\
                      symlstlst,moslstlst,basdiclst =\
                      rwfile.ReadMOsInOrbFile(filename)
            self.ngrps = len(atomcclst)
            title = orbinfo['TITLES'][0]
            items = title.split('/')
            if len(items) > 1:
                title = items[1]
                prog = items[0].strip().upper()
                if   prog == 'GAMESS': self.cmpord = 0
                elif prog == 'LOTUS':  self.cmpord = 2
                else:                  self.cmpord = 1
            titlelst   = orbinfo['TITLES']

            natomslst  = orbinfo['NATOMS']
            nbasislst  = orbinfo['NBASIS']
            grpnamelst = []
            noccslst   = []
            for i in range(self.ngrps):
                noccslst.append([orbinfo['NOCCA'][i],orbinfo['NOCCB'][i]])
                #grpnamelst.append('MOL'+str(i+1))
            basoptlst  = [] # no in .orb file
        elif ext == '.out' or ext == '.log': # GAMESS output file (.lig or .out)
            natoms,nbasis,atomcc,noccs,eiglst,symlst,moslst,basdic,basoptlst = \
                      rwfile.ReadMOsInGMSOutput(filename)
            if natoms < 0: return
            if not self.CheckBasis(nbasis,basdic['shltyp']):
                return
            self.ngrps = 1
            grpnamelst = []
            natomslst = [natoms]; nbasislst = [nbasis]; noccslst  = [noccs]
            atomcclst = [atomcc]; symlstlst = [symlst]; eiglstlst = [eiglst]
            moslstlst = [moslst]; basdiclst = [basdic]
        # group looop
        curdat = name
        #oldname = name
        if merge:
            grplst = self.grplstdic[self.curdat]
            curdat = self.curdat
            if self.labelgroup: self.drawlablegroup = True
        else: grplst = []

        for ig in range(self.ngrps):
            if ext == '.orb' and ig > 0:
                merge = True
                self.merge = True
                if self.labelgroup: self.drawlablegroup = True
            natoms = natomslst[ig]
            nbasis = nbasislst[ig]

            gridmo = self.MakeGridMO(noccslst[ig],atomcclst[ig],eiglstlst[ig],
                                     symlstlst[ig],moslstlst[ig],basdiclst[ig])
            gridmo.file = filename
            gridmo.prop = 'MO'
            gridmo.cmpord = self.cmpord
            try: grpname = grpnamelst[ig]
            except:
                if merge:
                    grpnamelst = self.grpchoice.GetItems()
                    grpname = self.CheckName('MOL',grpnamelst)
                else: grpname = 'MOL1'

            [minmo,maxmo]   = gridmo.morange
            self.curnum     = maxmo - gridmo.homo
            curdatgrp = curdat + ':' + grpname
            gridmo.name = curdatgrp # name

            self.moobjdic[curdatgrp] = gridmo #cube
            self.curmodic[curdatgrp] = self.curnum
            #
            curgrp = grpname
            curdatgrp = curdat + ':' + curgrp
            self.gridmodic[curdatgrp] = gridmo

            mol = self.BuildCubeMol(gridmo.atomcc,merge=merge)
            mol.inpfile = gridmo.file
            mol.cubeobj = gridmo
            mol.grpnam = grpname
            if not merge: mol.name = curdat # = name
            self.model.SetUpBuildMol(mol)
            grplst.append(grpname)
            self.grporgdic[curdatgrp] = name
            # print
            if messout: self.PrintMOInfo(filename,natoms,nbasis,gridmo.homo,
                                         gridmo.lumo,gridmo.morange,basoptlst)
        #
            self.curdat = curdat
            self.grplst = grplst
            self.grplstdic[self.curdat] = self.grplst[:]

            self.curgrp = grpname
            curdatgrp = self.curdat + ':' + self.curgrp
            self.curgrpdic[self.curdat] = self.curgrp
            self.gridmo = gridmo

            self.SetItemsToMOChoice()
            self.grpchoice.SetItems(self.grplst)
            self.grpchoice.SetStringSelection(self.curgrp)

            if not merge: self.datlst.append(name)
            self.datchoice.SetItems(self.datlst)
            self.datchoice.SetStringSelection(self.curdat)
            #
            ithmo = self.gridmo.morange[1] - self.curnum

            self.DrawCubeData(ithmo=ithmo)

    def CheckName(self,name,namelst):
        """ Assuming that "name" consists of "string" + "str(sequence number)" """
        newname = name
        nstr = len(name)
        count = 0
        for dat in namelst:
            if dat.startswith(name,0,nstr): count += 1
        newname = name + str(count+1)
        #if count > 0: newname = name + str(count+1)
        return newname

    def PrintMOInfo(self,filename,natoms,nbasis,homo,lumo,morange,basoptlst):
        morange1 = [morange[0]+1,morange[1]+1]
        mess  = 'MO info in ' + filename + '\n'
        mess += '    GAMESS ver. 1 MAY 2013 (R1)\n'
        mess += '    Number of atoms   = ' + str(natoms) + '\n'
        mess += '    Number of MOs     = ' + str(nbasis) + '\n'
        mess += '    HOMO              = ' + str(homo+1) + '\n'
        mess += '    LUMO              = ' + str(lumo+1) + '\n'
        mess += '    MO range for draw = ' + str(morange1)
        self.ConsoleMessage(mess)
        try:
            if len(basoptlst) > 0:
                mess =  'BASIS SET OPTIONS:\n'
                mess += '    '
                for key,val in basoptlst:
                    mess += key + '=' + val + ', '
                mess = mess[:-2]
                self.ConsoleMessage(mess)
        except: pass

    def CurrentMolPosition(self):
        """ return center """
        pass

    def MolSize(self):
        """ Return xmin,xmax,ymin,ymax,zmin,zmax"""
        pass

    def CheckBasis(self,nbasis,shltyp):
        ans = True
        fbas = False
        mess = 'Sorry, '
        nshl = len(shltyp)
        ibas = 0
        #print 'shlbas',shlbas
        for ish in range(nshl):
            ibas += shltyp[ish]
            if shltyp[ish] == 10:
                mess += 'F bsis is not supported.'
                ans  = False
                fbas = True
                break
        if not fbas and ibas != nbasis:
            ans = False
            mess += '5D basis ? is not supported'
        if not ans:
            wx.MessageBox(mess,'DrawCubeData_Frm.CheckBasis')
        return ans

    def SetItemsToMOChoice(self):
        ff12 = '%12.3f'; fi3 = '%3d'

        eiglst = []
        orgord = []
        for i in range(self.gridmo.morange[0],self.gridmo.morange[1]+1):
            eiglst.append(self.gridmo.eiglst[i])
            orgord.append(i)
        nmo = len(eiglst)
        itemlst = []
        for i in reversed(list(range(nmo))):
            ene = (ff12 % eiglst[i]).strip()
            ind = ''
            if orgord[i] == self.gridmo.homo: ind = 'H'
            if orgord[i] == self.gridmo.lumo: ind = 'L'
            itemlst.append(fi3 % (orgord[i]+1) + ':' + ene + ind)

        self.itemchoice.SetItems(itemlst)
        self.itemchoice.SetSelection(self.curnum)

    def GetCurrentMONumber(self):
        dat = self.itemchoice.GetValue()
        n = dat.find(':')
        ithmo = int(dat[:n]) -1
        return ithmo

    def ReadGridDataInCubeFile(self,filename,outunit='BOHR'): # ,property):
        """ outunit='BOHR' or 'ANGS' """
        # read density and mep cube file
        # format: a comment and a blank lines are assumed at the head of the file
        # ' $END' line is needed at the end of the file.
        if outunit == 'ANGS': uconv=const.PysCon['bh2an']
        else: uconv =1.0
        #
        info=[]; atomcc=[]; natoms=-1
        if not os.path.exists(filename):
            mess='file: '+filename+ 'not found.'
            lib.MessageBoxOK(mess,"ReadGridDataInCubeFile")
            return [],-1,[]
        f=open(filename,'r')
        # skip a comment line
        s=f.readline()
        # skip a blank line
        s=f.readline()
        # natoms,xmin,ymin,zmin
        s=f.readline(); s=s.replace('\r',''); s=s.replace('\n','')
        item=s.split()
        natoms=int(item[0])
        xmin=float(item[1])
        ymin=float(item[2])
        zmin=float(item[3])
        # nx,dx, the same data for y and z
        s=f.readline(); s=s.replace('\r',''); s=s.replace('\n','')
        item=s.split(); nx=int(item[0]); dx=float(item[1])
        s=f.readline(); s=s.replace('\r',''); s=s.replace('\n','')
        item=s.split(); ny=int(item[0]); dy=float(item[2])
        s=f.readline(); s=s.replace('\r',''); s=s.replace('\n','')
        item=s.split(); nz=int(item[0]); dz=float(item[3])
        xmax=xmin+nx*dx; ymax=ymin+ny*dy; zmax=zmin+nz*dz
        center=[(xmax+xmin)/2.0,(ymax+ymin)/2.0,(zmax+zmin)/2.0]
        # atomcc, [[an, x,y, and z],...]
        for i in range(natoms):
            s=f.readline(); s=s.replace('\r',''); s=s.replace('\n','')
            item=s.split()
            atomcc.append([int(item[0]),float(item[2])*uconv,
                           float(item[3])*uconv,float(item[4])*uconv])
        vmin=1000000.0; vmax=-1000000.0
        for s in f.readlines():
            s=s.replace('\r',''); s=s.replace('\n',''); s=s.strip()
            if s == ' $END': break
            item=s.split()
            for val in item:
                try:
                    if float(val) > vmax: vmax=float(val)
                except: pass
                try:
                    if float(val) < vmin: vmin=float(val)
                except: pass
        f.close()
        #
        info.append(center)
        info.append(xmin); info.append(xmax); info.append(nx)
        info.append(ymin); info.append(ymax); info.append(ny)
        info.append(zmin); info.append(zmax); info.append(nz)
        info.append(vmin); info.append(vmax)
        #
        return info,natoms,atomcc

    def MessageNoData(self,title):
        mess = 'No data'
        wx.MessageBox('No data','DrawCubeData.'+title)

    def SaveImage(self):
        if len(self.cubeobjdic) <= 0: return
        #
        formlst = ['bmp','png','gif','jpeg','tiff']
        wcard = "image(*.png;*.bmp;*.'jpeg')|*.png;*.bmp;*.jpeg"
        filename = lib.GetFileName(wcard=wcard,rw='w')
        base,ext = os.path.splitext(filename)
        form = ext[1:]
        if not form in formlst:
            mess = 'Unknown image format : ' + form
            wx.MessageBox(mess,'ImageSheet_Frm.SaveImageToFile')
            return
        if len(filename) <= 0: return

        img = self.model.draw.GetGLCanvasImage()
        ret = lib.SaveImageOnFile(filename,img)
        mess = 'Cube image was saved to ' + filename
        self.ConsoleMessage(mess)

    def SaveMODataOnORBFile(self):
        wcard = "MO data(*.orb)|*.orb"
        filename = lib.GetFileName(wcard=wcard,rw='w')
        if len(filename) <= 0: return
        head,ext = os.path.splitext(filename)
        if ext != '.orb': filename = os.path.join(filename,'.orb')
        #
        self.WriteORBsToFile(filename)
        mess = 'Created orbital file = ' + filename
        self.ConsoleMessage(mess)

    def SetPlotEnergyRange(self):
        title = 'SetPlotEnergyRange'
        mess = 'Enter emin and emax in eV.\n'
        mess += 'The current values are ' + str(self.drweigmin)
        mess += ' and ' + str(self.drweigmax) +', respectively.'
        string = wx.GetTextFromUser(mess,title)
        string = string.strip()
        changed = False
        if len(string) <= 0: return
        else:
            strlst = lib.SplitStringAtSpacesOrCommas(string)
            try:
                self.drweigmin = float(strlst[0])
                self.drweigmax = float(strlst[1])
                changed = True
            except:
                mess = 'Wrong input. Enter two floating values.'
                wx.MessageBox(mess,title)
                changed = False
        if changed:
            mess = 'min and max orbital energies in "Plot Enegy" '
            mess += 'have changed to \n'
            mess += '    ' + str(self.drweigmin)
            mess += ' and ' + str(self.drweigmax) + ', respectively.'
            self.ConsoleMessage(mess)

    def PlotOrbitalEnergies(self):
        if self.drwene is not None:
            try: self.drwene.SetFocus()
            except: pass
            return
        #
        lumomax = 0
        for grp in self.grplst:
            datgrp = self.curdat + ':' + grp
            gridmo = self.gridmodic[datgrp]
            if gridmo.eiglst[gridmo.lumo] > lumomax:
                lumomax = gridmo.eiglst[gridmo.lumo]
        eigmin = self.drweigmin
        eigmax = max([self.drweigmax,lumomax])

        curdat = self.curdat
        eiglstlst = []
        self.eigidxlst = []
        emin =  1000.0
        emax = -10000.0
        for grp in self.grplst:
            datgrp = self.curdat + ':' + grp
            gridmo = self.gridmodic[datgrp]
            eiglst = []
            orgord = []
            for i in range(gridmo.morange[0],gridmo.morange[1]+1):
                eig = gridmo.eiglst[i]
                if eig < eigmin or eig > eigmax: continue
                if eig < emin: emin = eig
                if eig > emax: emax = eig
                eiglst.append(eig)
                orgord.append(i)
            eiglstlst.append(eiglst)
            self.eigidxlst.append(orgord)

        if len(eiglstlst) <= 0:
            mess = 'No orbitals'
            wx.MessageBox(mess,'DrawCubeData_Frm.PlotOrbitalEnergies')
            return
        norbdat = len(eiglstlst)
        self.drwene = PlotEnergy_Frm(self,self.model,mode=1,norbdat=norbdat,
                                     orbtitle=curdat,erange=[emin-2,emax+2])
        messtext = self.grplst # ['MOL1','MOL2','MOL3']
        self.drwene.SetGraphMessageText(messtext)
        title = 'MOLs='
        for i in range(len(self.grplst)):
            title += self.grplst[i] + ','
        title = title[:-1]
        self.drwene.SetTitle(title)
        self.drwene.PlotEnergy(eiglstlst,self.eigidxlst)

    def WriteORBsToFile(self,filename,perRow=5,eigau=True):
        rwfile.WriteORBFile(filename,self.curdat,self.grplst,self.gridmodic,
                         perRow=perRow,eigau=eigau)

    def ShellDataString(self,atmlab,shlcntr,shltyp,shlgau,
                        ex,cs,cp,cd,cf):
        nl = '\n'; fi7 = '%7d'; ff18='%18.10f'; blk5 = 5 * ' '; blk3 = 3 * ' '
        shltyplst = ['','S ','','P ','L ','','D ','','','','F ']
        mess = ''
        ncntr = max(shlcntr) + 1
        cntrlst = []
        nshlcntr = ncntr * [0]
        for j in range(len(shlcntr)):
            cntrlst.append(shlcntr[j])
            nshlcntr[shlcntr[j]] += 1
        nshell = len(shltyp)
        ncntr = len(cntrlst)
        ngaus  = len(ex)
        igauss = -1
        icentr = 0
        text = ''
        donelst = []
        for j in range(nshell):
            k = cntrlst[j]
            label = atmlab[k]
            if not label in donelst:
                text += ' ' + label + nl
                text += nl
                donelst.append(label)
            ist = shlgau[j][0]
            ied = shlgau[j][1] + 1
            for ig in range(ist,ied):
                igauss += 1
                exstr = ff18 % ex[igauss]
                text  += fi7 % (j+1) + blk3
                if shltyp[j] == 1: # 'S'
                    text += shltyplst[shltyp[j]] + fi7 % (igauss+1)
                    text += blk5 + exstr
                    text += ff18 % cs[igauss] + nl
                elif shltyp[j] == 3: # 'P'
                    text += shltyplst[shltyp[j]] + fi7 % (igauss+1)
                    text += blk5 + exstr
                    text += ff18 % cp[igauss] + nl
                elif shltyp[j] == 4: # 'L'
                    text += shltyplst[shltyp[j]] + fi7 % (igauss+1)
                    text += blk5 + exstr
                    text += ff18 % cs[igauss]
                    text += ff18 % cp[igauss] + nl
                elif shltyp[j] == 6: # 'D'
                    text += shltyplst[shltyp[j]] + fi7 % (igauss+1)
                    text += blk5 + exstr
                    text += ff18 % cd[igauss] + nl
                elif shltyp[j] == 10: # 'F'
                    text += shltyplst[shltyp[j]] + fi7 % (igauss+1)
                    text += blk5 + exstr
                    text += ff18 % cf[igauss] + nl
            icentr += 1
            mess += text + nl
            text = ''
        return mess


    def SaveMOCubeData(self):
        if self.gridmo is None:
            self.MessageNoData('SaveMOCubeData')
            return
        self.gridmo.SaveMOCubeDataOnFile()

    def SaveMOImages(self):
        if self.gridmo is None:
            self.MessageNoData('SaveMOImages')
            return
        self.gridmo.SaveMOImagesOnFile(save=True)

    def ViewMOImages(self):
        if self.gridmo is None:
            self.MessageNoData('ViewMOImages')
            return
        bigimg = self.gridmo.SaveMOImagesOnFile(save=None)

    def ClearData(self,all=True):
        #datlst = self.datchoice.GetItems()
        # Molde
        try: self.model.RemoveMol(allmol=True)
        except: pass
        try: self.drwene.Close(1)
        except: pass
        #
        self.RemoveMO()
        self.curdat = ''
        self.datlst = []
        self.datchoice.SetItems(self.datlst)
        self.curgrp = ''
        self.grplst = []
        self.grpchoice.SetItems(self.grplst)
        self.curitem = ''
        self.curnum = -1
        self.itemlst = []
        self.itemchoice.SetItems(self.itemlst)

    def OpenNotePad(self):
        if self.property == 0:
            filename=self.denobjdic[self.curden].file
        if self.property == 1:
            filename=self.mepobjdic[self.curmep].file
        if len(filename) <= 0:
            mess='cube file not found.'
            lib.MessageBoxOK(mess,"OpenNotePad")
        # open notepad
        else: lib.Editor(filename)

    def ConsoleMessage(self,mess):
        try: self.model.ConsoleMessage(mess)
        except: print (mess)

    def Message(self,mess,loc,col):
        try: self.model.Message(mess,loc,col)
        except: print (mess)

    def ChangeTextMessageColor(self,color,drw=True):
        for i in range(len(self.colorlst)):
            id = self.fontcolorids[i]
            menuitem = self.menubar.FindItemById(id)
            menuitem.Check(False)

        self.colornum = self.colorlst.index(color)
        id = self.fontcolorids[self.colornum]
        menuitem = self.menubar.FindItemById(id)
        menuitem.Check(True)
        #
        if   color == 'Black':
            self.textmessagecolor = [0,0,0,1]
        elif color == 'White':
            self.textmessagecolor = [1,1,1,1]
        elif color == 'Green':
            self.textmessagecolor = [0,1,0,1]
        elif color == 'Yellow':
            self.textmessagecolor = [1,1,0,1]
        else:
            rgbcol=lib.ChooseColorOnPalette(self,False,1.0)
            if len(rgbcol) <= 0: return []
            self.textmessagecolor = rgbcol
        if drw: self.RedrawMO()

    def CheckFontMenuItem(self,style):
        id = self.fontmenuids[self.fontstyle]
        menuitem = self.menubar.FindItemById(id)
        menuitem.Check(False)
        id = self.fontmenuids[style]
        menuitem = self.menubar.FindItemById(id)
        menuitem.Check(True)

    def SetFontStyle(self,fontname):
        if   fontname == "BITMAP_8_BY_13":        style = 0 # 8 by 13 pixel
        elif fontname == "BITMAP_9_BY_15":        style = 1
        elif fontname == "BITMAP_TIMES_ROMAN_10": style = 2
        elif fontname == "BITMAP_TIMES_ROMAN_24": style = 3
        elif fontname == "BITMAP_HELVETICA_10":   style = 4
        elif fontname == "BITMAP_HELVETICA_12":   style = 5
        elif fontname == "BITMAP_HELVETICA_18":   style = 6
        else: style = 0
        # check menuitem
        self.CheckFontMenuItem(style)
        return style

    def TextMessage1(self,messlst,drw=False):
        try: self.model.TextMessage1(messlst,self.textmessagecolor,
                                     fontstyle=self.fontstyle,drw=drw)
        except: print (messlst)

    def OpenTextViewer(self):
        if self.curdat is None:
            mess = 'No data is opened'
            wx.MessageBox(mess,'DrawCubeData_Frm.OpenTextViewer')
            return
        winpos  = [self.GetPosition()[0]+10,self.GetPosition()[1]+10]
        winsize = [400,200]
        viewer  = subwin.TextViewer_Frm(self,winpos,winsize)
        if self.mode == 0 or self.mode == 1:
            try:
                curobj = self.cubeobjdic[self.curdat]
                mess = self.CubeDataInfo(curobj)
            except: return
        if self.mode == 2:
            mess = self.MODrawInfo()
        viewer.SetText(mess)

    def MODrawInfo(self):
        gridsize  = self.model.setctrl.GetParam('cube-mo-grid-size')
        morange   = self.model.setctrl.GetParam('cube-mo-range')
        linethick = self.model.setctrl.GetParam('cube-line-thick')
        mess = ''
        mess += '\nDrawMOsWin default setting params:\n'
        mess += '    "cube-mo-grid-size" = ' + str(gridsize) + '\n'
        mess += '    "cube-mo-range"     = ' + str(morange) +'\n'
        mess += '    "cube-line-thick"   = ' + str(linethick) + '\n'
        mess += '    ' + 'These parameters can be changed. '
        mess += 'See "Help"-"Document".\n'
        #
        mess += '\nCurrent data: ' + self.curdat +'\n'
        ngrp = len(self.grplst)
        for i in range(ngrp):
            datgrp = self.curdat + ':' + self.grplst[i]
            gridmo = self.gridmodic[datgrp]
            morange = [x+1 for x in gridmo.morange]
            mess += '\nMO info in group: ' + gridmo.name +'\n'
            mess += '    file name = ' + gridmo.file + '\n'
            mess += '    GAMESS ver. 1 MAY 2013 (R1)\n'
            mess += '    Number of atoms   = ' + str(gridmo.natoms) + '\n'
            mess += '    Number of MOs     = ' + str(gridmo.nbasis) + '\n'
            mess += '    HOMO              = ' + str(gridmo.homo+1) + '\n'
            mess += '    LUMO              = ' + str(gridmo.lumo+1) + '\n'
            mess += '    MO range for draw = ' + str(morange)+'\n'
            try:
                if len(self.gridmo.basoptlst) > 0:
                    mess +=  '\nBASIS SET OPTIONS:\n'
                    mess += '    '
                    for key,val in gridmo.basoptlst:
                        mess += key + '=' + val + ', '
                    mess = mess[:-2] + '\n'
            except: pass
        return mess

    def InfoMessage(self):
        linethick    = self.model.setctrl.GetParam('cube-line-thick')

        if self.mode == 2:
            title = 'DrawMOsWin'
            gridsize = self.model.setctrl.GetParam('cube-mo-grid-size')
            morange  = self.model.setctrl.GetParam('cube-mo-range')
            mess1  = '    "cube-mo-grid-size" = ' + str(gridsize) + '\n'
            mess1 += '    "cube-mo-range"     = ' + str(morange) +'\n'
        else:
            title = 'DrawCubeWin'
            mess1 = ''
        mess1 += '    "cube-line-thick"   = ' + str(linethick) + '\n'
        #
        mess  = title + ' default setting params:\n'
        mess += mess1
        mess += '    ' + 'These parameters can be changed. See "Help"-"Document".'
        self.ConsoleMessage(mess)

    def HelpMessage(self):
        helpdir=self.model.setctrl.GetDir('FUdocs')
        if self.mode == 2:
            helpfile='MODraw//html//MODraw.html'
            helpfile=os.path.join(helpdir,helpfile)
            title='MODraw Help'
            #HelpTextWin_Frm(self,title=title,textfile=helpfile,fumodel=self.model)
        else:
            helpfile='CubeDraw//html//CubeDraw.html'
            helpfile=os.path.join(helpdir,helpfile)
            title='Cube Draw Help'

        [x,y]=self.GetPosition()
        winpos=[x+20,y+20]
        subwin.HelpMessage(helpfile,title=title,winpos=winpos,parent=self)

    def MenuItems(self):
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        if self.mode == 2:
            submenu.Append(-1,"Open MO file","Open...")
            submenu.Append(-1,"Open file and Merge","Open...")
            submenu.AppendSeparator()
            submenu.Append(-1,"Save MO data(.orb)","Save MO data to orb file")
            submenu.AppendSeparator()
            submenu.Append(-1,"Save MO cube data","MO cube file")
            submenu.Append(-1,"Save MO images","MO cube file")
            """
            subsubmenu = wx.Menu()
            subsubmenu.Append(-1,"MO cube data","MO cube file")
            subsubmenu.AppendSeparator()
            subsubmenu.Append(-1,"MO images","MO cube file")
            ###subsubmenu.Append(-1,"MO level images","MO cube file")
            submenu.AppendMenu(-1,"Save",subsubmenu)
            """
        else:
            submenu.Append(-1,"Open cube file","Open...")
            submenu.AppendSeparator()
            submenu.Append(-1,"Save images","Save image")
        #submenu.AppendSeparator()
        #submenu.Append(-1,"Clear","Clear current data...")
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear all","Clear all...")
        submenu.AppendSeparator()
        submenu.Append(-1,"Quit","Quit...")
        menubar.Append(submenu,'File')
        # Info
        submenu=wx.Menu()
        submenu.Append(-1,"Info","View MO Info")
        ###submenu.Append(-1,"MO images","View MO images")
        if self.mode == 2:
            submenu.AppendSeparator()
            submenu.Append(-1,"Plot energy","Plot energy")
            submenu.Append(-1,"Set plot energy range","Set lot energy range")
            submenu.AppendSeparator()
        #id1=wx.NewId()
        subsubmenu = wx.Menu()
        ic0 = wx.NewId()
        subsubmenu.Append(ic0,"Black","black",True)
        ic1 = wx.NewId()
        subsubmenu.Append(ic1,"White","White",True)
        ic2 = wx.NewId()
        subsubmenu.Append(ic2,"Green","Green",True)
        ic3 = wx.NewId()
        subsubmenu.Append(ic3,"Yellow","Yellow",True)
        ic4 = wx.NewId()
        subsubmenu.Append(ic4,"Pickup in palett","Palett",True)
        ###subsubmenu.Append(-1,"MO level images","MO cube file")
        #py3#submenu.AppendMenu(-1,"Text Message color",subsubmenu)
        lib.AppendMenuWx23(submenu, -1, 'Change color', subsubmenu)
        self.fontcolorids = [ic0,ic1,ic2,ic3,ic4]

        subsubmenu = wx.Menu()
        id0 = wx.NewId()
        subsubmenu.Append(id0,"BITMAP_8_BY_13","GLUT_BITMAP_8_BY_13",True)
        id1 = wx.NewId()
        subsubmenu.Append(id1,"BITMAP_9_BY_15","GLUT_BITMAP_9_BY_15",True)
        id2 = wx.NewId()
        subsubmenu.Append(id2,"BITMAP_TIMES_ROMAN_10",
                          "GLUT_BITMAP_TIMES_ROMAN_10",True)
        id3 = wx.NewId()
        subsubmenu.Append(id3,"BITMAP_TIMES_ROMAN_24",
                          "GLUT_BITMAP_TIMES_ROMAN_24",True)
        id4 = wx.NewId()
        subsubmenu.Append(id4,"BITMAP_HELVETICA_10",
                          "GLUT_BITMAP_HELVETICA_10",True)
        id5 = wx.NewId()
        subsubmenu.Append(id5,"BITMAP_HELVETICA_12",
                          "GLUT_BITMAP_HELVETICA_12",True)
        id6 = wx.NewId()
        subsubmenu.Append(id6,"BITMAP_HELVETICA_18",
                          "GLUT_BITMAP_HELVETICA_18",True)
        ###subsubmenu.Append(-1,"MO level images","MO cube file")
        ###submenu.AppendMenu(-1,"Text Message font",subsubmenu)
        lib.AppendMenuWx23(submenu, -1, 'Text Message font', subsubmenu)
        self.fontmenuids = [id0,id1,id2,id3,id4,id5,id6]
        #submenu.Append(-1,"Text message->black","Text message black",True)
        if self.mode == 2:
            submenu.AppendSeparator()
            id=wx.NewId()
            submenu.Append(id,"Show group name","Show group name",True)
        menubar.Append(submenu,'View')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,"Document","Help document")
        menubar.Append(submenu,'Help')

        if self.mode == 2: menubar.Check(id,True)
        id = self.fontmenuids[self.fontstyle]
        menuitem = menubar.FindItemById(id)
        menuitem.Check(True)

        id = self.fontcolorids[self.colornum]
        menuitem = menubar.FindItemById(id)
        menuitem.Check(True)
        return menubar

    def OpenFile(self,form='cube'):
        """ form = 'cube' or 'gmsout' """
        if form == 'cube': # open file
            wcard = "mep;den;cube(*.mep;*.den;*.cube;*.cub)|"
            wcard += "*.mep;*.den;*.cube;*.cub|all(*.*)|*.*"
            filenames = lib.GetFileName(self,wcard,"r",True,"")
            if not isinstance(filenames,list): filenames=[filenames]
            if len(filenames) > 0:
                ndat=0
                for filename in filenames:
                    if len(filename) > 0:
                        if not os.path.exists(filename):
                            self.ConsoleMessage(filename+' file not found. skipped.')
                        else:
                            base,ext = os.path.splitext(filename)
                            extlst = ['.mep','.den','.cube','.cub']
                            if ext in extlst:
                                err = self.AddToCubeObjDic(filename)
                                if not err:
                                    self.ConsoleMessage('Read cube file: '+filename)
                                    ndat += 1
                            else:
                                mess='Can not read file with extention: "'+ext+'"'
                                lib.MessageBoxOK(mess,"OnMenu")
                                continue
                    name = lib.BaseNameInFileName(filename)
                mess=str(ndat) + ' cube data were read.'
                self.ConsoleMessage(mess)

        else: #'gmsout' or 'orb' file
            wcard = "GMS output(*.out;*.log)|*.out;*.log|orb file(*.orb)|*.orb|"
            wcard += "all(*.*)|*.*"
            filename = lib.GetFileName(self,wcard,"r",True,"")
            if len(filename) <= 0: return

            self.MakeMOCubeData(filename)

    def OnMenu(self,event):
        # menu event handler
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        try: bChecked=self.menubar.IsChecked(menuid)
        except: bChecked=False
        # File menu
        if item   == "Open cube file": self.OpenFile(form='cube')
        elif item == "Open MO file": self.OpenFile(form='mo')
        elif item == "Open file and Merge": self.MergeWithExistingMol()
        # Save
        elif item == "Save MO data(.orb)":
            self.SaveMODataOnORBFile()
        elif item == "Save MO cube data":
            self.SaveMOCubeData()
        elif item == "Save MO images":
            self.SaveMOImages()
        elif item == "MO level images":
            pass
        # mode != 2: Cube
        elif item == "Save images":
            self.SaveImage()

        elif item == "Clear":
            self.ClearData(False)
        elif item == "Clear all":
            self.ClearData(True)
        elif item == "Quit":
            self.OnClose(1)
        # View
        elif item == "Info":
            self.OpenTextViewer()
        elif item == "Show group name":
            if self.menubar.IsChecked(menuid):
                self.labelgroup = True
                self.drawlablegroup = True
            else:
                self.labelgroup = False
                self.drawlablegroup = False
            self.RedrawMO()
        # textmessage text color
        elif item == "Black":
            self.ChangeTextMessageColor(item)
        elif item == "White":
            self.ChangeTextMessageColor(item)
        elif item == "Green":
            self.ChangeTextMessageColor(item)
        elif item == "Yellow":
            self.ChangeTextMessageColor(item)
        elif item == "Pickup in palett":
            self.ChangeTextMessageColor(item)

        # textmessage fontstyle
        elif item.startswith("BITMAP",0,6):
            self.fontstyle = self.SetFontStyle(item)
            self.RedrawMO()
        #
        elif item == "Plot energy":
            self.PlotOrbitalEnergies()
        elif item == "Set plot energy range":
            self.SetPlotEnergyRange()
        elif item == "MO images":
            self.ViewMOImage()
        # Help
        elif item == "Document":
            self.HelpMessage()

    def PopupMenuItem(self):
        if self.mode != 2: return [],[]

        self.toplabel='Popup'
        tiplst = []
        self.model.mdlwin.popupmenuhandler=self.OnPopupMenu
        menulst = self.grpchoice.GetItems()
        for i in range(len(menulst)):
            menulst[i] = self.curdat + ':' + menulst[i]
        tiplst.append('Draw/remove MO(toggle)')

        return menulst,tiplst

    def PopupMenu(self):
        self.model.mdlwin.SetPopupMenu(menuitems=self.PopupMenuItem,
                                       menuhandler=self.OnPopupMenu)

    def OnPopupMenu(self,selected,label):
        if self.mode != 2: return

        selected = selected.strip()
        self.SwitchDrawAndRemoveGroup(selected)
        """
        delitem = False
        if selected in self.donotshowlst: delitem = True
        if delitem:
            try:
                while True: self.donotshowlst.remove(selected)
            except: pass
        else: self.donotshowlst.append(selected)

        self.RemoveMO()
        self.RedrawMO(current=None)
        """
    def SwitchDrawAndRemoveGroup(self,selected):
        delitem = False
        if selected in self.donotshowlst: delitem = True
        if delitem:
            try:
                while True: self.donotshowlst.remove(selected)
            except: pass
        else: self.donotshowlst.append(selected)

        self.RemoveMO()
        self.RedrawMO(current=None)



    def RedrawMO(self,current=None):
        polyg,messlst = self.MergeGroupPolyg(current=current)
        if len(polyg[0]) <= 0 and len(polyg[1]) <= 0:
            mess = 'polyg0,polyg1 are zero in DrawCubeData_Frm.RedrawMO'
            self.ConsoleMessage(mess)
            return

        label='cube-data'
        thick = self.model.setctrl.GetParam('cube-line-thick')
        if thick is None: thick = 0.5
        params=[self.style,thick]
        self.draw.SetDrawData(label,'CUBE',[params,polyg])
        #self.model.DrawMol(True)
        self.TextMessage1(messlst)
        self.ondraw = True

        self.model.DrawLabelGroup(self.drawlablegroup,drw=False)
        self.model.DrawMol(True)


class CubeObj():
    def __init__(self):
        # cube data object
        self.file = ''  # null string
        self.name = ' ' # a space
        # self.info: [center,xmin,xmax,nx,ymin,ymax,ny,zmin,zmax,nz,vmin,vmax]
        self.gridinfo = [[0.0,0.0,0.0], 0.0,0.0,0, 0.0,0.0,0, 0.0,0.0,0, 0.0,0.0]
        # self.atomcc: [[an,x,y,z],...]
        self.atomcc   = [] # [[an,x,y,z],...], use AN instead of elm
        self.natoms   = -1
        self.gridobj  = None

    def ErrorMessage(self,attrib,method):
        mess = 'The attribute ' + sttrib + ' is not set(None)'
        wx.MassageBox(mess,'CubeObj.'+method)

    def GetGridInfo(self):
        return self.gridinfo

    def SetGridInfo(self,grisinfo):
        self.gridinfo = gridinfo

    def SetGridObj(self,gridobj):
        self.gridobj = gridobj

    def GetAtomCC(self):
        return self.atomcc

class GridMO():
    def __init__(self,parent):
        # cube data object
        self.parent = parent
        try: self.model  = self.parent.model
        except: self.model  = None
        self.prop = 'MO' # 'MO',...
        self.file = ''  # null string
        self.name = ' ' # a space
        # self.info: [center,xmin,xmax,nx,ymin,ymax,ny,zmin,zmax,nz,vmin,vmax]
        ###self.gridinfo = [[0.0,0.0,0.0], 0.0,0.0,0, 0.0,0.0,0, 0.0,0.0,0, 0.0,0.0]
        # self.atomcc: [[an,x,y,z],...]
        self.allatmcc = []
        self.thislst  = []
        #
        self.atomcc   = None  # [[an,x,y,z],...], use AN instead of elm
        self.natoms   = -1

        self.nbasis   = None
        self.coorddic = None
        self.eiglst   = None
        self.symlst   = None
        self.moslst   = None
        self.basdic   = None
        self.basoptlst= None

        self.ngrids    = None
        self.origin   = None
        self.size0    = None # size in Angs
        self.margin   = None

        self.noccs    = None
        self.homo     = None
        self.homo     = None
        self.homob    = None
        self.lumob    = None
        self.morange  = None
        self.gridmargin = None

        self.smallcsqlst   = None
        self.saveimgparams = self.DefaultSaveImageParams()

    def DefaultSaveImageParams(self):
        saveimgparams = {
            'wbitmap'   : 700, # bitmap width
            'margin'    : 50, # margin for left,right, top,bottom
            'wmo'       : 300, # mo width
            'hmo'       : 300, # mo height
            'perRow'    : 2, # mos per row
            'drawmodel' : 1, # stick
            'fontstyle' : 6, # GLUT_BITMAP_HELVETICA_18
            'savedir'   : None # save directory
             }
        return saveimgparams

    def Message(self,mess):
        self.model.ConsoleMessage(mess)

    def SetSize0(self,size0):
        self.size0 = size0

    def ErrorMessage(self,attrib,method):
        mess = 'The attribute ' + sttrib + ' is not set(None)'
        wx.MassageBox(mess,'CubeObj.'+method)

    def GetAtomCC(self):
        return self.atomcc

    def SetAtomCC(self,atomcc):
        self.atomcc = atomcc[:]
        natm = len(atomcc)
        for i in range(natm):
            for j in range(self.basdic['shlxyz']):
                if self.basdic['shlcntr'][j] == i:
                    self.basdic['shlxyz'][j][0] = atomcc[i][0]
                    self.basdic['shlxyz'][j][1] = atomcc[i][1]
                    self.basdic['shlxyz'][j][2] = atomcc[i][2]
        return


    def GetHOMONo(self):
        return self.homo

    def GetHOMO(self):
        if self.molslst is None:
            self.ErrorMessage('self.moslst','GetHOMO')
            return None
        mo = []
        for ib in range(self.nbasis):
            mo[ib] = self.moslst[ib][self.homo]
        return mo

    def GetLUMONo(self):
        return self.lumo

    def GetLUMO(self):
        if self.molslst is None:
            self.ErrorMessage('self.molslst','GetLUMO')
            return None
        mo = []
        for ib in range(self.nbasis):
            mo[ib] = self.moslst[ib][self.lumo]
        return mo

    def GetMO(self,level,messout=True):
        if self.moslst is None:
            self.ErrorMessage('self.moslst is None','GetMO')
            return None
        mo = numpy.zeros(self.nbasis)
        if level >= self.nbasis:
            if messout:
                mess = 'No such mo. the number of MOs is ' + str(self.nbasis)
                wx.MessageBox(mess,'GidMO.GetMO')
            return None
        for ib in range(self.nbasis):
            mo[ib] = self.moslst[ib][level]
        return mo

    def GetEigAndMO(self,level):
        if self.moslst is None or self.eiglst is None:
            self.ErrorMessage('self.moslst,self.eiglst','GetEigAndMO')
            return None,None
        mo = []
        if level >= self.nbasis:
            mess = 'The number of MOs is ' + self.nbasis
            wx.MessageBox(mess,'CubeObj.GetMO')
            return mo
        for ib in range(self.nbasis):
            mo[ib] = self.moslst[ib][level]
        return self.eiglst[level],mo

    def GetEigenvalue(self):
        if self.eiglst is None:
            self.ErrorMessage('self.eiglst','GetEigenValues')
            return None
        return self.eiglst

    def GetOrbSymmetry(self):
        if self.symlst is None:
            self.ErrorMessage('self.symlst','GetOrbSymmetry')
            return None
        self.symlst

    def IsVerySmall(self,ish,shlbas,mo,cutoff=1e-12):
        ans = False
        shlbasish = shlbas[ish]
        csq = 0.0
        nb = len(shlbasish)
        for i in range(nb):
            ib = shlbasish[i]
            csq += (mo[ib]*mo[ib])
        if csq < cutoff: ans = True
        return True

    def ComputeMOAtPoint(self,pnt,mo,
                         shlcntr,shltyp,shlxyz,shlgau,
                         ex,cs,cp,cd,cf,cmpord=0):
        """ all coordinates should be in bohr

        :param float pnt: point coordinates, [x,y,z] in Bohr
        :param dic basdic: dictionary of basis set data
        :param lst mo: list of MO coefficients, [C1,C2,...Cnbasis]
        :param int cmpord: order of AO components
            0: GAMESS order of d's: xx,yy,zz,xy,yz,zx
               GAMESS order of f's:xxx,yyy,zzz,xxy,xxz,xyy,yyz,yzz,xzz,xyz
            1: canonical order of d's: xx,xy,xz,yy,yz,zz
               canonical order of f's: xxx,xxy,xxz,xyy,xyz,xzz,yyy,yyz,yzz,zzz
            2: LOTUS  order of d's: xx,xy,yy,xz,yz,zz
        """
        cmpord = self.cmpord

        pi = numpy.pi
        val = 0.0
        [x,y,z] = pnt
        nshl = len(shltyp)
        ibas = 0
        for ish in range(nshl):
            #print 'ish,shlbas[ish]',ish,shlbas[ish]
            #if self.IsVerySmall(ish,shlbas,mo): continue
            if shlcntr[ish] in self.smallcsqlst:
                ibas += shltyp[ish]
                continue
            x0 = shlxyz[ish][0]
            y0 = shlxyz[ish][1]
            z0 = shlxyz[ish][2]
            px = x - x0
            py = y - y0
            pz = z - z0
            rr = px * px + py * py + pz * pz
            if shltyp[ish] == 1:
                sums = 0.0
                ist = shlgau[ish][0]
                ied = shlgau[ish][1] + 1
                for ig in range(ist,ied):
                    exrr = -ex[ig] * rr
                    if exrr < -12.0: continue # exp(-12)=6.14*1e-6
                    nms = self.NormConstOfGaussian(ex[ig],0,0,0)
                    exval = nms * numpy.exp(exrr)
                    sums += cs[ig] * exval
                val += mo[ibas+0] * sums
                ibas += 1
            elif shltyp[ish] == 3:
                sumpx = 0.0
                sumpy = 0.0
                sumpz = 0.0
                ist = shlgau[ish][0]
                ied = shlgau[ish][1] + 1
                for ig in range(ist,ied):
                    exrr = -ex[ig] * rr
                    if exrr < -12.0: continue
                    nmp = self.NormConstOfGaussian(ex[ig],1,0,0)
                    exval = numpy.exp(exrr) * nmp
                    sumpx += cp[ig] * px * exval
                    sumpy += cp[ig] * py * exval
                    sumpz += cp[ig] * pz * exval
                val += mo[ibas+0] * sumpx
                val += mo[ibas+1] * sumpy
                val += mo[ibas+2] * sumpz
                ibas += 3
            elif shltyp[ish] == 4:
                sums  = 0.0
                sumpx = 0.0
                sumpy = 0.0
                sumpz = 0.0
                ist = shlgau[ish][0]
                ied = shlgau[ish][1] + 1
                for ig in range(ist,ied):
                    exrr = -ex[ig] * rr
                    if exrr < -12.0: continue
                    exval = numpy.exp(exrr)
                    nms = self.NormConstOfGaussian(ex[ig],0,0,0)
                    nmp = self.NormConstOfGaussian(ex[ig],1,0,0)
                    sums  += cs[ig] * exval * nms
                    sumpx += cp[ig] * px * exval * nmp
                    sumpy += cp[ig] * py * exval * nmp
                    sumpz += cp[ig] * pz * exval * nmp
                val += mo[ibas+0] * sums
                val += mo[ibas+1] * sumpx
                val += mo[ibas+2] * sumpy
                val += mo[ibas+3] * sumpz
                ibas += 4
            elif shltyp[ish] == 6:
                sumdxx = 0.0
                sumdyy = 0.0
                sumdzz = 0.0
                sumdxy = 0.0
                sumdyz = 0.0
                sumdzx = 0.0
                ist = shlgau[ish][0]
                ied = shlgau[ish][1] + 1
                for ig in range(ist,ied):
                    exrr = -ex[ig] * rr
                    if exrr < -12.0: continue
                    exval = numpy.exp(exrr)
                    nmdx2 = self.NormConstOfGaussian(ex[ig],2,0,0)
                    nmdxy = self.NormConstOfGaussian(ex[ig],1,1,0)
                    sumdxx += cd[ig] * px * px * exval * nmdx2
                    sumdyy += cd[ig] * py * py * exval * nmdx2
                    sumdzz += cd[ig] * pz * pz * exval * nmdx2
                    sumdxy += cd[ig] * px * py * exval * nmdxy
                    sumdyz += cd[ig] * py * pz * exval * nmdxy
                    sumdzx += cd[ig] * pz * px * exval * nmdxy
                if cmpord == 0: # GAMESS
                    val += mo[ibas+0] * sumdxx
                    val += mo[ibas+1] * sumdyy
                    val += mo[ibas+2] * sumdzz
                    val += mo[ibas+3] * sumdxy
                    val += mo[ibas+4] * sumdyz
                    val += mo[ibas+5] * sumdzx
                elif cmpord == 1: # canonical
                    val += mo[ibas+0] * sumdxx
                    val += mo[ibas+1] * sumdxy
                    val += mo[ibas+2] * sumdzx
                    val += mo[ibas+3] * sumdyy
                    val += mo[ibas+4] * sumdyz
                    val += mo[ibas+5] * sumdzz
                elif cmpord == 2: # lotus 10NOV2017
                    val += mo[ibas+0] * sumdxx
                    val += mo[ibas+1] * sumdxy
                    val += mo[ibas+2] * sumdyy
                    val += mo[ibas+3] * sumdzx
                    val += mo[ibas+4] * sumdyz
                    val += mo[ibas+5] * sumdzz
                ibas += 6
        return val

    def NormConstOfGaussian(self,a,l,m,n):
        """
        G = N(x-x0)**l*(y-y0)**m*(z-z0)**n*exp(-a*(r-r0)**2)
        N = (2a/pi)**(3/4)*[(8a)**(l+m+n)*l!*m!*n!/(2l)!(2m)!(2n)!]**(1/2)
        """
        pi = numpy.pi
        nc1 = pow((2.0 * a / pi), 0.75) # 0.75 = 3/4
        if l == 0 and m == 0 and n == 0: nc = nc1
        else:
            nc2 = pow((8.0 * a),l+m+n) * math.factorial(l)
            nc2 *= math.factorial(m) * math.factorial(n)
            nc2 /= (math.factorial(2*l) * math.factorial(2*m) * math.factorial(2*n))
            nc = nc1 * numpy.sqrt(nc2)
        return nc

    def MakeMOCubeObject(self,filename):
        pass


    def MakeGridData(self,mo=None,size0=None):
        atomcc = self.GetAtomCC()
        natm = len(atomcc)
        bascntr = self.basdic['bascntr']
        nbas = len(bascntr)
        #
        xmin =  1000.0
        ymin =  1000.0
        zmin =  1000.0
        xmax = -1000.0
        ymax = -1000.0
        zmax = -1000.0
        # angs
        tobohr = 1.8870854
        if size0 is None: size0 = self.size0

        size  = size0 * tobohr
        # coords in atomcc are in Bohr
        atmlst = list(range(natm))
        smallcsqlst = []
        if mo is not None:
            cutoff = 1e-6
            atmcsq = natm * [0.0]
            nbasis = len(mo)
            for ib in range(nbas):
                ia = bascntr[ib]
                try:
                    atmcsq[ia] += mo[ib] * mo[ib]
                except:
                    print(('---index out of range in MakeGridData: ia,ib=',ia,ib))
            atmlst = []
            for i in range(natm):
                if atmcsq[i] > cutoff: atmlst.append(i)
                else: smallcsqlst.append(i)
        self.smallcsqlst = smallcsqlst
        for i in atmlst:
            if atomcc[i][1] < xmin: xmin = atomcc[i][1]
            if atomcc[i][2] < ymin: ymin = atomcc[i][2]
            if atomcc[i][3] < zmin: zmin = atomcc[i][3]
            if atomcc[i][1] > xmax: xmax = atomcc[i][1]
            if atomcc[i][2] > ymax: ymax = atomcc[i][2]
            if atomcc[i][3] > zmax: zmax = atomcc[i][3]

        margin0 = self.gridmargin
        margin = margin0 * tobohr
        xmin = (xmin - margin)
        xmax = (xmax + margin)
        ymin = (ymin - margin)
        ymax = (ymax + margin)
        zmin = (zmin - margin)
        zmax = (zmax + margin)

        nx = int((xmax-xmin) / size)
        ny = int((ymax-ymin) / size)
        nz = int((zmax-zmin) / size)

        zero = 0.0
        boxmin = numpy.array([xmin,ymin,zmin])
        ex     = numpy.array([size,zero,zero])
        ey     = numpy.array([zero,size,zero])
        ez     = numpy.array([zero,zero,size])
        nptlst = [nx,ny,nz]

        return nptlst,boxmin,ex,ey,ez

    def GetMOLeves(self):
        homo = self.homo
        lumo = self.lumo
        allmos = list(range(len(self.eiglst)))
        allmos1 = [x+1 for x in allmos]
        mo0 = self.morange[0]
        mo1 = self.morange[1]
        allmos = [i+1 for i in range(mo0,mo1)]
        strallmos = lib.IntegersToString(allmos)
        mess  = 'Input MO levels, e.g. "2,3-8,10" (no quotations)\n'
        mess += '    ' + str(homo+1) + ':HOMO and ' + str(lumo+1) +':LUMO,'
        mess += ' All MOs are ' + strallmos
        molevs = lib.GetIntegersFromUser(mess)
        molevs = [x-1 for x in molevs]
        return molevs

    def SaveMOCubeDataOnFile(self):
        homo = self.homo
        lumo = self.lumo
        mo0 = self.morange[0] - 1
        mo1 = self.morange[1]
        # internal #: 0,1,2...
        allmos = [i for i in range(mo0,mo1)]
        savecurmo = self.parent.curnum #item

        molevs = self.GetMOLeves()
        if len(molevs) <= 0: return
        if len(molevs) == 1:
            wcard = "cube(*.cube;*.cub)|*.cube;*.cub"
            filename = lib.GetFileName(wcard=wcard,rw='w')
            if len(filename) <= 0: return
        else:
            dirname = lib.GetDirectoryName()
            if not os.path.isdir(dirname):
                mess = dirname + ' does not exist. '
                mess += 'Would you like to create it?'
                dlg = wx.MessageDialog(None,mess,'SaveMOCubeData',
                             style=wx.YES_NO|wx.ICON_QUESTION|wx.STAY_ON_TOP)
                if dlg.ShowModal() == wx.ID_NO: return True
                os.mkdir(dirname)
        #self.textbox = self.CreatingMessage()
        self.model.mdlwin.BusyIndicator('On','Creating cube ..')
        for ith in molevs:
            if not ith in allmos: continue
            if len(molevs) == 1: file = filename
            else:
                name = self.name
                name = name.replace(':','-')
                file = name + '-mo' + str(ith+1) + '.cube'
                file = os.path.join(dirname,file)

            self.WriteCubeFile(file,ith)
        self.model.mdlwin.BusyIndicator('Off')

        self.parent.itemchoice.SetSelection(savecurmo)

    def SaveMOImagesOnFile(self,save=True):
        self.saveimage = save
        retmethod = self.GetSaveImageParams
        paramfrm = SaveImageParams_Frm(self.parent,retmethod=retmethod)

    def GetSaveImageParams(self,filename,params):
        wx.MessageBox('GetSaveImageParams='+str(params))
        
        if len(filename) <= 0: return

        mess  = 'Parameters for save MO images:\n'
        mess += '    ' + str(params)
        self.Message(mess)

        self.WriteMOImagesOnFile(filename,params,save=self.saveimage)

    def ReplaceHOMOLUMO(self,numtxt):
        homo = False
        lumo = False
        nc =  numtxt.find('HOMO')
        if nc >= 0:
            numtxt = numtxt.replace('HOMO,','')
            numtxt = numtxt.replace('HOMO','')
            homo = True
        nc = numtxt.find('LUMO')
        if nc >= 0:
            numtxt = numtxt.replace('LUMO,','')
            numtxt = numtxt.replace('LUMO','')
            lumo = True
        numtxt = numtxt.strip()
        molevs = []
        if len(numtxt) > 0:
            molevs = lib.StringToInteger(numtxt)
        if homo:
            if not self.homo in molevs: molevs.append(self.homo)
        if lumo:
            if not self.lumo in molevs: molevs.append(self.lumo)
        return molevs

    def CompImageSize(self,width):
        wximg = self.model.mdlwin.draw.GetGLCanvasImage()
        [wimg,himg] = wximg.GetSize()
        maxs = max(wimg,himg)
        sc = float(width) / maxs # scale factor
        return sc,int(wimg*sc),int(himg*sc)

    def WriteMOImagesOnFile(self,filename,params,save=True):
        #molevs = self.GetMOLeves()
        numtxt = params['molevs']
        if len(numtxt) <= 0: return

        molevs = self.ReplaceHOMOLUMO(numtxt)

        mo0 = self.morange[0] - 1
        mo1 = self.morange[1]
        # internal #: 0,1,2...
        allmos = [i for i in range(mo0,mo1)]

        nmos   = len(molevs)
        width  = params['wmo'] #200
        height = params['hmo'] #200

        sc ,width,height = self.CompImageSize(width)


        perRow = params['perRow'] #2
        margin = params['margin'] #50
        nrow   = int(nmos / perRow)
        if nmos % perRow != 0: nrow += 1
        w = width * perRow + 2 * margin
        h = height * nrow  + 2 * margin
        if lib.IsWxVersion2(): 
            bigimg = wx.EmptyImage(w,h)
            bigimg.SetRGBRect((0,0,w,h),255,255,255)
        else: 
            bigimg = wx.Image(w,h)
            bigimg.SetRGB((0,0,w,h),255,255,255)
        #savecurmo = self.parent.curmo
        bgcolor = [1,1,1,1]
        savebgcolor = self.model.mdlwin.draw.bgcolor
        self.model.ChangeBackgroundColor(bgcolor)
        modeldic = {'line':0,'stick':1,'ball-and-stic':2}
        if not params['drawmodel'] == 'as is':
            self.model.SaveAtomModel(True)
            drawmodel = modeldic[params['drawmodel']]
            self.model.ChangeDrawModel(drawmodel)
        fontstyle = params['fontstyle']

        imgno = -1
        x = margin
        y = margin - height
        over = False
        for i  in range(nrow):
            if over: break
            y += height
            x = margin - width
            for j in range(perRow):
                x += width
                imgno += 1
                if imgno > nmos - 1:
                    over = True
                    break
                ith = molevs[imgno]
                if not ith in allmos: continue
                self.parent.DrawCubeData(ithmo=ith,fontstyle=6)
                # wx.Image
                wximg = self.model.mdlwin.draw.GetGLCanvasImage()
                wximg = wximg.Mirror(True)
                wximg = wximg.Mirror(True) # neeed two times !!
                [wimg,himg] = wximg.GetSize()
                wid = int(sc * wimg)
                hei = int(sc * himg)
                wximg.Rescale(wid, hei)
                bigimg.Paste(wximg, x, y)
        if not params['drawmodel'] == 'as is':
            self.model.SaveAtomModel(False)
        self.model.ChangeBackgroundColor(savebgcolor)

        self.parent.OnDraw(1)
        # save
        if save:
            bigimg.SaveFile(filename,wx.BITMAP_TYPE_PNG)
            mess = str(imgno+1) +' MO images were saved on file = ' + filename
            self.Message(mess)
        else:
            return bigimg

    def CreatingMessage(self):
        winpos = self.parent.GetPosition()
        winsize = [200,100]
        textbox = subwin.TextBox_Frm(self.parent,
                          winpos=winpos,winsize=winsize,
                          ok=False,cancel=False,yes=False,no=False)
        textbox.SetBackgroundColor('yellow')
        return textbox

    def WriteCubeFile(self,cubefile,ithmo): # --> MakePolygon later
        #filename = self.file
        name = self.name    # 'MO'
        atomcc = self.atomcc
        natoms = self.natoms
        nbasis = self.nbasis
        #coordic = self.coorddic
        eiglst = self.eiglst
        symlst = self.symlst
        moslst = self.moslst
        basdic = self.basdic
        #
        mo = self.GetMO(ithmo)
        [nx,ny,nz],[xmin,ymin,zmin],ex,ey,ez = self.MakeGridData(mo)
        size = ex[0] # assuming size is the same for y,y,and z
        zero = 0.0
        shltyp  = self.basdic['shltyp']
        shlcntr = self.basdic['shlcntr']
        shlxyz  = self.basdic['shlxyz']
        shlgau  = self.basdic['shlgau']
        #
        ex = self.basdic['ex']
        cs = self.basdic['cs']
        cp = self.basdic['cp']
        cd = self.basdic['cd']
        cf = self.basdic['cf']

        mo = numpy.array(mo)

        #
        fi5='%5d'; ff12='%12.6f'; fe13 ='%13.5e'
        nl = '\n'
        # open file
        f = open(cubefile,'w')
        title = 'Cube for MOPlot'
        if len(name) > 0: title += ' - ' + name
        f.write(title+nl)
        dat = 'MO number=' + str(ithmo) + ', occ=??' + ' sym=??'
        f.write(dat+nl) # the second line

        dat = fi5 % natoms + ff12 % xmin + ff12 % ymin + ff12 % zmin
        f.write(dat+nl)
        sizelst = [[nx,size,zero,zero],[ny,zero,size,zero],[nz,zero,zero,size]]
        # grid data
        for i in range(3):
            dat  = fi5 % sizelst[i][0] + ff12 % sizelst[i][1]
            dat += ff12 % sizelst[i][2] + ff12 % sizelst[i][3]
            f.write(dat+nl)
        # atoms
        #fc = tobohr = 1.8870854
        fc = 1.0 # already in BOHR
        for i in range(natoms):
            an = atomcc[i][0]
            dat = fi5 % an + ff12 % float(an) + ff12 % (fc*atomcc[i][1])
            dat += ff12 % (fc*atomcc[i][2]) + ff12 % (fc*atomcc[i][3])
            f.write(dat+nl)
        maxval = -1000.0
        minval =  1000.0
        vallst = []
        # value at grid
        for i in range(nx):
            x = xmin + size * i
            for j in range(ny):
                y = ymin + size * j
                count = 0
                dat = ''
                count = 0
                for k in range(nz):
                    z = zmin + size * k
                    val = self.ComputeMOAtPoint([x,y,z],mo,
                          shlcntr,shltyp,shlxyz,shlgau,
                          ex,cs,cp,cd,cf)
                    if val > maxval: maxval = val
                    if val < minval: minval = val
                    vallst.append([x,y,z,val])
                    count += 1
                    dat += fe13 % val
                    if count % 6 == 0:
                        f.write(dat+nl)
                        dat = ''
                if len(dat) > 0:
                    f.write(dat+'\n')
        f.write(' $END\n') # GAMESS
        f.close()
        mess = 'Created cube file = ' + cubefile
        self.Message(mess)

    def ChangeSignOfMO(self,ithmo):
        mo = self.GetMO(ithmo,messout=False)
        if mo is None: return
        nbas = len(mo)
        for i in range(nbas): mo[i] *= -1.0
        for i in range(nbas): self.moslst[i][ithmo] = mo[i]

    def ComputeMOValues(self,ithmo,thres,ndiv,cmpord=0):
        cmpord = self.cmpord
        #print 'cmpord in ComputeMOValues',cmpord

        #basdic = self.basdic
        mo = self.GetMO(ithmo,messout=False)
        if mo is None: return

        [nx,ny,nz],xyzmin,eex,eey,eez = self.MakeGridData(mo)

        [xmin,ymin,zmin] = xyzmin # bohr
        gsize   = eex[0] # bohr

        toangs = 0.529177249
        eex     *= toangs
        eey     *= toangs
        eez     *= toangs
        boxmin = xyzmin * toangs
        #
        shltyp  = self.basdic['shltyp']
        shlcntr = self.basdic['shlcntr']
        shlxyz  = self.basdic['shlxyz']
        shlgau  = self.basdic['shlgau']
        #
        ex = self.basdic['ex']
        cs = self.basdic['cs']
        cp = self.basdic['cp']
        cd = self.basdic['cd']
        cf = self.basdic['cf']

        mo = numpy.array(mo)
        moval = numpy.zeros((nx,ny,nz))
        #
        #print "gridmo.ComputeMOValues"
        #print 'nx,ny,nz',nx,ny,nz

        #test=True
        #if test:
        try: # Fortran codes
            #if gmsord: aoorder = 0
            #else:      aoorder = 1
            for i in range(nx):
                x = xmin + gsize * i
                for j in range(ny):
                    y = ymin + gsize * j
                    for k in range(nz):
                        z = zmin + gsize * k
                        #print 'i,j,k,x,y,z',i,j,k,x,y,z
                        val = comp_mo.mo_value_at(x,y,z,mo,
                              shltyp,shlxyz,shlgau,
                              ex,cs,cp,cd,cf,cmpord)
                        #print 'i,j,k,val',i,j,k,val

                        moval[i][j][k] = val
        except: # Python codes
        #else:
            mess = 'Failed Fortran(comp_mo) in ComputeMOValues. Executing Python codes.'
            self.Message(mess)
            for i in range(nx):
                x = xmin + gsize * i
                for j in range(ny):
                    y = ymin + gsize * j
                    for k in range(nz):
                        z = zmin + gsize * k
                        val = self.ComputeMOAtPoint([x,y,z],mo,
                              shlcntr,shltyp,shlxyz,shlgau,
                              ex,cs,cp,cd,cf,cmpord=cmpord)
                        moval[i][j][k] = val
        return moval,eex,eey,eez,boxmin

#class for Marching Cubes
class MC:
    midvtx = [
              [[0,0,0],[1,0,0]],
              [[0,1,0],[1,1,0]],
              [[0,0,0],[0,1,0]],
              [[1,0,0],[1,1,0]],
              [[0,0,1],[1,0,1]],
              [[0,1,1],[1,1,1]],
              [[0,0,1],[0,1,1]],
              [[1,0,1],[1,1,1]],
              [[0,0,0],[0,0,1]],
              [[1,0,0],[1,0,1]],
              [[0,1,0],[0,1,1]],
              [[1,1,0],[1,1,1]]
             ]

    cubepoly = [
                [],
                [[0,8,2]],
                [[3,9,0]],
                [[2,3,8],[3,9,8]],
                [[10,1,2]],
                [[8,10,0],[10,1,0]],
                [[0,3,9],[1,10,2]],
                [[1,3,9],[1,9,10],[8,10,9]],
                [[1,11,3]],
                [[3,1,11],[2,8,0]],
                [[0,1,9],[1,11,9]],
                [[2,1,11],[2,11,8],[9,8,11]],
                [[3,2,11],[2,10,11]],
                [[3,0,8],[3,8,11],[10,11,8]],
                [[0,2,10],[0,10,9],[11,9,10]],
                [[8,10,9],[9,10,11]],
                [[4,6,8]],
                [[0,4,2],[4,6,2]],
                [[8,4,6],[9,3,0]],
                [[9,4,6],[9,6,3],[2,3,6]],
                [[2,10,1],[6,4,8]],
                [[6,10,1],[6,1,4],[0,4,1]],
                [[0,3,9],[1,2,10],[4,6,8]],
                [[1,3,9],[1,9,10],[9,4,10],[4,6,10]],
                [[1,11,3],[4,6,8]],
                [[0,2,4],[2,4,6],[1,11,3]],
                [[0,9,1],[9,1,11],[4,6,8]],
                [[1,11,9],[1,9,2],[2,9,6],[4,6,9]],
                [[10,2,11],[2,11,3],[8,4,6]],
                [[6,10,11],[6,11,4],[4,11,0],[3,0,11]],
                [[0,2,1],[2,10,9],[9,10,11],[4,6,8]],
                [[9,4,6],[10,9,6],[9,10,11]],
                [[9,7,4]],
                [[4,9,7],[0,2,8]],
                [[4,0,7],[0,3,7]],
                [[4,8,2],[4,2,7],[3,7,2]],
                [[9,7,4],[10,1,2]],
                [[8,0,10],[0,10,1],[9,7,4]],
                [[3,0,7],[0,7,4],[2,10,1]],
                [[1,3,7],[1,7,10],[10,7,8],[4,8,7]],
                [[11,3,1],[9,4,7]],
                [[3,1,11],[2,0,8],[7,4,9]],
                [[1,11,7],[4,1,7],[1,4,0]],
                [[2,1,11],[2,11,8],[11,7,8],[7,4,8]],
                [[10,3,11],[2,10,3],[7,4,9]],
                [[3,0,2],[0,8,11],[11,8,10],[7,4,9]],
                [[2,10,11],[2,11,0],[0,11,4],[7,4,11]],
                [[7,4,8],[7,8,11],[10,11,8]],
                [[8,9,6],[9,7,6]],
                [[0,9,7],[0,7,2],[6,2,7]],
                [[8,0,3],[8,3,6],[7,6,3]],
                [[2,3,6],[6,3,7]],
                [[8,6,9],[6,9,7],[10,1,2]],
                [[9,7,6],[9,6,0],[0,6,1],[10,1,6]],
                [[8,0,9],[0,3,6],[6,3,7],[10,1,2]],
                [[6,10,1],[3,6,1],[6,3,7]],
                [[8,7,9],[6,8,7],[3,1,11]],
                [[0,9,4],[9,7,2],[2,7,6],[1,11,3]],
                [[0,1,11],[7,0,11],[6,0,7],[0,6,8]],
                [[1,11,7],[1,7,2],[6,2,7]],
                [[2,10,3],[3,10,11],[6,8,7],[7,8,9]],
                [[3,0,11],[0,10,11],[7,0,9],[6,0,7],[0,6,10]],
                [[8,0,6],[0,7,6],[10,0,2],[11,0,10],[0,11,7]],
                [[7,10,11],[7,6,10]],
                [[6,5,10]],
                [[10,6,5],[8,0,2]],
                [[6,5,10],[3,9,0]],
                [[2,8,3],[8,3,9],[6,5,10]],
                [[2,6,1],[6,5,1]],
                [[8,6,5],[8,5,0],[1,0,5]],
                [[2,1,6],[1,6,5],[3,9,0]],
                [[6,5,1],[6,1,8],[8,1,9],[3,9,1]],
                [[5,10,6],[1,3,11]],
                [[10,6,5],[8,2,0],[11,3,1]],
                [[0,11,1],[9,0,11],[10,6,5]],
                [[2,1,3],[1,11,8],[8,11,9],[6,5,10]],
                [[6,5,11],[3,6,11],[6,3,2]],
                [[8,6,5],[8,5,0],[5,11,0],[11,3,0]],
                [[2,6,5],[11,2,5],[9,2,11],[2,9,0]],
                [[6,5,11],[6,11,8],[9,8,11]],
                [[10,8,5],[8,4,5]],
                [[10,2,0],[10,0,5],[4,5,0]],
                [[4,8,5],[8,5,10],[0,3,9]],
                [[9,4,5],[9,5,3],[3,5,2],[10,2,5]],
                [[2,8,4],[2,4,1],[5,1,4]],
                [[0,4,1],[1,4,5]],
                [[2,8,6],[8,4,1],[1,4,5],[3,9,0]],
                [[1,3,9],[4,1,9],[1,4,5]],
                [[4,10,5],[8,4,10],[11,3,1]],
                [[10,2,8],[2,0,5],[5,0,4],[11,3,1]],
                [[8,4,10],[10,4,5],[9,0,11],[11,0,1]],
                [[10,2,5],[2,4,5],[11,2,1],[9,2,11],[2,9,4]],
                [[8,4,5],[8,5,2],[2,5,3],[11,3,5]],
                [[11,3,0],[11,0,5],[4,5,0]],
                [[0,2,9],[2,11,9],[4,2,8],[5,2,4],[2,5,11]],
                [[11,4,5],[11,9,4]],
                [[7,4,9],[6,10,5]],
                [[4,9,7],[0,8,2],[5,10,6]],
                [[3,4,7],[0,3,4],[5,10,6]],
                [[4,8,0],[8,2,7],[7,2,3],[5,10,6]],
                [[2,5,6],[1,2,5],[4,9,7]],
                [[8,6,10],[6,5,0],[0,5,1],[9,7,4]],
                [[0,3,4],[4,3,7],[1,2,5],[5,2,6]],
                [[4,8,7],[8,3,7],[5,8,6],[1,8,5],[8,1,3]],
                [[5,10,6],[1,11,3],[4,9,7]],
                [[0,8,2],[1,11,3],[4,9,7],[5,10,6]],
                [[11,7,9],[7,4,1],[1,4,0],[10,6,5]],
                [[4,10,6],[4,8,2],[1,4,2],[1,4,10],[5,11,7]],
                [[5,11,1],[11,3,6],[6,3,2],[4,9,7]],
                [[3,4,9],[3,0,8],[6,3,8],[6,3,4],[7,5,11]],
                [[4,11,7],[4,0,11],[5,11,6],[6,11,2],[0,2,11]],
                [[7,4,11],[6,5,11],[6,11,8],[4,11,8]],
                [[9,7,5],[10,9,5],[9,10,8]],
                [[0,9,7],[0,7,2],[7,5,2],[5,10,2]],
                [[0,3,7],[0,7,8],[8,7,10],[5,10,7]],
                [[5,10,2],[5,2,7],[3,7,2]],
                [[8,9,7],[5,8,7],[1,8,5],[8,1,2]],
                [[9,7,5],[9,5,0],[1,0,5]],
                [[2,8,1],[8,5,1],[3,8,0],[7,8,3],[8,7,5]],
                [[5,3,7],[5,1,3]],
                [[7,5,6],[5,10,9],[9,10,8],[3,1,11]],
                [[10,3,1],[10,2,0],[9,10,0],[9,10,3],[11,7,5]],
                [[10,7,5],[10,8,7],[11,7,1],[1,7,0],[8,0,7]],
                [[5,10,7],[1,11,7],[1,7,2],[10,7,2]],
                [[3,5,11],[3,2,5],[7,5,9],[9,5,8],[2,8,5]],
                [[11,3,5],[9,7,5],[9,5,0],[3,5,0]],
                [[2,8,0],[11,7,5]],
                [[11,7,5]],
                [[5,7,11]],
                [[0,8,2],[5,7,11]],
                [[5,7,11],[3,0,9]],
                [[2,9,3],[8,2,9],[11,5,7]],
                [[7,11,5],[10,2,1]],
                [[8,1,10],[0,8,1],[5,7,11]],
                [[1,2,10],[0,3,9],[5,7,11]],
                [[1,3,0],[3,9,10],[10,9,8],[5,7,11]],
                [[7,3,5],[3,1,5]],
                [[1,3,5],[3,5,7],[0,8,2]],
                [[5,7,9],[0,5,9],[5,0,1]],
                [[1,5,7],[9,1,7],[8,1,9],[1,8,2]],
                [[2,10,5],[7,2,5],[2,7,3]],
                [[0,8,10],[0,10,3],[3,10,7],[5,7,10]],
                [[0,2,10],[0,10,9],[10,5,9],[5,7,9]],
                [[5,7,9],[5,9,10],[8,10,9]],
                [[11,5,7],[4,8,6]],
                [[0,6,4],[2,0,6],[7,11,5]],
                [[9,0,3],[8,4,6],[11,5,7]],
                [[9,4,8],[4,6,3],[3,6,2],[11,5,7]],
                [[6,8,4],[2,10,1],[7,11,5]],
                [[6,10,2],[10,1,4],[4,1,0],[7,11,5]],
                [[3,9,0],[2,10,1],[7,11,5],[6,8,4]],
                [[6,11,5],[6,10,1],[3,6,1],[3,6,11],[7,9,4]],
                [[7,5,3],[5,3,1],[6,8,4]],
                [[2,0,6],[6,0,4],[3,1,7],[7,1,5]],
                [[11,7,9],[0,5,7],[1,5,0],[4,6,8]],
                [[6,9,4],[6,2,9],[7,9,5],[5,9,1],[2,1,9]],
                [[1,10,5],[7,2,10],[3,2,7],[6,8,4]],
                [[7,10,5],[7,3,10],[6,10,4],[4,10,0],[3,0,10]],
                [[7,8,4],[7,9,0],[2,7,0],[2,7,8],[6,10,5]],
                [[9,5,7],[9,4,6],[10,9,6],[10,9,5]],
                [[5,4,11],[4,9,11]],
                [[9,4,11],[4,11,5],[8,2,0]],
                [[0,3,11],[5,0,11],[0,5,4]],
                [[8,2,3],[8,3,4],[4,3,5],[11,5,3]],
                [[5,11,4],[11,4,9],[1,2,10]],
                [[0,8,1],[1,8,10],[4,9,5],[5,9,11]],
                [[9,3,11],[5,0,3],[4,0,5],[1,2,10]],
                [[5,3,11],[5,4,3],[1,3,10],[10,3,8],[4,8,3]],
                [[9,3,1],[9,1,4],[5,4,1]],
                [[7,9,3],[1,4,9],[5,4,1],[0,8,2]],
                [[5,4,1],[1,4,0]],
                [[4,8,2],[1,4,2],[4,1,5]],
                [[5,4,9],[3,5,9],[2,5,3],[5,2,10]],
                [[9,3,4],[3,5,4],[8,3,0],[10,3,8],[3,10,5]],
                [[0,2,10],[5,0,10],[0,5,4]],
                [[5,8,10],[5,4,8]],
                [[11,5,6],[8,11,6],[11,8,9]],
                [[9,11,5],[6,9,5],[2,9,6],[9,2,0]],
                [[8,0,3],[8,3,6],[3,11,6],[11,5,6]],
                [[11,5,6],[11,6,3],[2,3,6]],
                [[7,5,6],[8,11,5],[9,11,8],[10,1,2]],
                [[1,6,10],[1,0,6],[5,6,11],[11,6,9],[0,9,6]],
                [[5,2,10],[5,6,8],[0,5,8],[0,5,2],[1,3,11]],
                [[6,11,5],[6,10,1],[3,6,1],[3,6,11]],
                [[6,8,9],[6,9,5],[5,9,1],[3,1,9]],
                [[0,9,2],[9,6,2],[1,9,3],[5,9,1],[9,5,6]],
                [[5,6,8],[0,5,8],[5,0,1]],
                [[1,6,2],[1,5,6]],
                [[10,5,2],[5,3,2],[8,5,6],[9,5,8],[5,9,3]],
                [[10,5,6],[0,9,3]],
                [[5,2,10],[5,6,8],[0,5,8],[0,5,2]],
                [[10,5,6]],
                [[11,10,7],[10,6,7]],
                [[6,10,7],[10,7,11],[2,0,8]],
                [[11,7,10],[7,10,6],[9,0,3]],
                [[8,2,9],[9,2,3],[10,6,11],[11,6,7]],
                [[7,11,1],[2,7,1],[7,2,6]],
                [[6,7,11],[1,6,11],[0,6,1],[6,0,8]],
                [[5,11,1],[2,7,11],[6,7,2],[3,9,0]],
                [[9,1,3],[9,8,1],[11,1,7],[7,1,6],[8,6,1]],
                [[1,10,6],[1,6,3],[7,3,6]],
                [[11,1,10],[6,3,1],[7,3,6],[2,0,8]],
                [[9,0,1],[9,1,7],[7,1,6],[10,6,1]],
                [[2,1,8],[1,9,8],[6,1,10],[7,1,6],[1,7,9]],
                [[7,3,6],[6,3,2]],
                [[3,0,8],[6,3,8],[3,6,7]],
                [[7,9,0],[2,7,0],[7,2,6]],
                [[6,9,8],[6,7,9]],
                [[8,4,7],[11,8,7],[8,11,10]],
                [[2,0,4],[2,4,10],[10,4,11],[7,11,4]],
                [[6,4,7],[11,8,4],[10,8,11],[9,0,3]],
                [[11,4,7],[11,10,4],[9,4,3],[3,4,2],[10,2,4]],
                [[2,8,4],[2,4,1],[4,7,1],[7,11,1]],
                [[7,11,1],[7,1,4],[0,4,1]],
                [[11,0,3],[11,1,2],[8,11,2],[8,11,0],[9,4,7]],
                [[1,7,11],[1,3,9],[4,1,9],[4,1,7]],
                [[7,3,1],[10,7,1],[8,7,10],[7,8,4]],
                [[1,10,3],[10,7,3],[0,10,2],[4,10,0],[10,4,7]],
                [[4,7,8],[7,10,8],[0,7,9],[1,7,0],[7,1,10]],
                [[4,7,9],[2,1,10]],
                [[2,8,4],[7,2,4],[2,7,3]],
                [[7,0,4],[7,3,0]],
                [[7,8,4],[7,9,0],[2,7,0],[2,7,8]],
                [[4,7,9]],
                [[6,4,9],[6,9,10],[11,10,9]],
                [[5,6,4],[9,10,6],[11,10,9],[8,2,0]],
                [[11,10,6],[4,11,6],[0,11,4],[11,0,3]],
                [[6,4,10],[4,11,10],[2,4,8],[3,4,2],[4,3,11]],
                [[1,2,6],[1,6,11],[11,6,9],[4,9,6]],
                [[8,6,0],[6,1,0],[9,6,4],[11,6,9],[6,11,1]],
                [[3,11,0],[11,4,0],[2,11,1],[6,11,2],[11,6,4]],
                [[3,11,1],[8,6,4]],
                [[1,10,6],[1,6,3],[6,4,3],[4,9,3]],
                [[9,2,0],[9,3,1],[10,9,1],[10,9,2],[8,6,4]],
                [[1,10,6],[4,1,6],[1,4,0]],
                [[1,8,2],[1,10,6],[4,1,6],[4,1,8]],
                [[6,4,9],[3,6,9],[6,3,2]],
                [[6,0,8],[6,4,9],[3,6,9],[3,6,0]],
                [[2,4,0],[2,6,4]],
                [[8,6,4]],
                [[11,10,9],[9,10,8]],
                [[10,2,0],[9,10,0],[10,9,11]],
                [[8,0,3],[11,8,3],[8,11,10]],
                [[11,2,3],[11,10,2]],
                [[11,1,2],[8,11,2],[11,8,9]],
                [[9,1,0],[9,11,1]],
                [[11,0,3],[11,1,2],[8,11,2],[8,11,0]],
                [[3,11,1]],
                [[9,3,1],[10,9,1],[9,10,8]],
                [[9,2,0],[9,3,1],[10,9,1],[10,9,2]],
                [[0,10,8],[0,1,10]],
                [[2,1,10]],
                [[8,3,2],[8,9,3]],
                [[0,9,3]],
                [[2,8,0]],
                []
               ]

    # make polygon data from grid data
    @staticmethod
    def MakePolygons( moval, ex, ey, ez, boxmin,  thres, ndiv ):
        try:
            nx = len(moval)
            ny = len(moval[0])
            nz = len(moval[0][0])

            # interpolation
            nxdiv = (nx-1) * ndiv + 1
            nydiv = (ny-1) * ndiv + 1
            nzdiv = (nz-1) * ndiv + 1
            movaldiv = [[[0.0 for k in range(nzdiv)] for j in range(nydiv)] for i in range(nxdiv)]

            weight = [[[None for k in range(ndiv+1)] for j in range(ndiv+1)] for i in range(ndiv+1)]
            for ixdiv in range(0, ndiv+1):
                for iydiv in range(0, ndiv+1):
                    for izdiv in range(0, ndiv+1):
                        w = [[[0.0 for k in range(2)] for j in range(2)] for i in range(2)]
                        x = [0.0 for k in range(2)]
                        y = [0.0 for k in range(2)]
                        z = [0.0 for k in range(2)]
                        x[0] = float(ixdiv) / ndiv
                        y[0] = float(iydiv) / ndiv
                        z[0] = float(izdiv) / ndiv
                        x[1] = 1.0 - x[0]
                        y[1] = 1.0 - y[0]
                        z[1] = 1.0 - z[0]
                        for jx in range(2):
                            for jy in range(2):
                                for jz in range(2):
                                    w[jx][jy][jz] = x[1-jx] * y[1-jy] * z[1-jz]
                        weight[ixdiv][iydiv][izdiv] = w;

            for ix in range(nx-1):
                for iy in range(ny-1):
                    for iz in range(nz-1):
                        for ixdiv in range(ndiv+1):
                            for iydiv in range(ndiv+1):
                                for izdiv in range(ndiv+1):
                                    w = weight[ixdiv][iydiv][izdiv]
                                    v = 0.0
                                    for jx in range(2):
                                        for jy in range(2):
                                            for jz in range(2):
                                                v += moval[ix+jx][iy+jy][iz+jz] * w[jx][jy][jz]

                                    ixx = ix * ndiv + ixdiv
                                    iyy = iy * ndiv + iydiv
                                    izz = iz * ndiv + izdiv
                                    movaldiv[ixx][iyy][izz] = v
            moval = movaldiv
            nx = nxdiv
            ny = nydiv
            nz = nzdiv
            ex /= ndiv
            ey /= ndiv
            ez /= ndiv

            # determine each vertices wherther in/out of the threshold surface
            bvtx = [[[0 for k in range(nz)] for j in range(ny)] for i in range(nx)]
            for ix in range(0, nx):
                for iy in range(0, ny):
                    for iz in range(0, nz):
                        if moval[ix][iy][iz] > thres:
                            bvtx[ix][iy][iz] = 1

            polygons = []
            for ix in range(0, nx-1):
                for iy in range(0, ny-1):
                    for iz in range(0, nz-1):
                        posxyz = array([ix,iy,iz])
                        icube = 0
                        ibit = 1
                        for k in range(0, 2):
                            for j in range(0, 2):
                                for i in range(0, 2):
                                    icube += bvtx[ix+i][iy+j][iz+k] * ibit
                                    ibit *= 2

                        polys = MC.cubepoly[icube]
                        for triangle in polys:
                            midpos = []
                            for imid in range(0,3):
                                vtxs = MC.midvtx[ triangle[imid] ]
                                pos0 = array(vtxs[0])
                                pos1 = array(vtxs[1])
                                moval0 = moval[ix+vtxs[0][0]][iy+vtxs[0][1]][iz+vtxs[0][2]]
                                moval1 = moval[ix+vtxs[1][0]][iy+vtxs[1][1]][iz+vtxs[1][2]]
                                dif01 = moval0 - moval1
                                if dif01 * dif01 < 1e-20:
                                    pos = ( pos0 + pos1 ) * 0.5
                                else:
                                    dif0 = moval0 - thres
                                    dif1 = moval1 - thres
                                    pos = ( dif0 * pos1 - dif1 * pos0 ) / dif01
                                pos += posxyz
                                pos = pos[0] * ex + pos[1] * ey + pos[2] * ez
                                pos += boxmin
                                midpos.append( pos )

                            vec01 = midpos[1] - midpos[0]
                            vec02 = midpos[2] - midpos[0]
                            vnorm = cross(vec02, vec01)
                            v = linalg.norm(vnorm)
                            if v < 1e-10:
                                continue
                            vnorm /= v

                            midpos0 = midpos[0].tolist()
                            midpos1 = midpos[1].tolist()
                            midpos2 = midpos[2].tolist()
                            vnorm   = vnorm.tolist()
                            polygons.append( [ midpos0, midpos1, midpos2, vnorm ] )

        except BaseException as e:
            print (e)
            print ("Failed to Make polygon data")
            return []

        return polygons

    # return polygon data
    @staticmethod
    def CubePolygons( fval,ex,ey,ez,boxmin,thres,ndiv ):
        try:
            maxpoly = 1000000
            polys1, npoly1 = fucubelib.make_polygons( fval, ex, ey, ez, boxmin,
                                                      thres, ndiv, maxpoly )
            if npoly1 == maxpoly:
                raise
            polys1 = polys1[:npoly1]
            polys2, npoly2 = fucubelib.make_polygons( fval, ex, ey, ez, boxmin,
                                                      -thres, ndiv, maxpoly )
            if npoly2 == maxpoly:
                raise
            polys2 = polys2[:npoly2]
        except BaseException as e:
            print (e)
            print ('Failed to make polygons by fortran, try python routine')
            polys1 = MC.MakePolygons( fval, ex, ey, ez, boxmin,  thres, ndiv )
            polys2 = MC.MakePolygons( fval, ex, ey, ez, boxmin, -thres, ndiv )

        return [ polys1, polys2 ]

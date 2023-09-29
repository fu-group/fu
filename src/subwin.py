#!/bin/sh
# -*- coding: utf-8 -*-



import sys
import wx
import wx.glcanvas
import wx.lib.scrolledpanel as scrolled


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


#import wx.html

#from OpenGL.GL import *
#from OpenGL.GLU import *
#from OpenGL.GLUT import *

import getpass
import os
import shutil
try: import psutil # downloaded from http://code.google.com/p/psutil/downloads/detail?name=psutil-1.0.1.win32-py2.7.exe&can=2&q=
except: pass
import wx.py
import wx.html
import wx.lib.scrolledpanel
#import wx.grid

try: from wx import grid as wxgrid
except: pass

import json
import copy
import numpy
from math import log10

import functools
import threading
#import multiprocessing
import subprocess
import datetime
import time

try:
    import matplotlib
    matplotlib.interactive( True )
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
except ImportError:
    pass
try:
    #py3# from matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
    from matplotlib.backends.backend_wx import NavigationToolbar2Wx
except ImportError:
    pass
try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem import Draw
    rdkit_ready = True
except: rdkit_ready = False

import PIL

import fu_molec as molec
#####import molec
import fu_draw as draw
#####import draw
import const
import lib
import graph
import ctrl
try: import fortlib
except: pass
import custom
import rwfile
import build

from wx.lib.mixins.listctrl import CheckListCtrlMixin

#from wx import import Notebook
"""
class Progress_Bar(wx.frame):
    def __init__(self,parent,id,model,ctrlflag,molnam,winpos):
    self.statusbar = self.CreateStatusBar()
    self.statusbar.SetFieldsCount(3)
    self.statusbar.SetStatusWidths([320, -1, -2])

    self.progress_bar = wx.Gauge(self.statusbar, -1, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
    rect = self.statusbar.GetFieldRect(1)
    self.progress_bar.SetPosition((rect.x+2, rect.y+2))
    self.progress_bar.SetSize((rect.width-4, rect.height-4))
    #Then whenever I want to use the progress bar, I call
    def ProgressBar(self,on):
        if on: self.progress_bar.Show()
        else: self.progress_bar.Destroy() or Hide()
"""


class ImageSetting_Frm(wx.MiniFrame):
    """ Set params for saving image. Called by SlideShowCtrl_Frm class """
    def __init__(self,parent,id,winpos,winsize=[],icondir=None):
        if len(winsize) <= 0: winsize=[320,150]
        winsize=lib.WinSize(winsize,False)
            #if lib.GetPlatform() == 'MACOSX': winsize=[300,130] #[250,95]
            #elif lib.GetPlatform() == 'WINDOWS': winsize=[300,110] #[250,185]
            #else: winsize=[300,130]
        winpos  = lib.SetWinPos(winpos)
        self.title='Image setting'
        wx.MiniFrame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        #self.winlabel='Open SlideShowCtrl'
        self.parent=parent
        self.mdlwin=parent.mdlwin
        self.model=self.mdlwin.model
        self.icondir=icondir
        #
        self.bgcolor='light gray' #'gray'
        self.SetBackgroundColour(self.bgcolor)
        self.imgformlst=['png','bmp','jpeg','pcx','pnm','xpm']
        self.saveevery=self.parent.saveevery
        if self.saveevery < 0: self.saveevery=1
        self.format=self.parent.imageformat
        self.imagewidth=-1
        if len(self.format) <= 0: self.format='jpeg'
        self.imagepath=self.parent.imagepath
        if len(self.imagepath) <= 0:
            self.imagepath=self.model.setctrl.GetDir('Images')
        #
        self.CreatePanel()
        self.Show()
        # event handlers
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreatePanel(self):
        """ create panel """
        [w,h]=size=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=[-1,-1],size=size)
        #
        htext=22 #18 #20
        hcb=24 #const.HCBOX
        xloc=2; yloc=2
        #
        yloc=5; xloc=10
        wx.StaticText(self.panel,-1,'Save every:',pos=(xloc,yloc+2),
                      size=(75,htext))
        #xloc += 30
        self.scevry=wx.SpinCtrl(self.panel,-1,value=str(self.saveevery),
                                pos=(xloc+75,yloc),size=(50,22),
                              style=wx.SP_ARROW_KEYS,min=1,max=1000)
        wx.StaticText(self.panel,-1,"Image format:",pos=(xloc+135,yloc+2),
                      size=(90,htext))
        self.cmbimg=wx.ComboBox(self.panel,wx.ID_ANY,'',pos=(xloc+230,yloc),
                                size=(60,hcb))
        #self.cmbimg.Bind(wx.EVT_COMBOBOX,self.OnImageFormat)
        self.cmbimg.SetItems(self.imgformlst)
        self.cmbimg.SetValue(self.format)
        yloc += 30
        wx.StaticText(self.panel,-1,"Image width(pixels):",pos=(xloc,yloc),
                      size=(120,htext))
        self.tclsiz=wx.TextCtrl(self.panel,-1,'-1',pos=(xloc+140,yloc),
                                size=(60,22))
        self.tclsiz.Bind(wx.EVT_TEXT,self.OnImageSize)

        self.tclsiz.Disable() # this functio does not work

        yloc += 30; xloc=10
        stpath=wx.StaticText(self.panel,-1,"path:",pos=(xloc,yloc),
                             size=(30,htext))
        #stpath.SetToolTipString('directory to save image files')
        lib.SetTipString(stpath,'directory to save image files')
        self.tcpath=wx.TextCtrl(self.panel,-1,self.imagepath,pos=(xloc+35,yloc),
                                size=(230,22))
        #btnbrws=wx.Button(self.panel,wx.ID_ANY,"browse",pos=(xloc+220,yloc),
        #                  size=(60,22))
        iconfile=os.path.join(self.icondir,'browse20.png')
        btnpos=(xloc+270,yloc)
        btnbrws=lib.BitmapIcon(self.panel,iconfile,btnchr='B',btnpos=btnpos,btnsize=[20,20])
        btnbrws.Bind(wx.EVT_BUTTON,self.OnBrowseDir)
        lib.SetTipString(btnbrws, 'browse folders')
        yloc += 30; xloc=10
        xloc=90
        btnsav=wx.Button(self.panel,wx.ID_ANY,"Apply",pos=(xloc,yloc+2),
                         size=(50,22))
        btnsav.Bind(wx.EVT_BUTTON,self.OnApply)
        btnsav=wx.Button(self.panel,wx.ID_ANY,"Close",pos=(xloc+80,yloc+2),
                         size=(50,22))
        btnsav.Bind(wx.EVT_BUTTON,self.OnClose)

    def OnBrowseDir(self,event):
        """ Event handler to browse directory """
        imagepath=lib.GetDirectoryName(self)
        if len(imagepath) <= 0: return
        self.imagepath=imagepath
        self.tcpath.SetValue(self.imagepath)

    def OnApply(self,event):
        """ Event handler to accept input param """
        self.saveevery=int(self.scevry.GetValue())
        self.format=self.cmbimg.GetValue()
        self.imagepath=self.tcpath.GetValue()
        self.imagewidth=int(self.tclsiz.GetValue())
        self.parent.SetSaveImageParams(self.saveevery,self.format,
                                       self.imagepath,self.imagewidth)
        self.OnClose(1)

    def OnImageSize(self,event):
        pass
        #obj=event.GetEventObject()
        #self.imagewidth=int(obj.GetValue())

    def OnClose(self,event):
        """ Event handler to close the window """
        self.Destroy()

class SlideShowCtrl_Frm(wx.MiniFrame):
    """ Slide show class """
    def __init__(self,parent,winpos=[],winsize=[],icondir=None):
        self.model=parent; self.mdlwin=self.model.mdlwin
        if len(winsize) <= 0: winsize=[260,150]
        winsize=lib.WinSize(winsize)
        if len(winpos) <= 0: winpos=lib.WinPos(self.mdlwin)
        winpos  = lib.SetWinPos(winpos)
        self.title='Slide show controller'
        wx.MiniFrame.__init__(self,parent,-1,self.title,pos=winpos,size=winsize,
                          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)

        self.winlabel='SlideShowCtrl'
        self.mdlwin.draw.SetShowDrawingMessage(False)
        self.mdlwin.draw.SetShowBusyCursor(False)
        self.helpname=self.winlabel
        if icondir is None:
            try:
                icondir=os.path.join(self.model.initdic['progpath'],'icons')
            except: pass
        self.icondir=icondir
        # timer instance
        self.timerid=wx.NewId()
        self.timer=wx.Timer(self,self.timerid)
        self.Bind(wx.EVT_TIMER,self.OnTimer)
        # Create Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[SlideShow]')
        self.Bind(wx.EVT_MENU,self.OnMenu)

        self.panelpos=(2,2)
        self.panel=None
        self.bgcolor='light gray' #'gray'
        self.SetBackgroundColour(self.bgcolor)
        #
        self.curpos=0
        self.pos_min=1
        self.pos_max=self.model.molctrl.GetNumberOfMols()
        if self.pos_max <= self.pos_min:self.pos_max=self.pos_min+1
        self.movable=False
        self.panpos=wx.GetMousePosition()
        self.now=None
        self.playon=False
        self.timeslice=10 #100
        self.interval=1
        self.repeattimes=1
        self.repeatnmb=0
        self.drawmolname=True
        self.superimpose=False # flag
        self.superimposedmol=None # object
        self.supermolidx=-1
        self.groupnamlst=[]
        self.rotate=False
        self.clockwise=True
        self.rotangle=10
        self.translate=False
        self.right=True
        self.trandif=20
        self.tranvec=[]
        self.zoom=False
        self.magnify=True
        self.zoomdif=100
        #self.imgtyp=self.model.setctrl.GetParam('image-format') # default 'png'
        self.scnnames=['None'] # Scenario file list
        self.currentscn='None'
        self.scnfiledic={}
        self.scnstep=False
        self.scnstepobjlst=[]
        self.curscnsetp=0
        self.maxscnsteps=0
        self.pause=False
        self.pausesteps=0
        self.stepsteps=0
        self.saveimage=False
        #
        if not lib.IsWxVersion2(pltfrm='MACOSX'):
            self.btnstyle=wx.BORDER_NONE
        else: self.btnstyle=0
        self.imagepath=self.model.setctrl.GetDir('Images')
        self.imgsetwin=None
        self.imageformat='jpeg'
        self.saveimage=False
        self.imagenumber=0
        self.imagewidth=-1
        self.saveevery=1
        self.imgfiledic={}
        # supress message in molde object
        self.savesuppressmess=self.model.GetSuppressMessage()
        self.model.SetSuppressMessage(True)
        # create panel
        #self.LoadBitmaps()
        self.LoadBitmapsFromFile()
        self.CreatePanel()
        self.Show()
        # event handlers
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def LoadBitmapsFromFile(self):
        """ Load bitmap image data for bitmapbutton """
        self.playbmp=self.model.setctrl.GetIconBmp('blueberry-play-20',
                                                   imgfrm='.png')
        self.nextbmp=self.model.setctrl.GetIconBmp('blueberry-next-20',
                                                   imgfrm='.png')
        self.previousbmp=self.model.setctrl.GetIconBmp('blueberry-previous-20',
                                                       imgfrm='.png')
        self.pausebmp=self.model.setctrl.GetIconBmp('blueberry-pause-20',
                                                    imgfrm='.png')

    def LoadBitmaps(self):
        """ Not used. 22Mar2016. use LoadBitmapsFromFile() """

        #self.playbmp=const.blueberry_play_20.GetBitmap()
        self.nextbmp=const.blueberry_next_20.GetBitmap()
        #self.previousbmp=const.blueberry_previous_20.GetBitmap()
        #self.pausebmp=const.blueberry_pause_20.GetBitmap()

    def CreatePanel(self):
        """ Create panel """

        [w,h]=size=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=[-1,-1],size=size)
        #
        htext=22 #20
        hcb=25 #const.HCBOX
        xloc=2; yloc=2
        #
        yloc=5; xloc=10
        wx.StaticText(self.panel,-1,"Scenario:",pos=(xloc,yloc+2),size=(55,18))
        self.cmbscn=wx.ComboBox(self.panel,wx.ID_ANY,"",pos=(xloc+65,yloc),
                                size=(120,hcb))
        self.cmbscn.Bind(wx.EVT_COMBOBOX,self.OnScenario)
        self.cmbscn.SetItems(self.scnnames)
        self.cmbscn.SetStringSelection(self.currentscn)
        #self.cmbscn.SetToolTipString('Select a script to execute')
        lib.SetTipString(self.cmbscn,'Select a script to execute')
        wx.StaticText(self.panel,-1,"Rec:",pos=(xloc+200,yloc+2),size=(30,18))
        #self.btnsav=wx.ToggleButton(self.panel,-1,'',pos=(w-30,yloc+5),
        #                            size=(20,20),style=wx.BORDER_NONE)
        self.btnsav=wx.Button(self.panel,-1,'',pos=(w-30,yloc+5),
                                    size=(20,15),style=self.btnstyle)

        mess='Toggle button to turn save image on,off (red,black)'
        self.btnsav.SetBackgroundColour(wx.BLACK)
        self.btnsav.Bind(wx.EVT_BUTTON,self.OnSaveImage)
        #self.btnsav.SetToolTipString(mess)
        lib.SetTipString(self.btnsav,mess)

        yloc += 30
        wx.StaticText(self.panel,-1,"Repeat times:",pos=(xloc,yloc),
                      size=(85,18))
        xloc += 90
        self.scerep=wx.SpinCtrl(self.panel,-1,value=str(self.repeattimes),
                                pos=(xloc,yloc),size=(50,22),
                              style=wx.SP_ARROW_KEYS,min=-1,max=100)
        #self.scerep.SetToolTipString('Repeat times, "-1" for infinite loop')
        lib.SetTipString(self.scerep,'Repeat times, "-1" for infinite loop')
        self.stmes=wx.StaticText(self.panel,-1,'0',pos=(160,yloc+2),
                                 size=(25,htext))

        #self.scerep.Bind(wx.EVT_SPINCTRL,self.OnPlayRepeatTimes)
        yloc +=20
        xloc=10
        self.slpos=wx.Slider(self.panel,pos=(xloc,yloc+2),size=(w-25,22),
                             minValue=self.pos_min,maxValue=self.pos_max,
                             style=wx.SL_HORIZONTAL)
        self.slpos.Bind(wx.EVT_SLIDER,self.OnSlider)
        #self.slpos.Bind(wx.EVT_LEFT_UP,self.OnLeftClick)
        #self.slpos.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)

        st1=wx.StaticText(self.panel,wx.ID_ANY,str(self.pos_max),
                          pos=(w-35,yloc-12),size=(25,htext))
        color=[122,198,20]
        yloc += 25; xloc += 10
        self.btnplay=wx.BitmapButton(self.panel,-1,bitmap=self.playbmp,
                                     pos=(xloc,yloc),
                #size=(self.playbmp.GetWidth(),self.playbmp.GetHeight()))
                size=(25,25))
        self.btnplay.SetBackgroundColour(color)
        self.btnplay.Bind(wx.EVT_BUTTON,self.OnPlay)
        #self.btnplay.SetToolTipString('start play')
        lib.SetTipString(self.btnplay,'start play')
        xloc += 30
        self.btnpause=wx.BitmapButton(self.panel,-1,bitmap=self.pausebmp,
                                      pos=(xloc,yloc),
                #size=(self.pausebmp.GetWidth(),self.pausebmp.GetHeight()))
                size=(25,25))
        self.btnpause.Bind(wx.EVT_BUTTON,self.OnPause)
        self.btnpause.SetBackgroundColour(color)
        #self.btnpause.SetToolTipString('Pause play')
        lib.SetTipString(self.btnpause,'Pause play')
        xloc += 30
        #self.txtspn=wx.StaticText(self.panel,-1,"Interval",pos=(120,yloc),size=(95,18))
        self.scintvl=wx.SpinCtrl(self.panel,-1,value=str(self.interval)
                                 ,pos=(xloc,yloc+2),size=(50,22),
                              style=wx.SP_ARROW_KEYS,min=0,max=10000)
        self.scintvl.Bind(wx.EVT_SPINCTRL,self.OnInterval)
        mess='Inteval in unit of '+str(self.timeslice)+'ms'
        #self.scintvl.SetToolTipString(mess)
        lib.SetTipString(self.scintvl,mess)
        xloc += 75 #65
        self.btnprev=wx.BitmapButton(self.panel,-1,bitmap=self.previousbmp,
                                     pos=(xloc,yloc),
                #size=(self.previousbmp.GetWidth(),self.previousbmp.GetHeight()))
                size=(25,25))
        self.btnprev.SetBackgroundColour(color)
        self.btnprev.Bind(wx.EVT_BUTTON,self.OnPrevious)
        #self.btnprev.SetToolTipString('Previous molecule')
        lib.SetTipString(self.btnprev,'Previous molecule')
        xloc += 30
        self.btnnext=wx.BitmapButton(self.panel,-1,bitmap=self.nextbmp,
                                     pos=(xloc,yloc),
                #size=(self.nextbmp.GetWidth(),self.nextbmp.GetHeight()))
                size=(25,25))
        self.btnnext.Bind(wx.EVT_BUTTON,self.OnNext)
        self.btnnext.SetBackgroundColour(color)
        #self.btnnext.SetToolTipString('Next molecule')
        lib.SetTipString(self.btnnext,'Next molecule')
        xloc += 30
        self.tccur=wx.TextCtrl(self.panel,-1,str(self.curpos),
                               pos=(xloc,yloc+2),
                               size=(35,22),style=wx.TE_PROCESS_ENTER)
        #self.tccur.SetToolTipString('Input molecule number and "ENETR"')
        lib.SetTipString(self.tccur,'Input molecule number and "ENETR"')
        self.tccur.Bind(wx.EVT_TEXT_ENTER,self.OnCurrent)

    def OnSaveImage(self,event):
        """ Event handler to save image

        """
        #self.saveimage=self.btnsav.GetValue()
        if self.saveimage: self.saveimage=False
        else: self.saveimage=True
        if self.saveimage: self.btnsav.SetBackgroundColour(wx.RED)
        else: self.btnsav.SetBackgroundColour(wx.BLACK)

    def SuperimposedMol(self,on):
        """ Set superimpose molecule flag

        :param bool on: True for make, False for destroy
        """
        if on:
            if not self.superimposedmol:
               self.model.MakeSuperMolecule()
               name,self.superimposedmol=self.model.molctrl.GetCurrentMol()
               self.supermolidx=self.model.molctrl.GetCurrentMolIndex()
               self.groupnamlst=self.model.ListGroupName()
        else:
            try:
                molidx=self.model.molctrl.GetCurrentMolIndex()
                if molidx != self.supermolidx:
                   self.model.SwitchMol(self.supermolidx,self.superimposedmol,
                                        False,False)
                   self.model.DrawMol(True)
                self.model.RemoveMol(False)
                self.superimposedmol=None
            except: pass

    def OnScenario(self,event):
        """ Event handler to execute Scenario script.

        """
        if self.timer.IsRunning():
            mess='Working. Please wait and try later.'
            lib.MessageBoxOK(mess,'OnScenario')
            self.currentscn='None'
            self.cmbscn.SetStringSelection(self.currentscn)
            self.cmbscn.Refresh()
            return
        self.currentscn=self.cmbscn.GetValue()
        nmol=self.model.molctrl.GetNumberOfMols()
        if nmol <= 0:
            self.currentscn='None'
            self.cmbscn.SetStringSelection(self.currentscn)
            mess='No molecular data in fumodel.'
            lib.MessageBoxOK(mess,'SlideShowCtrl(OnScenario)')
            return
        if self.currentscn != 'None':
            #self.EnableWidgets(False)
            scnfile=self.scnfiledic[self.currentscn]
            self.model.ExecuteScript1(scnfile)
            #self.EnableWidgets(True)

    def PlayScenarioSteps(self,scnobjlst):
        self.scnstep=True
        self.scnstepobjlst=scnobjlst
        self.curscnstep=-1
        self.maxscnsteps=len(self.scnstepobjlst)
        self.steptimer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.OnStepTimer,self.steptimer)
        self.steptimer.Start(10)

    def OnStepTimer(self,event):
        self.stepsteps += 1
        if self.timer.IsRunning(): return
        if self.pause:
            if self.stepsteps < self.pausesteps: return
            else:
                self.pause=False; self.pausesteps=0
        self.curscnstep += 1
        if self.curscnstep >= self.maxscnsteps:
            self.steptimer.Stop()
            self.scnstep=False
            self.scnstepobjlst=[]
            self.curscnstep=-1
            self.maxscnsteps=0
            self.pause=True
            self.pausesteps=0
        else:
            exeobj=self.scnstepobjlst[self.curscnstep]()

    def PauseStep(self,steps):
        self.pausesteps=steps
        if steps == 0: self.pause=False
        else: self.pause=True
        self.stepsteps=0

    def GetDrawMolName(self):
        """ Get molecular name

        :return: molecular name drawn on screen
        """
        return self.drawmolname

    def OnBrowseDir(self,event):
        """ Event handler. Browse directory

        """
        imagepath=lib.GetDirectoryName(self)
        if len(imagepath) <= 0: return
        self.imagepath=imagepath
        self.tcpath.SetValue(self.imagepath)

    def OnLeftDown(self,event):
        """ Mouse event handler. Not used.

        """
        self.leftdown=True
        event.Skip()

    def OnLeftClick(self,event):
        """ Mouse event handler. Not used. does not work as expected

        """
        if not self.leftdown: return
        self.leftdown=False
        pos=event.GetPosition()
        curpos=self.GetSliderValueAtClick(pos)
        if curpos < 0: return
        self.curpos=curpos
        curmol=self.curpos-1
        name=self.model.molctrl.GetMolName(curmol)
        try: self.mdlwin.molchoice.ChoiceMol(name,False)
        except: pass
        self.slpos.SetValue(self.curpos)
        self.tccur.SetValue(str(self.curpos))
        event.Skip()

    def GetSliderValueAtClick(self,pos):
        """ Get value on slider. does not work as expected. """
        slwinpos=self.slpos.GetPosition()
        slwinsize=self.slpos.GetSize()
        slposx=pos[0]-slwinpos[0]
        slposy=pos[1]-slwinpos[1]
        if slposx < 0: return -1
        if slposx > slwinsize[0]: return -1
        if slposy < 0: return -1
        if slposy > slwinsize[1]: return -1
        curpos=int((float(slposx)/float(slwinsize[0]))*self.pos_max)+1
        return curpos

    def OnCurrent(self,event):
        """ Event handler to get current position (current molecule)

        """
        self.curpos=int(self.tccur.GetValue())
        curmol=self.curpos-1
        if self.superimpose:
            name=self.groupnamlst[curmol]
            self.curpos=curmol
        else:
            name=self.model.molctrl.GetMolName(curmol)
            try: self.mdlwin.molchoice.ChoiceMol(name)
            except: pass
            self.slpos.SetValue(self.curpos)

    def OnSlider(self,event):
        """ Event handler to get molecule number at slider position

        """
        self.curpos=self.slpos.GetValue()
        curmol=self.curpos-1

        if self.superimpose:
            name=self.groupnamlst[curmol]
        else:
            name=self.model.molctrl.GetMolName(curmol)

            try: self.mdlwin.molchoice.ChoiceMol(name,False)
            except: pass
            self.tccur.SetValue(str(self.curpos))

    def OnInterval(self,event):
        """ Event handler to get interval

        """
        obj=event.GetEventObject()
        self.interval=obj.GetValue()
        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start(self.interval*self.timeslice)

    def SelectNextGroup(self):
        """ Select next group in superimpose mode

        """
        self.curpos += 1
        if self.curpos >= len(self.groupnamlst): self.curpos=0
        self.model.SetSelectAll(False)
        name=self.groupnamlst[self.curpos]
        self.model.SetSelectGroup(name,True)
        #self.model.DrawMol(True)

        mess='current group='+name
        self.model.Message(mess,0,'')

    def SelectPreviousGroup(self):
        """ Select next group in superimposed mode

        """
        self.curpos -= 1
        if self.curpos < 0: self.curpos=len(self.groupnamlst)-1
        self.model.SetSelectAll(False)
        name=self.groupnamlst[self.curpos]
        self.model.SetSelectGroup(name,True)
        #self.model.DrawMol(True)

        mess='current group='+name
        self.model.Message(mess,0,'')

    def OnNext(self,event):
        """ Event handler to proceed next molecule

        """
        name=self.model.molctrl.GetCurrentMolName()
        hbond=self.mdlwin.menuctrl.IsChecked("Hydrogen/vdW bond")
        if hbond: drw=False
        else: drw=True
        if self.superimpose:
            self.SelectNextGroup()
            name=self.groupnamlst[self.curpos]
        else:
            try:
                self.mdlwin.molchoice.ChoiceNextMol(name,False,drw)
                self.curpos=self.model.molctrl.GetCurrentMolIndex()+1
                name=self.model.molctrl.GetCurrentMolName()
            except: pass
        if hbond: self.model.MakeHydrogenBond()
        self.tccur.SetValue(str(self.curpos))
        self.slpos.SetValue(self.curpos)

        if self.drawmolname:
            self.model.DrawMessage('MolName',name,'',[],[])
        else: self.model.RemoveDrawMessage('MolName')
        mess='current molecule='+name
        self.model.Message(mess,0,'')

    def OnPrevious(self,event):
        """ Event handler to proceed previous molecule

        """
        name=self.model.molctrl.GetCurrentMolName()
        hbond=self.mdlwin.menuctrl.IsChecked("Hydrogen/vdW bond")
        if hbond: drw=False
        else: drw=True
        if self.superimpose:
            self.SelectPreviousGroup()
            name=self.groupnamlst[self.curpos]
        else:
            try:
                self.mdlwin.molchoice.ChoicePrevMol(name,False,drw)
                self.curpos=self.model.molctrl.GetCurrentMolIndex()+1
                name=self.model.molctrl.GetCurrentMolName()
            except: pass
        if hbond:  self.model.MakeHydrogenBond()
        self.tccur.SetValue(str(self.curpos))
        self.slpos.SetValue(self.curpos)

        if self.drawmolname:
            self.model.DrawMessage('MolName',name,'',[],[])
        else: self.model.RemoveDrawMessage('MolName')
        mess='current molecule='+name
        self.model.Message(mess,0,'')

    def OnPause(self,event):
        """ Event handler to pause(stop) play

        """
        self.StopPlay()

    def StopPlay(self):
        """ Stop play

        """
        self.playon=False
        self.timer.Stop()
        self.repeatnmb=0
        self.stmes.SetLabel('0')
        self.repeattimes=1
        self.cmbscn.SetStringSelection('None')

    def OnPlay(self,event):
        """ Event handler to start play

        """
        self.StartPlay()

    def StartPlay(self):
        """ Stary play

        """
        nmol=self.model.molctrl.GetNumberOfMols()
        if nmol <= 0:
            mess='No molecular data in fumodel.'
            lib.MessageBoxOK(mess,'SlideShowCtrl(StartPlay)')
            return
        # start
        self.playon=True
        self.repeatnmb=0
        self.repeattimes=int(self.scerep.GetValue())
        self.timer.Start(self.interval*self.timeslice)
        self.curpos=int(self.tccur.GetValue())-2
        if self.curpos < 0:
            if self.superimpose:
                self.curpos=len(self.groupnamlst)-1
            else:
                self.curpos=self.model.molctrl.GetNumberOfMols()-1
        if self.saveimage:
            mess='Image files will be created in '+self.imagepath
            self.model.ConsoleMessage(mess)
        self.busy=False

    def OnTimer(self,event):
        """ Event handler for timer event

        """
        self.Play()
        self.busy=False
        event.Skip()

    def Play(self):
        """ Play slide show

        """
        self.busy=True
        self.repeatnmb += 1
        nmol=self.model.molctrl.GetNumberOfMols()
        if self.repeattimes >= 0 and self.repeatnmb > self.repeattimes*nmol:
            self.OnPause(1)
            return
        if self.superimpose:
            self.SelectNextGroup()
            name=self.groupnamlst[self.curpos]
        else:
            name=self.model.molctrl.GetCurrentMolName()
            #
            hbond=self.mdlwin.menuctrl.IsChecked("Hydrogen/vdW bond")
            if hbond: drw=False
            else: drw=True

            drw=False
            try: self.mdlwin.molchoice.ChoiceNextMol(name,False,drw)
            except: pass
            if hbond: self.model.MakeHydrogenBond()

            name=self.model.molctrl.GetCurrentMolName()
            self.curpos=self.model.molctrl.GetCurrentMolIndex()+1
            nmb=(self.repeatnmb-1)/nmol+1
            self.stmes.SetLabel(str(nmb))

        self.tccur.SetValue(str(self.curpos))
        self.slpos.SetValue(self.curpos)

        if self.rotate or self.translate or self.zoom:
            if self.rotate:
                axis=self.model.mousectrl.GetRotateAxis()
                if self.clockwise: rot=[self.rotangle,0]
                else: rot=[-self.rotangle,0]
                self.model.Rotate(axis,rot)
            if self.translate:
                if len(self.tranvec) <= 0:
                    tran=self.trandif
                    if not self.right: tran=-tran
                    tran=[tran,0]
                else: tran=self.tranvec
                self.model.Translate(tran)
            if self.zoom:
                zoom=self.zoomdif
                if self.magnify: zoom=-zoom
                self.model.Zoom(zoom)
        else: self.model.DrawMol(True)

        if self.drawmolname:
            self.model.DrawMessage('MolName',name,'',[],[])
        else: self.model.RemoveDrawMessage('MolName')
        # save image
        save=(self.repeatnmb-1) % self.saveevery
        if self.saveimage and (self.repeatnmb == 1 or save == 0):
            self.imagenumber += 1
            filename=name+'-'+str(self.imagenumber)+'.'+self.imageformat
            filename=os.path.join(self.imagepath,filename)
            self.model.SaveCanvasImage(filename,imgwidth=self.imagewidth)
            molnmb=self.model.molctrl.GetCurrentMolIndex()
            self.imgfiledic[filename]=molnmb
            #mess='Saved image. filename='+filename
            #self.model.ConsoleMessage(mess)
        #
        self.busy=False

    def OpenImageSettingPanel(self):
        """ Open setting panel for save image

        """
        pos=self.GetPosition()
        winpos=[pos[0]+20,pos[1]+50]
        winsize=[]
        self.imgsetwin=ImageSetting_Frm(self,-1,winpos,winsize,icondir=self.icondir)

    def RestoreMolecules(self):
        """ Restore molecules in fumodel instance

        """
        self.pos_max=self.model.molctrl.GetNumberOfMols()
        if self.pos_max <= self.pos_min:self.pos_max=self.pos_min+1
        self.panel.Destroy()
        self.CreatePanel()

    def SetSaveImageParams(self,every,format,savepath,width):
        """ Set params for save image

        """
        self.saveevery=every
        self.imageformat=format
        self.imagepath=savepath
        self.imagewidth=width
        self.PrintSaveImageParams()

    def PrintSaveImageParams(self):
        """ Print save image params on fumodel console

        """
        mess='Set save image params: every='+str(self.saveevery)+', format='+self.imageformat
        mess=mess+', savepath='+self.imagepath
        self.model.ConsoleMessage(mess)

    def SetRotate(self,on):
        """ Set rotation flag on/off

        :param bool on: True for on, False for off
        """
        self.rotate=on
    def SetTranslate(self,on):
        """ Set translation flag on/off

        :param bool on: True for on, False for off
        """
        self.translate=on
    def SetZoom(self,on):
        """ Set zoom flag on/off

        :param bool on: True for on, False for off
        """
        self.zoom=on
    def SetRotateAngle(self,rotangle):
        """ Set rotation angle per step

        :param int rotangle: rotation angle
        """
        self.rotangle=rotangle

    def GetRotateAngle(self):
        return self.rotangle
    def SetTranslateDif(self,trandif):
        """ Set translation move distance per step

        :param int trandif: move distance
        """
        self.trandif=trandif
    def GetTranslateDif(self):
        return self.trandif
    def SetTranslateVec(self,vec):
        """ Set translation move vector per step

        :param lst vec: [xmov(int),ymov(int)]
        """
        self.tranvec=vec

    def SetTranslateRight(self,on):
        self.right=on
    def SetZoomMagnify(self,on):
        self.magnify=on
    def SetRotateClockwise(self,on):
        self.clockwise=on
    def GetTranslateRight(self):
        return self.right
    def GetZoomMagnify(self):
        return self.magnify
    def GetRotateClockwise(self):
        return self.clockwise


    def SetZoomDif(self,zoomdif):
        """ Set zoom mgnify/reduce amount per step

        :param int zoomdif: amount of change size
        """
        self.zomdif=zomdif
    def GetZoomDif(self):
        return self.zomdif

    def SetTimeSlice(self,timeslice):
        """ Set time slice

        :param int timeslice: in unit of ms
        """
        self.timeslice=timeslice
    def SetInterval(self,interval):
        """ Set interval

        :param int interval: in unit of time slice
        """
        self.scintvl.SetValue(interval)
        self.interval=interval

    def SetRepeatTimes(self,repeattimes):
        """ Set repeat times

        :param int repeattimes: repeat times
        """
        self.scerep.SetValue(repeattimes)
        self.repeattimes=repeattimes

    def SetCurrentMolecule(self,curmol):
        """ Set current molecule

        :param int curmol: molecule number
        """
        self.tccur.SetValue(curmol)
        self.OnCurren(1)

    def SetSaveImage(self,on):
        """ Set save image flag on/off

        :param bool on: True for on, False for off
        """
        self.saveimage=on
        self.btnsav.SetValue(on)
        if self.saveimage: self.btnsav.SetBackgroundColour('red')
        else: self.btnsav.SetBackgroundColour('black')

    def SetSaveImageFormat(self,format):
        """ Set image format

        :param str format: image format. 'png','bmp','jpeg','pcx','pnm', or 'xpm'
        """
        self.imageformat=format
    def SetImagePath(self,path):
        """ Set path for image file. Default:FUPATH/Images

        :param str path: directory name
        """
        self.imagepath=path
    def SetImageNumber(self,number):
        """ Set initial number to add image file name, image file name will be
        molname-xxx.jpeg(xxx:sequence number of created image file)

        :param int number: initial number
        """
        self.imagenumber=number

    def SetSaveImageEvery(self,every):
        """ Set every steps to save image

        :param int every: image will be saved evey steps
        """
        self.saveevery=every
    def SetSuppressMessage(self,on):
        """ Set suppress message flag

        :param bool on: True for suppress, False for not
        """
        self.suppressmess=on
    def SetSuperimpose(self,on):
        """ Set superimpose flag

        :param bool on: True for on, False for off
        """
        self.superimpose=on

    def PrintMotionParams(self):
        """ Print Motion params on fumodel console
        """
        mess='rotangle='+str(self.rotangle)+', transdif='+str(self.transdif)
        mess=mess+', zoomdif='+str(self.zoomdif)
        self.model.ConsoleMessage(mess)
    def PrintRotateParams(self):
        """ Print rotation params on fumodel console
        """
        clockwise='clockwise'
        if not self.clockwise: clockwise='antclockwise'
        mess='Rotate: '+clockwise+', rotangle='+str(self.rotangle)
        return mess

    def PrintTranslateParams(self):
        """ Print translation params on fumodel console
        """
        right='right'
        if not self.right: right='left'
        mess='Translate: '+right+', trandif='+str(self.trandif)
        return mess

    def PrintZoomParams(self):
        """ Print zoom params on fumodel console
        """
        magnify='magnify'
        if not self.magnify: magnify='reduce'
        mess='Zoom: '+magnify+', zoomdif='+str(self.zoomdif)
        return mess

    def SetDrawParams(self,all):
        """ Copy draw params of current molecule to all or following

        :param bool all: True for all, False for following
        """
        curmol,mol=self.model.molctrl.GetCurrentMol()
        nmol=self.model.molctrl.GetNumberOfMols()
        atmprms=[]
        for atom in mol.atm:
           atmprms.append(atom.GetDrwParamDic())
        drwobjs=self.mdlwin.draw.GetDrawObjs()
        viewitems=self.mdlwin.draw.GetViewItems()
        #
        mol.SetDrawObjs(drwobjs)
        mol.SetViewItems(viewitems)
        natm=len(mol.atm)
        if all: ist=0
        else: ist=curmol
        #
        for imol in range(ist,nmol):
            if imol == curmol: continue
            mol=self.model.molctrl.GetMol(imol)
            if len(mol.atm) != natm: continue
            mol.SetDrawObjs(drwobjs)
            mol.SetViewItems(viewitems)
            for i in range(len(mol.atm)):
                mol.atm[i].SetDrwParams(atmprms[i])

    def ReadScenarioFile(self):
        """ Read scenario file

        """
        wcard='scenario script(*.py)|*.py;all(*.*)|*.*'
        scnfiles=lib.GetFileNames(self.mdlwin,wcard,'r',False,'')
        if len(scnfiles) <= 0: return
        # drwfile(str): file name
        for scnfile in scnfiles:
            if not os.path.exists(scnfile):
                mess='Scenario file, '+scnfile+' is not found.'
                lib.MessageBoxOK(mess,'ReadScenarioFile')
                continue
            head,tail=os.path.split(scnfile)
            base,ext=os.path.splitext(tail)
            if base in self.scnnames:
                mess='Neglected. since there is the same name script.'
                lib.MessageBoxOK(mess,'ReadScenarioFile')
                continue
            self.scnfiledic[base]=scnfile
            self.scnnames.append(base)

        self.cmbscn.SetItems(self.scnnames)
        self.cmbscn.SetStringSelection('None')

    def ResetMotion(self,fit,rot):
        """ Reset Motion(rotate,translate,zoom) flags

        :param bool fit: True for forFitToScreen, False do not
        :param bool rot: True for ResetRotation, False do not
        """
        self.rotate=False
        self.translate=False
        self.zoom=False
        self.menubar.Check(self.id2,False)
        self.menubar.Check(self.id3,False)
        self.menubar.Check(self.id4,False)
        self.menubar.Check(self.id5,False)
        self.menubar.Check(self.id6,False)
        self.menubar.Check(self.id7,False)
        #
        if fit: self.model.FitToScreen(True,False)
        if rot: self.model.ResetRotate()

        self.OnPause(1)

    def EnableWidgets(self,on):
        """ Enable/Disable widgets

        :param bool on: True for eable, False for disable
        """
        if on:
            self.btnsav.Enable(); self.scerep.Enable(); self.slpos.Enable()
            self.btnplay.Enable(); self.btnpause.Enable(); self.scintvl.Enable()
            self.btnprev.Enable(); self.btnnext.Enable(); self.tccur.Enable()
        else:
            self.btnsav.Disable(); self.scerep.Disable(); self.slpos.Disable()
            self.btnplay.Disable(); self.btnpause.Disable(); self.scintvl.Disable()
            self.btnprev.Disable(); self.btnnext.Disable(); self.tccur.Disable()

    def OnMovable(self,event):
        """ need codes """
        self.movable= not self.movable
        print(('movable',self.movable))

    def RemoveMdlWinMess(self):
        try: self.model.RemoveDrawMessage('MolName')
        except: pass

    def OnClose(self,event):
        """ Event handler to close the panel

        """
        self.Close()

    def Close(self):
        try: self.model.SuppressMessage(self.savesuppressmess)
        except: pass

        try: self.model.RemoveDrawMessage('MolName')
        except: pass

        try: self.model.winctrl.Close(self.winlabel)
        except: pass

        try: self.savimgwin.Destroy()
        except: pass

        try: self.timer.Destroy()
        except: pass

        try: self.Destroy()
        except: pass

    def HelpDocument(self):
        self.model.helpctrl.Help(self.helpname)

    def Tutorial(self):
        self.model.helpctrl.Tutorial(self.helpname)

    def MenuItems(self):
        """ Menu and menuBar data

        """
        # Menu items
        menubar=wx.MenuBar()
        # Open menu
        submenu=wx.Menu()
        submenu.Append(-1,'Read scenario','Read scenario file')
        submenu.AppendSeparator()
        submenu.Append(-1,'Restore draw parameters','Restore')
        submenu.Append(-1,'Save draw parameters','Save')
        #submenu.AppendSeparator()
        # Save images
        #submenu.Append(-1,'Save images','Save')
        # Quit
        submenu.AppendSeparator()
        submenu.Append(-1,'Restore molecules','Restore molecular data')
        # Quit
        submenu.AppendSeparator()
        submenu.Append(-1,'Quit','Close the window')
        menubar.Append(submenu,'File')
        # SetView
        submenu=wx.Menu()
        submenu.Append(-1,"Current view to all","Set curren view to all molecules")
        submenu.Append(-1,"Current view to end","Set curren view to the end")
        submenu.AppendSeparator()
        id0=wx.NewId()
        submenu.Append(id0,"Superimpose view",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        id1=wx.NewId()
        submenu.Append(id1,"Display molname",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        menubar.Append(submenu,'SetView')
        # Motion
        submenu=wx.Menu()
        # Rotate
        subsubmenu=wx.Menu()
        self.id2=wx.NewId()
        subsubmenu.Append(self.id2,"Clockwise",kind=wx.ITEM_CHECK)
        self.id3=wx.NewId()
        subsubmenu.Append(self.id3,"Anticlockwise",kind=wx.ITEM_CHECK)
        #submenu.AppendMenu(-1,'Rotate',subsubmenu)
        lib.AppendMenuWx23(submenu,-1,'Rotate',subsubmenu)
         # Tranelate
        subsubmenu=wx.Menu()
        self.id4=wx.NewId()
        subsubmenu.Append(self.id4,"Right",kind=wx.ITEM_CHECK)
        self.id5=wx.NewId()
        subsubmenu.Append(self.id5,"Left",kind=wx.ITEM_CHECK)
        #submenu.AppendMenu(-1,'Translate',subsubmenu)
        lib.AppendMenuWx23(submenu,-1,'Translate',subsubmenu)

        # Zoom
        subsubmenu=wx.Menu()
        self.id6=wx.NewId()
        subsubmenu.Append(self.id6,"Magnify",kind=wx.ITEM_CHECK)
        self.id7=wx.NewId()
        subsubmenu.Append(self.id7,"Reduce",kind=wx.ITEM_CHECK)
        #submenu.AppendMenu(-1,'Zoom',subsubmenu)
        lib.AppendMenuWx23(submenu,-1,'Zoom',subsubmenu)
        # Reset
        submenu.AppendSeparator()
        submenu.Append(-1,'Reset','Reset orientation,position and zoom')
        #
        menubar.Append(submenu,'Motion')
        # Image setting
        submenu=wx.Menu()
        submenu.Append(-1,"Open panel","Open Image setting panel")
        menubar.Append(submenu,'Image')
        # Help setting
        submenu=wx.Menu()
        submenu.Append(-1,"Document","Open help document")
        submenu.Append(-1,"Tutorial","Open tutorial panel")
        menubar.Append(submenu,'Help')
        # check/uncheck menuitem
        menubar.Check(id0,False)
        menubar.Check(id1,True)
        # Rotate
        menubar.Check(self.id2,False)
        menubar.Check(self.id3,False)
        # Translate
        menubar.Check(self.id4,False)
        menubar.Check(self.id5,False)
        # Zoom
        menubar.Check(self.id6,False)
        menubar.Check(self.id7,False)
        #
        return menubar

    def OnMenu(self,event):
        """ Menu event handler

        """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        # File menu items
        if item == 'Read scenario':
            self.ReadScenarioFile()

        elif item == 'Restore molecules':
            self.RestoreMolecules()

        elif item == 'Restore draw parameters':
            self.model.RestoreDrawItems()

        elif item == 'Save draw parameters':
            self.model.DumpDrawItems()

        elif item == "Quit":
            self.OnClose(1)
        # SetView
        elif item == "Current view to all":
            self.SetDrawParams(True)

        elif item == "Current view to end":
            self.SetDrawParams(False)

        elif item == "Superimpose view":
            self.superimpose=self.menubar.IsChecked(menuid)
            self.SuperimposedMol(self.superimpose)

        elif item == "Display molname":
            self.drawmolname=self.menubar.IsChecked(menuid)
        # Acrtion
        # Rotate
        elif item == "Clockwise":
            self.rotate=self.menubar.IsChecked(menuid)
            self.clockwise=True
            if self.rotate:
                self.menubar.Check(self.id3,False)
                self.PrintRotateParams()

        elif item == "Anticlockwise":
            self.rotate=self.menubar.IsChecked(menuid)
            self.clockwise=False
            if self.rotate:
                self.menubar.Check(self.id2,False)
                self.PrintRotateParams()
        # Translate
        elif item == "Right":
            self.translate=self.menubar.IsChecked(menuid)
            self.right=True
            if self.translate:
                self.menubar.Check(self.id5,False)
                self.tranvec=[]
                self.PrintTranslateParams()

        elif item == "Left":
            self.translate=self.menubar.IsChecked(menuid)
            self.right=False
            if self.translate:
                self.menubar.Check(self.id4,False)
                self.tranvec=[]
                self.PrintTranslateParams()

        # Zoom
        elif item == "Magnify":
            self.zoom=self.menubar.IsChecked(menuid)
            self.magnify=True
            if self.zoom:
                self.menubar.Check(self.id7,False)
                self.PrintZoomParams()

        elif item == "Reduce":
            self.zoom=self.menubar.IsChecked(menuid)
            self.magnify=False
            if self.zoom:
                self.menubar.Check(self.id6,False)
                self.PrintZoomParams()

        elif item == "Reset":
            self.ResetMotion(True,True)

        elif item == "Open panel":
            self.OpenImageSettingPanel()

        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()

class FrameData_Frm(wx.Frame):
    def __init__(self,parent,id,winpos,winlabel):
        self.title='Frame data manipulation'
        winsize=lib.WinSize([380,380],False)
        #if lib.GetPlatform() == "WINDOWS": winsize=[380,380]
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER) #|wx.FRAME_FLOAT_ON_PARENT)
        #
        self.mdlwin=parent
        #xxself.ctrlflag=model.ctrlflag
        self.model=self.mdlwin.model
        self.setctrl=self.model.setctrl
        self.winctrl=self.model.winctrl
        self.winlabel=winlabel

        self.winsize=winsize
        self.framedir=self.setctrl.GetDir('Frames')
        self.platform=lib.GetPlatform() #self.setctrl.GetParam('platform')
        # Create StatusBar
        self.statusbar=self.CreateStatusBar()
        self.CreatePanel()

        self.monolst=[]; self.statlst=[]
        self.OnReset(1)
        #self.existlst=self.GetExistingMonomers()
        #self.SetToExistListCtrl()
        #
        self.Show()
        #
        #self.Bind(wx.EVT_MENU,self.OnMenu)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=[w,h]) #,size=(xsize,yupper)) #ysize))
        self.panel.SetBackgroundColour("light gray")
        yloc0=50
        yloc=10; xloc=20
        mess='Existing monomers'
        wx.StaticText(self.panel,-1,mess,pos=(10,yloc),size=(120,20))
        yloc += 25
        self.lstctrl=wx.ListCtrl(self.panel,-1,pos=(15,yloc),size=(55,h-45),style=wx.LC_REPORT|wx.LC_SORT_ASCENDING) #|wx.LC_EDIT_LABELS) #,
        #                         style=wx.LC_SINGLE_SEL) #LC_REPORT) #|wx.LC_EDIT_LABELS) # LC_SINGLE_SEL
        self.lstctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelected)
        #self.lstctrl.SetToolTipString('Select a line and push keyboard key ("space" key cancels)')
        lib.SetTipString(self.lstctrl,'Select a line and push keyboard key ("space" key cancels)')
        #self.lstctrl.Bind(wx.EVT_LIST_KEY_DOWN,self.OnKeyDown)
        #self.lstctrl.InsertColumn(0,'#',width=20,format=wx.LIST_FORMAT_RIGHT)
        self.lstctrl.InsertColumn(0,'name',width=50,format=wx.LIST_FORMAT_LEFT)
        yloc1=60; xloc1=80
        btnview=wx.Button(self.panel,-1,"View",pos=(xloc1,yloc1),size=(55,20))
        #btnview.SetToolTipString('View or edit the file with editor')
        lib.SetTipString(btnview,'View or edit the file with editor')
        btnview.Bind(wx.EVT_BUTTON,self.OnView)
        yloc1 += 30
        btndel=wx.Button(self.panel,-1,"Del",pos=(xloc1,yloc1),size=(55,20))
        #btndel.SetToolTipString('Delete selected data')
        lib.SetTipString(btndel,'Delete selected data')
        btndel.Bind(wx.EVT_BUTTON,self.OnDel)
        yloc1 += 30
        btndelall=wx.Button(self.panel,-1,"Del all",pos=(xloc1,yloc1),size=(55,20))
        #btndel.SetToolTipString('Delete all data')
        lib.SetTipString(btndelall,'Delete all data')
        btndelall.Bind(wx.EVT_BUTTON,self.OnDelAll)
        yloc1 += 30
        btnreset=wx.Button(self.panel,-1,"Reset",pos=(xloc1,yloc1),size=(55,20))
        #btnreset.SetToolTipString('Reset panel')
        lib.SetTipString(btnreset,'Reset panel')
        btnreset.Bind(wx.EVT_BUTTON,self.OnReset)
        #
        xloc1 += 65; xloc0=xloc1
        wx.StaticLine(self.panel,pos=(xloc1,0),size=(4,h),style=wx.LI_VERTICAL)
        #
        yloc2=10; xloc1 += 15 #20
        mess='Input monomer names, like "FK5,'
        mess1='..." and "ENTER"'
        wx.StaticText(self.panel,-1,mess,pos=(xloc1,yloc2),size=(200,18))
        wx.StaticText(self.panel,-1,mess1,pos=(xloc1,yloc2+20),size=(200,18))
        yloc2 += 40
        self.tclinp=wx.TextCtrl(self.panel,-1,'',pos=(xloc1,yloc2),size=(210,25),
                                style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        
        if not lib.IsWxVersion2(pltfrm='MACOSX'):
            self.tclinp.Bind(wx.EVT_KEY_UP,self.OnKeyUp)
        else: self.tclinp.Bind(wx.EVT_TEXT_ENTER,self.OnMonomers)
        #self.tclinp.SetToolTipString('The input monomers will be set to "Monomer list" below')
        lib.SetTipString(self.tclinp,'The input monomers will be set to "Monomer list" below')
        yloc2 += 25; yloc20=yloc2
        mess='Pick up monomers in'
        mess1='PDB file(input file name)'
        wx.StaticText(self.panel,-1,mess,pos=(xloc1,yloc2),size=(135,18))
        wx.StaticText(self.panel,-1,mess1,pos=(xloc1,yloc2+20),size=(135,18))
        self.btnbrws=wx.Button(self.panel,wx.ID_ANY,"Browse",pos=(xloc1+150,yloc2+5),size=(60,20))
        self.btnbrws.Bind(wx.EVT_BUTTON,self.OnBrowse)
        yloc2 += 40
        self.tclname=wx.TextCtrl(self.panel,-1,'',pos=(xloc1,yloc2),size=(210,30),
                                 style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        #self.tclname.SetToolTipString('Non-aa residues in the data will be set to "Monomer list" below')
        lib.SetTipString(self.tclname,'Non-aa residues in the data will be set to "Monomer list" below')
        if not lib.IsWxVersion2(pltfrm='MACOSX'):
            self.tclname.Bind(wx.EVT_KEY_UP,self.OnKeyUp)
        else: self.tclname.Bind(wx.EVT_TEXT_ENTER,self.OnPDBFile)
        yloc2 += 40 #25
        wx.StaticLine(self.panel,pos=(xloc0+20,yloc2),size=(w-xloc0-40,2),style=wx.LI_HORIZONTAL)
        yloc2 += 5; yloc20=yloc2
        height=h-yloc2-60
        mess='Monomer list to be downloaded'
        wx.StaticText(self.panel,-1,mess,pos=(xloc1,yloc2),size=(200,20))
        yloc2 += 20
        self.lstinp=wx.ListCtrl(self.panel,-1,pos=(xloc1+10,yloc2),size=(100,height),style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.LC_SORT_ASCENDING) #,
        self.lstinp.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelected)
        #self.lstinp.SetToolTipString('Select a monomer to delete and push "Del" button')
        lib.SetTipString(self.lstinp,'Select a monomer to delete and push "Del" button')
        self.lstinp.InsertColumn(0,'name',width=50,format=wx.LIST_FORMAT_LEFT)
        self.lstinp.InsertColumn(1,'stat',width=50,format=wx.LIST_FORMAT_LEFT)
        yloc3=yloc20+30; xloc2=xloc1+120
        btndel=wx.Button(self.panel,-1,"Del",pos=(xloc2,yloc20+50),size=(55,20))
        #btndel.SetToolTipString('Delete selected data')
        lib.SetTipString(btndel,'Delete selected data')
        btndel.Bind(wx.EVT_BUTTON,self.OnDelToBe)
        #yloc3 += 30
        btndelall=wx.Button(self.panel,-1,"Del all",pos=(xloc2,yloc20+80),size=(55,20))
        #btndelall.SetToolTipString('Remove all data')
        lib.SetTipString(btndelall,'Remove all data')
        yloc2 += 110
        yloc2=h-30
        btndel.Bind(wx.EVT_BUTTON,self.OnDelAllToBe)
        btndownload=wx.Button(self.panel,-1,"Download",pos=(xloc1+20,yloc2),size=(80,20))
        #btndownload.SetToolTipString('Download monomer data from "ftp://ftp.wwpdb.org/"')
        lib.SetTipString(btndownload,'Download monomer data from "ftp://ftp.wwpdb.org/"')
        btndownload.Bind(wx.EVT_BUTTON,self.OnDownload)
        btncan=wx.Button(self.panel,-1,"Cancel",pos=(xloc1+120,yloc2),size=(60,20))
        #btncan.SetToolTipString('Close the window')
        lib.SetTipString(btncan,'Close the window')
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)

    def OnKeyUp(self,event):
        """ EVT_TEXT_ENTER ha no effect on MacOSX 2019.Apl.10
            This handler is an alternate
        """
        if event.GetKeyCode()  == wx.WXK_RETURN:
            obj=event.GetEventObject()
            text=obj.GetValue()
            if len(text.strip()) <= 0: return
            if obj == self.tclinp:
                obj.SetValue('')
                self.SetMonomers(text)
            elif obj == self.tclname:
                obj.SetValue('')
                self.SetPDBFile(text)
        
    def SetMonomers(self,text):
        if len(text) <= 0: return
        itemlst=text.split(','); monolst=[]
        for i in range(len(itemlst)):
            mono=itemlst[i].strip()
            if len(mono) > 0: ans=self.IsDuplicate(mono)
            if not ans: monolst.append(mono)
        self.monolst=self.monolst+monolst
        statlst=len(monolst)*['']
        self.statlst=self.statlst+statlst
        #self.monolst.sort()
        self.SetToInputListCtrl()
    
    def OnMonomers(self,event):
        text=self.tclinp.GetValue()
        self.tclinp.SetValue('')
        #self.tclinp.SetValue('')
        self.SetMonomers(text)
        
    def OnPDBFile(self,event):
        pdbfile=self.tclname.GetValue()
        self.SetPDBFile(pdbfile)
        
    def SetPDBFile(self,pdbfile):
        pdbfile=pdbfile.strip()
        if len(pdbfile) <= 0: return
        pdbfile=os.path.expanduser(pdbfile)
        if not os.path.exists(pdbfile):
            self.Message('PDB file "'+pdbfile+'" does not exist.'); return
        wx.BeginBusyCursor()
        self.Message('Reading PDB file.')
        reslst=self.FindNonAAResidues(pdbfile,True,True)
        wx.EndBusyCursor()
        self.Message('')
        #
        monolst=[]
        for mono in reslst:
            if len(mono) <= 0 or mono == 3*' ': continue
            ans=self.IsDuplicate(mono)
            if not ans: monolst.append(mono)
        # remove 'UNK': unknown residue
        statlst=len(monolst)*['']
        self.monolst=self.monolst+monolst
        self.statlst=self.statlst+statlst
        self.SetToInputListCtrl()

    def IsDuplicate(self,mono):
        ans=True
        try: idx=self.monolst.index(mono)
        except: ans=False
        return ans

    def FindNonAAResidues(self,pdbfile,nowat,nounk):
        resdic={}
        pdbatm,pdbcon,fuoptn=rwfile.ReadPDBAtom(pdbfile)
        for i in range(len(pdbatm)):
            res=pdbatm[i][4]
            if res in const.AmiRes3: continue
            if nowat and (res == 'WAT' or res == 'HOH'): continue
            if nounk and (res == 'UNK'): continue
            resdic[res]=True
        reslst=list(resdic.keys())
        reslst.sort()
        return reslst

    def OnDownload(self,event):
        downlst=[]
        existdic={}
        for mono in self.existlst: existdic[mono]=True #dict(zip(self.existlst,self.statlst))
        for i in range(len(self.monolst)):
            if self.statlst[i] != '': continue
            mono=self.monolst[i]
            if  mono in existdic:
                mess='Frame data "'+mono+'" already exists. Would you like to replace it.'
                dlg=lib.MessageBoxYesNo(mess,"")
                if not dlg:
                    self.statlst[i]='skip'; continue
            downlst.append(mono)
        ftpserver=self.setctrl.GetParam('pdb-monomer-ftp-server')
        mess,saved,failed=lib.GetMonomersFromPDBFTPServer(ftpserver,downlst,self.framedir)
        if len(mess) > 0: self.Message('OnDownload message: '+mess)
        else:
            mess='succeeded='+str(len(saved))+', failed='+str(len(failed))
            self.Message('Downloaded monomer data: '+mess)
        savedic={}; faildic={}
        for mono in saved: savedic[mono]=True
        for mono in failed: faildic[mono]=True
        for i in range(len(self.monolst)):
            mono=self.monolst[i]
            if mono in savedic: self.statlst[i]='OK'
            if mono in faildic: self.statlst[i]='NG'
        self.SetToInputListCtrl()
        # reset exist monomer panel
        self.OnReset(1)

    def OnReset(self,event):
        self.existlst=self.GetExistingMonomers()
        self.SetToExistListCtrl()
        # update setting
        self.setctrl.MakeFrameDataDic()

    def OnCancel(self,event):
        self.OnClose(1)

    def OnBrowse(self,event):
        filename=lib.GetFileName(self,"PDB file(*.pdb)|*.pdb",'r',False,'')
        if len(filename) > 0:
            filename=lib.CompressUserFileName(filename)
            self.tclname.SetValue(filename)
            self.tclname.SetInsertionPointEnd()
            self.OnPDBFile(1)

    def OnDelToBe(self,event):
        it=self.lstinp.GetFirstSelected()
        item=self.lstinp.GetItem(it,0)
        mono=item.GetText(); mono=mono.strip()
        if len(mono) <= 0:
            self.Message('Nothing selected. Click a monomer to select.'); return
        try:
            idx=self.monolst.index(mono)
            del self.monolst[idx]; del self.statlst[idx]
        except: pass
        self.SetToInputListCtrl()

    def OnDelAllToBe(self,event):
        self.lstinp.DeleteAllItems()
        self.monolst=[]; self.statlst=[]

    def SetToExistListCtrl(self):
        self.lstctrl.DeleteAllItems()
        for i in range(len(self.existlst)):
            mono=self.existlst[i]
            if lib.IsWxVersion2():
                idx=self.lstctrl.InsertStringItem(1,str(i+1))
                self.lstctrl.SetStringItem(idx,0,mono)
            else:
                idx=self.lstctrl.InsertItem(1,str(i+1))
                self.lstctrl.SetItem(idx,0,mono)

    def SetToInputListCtrl(self):
        #self.lstinp.DeleteColumn(0)
        #self.lstinp.DeleteColumn(1)
        self.lstinp.DeleteAllItems()
        for i in range(len(self.monolst)):
            mono=self.monolst[i]; stat=self.statlst[i]
            if lib.IsWxVersion2():
                idx=self.lstinp.InsertStringItem(i,str(i+1))
                self.lstinp.SetStringItem(idx,0,mono)
                self.lstinp.SetStringItem(idx,1,stat) # 'NG'
            else:
                idx=self.lstinp.InsertItem(i,str(i+1))
                self.lstinp.SetItem(idx,0,mono)
                self.lstinp.SetItem(idx,1,stat) # 'NG'

    def GetExistingMonomers(self):
        existlst=[]
        files=self.setctrl.GetFrameDataList() #GetFilesList('Frames')
        for fil in files:
            head,tail=os.path.split(fil)
            base,ext=os.path.splitext(tail)
            existlst.append(base)
        existlst.sort()
        return existlst

    def MakeFileName(self,mononam):
        filename=mononam+'.frm'
        filename=os.path.join(self.framedir,filename)
        if not os.path.exists(filename):
            self.Message('frame file "'+filename+'" is not found.'); return ''
        return filename

    def OnView(self,event):
        it=self.lstctrl.GetFirstSelected()
        item=self.lstctrl.GetItem(it,0)
        mono=item.GetText()
        if len(mono) <= 0:
            self.Message('Nothing selected. Click a monomer to select.'); return
        filename=self.MakeFileName(mono)
        if filename != '': lib.Editor(filename) #1(self.platform,filename)

    def OnSelected(self,event):
        pass

    def OnDel(self,event):
        it=self.lstctrl.GetFirstSelected()
        item=self.lstctrl.GetItem(it,0)
        mono=item.GetText()
        if len(mono) <= 0:
            self.Message('Nothing selected. Click a monomer to select.'); return
        filename=self.MakeFileName(mono)
        if filename != '':
            os.remove(filename)
            self.Message('Deleted "'+filename+'".')
        self.OnReset(1)

    def OnDelAll(self,event):
        mess='Are you sure to delete all frame data in "Frames" directory?'
        dlg=lib.MessageBoxYesNo(mess,"")
        if not dlg: return
        #
        lib.DeleteFilesInDirectory(self.framedir,'all')
        self.Message('All frame data in "Frames" were deleted.')
        self.OnReset(1)

    def Message(self,mess):
        self.SetStatusText(mess,0)

    def OnResize(self,event):
        self.panel.Destroy()
        self.SetMinSize(self.winsize)
        self.SetMaxSize([self.winsize[0],2000])
        self.CreatePanel()
        self.OnReset(1)
        self.SetToInputListCtrl()

    def OnClose(self,event):
        try: self.winctrl.Close(self.winlabel)
        except: self.Destory()

class PDBData_Frm(wx.Frame):
    def __init__(self,parent,id,winpos,winlabel):
        self.title='PDB data manipulation'
        winsize=lib.WinSize([380,330],False)
        #if lib.GetPlatform() == "WINDOWS": winsize=[380,330]
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER) #|wx.FRAME_FLOAT_ON_PARENT)
        #
        self.mdlwin=parent
        #xxself.ctrlflag=model.ctrlflag
        self.model=self.mdlwin.model
        self.setctrl=self.model.setctrl
        self.winctrl=self.model.winctrl
        self.winlabel=winlabel

        self.winsize=winsize
        self.pdbsdir=self.setctrl.GetDir('PDBs')
        self.platform=lib.GetPlatform() #self.setctrl.GetParam('platform')
        # Create StatusBar
        self.statusbar=self.CreateStatusBar()
        self.CreatePanel()

        self.pdblst=[]; self.statlst=[]
        self.OnReset(1)
        #self.existlst=self.GetExistingPDBs()
        #self.SetToExistListCtrl()
        #
        self.Show()
        #
        #self.Bind(wx.EVT_MENU,self.OnMenu)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=[w,h]) #,size=(xsize,yupper)) #ysize))
        self.panel.SetBackgroundColour("light gray")
        yloc0=50
        yloc=10; xloc=20
        mess='Existing PDB IDs'
        wx.StaticText(self.panel,-1,mess,pos=(10,yloc),size=(120,20))
        yloc += 25
        self.lstctrl=wx.ListCtrl(self.panel,-1,pos=(15,yloc),size=(55,h-45),style=wx.LC_REPORT|wx.LC_SORT_ASCENDING) #|wx.LC_EDIT_LABELS) #,
        #                         style=wx.LC_SINGLE_SEL) #LC_REPORT) #|wx.LC_EDIT_LABELS) # LC_SINGLE_SEL
        self.lstctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelected)
        #self.lstctrl.SetToolTipString('Select a name and push keyboard key ("space" key cancels)')
        lib.SetTipString(self.lstctrl,'Select a name and push keyboard key ("space" key cancels)')
        #self.lstctrl.Bind(wx.EVT_LIST_KEY_DOWN,self.OnKeyDown)
        #self.lstctrl.InsertColumn(0,'#',width=20,format=wx.LIST_FORMAT_RIGHT)
        self.lstctrl.InsertColumn(0,'name',width=50,format=wx.LIST_FORMAT_LEFT)
        yloc1=60; xloc1=80
        btnview=wx.Button(self.panel,-1,"View",pos=(xloc1,yloc1),size=(45,20))
        #btnview.SetToolTipString('View or edit the file with editor')
        lib.SetTipString(btnview,'View or edit the file with editor')
        btnview.Bind(wx.EVT_BUTTON,self.OnView)
        yloc1 += 30
        btndel=wx.Button(self.panel,-1,"Del",pos=(xloc1,yloc1),size=(55,20))
        #btndel.SetToolTipString('Delete selected data')
        lib.SetTipString(btndel,'Delete selected data')
        btndel.Bind(wx.EVT_BUTTON,self.OnDel)
        yloc1 += 30
        btndelall=wx.Button(self.panel,-1,"Del all",pos=(xloc1,yloc1),size=(55,20))
        #btndel.SetToolTipString('Delete all data')
        lib.SetTipString(btndelall,'Delete all data')
        btndelall.Bind(wx.EVT_BUTTON,self.OnDelAll)
        yloc1 += 30
        btnreset=wx.Button(self.panel,-1,"Reset",pos=(xloc1,yloc1),size=(55,20))
        #btndel.SetToolTipString('Reset panel')
        lib.SetTipString(btnreset,'Reset panel')
        btnreset.Bind(wx.EVT_BUTTON,self.OnReset)
        #
        xloc1 += 65; xloc0=xloc1
        wx.StaticLine(self.panel,pos=(xloc1,0),size=(4,h),style=wx.LI_VERTICAL)
        #
        yloc2=10; xloc1 += 15 #20
        mess='Input PDB IDs, like "163d,..."'
        mess1=' and "ENTER"'
        wx.StaticText(self.panel,-1,mess,pos=(xloc1,yloc2),size=(200,18))
        wx.StaticText(self.panel,-1,mess1,pos=(xloc1,yloc2+20),size=(200,18))
        yloc2 += 40
        self.tclinp=wx.TextCtrl(self.panel,-1,'',pos=(xloc1,yloc2),size=(210,25),
                                style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        self.tclinp.Bind(wx.EVT_TEXT_ENTER,self.OnPDBs)
        #self.tclinp.SetToolTipString('The input monomers will be set to "Monomer list" below')
        lib.SetTipString(self.tclinp,'The input monomers will be set to "Monomer list" below')
        yloc2 += 25; yloc20=yloc2
        wx.StaticLine(self.panel,pos=(xloc0+20,yloc2),size=(w-xloc0-40,2),style=wx.LI_HORIZONTAL)
        yloc2 += 5; yloc20=yloc2
        height=h-yloc2-60
        mess='PDB ID list to be downloaded'
        wx.StaticText(self.panel,-1,mess,pos=(xloc1,yloc2),size=(200,20))
        yloc2 += 20
        self.lstinp=wx.ListCtrl(self.panel,-1,pos=(xloc1+10,yloc2),size=(100,height),style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.LC_SORT_ASCENDING) #,
        self.lstinp.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelected)
        #self.lstinp.SetToolTipString('Select a PDB ID to delete and push "Del" button')
        lib.SetTipString(self.lstinp,'Select a PDB ID to delete and push "Del" button')
        self.lstinp.InsertColumn(0,'name',width=50,format=wx.LIST_FORMAT_LEFT)
        self.lstinp.InsertColumn(1,'stat',width=50,format=wx.LIST_FORMAT_LEFT)
        yloc3=yloc20+30; xloc2=xloc1+120
        btndel=wx.Button(self.panel,-1,"Del",pos=(xloc2,yloc20+50),size=(60,20))
        #btndel.SetToolTipString('Delete selected data')
        lib.SetTipString(btndel,'Delete selected data')
        btndel.Bind(wx.EVT_BUTTON,self.OnDelToBe)
        #yloc3 += 30
        btndel=wx.Button(self.panel,-1,"Del all",pos=(xloc2,yloc20+80),size=(60,20))
        #btndel.SetToolTipString('Remove all data')
        lib.SetTipString(btndel,'Remove all data')
        yloc2 += 110
        yloc2=h-30
        btndel.Bind(wx.EVT_BUTTON,self.OnDelAllToBe)
        btndownload=wx.Button(self.panel,-1,"Download",pos=(xloc1+20,yloc2),size=(75,20))
        #btndownload.SetToolTipString('Download PDB data from "ftp://ftp.pdbj.org/"')
        lib.SetTipString(btndownload,'Download PDB data from "ftp://ftp.pdbj.org/"')
        btndownload.Bind(wx.EVT_BUTTON,self.OnDownload)
        btncan=wx.Button(self.panel,-1,"Cancel",pos=(xloc1+120,yloc2),size=(60,20))
        #btncan.SetToolTipString('Close the window')
        lib.SetTipString(btncan,'Close the window')
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)

    def OnPDBs(self,event):
        text=self.tclinp.GetValue()
        self.tclinp.SetValue('')
        if len(text) <= 0: return
        itemlst=text.split(','); pdbidlst=[]
        for i in range(len(itemlst)):
            pdb=itemlst[i].strip()
            if len(pdb) > 0: ans=self.IsDuplicate(pdb)
            if not ans: pdbidlst.append(pdb)
        self.pdblst=self.pdblst+pdbidlst

        statlst=len(pdbidlst)*['']
        self.statlst=self.statlst+statlst
        #self.pdblst.sort()
        self.SetToInputListCtrl()

    def XXOnPDBFile(self,event):
        pdbfile=self.tclname.GetValue()
        pdbfile=pdbfile.strip()
        pdbfile=os.path.expanduser(pdbfile)
        if not os.path.exists(pdbfile):
            self.Message('PDB file "'+pdbfile+'" does not exist.'); return
        wx.BeginBusyCursor()
        self.Message('Reading PDB file.')
        reslst=self.FindNonAAResidues(pdbfile,True,True)
        wx.EndBusyCursor()
        self.Message('')
        #
        pdbidlst=[]
        for pdb in reslst:
            if len(pdb) <= 0 or pdb == 3*' ': continue
            ans=self.IsDuplicate(pdb)
            if not ans: pdbidlst.append(pdb)
        # remove 'UNK': unknown residue
        statlst=len(pdbidlst)*['']
        self.pdblst=self.pdblst+pdbidlst
        self.statlst=self.statlst+statlst
        self.SetToInputListCtrl()

    def IsDuplicate(self,pdb):
        ans=True
        try: idx=self.pdblst.index(pdb)
        except: ans=False
        return ans

    def FindNonAAResidues(self,pdbfile,nowat,nounk):
        resdic={}
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        for i in range(len(pdbatm)):
            res=pdbatm[i][4]
            if res in const.AmiRes3: continue
            if nowat and (res == 'WAT' or res == 'HOH'): continue
            if nounk and (res == 'UNK'): continue
            resdic[res]=True
        reslst=list(resdic.keys())
        reslst.sort()
        return reslst

    def OnDownload(self,event):
        downlst=[]
        existdic={}
        for pdb in self.existlst: existdic[pdb]=True #dict(zip(self.existlst,self.statlst))
        for i in range(len(self.pdblst)):
            if self.statlst[i] != '': continue
            pdb=self.pdblst[i]
            if  pdb in existdic:
                mess='PDB data "'+pdb+'" already exists. Would you like to replace it.'
                dlg=lib.MessageBoxYesNo(mess,"")
                if not dlg:
                    self.statlst[i]='skip'; continue
            downlst.append(pdb)
        ftpserver=self.setctrl.GetParam('pdb-model-ftp-server')
        mess,saved,failed=lib.GetPDBFilesFromPDBj(ftpserver,downlst,self.pdbsdir)
        if len(mess) > 0: self.Message('OnDownload message: '+mess)
        else:
            mess='succeeded='+str(len(saved))+', failed='+str(len(failed))
            self.Message('Downloaded pdb data: '+mess)
        savedic={}; faildic={}
        for pdb in saved:
            pdbid=self.PDBIDInFileName(pdb)
            savedic[pdbid]=True
        for pdb in failed:
            pdbid=self.PDBIDInFileName(pdb)
            faildic[pdbid]=True
        for i in range(len(self.pdblst)):
            pdb=self.pdblst[i]
            if pdb in savedic: self.statlst[i]='OK'
            if pdb in faildic: self.statlst[i]='NG'
        self.SetToInputListCtrl()

        self.UnzipFile(saved)
        # reset exist pdbmer panel
        self.OnReset(1)

    def PDBIDInFileName(self,pdbzipfilename):
        pdbid=''
        pdbid=pdbzipfilename[3:7]
        return pdbid

    def UnzipFile(self,saved):
        for zipfile in saved:
            zipfile=os.path.join(self.pdbsdir,zipfile)
            plane=zipfile.replace('.gz','',1)
            mess=lib.ZipFile(plane,zipfile,False)
            if mess[:7] == 'Created': os.remove(zipfile)

    def OnReset(self,event):
        self.existlst=self.GetExistingPDBs()
        self.SetToExistListCtrl()
        # update setting
        #???self.setctrl.MakeFrameDataDic()

    def OnCancel(self,event):
        self.OnClose(1)

    def OnDelToBe(self,event):
        it=self.lstinp.GetFirstSelected()
        item=self.lstinp.GetItem(it,0)
        pdb=item.GetText(); pdb=pdb.strip()
        if len(pdb) <= 0:
            self.Message('Nothing selected. Click a PDB ID to select.'); return
        try:
            idx=self.pdblst.index(pdb)
            del self.pdblst[idx]; del self.statlst[idx]
        except: pass
        self.SetToInputListCtrl()

    def OnDelAllToBe(self,event):
        self.lstinp.DeleteAllItems()
        self.pdblst=[]; self.statlst=[]

    def SetToExistListCtrl(self):
        self.lstctrl.DeleteAllItems()
        for i in range(len(self.existlst)):
            pdb=self.existlst[i]
            idx=self.lstctrl.InsertStringItem(1,str(i+1))
            self.lstctrl.SetStringItem(idx,0,pdb)

    def SetToInputListCtrl(self):
        #self.lstinp.DeleteColumn(0)
        #self.lstinp.DeleteColumn(1)
        self.lstinp.DeleteAllItems()
        for i in range(len(self.pdblst)):
            pdb=self.pdblst[i]; stat=self.statlst[i]
            idx=self.lstinp.InsertStringItem(i,str(i+1))
            self.lstinp.SetStringItem(idx,0,pdb)
            self.lstinp.SetStringItem(idx,1,stat) # 'NG'

    def GetExistingPDBs(self):
        existlst=[]
        files=lib.GetFilesInDirectory(self.pdbsdir,['.ent'])
        for fil in files:
            head,tail=os.path.split(fil)
            base,ext=os.path.splitext(tail)
            base=base[3:]
            existlst.append(base)
        existlst.sort()
        return existlst

    def MakeFileName(self,pdbnam):
        filename='pdb'+pdbnam+'.ent'
        filename=os.path.join(self.pdbsdir,filename)
        if not os.path.exists(filename):
            self.Message('PDB file "'+filename+'" is not found.'); return ''
        return filename

    def OnView(self,event):
        it=self.lstctrl.GetFirstSelected()
        item=self.lstctrl.GetItem(it,0)
        pdb=item.GetText()
        if len(pdb) <= 0:
            self.Message('Nothing selected. Click a PDB ID to select.'); return
        filename=self.MakeFileName(pdb)
        if filename != '': lib.Editor(filename) #1(self.platform,filename)

    def OnSelected(self,event):
        pass

    def OnDel(self,event):
        it=self.lstctrl.GetFirstSelected()
        item=self.lstctrl.GetItem(it,0)
        pdb=item.GetText()
        if len(pdb) <= 0:
            self.Message('Nothing selected. Click a PDB ID to select.'); return
        filename=self.MakeFileName(pdb)
        if filename != '':
            os.remove(filename)
            self.Message('Deleted "'+filename+'".')
        self.OnReset(1)

    def OnDelAll(self,event):
        mess='Are you sure to delete all frame data in "Frames" directory?'
        dlg=lib.MessageBoxYesNo(mess,"")
        if not dlg: return
        #
        lib.DeleteFilesInDirectory(self.pdbsdir,'all')
        self.Message('All frame data in "Frames" were deleted.')
        self.OnReset(1)

    def Message(self,mess):
        self.SetStatusText(mess,0)

    def OnResize(self,event):
        self.panel.Destroy()
        self.SetMinSize(self.winsize)
        self.SetMaxSize([self.winsize[0],2000])
        self.CreatePanel()
        self.OnReset(1)
        self.SetToInputListCtrl()

    def OnClose(self,event):
        try: self.winctrl.Close(self.winlabel)
        except: self.Destory()

class PlotAndSelectAtoms():
    def __init__(self,parent,id,model,title='',selectitem='atom',button=True,
                 onmolview=None,winpos=[0,20],winsize=[640,550],
                 resetmethod=None):
        """ Plot property using MatPlotLib and select item in molview
         by L-clicking a bar

        :param obj model: fumolde instance
        :param str title: window titile
        :param str selectitem: 'atom' or 'fragment'
        """

        self.parent=parent
        self.model=model
        self.winctrl=model.winctrl
        self.resetmethod=resetmethod
        self.title=title
        try: self.title=title+" ["+self.model.mol.name+"]"
        except: pass
        self.winpos=winpos; self.winsize=winsize
        if len(self.winpos) <= 0: self.winpos=lib.WinPos(self.parent)
        if len(self.winsize) <= 0: self.winsize=[640,550]
        self.onmolview=onmolview
        self.winlabel='PlotAndSelectAtoms'
        self.selectitem=selectitem
        self.button=button
        # icons
        self.selectbmp=self.model.setctrl.GetIconBmp('select')
        self.listbmp=self.model.setctrl.GetIconBmp('list')
        self.extractbmp=self.model.setctrl.GetIconBmp('extract')

        self.Initialize()
        self.CreateMPLPanel()
        #

    def OnNotify(self,event):
        #if event.jobid != self.winlabel: return
        try: item=event.message
        except: return
        if item == 'SwitchMol' or item == 'ReadFiles':
            self.model.ConsoleMessage('Reset mol object in "TreeSelector"')
            self.mpl.Reset()

    def OnReset(self,event):
        self.mpl.Reset()
        #lib.MessageBoxOK('Restored molecule object','')
        self.model.Message2('Restored molecule object')

    def CreateMPLPanel(self):
        wbtn=25; hbtn=25; [w,h]=self.winsize
        self.mpl=MatPlotLib_Frm(self.parent,-1,self.model,self.winpos,
                                self.winsize,self.title)

        ExecProg_Frm.EVT_THREADNOTIFY(self.mpl,self.OnNotify)

        btnrset=Reset_Button(self.mpl,-1,self.OnReset)

        if self.resetmethod is not None:
            btnrset=Reset_Button(self.mpl.toolbar,-1,self.resetmethod)
            btnrset.SetLabel('Reset')
        #
        #self.btntyp=wx.ToggleButton(self.mpl.toolbar,wx.ID_ANY,"Line/Bar",pos=(250,2),size=(80,25))
        #self.btntyp.Bind(wx.EVT_TOGGLEBUTTON,self.OnGraphType)
        ###self.itemlst=['atom','fragment','residue','other']
        #self.extractmenu=['all','selected','show atoms','by value']
        yloc=4
        if self.button:
            self.btnsel=wx.BitmapButton(self.mpl.toolbar,-1,
                         bitmap=self.selectbmp,pos=(250,yloc),size=(wbtn,hbtn))
            #self.btnsel.SetToolTipString('Select atoms by value')
            lib.SetTipString(self.btnsel,'Select atoms by value')
            self.btnview=wx.BitmapButton(self.mpl.toolbar,-1,
                         bitmap=self.listbmp,pos=(295,yloc),size=(wbtn,hbtn))
            #self.btnview.SetToolTipString('List values')
            lib.SetTipString(self.btnview,'List values')
            self.btnext=wx.BitmapButton(self.mpl.toolbar,-1,
                         bitmap=self.extractbmp,pos=(340,yloc),size=(wbtn,hbtn))
            text='Select an item in the right window and push this button'
            #self.btnext.SetToolTipString(text)
            lib.SetTipString(self.btnext,text)
            self.cmbext=wx.ComboBox(self.mpl.toolbar,-1,"",pos=(370,yloc+2),
                                    size=(85,25))
            self.extstat=wx.StaticText(self.mpl.toolbar,-1,'',pos=(460,yloc+6),
                                       size=(w-470,20))
            #self.extstat.SetToolTipString('Number of data: extracted///total')
            lib.SetTipString(self.extstat,'Number of data: extracted///total')
            self.btnsel.Bind(wx.EVT_BUTTON,self.OnSelect)
            self.btnext.Bind(wx.EVT_BUTTON,self.OnExtract)
            self.cmbext.SetItems(self.extractmenu)
            self.cmbext.SetBackgroundColour(wx.NullColour)
            self.cmbext.SetStringSelection('all')
            self.btnview.Bind(wx.EVT_BUTTON,self.OnViewData)
            """
            if self.onmolview:
                self.btnview=wx.Button(self.mpl.toolbar,-1,"Select",
                                       pos=(350,2),size=(80,25))
                self.btnview.Bind(wx.EVT_BUTTON,self.OnMolView)
            """
        #btnset=wx.Button(self.mpl.toolbar,wx.ID_ANY,"Refresh",pos=(370,2),size=(100,25))
        #btnset.Bind(wx.EVT_BUTTON,self.OnResetData)
        self.mpl.canvas.mpl_connect('button_press_event', self.OnClick)
        self.mpl.SetTitle(self.title)
        #
        self.mpl.Show()

    def Initialize(self):
        self.graphtype="line"
        self.color='b'
        self.width=1/1.5
        self.marker='+'
        self.input=["","","",
                    ">0.0,<20.0 or >>0.0, <<2.0 for absolute value"]
        self.plttyp=1
        self.plottitle=self.title
        self.xlabel='x'; self.ylabel='y'
        self.xvalue=[]
        self.yvalue=[]
        self.xvarlst=[]
        self.extractmenu=['all','selected','show atoms','by value']
        self.extracted=[]
        self.extmethod=None

    def SetExtractMenu(self,extractmenu):
        self.extractmenu=extractmenu
        self.btnext.SetItems(self.extractmenu)

    def SetXVarData(self,xvarlst):
        self.xvarlst=xvarlst

    def AddExtractMenu(self,menulst,extmethod):
        self.extractmenu=self.extractmenu+menulst
        self.extmethod=extmethod
        self.cmbext.SetItems(self.extractmenu)
        self.cmbext.SetStringSelection('all')

    def SetInput(self,input):
        """

        :param lst input:
        """
        self.input=input

    def AddInput(self,input):
        self.input+self.input+input

    def SetColor(self,color):
        # color: 'b':blue,'g':green,'c':cyan,'m':magenta,'y':yellow
        #        'k':black,'w':white, 'r':red
        self.color=color
        self.mpl.SetColor(color)

    def SetEnableSelect(self,on):
        if on: self.btnsel.Enable()
        else: self.btnsel.Disable()

    def SetWidth(self,width):
        self.mpl.SetWidth(width)

    def SetGraphType(self,type):
        self.mpl.SetGraphType(type)

    def SetMarker(self,marker):
        self.mpl.SetMarker(marker)

    def NewPlot(self):
        self.mpl.NewPlot()

    def PlotXY(self,x,y):
        self.plttyp=1
        self.xvalue=x; self.yvalue=y
        self.extracted=list(range(len(self.xvalue)))
        self.mpl.PlotXY(x,y)
        self.ExtractStatus()

    def PlotXY2(self,x,y,label):
        self.plttyp=2; self.label2=label
        self.xvalue=x; self.yvalue=y
        self.extracted=list(range(len(self.xvalue)))
        self.mpl.PlotXY2(x,y,label)
        self.ExtractStatus()

    def PlotXY3(self,x,y,marker,label):
        self.plttyp=3; self.label3=label; self.marker3=marker
        self.xvalue=x; self.yvalue=y
        self.extracted=list(range(len(self.xvalue)))
        self.mpl.PlotXY3(x,y,marker,label)
        self.ExtractStatus()

    def PlotTitle(self,text):
        self.plottitle=text
        self.mpl.PlotTitle(text)

    def PlotXLabel(self,text):
        self.xlabel=text
        self.mpl.PlotXLabel(text)

    def PlotYLabel(self,text):
        self.ylabel=text
        self.mpl.PlotYLabel(text)

    def ExtractStatus(self):
        text=str(len(self.extracted))+'/'+str(len(self.xvalue))
        self.extstat.SetLabel(text)

    def XTicks(self,label):
        #self.mpl.XTicks(label)
        pass

    def Clear(self):
        self.mpl.Clear()

    def OnSelect(self,event):
        # select atoms with large b-factor
        larger,smaller,absval=lib.GetMinMaxValuesFromUser()
        if larger is None and smaller is None: return
        vallst=[]
        for i in self.extracted: vallst.append(self.yvalue[i])
        extlst=lib.ExtractDataByValue(vallst,larger,smaller,
                                              absval)
        sellst=[]
        if self.selectitem == 'atom':
            for i in range(len(extlst)):
                ii=self.extracted[i]; sellst.append(ii)
        elif self.selectitem == 'other':
            for i in range(len(extlst)):
                ii=self.extracted[i]
                for j in self.xvarlst[ii]: sellst.append(j)
                    #if not j in sellst: sellst.append(j)
        #
        #self.Select(sellst)
        self.model.SetSelectAll(False)
        self.model.SelectAtomByList(sellst,True)
        #
        mess='Threshold [vmin='+str(smaller)+', vmax='+str(larger)
        if absval: mess=mess+' in absolute'
        mess=mess+']. Number of Selected atoms'
        mess=mess+'='+str(len(sellst))
        if self.selectitem != 'atom':
            mess=mess+', Number of selected item='+str(len(extlst))
        self.model.Message2(mess)

    def OnMolView(self,event):
        self.onmolvew()

    def OnExtract(self,event):
        item=self.cmbext.GetValue()
        self.ExtractData(item)

    def ExtractData(self,item):
        if item == 'all': self.extracted=list(range(len(self.xvalue)))
        elif item == 'selected' or item == 'show atoms':
            if item == 'selected': nsel,sellst=self.model.ListSelectedAtom()
            elif item == 'show atoms': sellst=self.model.ListShowAtoms()
            if len(sellst) <= 0:
                mess='Please select or set show atom(s)'
                lib.MessageBoxOK(mess,'PlotAndSeelct(ExtractData)')
                return
            if self.selectitem == 'atom':
                self.extracted=[]
                for i in sellst: self.extracted.append(i)
            elif self.selectitem == 'fragment':
                pass # not coded yet
            elif self.selectitem == 'other':
                if len(self.xvarlst) <= 0:
                    mess='xvardat are not set. Unable to extract data.'
                    lib.MessageBoxOK(mess,'PlotAndSeelct(ExtractData)')
                    return
                self.extracted=[]
                for i in range(len(self.xvarlst)):
                    for j in self.xvarlst[i]:
                        if j in sellst and not i in self.extracted:
                            self.extracted.append(i)
        elif item == 'by value':
            tiptext=self.input[3]
            larger,smaller,absval=lib.GetMinMaxValuesFromUser(tiptext=tiptext)
            if larger is None and smaller is None: return
            self.extracted=lib.ExtractDataByValue(self.yvalue,larger,smaller,
                                                  absval)
        else:
            if self.extmethod is not None:
                self.extracted=self.extmethod(item,self.xvarlst)
        #
        if self.extracted is None:
            self.extracted=[]; return
        #
        x=[]; y=[]
        for i in range(len(self.extracted)):
            ii=self.extracted[i]
            x.append(self.xvalue[ii]); y.append(self.yvalue[ii])
        self.Clear(); self.NewPlot()
        if self.plttyp == 1: self.mpl.PlotXY(x,y)
        elif self.plytyp == 2: self.mpl.PlotXY2(x,y,self.label2)
        elif self.plttyp == 3: self.mpl.PlotXY3(x,y,self.marker3,self.label3)
        self.mpl.SetColor(self.color)
        if len(self.plottitle) > 0: self.PlotTitle(self.plottitle)
        if len(self.xlabel) > 0: self.PlotXLabel(self.xlabel)
        if len(self.ylabel) > 0: self.PlotYLabel(self.ylabel)
        #
        self.ExtractStatus()

    def OnViewData(self,event):
        fi6='%06d'; ff8='%8.3f'
        # min max
        val=[]
        for i in range(len(self.extracted)): val.append(self.yvalue[i])
        miny=min(val); maxy=max(val)

        text=self.plottitle+'\n'
        text=text+'molecule='+self.model.mol.name+'\n'
        text=text+'file='+self.model.mol.inpfile+'\n'
        text=text+'Extaraced data number='+str(len(self.extracted))
        text=text+'/'+str(len(self.xvalue))+'\n'
        text=text+'Min. value='+(ff8 % miny)+', Max. value='+(ff8 %maxy)+'\n\n'
        text=text+'data number('+self.xlabel+'),value('+self.ylabel
        text=text+') and xvardat\n'
        for i in range(len(self.extracted)):
            ii=self.extracted[i]
            if self.selectitem == 'atom':
                atom=self.model.mol.atm[ii]
                elm=atom.elm
                text=text+(fi6 % (ii+1))+'('+elm+')  '
                text=text+(ff8 % self.yvalue[i])+'  '
                resdat=lib.ResDat(atom)
                text=text+resdat+'\n'
            elif self.selectitem == 'other':
                text=text+fi6 % (ii+1)
                text=text+2*' '
                text=text+ff8 % self.yvalue[ii]+2*' '
                if len(self.xvarlst) > 0:
                    restxt=''
                    for j in self.xvarlst[ii]:
                        atom=self.model.mol.atm[j]
                        elm=atom.elm; resdat=lib.ResDat(atom)
                        text=text+(fi6 % (j+1)) +'('+elm+'),'
                        restxt=restxt+resdat+','
                    text=text[:-1]+' '+restxt[:-1]+'\n'
        #
        viewer=TextViewer_Frm(self.mpl,text=text,menu=True)
        viewer.RemoveOpenMenu()

    def XXSelect(self,sellst):
        if len(sellst) <= 0:
            mess='No atoms to be selected.'
            lib.MessageBoxOK(mess,'PlotAndSelect(Select)')
            return
        self.model.SetSelectAll(False)
        if self.selectitem == 'atom':
            #nsel=self.model.SelectAtomByValue(self.extracted,self.yvalue,vmin,
            #                                  vmax,absol)
            self.model.SelectAtomByList(sellst,True)
        elif self.selectitem == 'fragment':
            pass
        """
        elif self.selectitem == 'atom pair':
            sellst=[]; nsel=0
            for i in range(len(self.xvalue)):
                if self.yvalue[i] > vmin and self.yvalue[i] < vmax:
                    sellst.append(self.atmpairlst[i][0])
                    sellst.append(self.atmpairlst[i][1])
                    nsel += 1
            self.model.SelectAtomBySeqNmb(sellst,True)
        """

    def OnResetData(self,event):
        self.mpl.SetTitle(self.title)
        self.mpl.Clear()
        self.parent.PlotData()

    def OnClick(self,event):
        # select atom of clicked x-value
        # get event.x, event.y,event.xdata, event.ydata (all float data)
        mess=''
        try: i=int(event.xdata)
        except: return
        if not i in self.extracted: return
        try: value=self.yvalue[i]
        except:
            mess='Out of range.'
            self.model.Message(mess,0,'black')
            return
        if self.selectitem == 'atom':
            self.model.SetSelectAll(False)
            self.model.SelectAtomBySeqNmb([i],True)
            mess='Select atom='+str(i+1)+', Value='+str(value) #('%8.3f' % value)
        elif self.selectitem == 'fragment':
            self.model.SetSelectAll(False)
            self.model.SelectFragmentByNmb(i,True)
            mess='Select fragment='+str(i+1)+', Value='+str(value) #('%8.3f' % value)
        elif self.selectitem == 'redisue':
            self.model.SetSelectAll(False)
            self.model.SelectResidueByNmb(i,True)
            mess='Select residue='+str(i+1)+', Value='+str(value) #('%8.3f' % value)
        elif self.selectitem == 'other':
            self.model.SetSelectAll(False)
            if len(self.xvarlst) <= 0:
                mess='xvardat is not set. Unable to select atoms.'
                lib.MessageBoxOK(mess,'PlotAndSelect(Select)')
                return
            atmlst=[]
            for j in self.xvarlst[i]:
                atmlst.append(j)
            self.model.SelectAtomBySeqNmb(atmlst,True)
            label = 'value'
            if len(atmlst) == 2:   label = 'length'
            elif len(atmlst) == 3: label = 'angle'
            elif len(atmlst) == 4: label = 'tosion'
            atmlst=[x+1 for x in atmlst]
            mess='atoms='+str(atmlst)
            mess=mess+', ' + label +'='+str(value) #('%8.3f' % value)
        else:
            i=int(event.x)
            value=event.ydata
            mess='Data number='+str(i+1)+', value='+str(value) #('%8.3f' % value)
        #
        #self.model.Message(mess,0,'black')
        self.model.Message2(mess)

    def OnClose(self,event):
        self.mpl.OnClose(1)

class MatPlotLib_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos,winsize,winlabel):
        title="MatPlotLib in fumodel"
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,title,pos=winpos,size=winsize,
                style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
        self.mdlwin=parent
        self.model=model
        #xxself.ctrlflag=model.ctrlflag
        try: self.winctrl=model.winctrl
        except: pass
        self.winlabel=winlabel
        # icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        #
        self.axes=None
        self.figure=None
        self.canvas=None
        #
        self.graphtype="line"
        self.color='b'
        self.width=1/1.5
        self.marker='+'
        #
        self.CreateMplCanvas()
        self.NewPlot()
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreateMplCanvas(self):
        self.figure=Figure(facecolor="white")
        self.canvas=FigureCanvas(self,-1,self.figure)
        self.toolbar=NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        #self.toolbar.Show()
        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar,0,wx.LEFT|wx.EXPAND)
        #sizer.Add(self.canvas,1,wx.TOP|wx.EXPAND)
        sizer.Add(self.canvas,1,wx.ALL|wx.EXPAND)
        #sizer.Add(self.canvas,1,wx.TOP|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND)
        self.SetSizer(sizer)

    def SetColor(self,color):
        # color: 'b':blue,'g':green,'c':cyan,'m':magenta,'y':yellow
        #        'k':black,'w':white, 'r':red
        self.color=color

    def SetWidth(self,width):
        self.width=width

    def SetGraphType(self,type):
        self.graphtype=type

    def SetMarker(self,marker):
        self.marker=marker

    def NewPlot(self):
        self.axes=self.figure.add_subplot(111)
        self.figure.subplots_adjust(bottom=0.2,left=0.15,right=0.95,top=0.85)

    def PlotXY(self,x,y):
        if len(y) <= 0: return
        if len(x) <= 0:
            for i in range(len(y)): x.append(i+1)
        if self.graphtype == "line":
            self.axes.plot(x,y,color=self.color)
        if self.graphtype == "bar":
            self.axes.bar(x,y,width=self.width,color=self.color)

        self.canvas.draw()

    def PlotXY2(self,x,y,label):
        if len(y) <= 0: return
        if len(x) <= 0:
            for i in range(len(y)): x.append(i+1)
        if self.graphtype == "line":
            self.axes.plot(x,y,color=self.color,label=label)
        if self.graphtype == "bar":
            self.axes.bar(x,y,width=self.width,color=self.color,label=label)
        self.axes.legend()
        self.canvas.draw()

    def PlotXY3(self,x,y,marker,label):
        if len(y) <= 0: return
        if len(x) <= 0:
            for i in range(len(y)): x.append(i+1)
        if self.graphtype == "line":
            self.axes.plot(x,y,marker=self.marker,color=self.color,label=label)
        if self.graphtype == "bar":
            self.axes.bar(x,y,width=self.width,marker=self.marker,color=self.color,label=label)
        self.axes.legend()
        self.canvas.draw()

    def XTicks(self,label):
        self.axes.xticks(self.width/2,label)

    def Clear(self):
        self.figure.clear()
        self.canvas.draw()

    def PlotTitle(self,text):
        self.axes.set_title(text)
        self.canvas.draw()

    def PlotXLabel(self,text):
        self.axes.set_xlabel(text)
        self.canvas.draw()

    def PlotYLabel(self,text):
        self.axes.set_ylabel(text)
        self.canvas.draw()

    def OnClose(self,event):
        #if self.winctrl != "":
        #    self.ctrlflag.Set('*MatPlotLibWin',False)
        try: self.winctrl.Close(self.winlabel)
        except: pass
        #$$$self.open=False
        self.Destroy()

class ProgramPath_Frm(wx.Frame):
    def __init__(self,parent,id,title,remark,setfile):
        self.title=title #'Set GAMESS path and command line args'
        # remark: ["text1','text2',...]
        # setfile: the file in which program data are written
        winsize=lib.WinSize([400,155]); winpos=(0,20)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent, id, self.title,size=winsize,pos=winpos,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.model=parent.model #self.parent.model
        self.winctrl=model.winctrl
        #xxself.ctrlflag=self.parent.ctrlflag
        self.setfile=self.model.setfile

        self.size=self.GetSize()
        #self.gmspath="c:\\gamess.64\\rungms.bat"
        #self.gmsarg="13-64.intel.linux.mkl 1 0"
        self.gmspath=""; self.gmsarg=""
        gms,text,self.gmspath,self.gmsarg=self.ReadGAMESSPathInSetFile(True)

        self.setpath=False
        self.quit=False
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreatePanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        yloc=8
        wx.StaticText(self.panel,-1,"     ex. 'c:/gamess.64/rungms.bat' and '13-64.intel.linux.mkl 1 0'",pos=(5,yloc),size=(380,18))
        yloc += 20
        wx.StaticText(self.panel,-1,"     ex. 'c:/wingamess/runwingms.bat' and '11 1 0'",pos=(5,yloc),size=(380,18))
        yloc += 25
        wx.StaticText(self.panel,-1,"Path:",pos=(10,yloc),size=(60,18))
        self.tclpath=wx.TextCtrl(self.panel,-1,self.gmspath,pos=(75,yloc-2),size=(245,18))
        btnbrws=wx.Button(self.panel,wx.ID_ANY,"browse",pos=(330,yloc-2),size=(50,20))
        btnbrws.Bind(wx.EVT_BUTTON,self.OnBrowse)

        yloc += 25
        wx.StaticText(self.panel,-1,"Arguments:",pos=(10,yloc),size=(65,18))
        self.tclcmd=wx.TextCtrl(self.panel,-1,self.gmsarg,pos=(80,yloc-2),size=(295,18))
        yloc += 25
        btnok=wx.Button(self.panel,wx.ID_ANY,"OK",pos=(100,yloc-2),size=(35,20))
        btnok.Bind(wx.EVT_BUTTON,self.OnOK)
        btnrmv=wx.Button(self.panel,wx.ID_ANY,"Clear",pos=(150,yloc-2),size=(45,20))
        btnrmv.Bind(wx.EVT_BUTTON,self.OnClear)
        btncan=wx.Button(self.panel,wx.ID_ANY,"Cancel",pos=(240,yloc-2),size=(50,20))
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)

    def SetProgramPath(self):
        self.CreatePanel()

    def OnBrowse(self,event):
        wcard="All(*.*)|*.*"
        pathname=lib.GetFileName(self,wcard,"r",True,"")
        if pathname != "": self.tclpath.SetValue(pathname)

    def OnApply(self,event):
        self.gmspath=self.tclpath.GetValue()
        self.gmsarg=self.tclcmd.GetValue()
        if not os.path.exists(self.gmspath):
            mess="Path '"+self.gmspath+"' not found. Enter again?."
            dlg=lib.MessageBoxYesNo(mess,"")
            if dlg:
                self.setpath=False; return
            else:
                self.quit=True; self.gmspath=""; self.gmsarg=""
                self.setpath=False
                self.Close(1)
        else:
            self.quit=False
            exenam="gamess."+self.gmsarg.split()[0]+".exe"
            pathnam,exe=os.path.split(self.gmspath)
            gmsexe=os.path.join(pathnam,exenam) #"gamess."+exenam+".exe"
            #
            if not os.path.exists(gmsexe):
                mess="GAMESS executable '"+gmsexe+"' not found. Re-enter."
                lib.MessageBoxOK(mess,"")
                return
            else:
                self.SetGAMESSPathAndArgInSetFile(True)
                self.setpath=True; self.quit=False

    def OnClear(self,event):
        self.gmspath=self.tclpath.SetValue("")
        self.gmsarg=self.tclcmd.SetValue("")

    def OnCancel(self,event):
        self.winctrl.Set('GmsSetWin',False)
        self.Destroy()

    def ReadGAMESSPathInSetFile(self,add):
        gmspath=""; gmsarg=""; found=False; text=[]; gmsdat=""
        gms="program GAMESS "+self.gmspath+" $inpfile "+self.gmsarg
        if os.path.exists(self.setfile):
            f=open(self.setfile,"r")
            for s in f.readlines():
                ss=s; ss=ss.strip()
                #print 'ss.find("program"),ss.find("GAMESS")',ss.find("program"),ss.find("GAMESS")
                if ss.find("program") >= 0 and ss.find("GAMESS") >= 0:
                    found=True; gmsdat=ss
                    if add: text.append(gms)
                else: text.append(s)
            f.close()
        if not found: gms=""
        if len(gmsdat) > 0:
            item=gmsdat.split()
            if len(item) >=3: gmspath=item[2]
            if len(item) >=5: gmsarg=item[4]
            if len(item) >=6: gmsarg=gmsarg+' '+item[5]
            if len(item) >=7: gmsarg=gmsarg+' '+item[6]
        return gms,text,gmspath,gmsarg

    def SetGAMESSPathAndArgInSetFile(self,add):
        # add: True for add or update, False: delete
        # read
        found=True
        gms,text,gmspath,gmsarg=self.ReadGAMESSPathInSetFile(True)
        if len(gms) <= 0: found=False
        # write
        f=open(self.setfile,"w")
        for s in text:
            if found and s.find('GAMESS') >=0: continue
            f.write(s) #+'\n')
        if add:
            gms="program GAMESS "+self.gmspath+" $inpfile "+self.gmsarg
            f.write(gms+'\n')
        f.close()

    def OnOK(self,event):
        self.OnApply(1)
        self.OnClose(1)

    def OnClose(self,event):
        if not self.setpath:
            mess="Do you want to keep GAMESS path and command in fumolde.set file."
            dlg=wx.MessageYesNo(mess,"")
            if dlg == wx.YES:
                #if wx.YES:
                self.SetGAMESSPathAndArgInSetFile(True)
                self.setpath=True
            else: pass
        self.winctrl.CloseWin('GmsSetWin')

        self.Destroy()

class CreateProject_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos,winlabel):

        """ Create project. use 'SettingProject' class.
        :params str winlabel: 'New project' or 'Import project'. this is used as Motion mode.
        :see: 'SettingProject' class.
        """
        winsize=lib.WinSize((400,215))
        title=winlabel
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent, id, title,size=winsize,pos=winpos,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        #
        panel=wx.Panel(self,-1,pos=[-1,-1],size=winsize)
        self.setpan=custom.CustomProject(self,panel,model,winlabel)
        self.model=model
        self.winctrl=model.winctrl
        self.winlabel=winlabel
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def Message(self,mess):
        self.model.Message2(mess)

    def OnClose(self,event):
        self.winctrl.Close(self.winlabel)
        self.Destroy()

class SetPathAndArgs_Frm(wx.Frame):
    def __init__(self,parent,id,setfile,program,item,remark):
        self.title='Set '+program+' path and argument'
        winsize=lib.WinSize((400,155)); winpos=(0,20)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent, id, self.title,size=winsize,pos=winpos,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.model=parent.model #self.parent.model
        self.winctrl=model.winctrl
        #xxself.ctrlflag=self.parent.ctrlflag
        self.setfile=setfile
        self.remark=remark
        self.MakeModal(True)
        #
        self.size=self.GetSize()
        #self.gmspath="c:\\gamess.64\\rungms.bat"
        #self.gmsarg="13-64.intel.linux.mkl 1 0"
        self.path=""; self.args=""
        self.path,self.args=self.ReadPathAndArgs(True)

        self.setpath=False
        self.quit=False
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreatePanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        yloc=8
        text1=self.remark[0]
        wx.StaticText(self.panel,-1,"     ex. 'c:/gamess.64/rungms.bat' and '13-64.intel.linux.mkl 1 0'",pos=(5,yloc),size=(380,18))
        yloc += 20
        text2=self.remark[1]
        wx.StaticText(self.panel,-1,"     ex. 'c:/wingamess/runwingms.bat' and '11 1 0'",pos=(5,yloc),size=(380,18))
        yloc += 25
        wx.StaticText(self.panel,-1,"Path:",pos=(10,yloc),size=(60,18))
        self.tclpath=wx.TextCtrl(self.panel,-1,self.gmspath,pos=(75,yloc-2),size=(245,18))
        btnbrws=wx.Button(self.panel,wx.ID_ANY,"browse",pos=(330,yloc-2),size=(50,20))
        btnbrws.Bind(wx.EVT_BUTTON,self.OnBrowse)

        yloc += 25
        wx.StaticText(self.panel,-1,"Arguments:",pos=(10,yloc),size=(65,18))
        self.tclcmd=wx.TextCtrl(self.panel,-1,self.gmsarg,pos=(80,yloc-2),size=(295,18))
        yloc += 25
        btnok=wx.Button(self.panel,wx.ID_ANY,"OK",pos=(100,yloc-2),size=(35,20))
        btnok.Bind(wx.EVT_BUTTON,self.OnOK)
        btnrmv=wx.Button(self.panel,wx.ID_ANY,"Clear",pos=(150,yloc-2),size=(45,20))
        btnrmv.Bind(wx.EVT_BUTTON,self.OnClear)
        btncan=wx.Button(self.panel,wx.ID_ANY,"Cancel",pos=(240,yloc-2),size=(50,20))
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)

    def SetProgramPath(self):
        self.CreatePanel()
        self.Show()

    def OnBrowse(self,event):
        wcard="All(*.*)|*.*"
        pathname=lib.GetFileName(self,wcard,"r",True,"")
        if pathname != "": self.tclpath.SetValue(pathname)

    def OnApply(self,event):
        self.gmspath=self.tclpath.GetValue()
        self.gmsarg=self.tclcmd.GetValue()
        if not os.path.exists(self.gmspath):
            mess="Path '"+self.gmspath+"' not found. Enter again?."
            dlg=lib.MessageBoxYesNo(mess,"")
            if dlg:
                self.setpath=False; return
            else:
                self.quit=True; self.gmspath=""; self.gmsarg=""
                self.setpath=False
                self.Close(1)
        else:
            self.quit=False
            exenam="gamess."+self.gmsarg.split()[0]+".exe"
            pathnam,exe=os.path.split(self.gmspath)
            gmsexe=os.path.join(pathnam,exenam) #"gamess."+exenam+".exe"
            #
            if not os.path.exists(gmsexe):
                mess="GAMESS executable '"+gmsexe+"' not found. Re-enter."
                lib.MessageBoxOK(mess,"")
                return
            else:
                self.SetGAMESSPathAndArgInSetFile(True)
                self.setpath=True; self.quit=False

    def OnClear(self,event):
        self.gmspath=self.tclpath.SetValue("")
        self.gmsarg=self.tclcmd.SetValue("")

    def OnCancel(self,event):
        self.winctrl.Set('GmsSetWin',False)
        self.MakeModal(False)
        self.Destroy()

    def ReadPathAndArgs(self,add):
        path=""; args=""; found=False; text=[]; dat=""
        gms="program GAMESS "+self.path+" $inpfile "+self.gmsarg
        if os.path.exists(self.setfile):
            f=open(self.setfile,"r")
            for s in f.readlines():
                ss=s; ss=ss.strip()
                #print 'ss.find("program"),ss.find("GAMESS")',ss.find("program"),ss.find("GAMESS")
                if ss.find("GAMESS") >= 0 and ss.find("program") >= 0:
                    found=True; gmsdat=ss
                    if add: text.append(gms)
                else: text.append(s)
            f.close()
        if not found: gms=""
        if len(gmsdat) > 0:
            item=gmsdat.split()
            if len(item) >=3: path=item[2]
            if len(item) >=5: args=item[4]
            if len(item) >=6: args=args+' '+item[5]
            if len(item) >=7: args=args+' '+item[6]
        return path,args

    def SetGAMESSPathAndArgInSetFile(self,add):
        # add: True for add or update, False: delete
        # read
        found=True
        gms,text,gmspath,gmsarg=self.ReadGAMESSPathInSetFile(True)
        if len(gms) <= 0: found=False
        # write
        f=open(self.setfile,"w")
        for s in text:
            if found and s.find('GAMESS') >=0: continue
            f.write(s) #+'\n')
        if add:
            gms="program GAMESS "+self.gmspath+" $inpfile "+self.gmsarg
            f.write(gms+'\n')
        f.close()

    def OnOK(self,event):
        self.OnApply(1)
        self.OnClose(1)

    def OnClose(self,event):
        if not self.setpath:
            mess="Do you want to keep GAMESS path and command in fumolde.set file."
            dlg=lib.MessageBoxYesNo(mess,"")
            if dlg:
                #if wx.YES:
                self.SetGAMESSPathAndArgInSetFile(True)
                self.setpath=True
            else: pass
        self.winctrl.CloseWin('GmsSetWin')

        self.MakeModal(False)
        self.Destroy()

class ThreadEvent(wx.PyEvent):
    """ reference: http://wiki.wxpython.org/LongRunningTasks """
    def __init__(self,jobid,message,killed=''):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_THREAD_ID)
        self.jobid=jobid
        self.message=message
        self.killed=killed

EVT_THREAD_ID=wx.NewId()

class ExecProg_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos,winsize,title,winlabel,
                 onclose=None):
        self.title=title
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize)
        #
        self.parent=parent
        self.mdlwin=parent
        self.model=model
        self.winctrl=model.winctrl
        self.panel=wx.Panel(self)
        self.winlabel=winlabel
        self.onclose=onclose
        # set icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
       # Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[ExecProg]')
        self.Bind(wx.EVT_MENU,self.OnMenu)
        #
        self.outtext=wx.TextCtrl(self.panel,style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER) #|wx.TE_READONLY|wx.TE_NOHIDESEL)
        self.outtext.SetValue('')
        self.outtext.Bind(wx.EVT_TEXT_ENTER,self.OnTextEntered)
        self.outtext.Bind(wx.EVT_TEXT_MAXLEN,self.OnTextMaxLen)

        self.outtext.SetMaxLength(0) # too late to be practical!

        self.outtext.SetBackgroundColour("white")
        self.outtext.SetForegroundColour("black")
        # accept drop files
        droptarget=lib.DropFileTarget(self)
        self.SetDropTarget(droptarget)
        #
        self.process=None
        self.prg=[]
        self.arg=[]
        self.outfile=""
        self.openmplwin=False
        self.trap=False
        self.fout=None
        self.jobid=''
        self.killed=False
        #self.trapover=False
        self.x=[]; self.y=[]
        self.org=True
        self.orgtext=""
        #
        self.jobqueue=[]
        self.jobdone=[]
        self.jobkilled=[]
        self.jobcancelled=[]
        self.running=False
        self.runplt=[]
        self.runpdir=""
        self.runarg=""
        self.runoutfile=""
        self.curcmd=""
        self.disp=True
        #
        self.statusbar=self.CreateStatusBar()
        #self.statusbar.SetFieldsCount(2)
        #self.statusbar.SetStatusWidths([-8,-2])

        sizer=wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.outtext,proportion=1,flag=wx.EXPAND)
        self.panel.SetSizerAndFit(sizer)
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    @staticmethod
    def EVT_THREADNOTIFY(win,handler):
        win.Connect(-1,-1,EVT_THREAD_ID,handler)

    def JobManager(self):
        #print 'jobid ended',self.jobid
        #if len(self.jobqueue) > 0:
        np=len(self.prg)-1
        self.jobdone.append([self.jobid,self.prg[np],self.arg[np]])
        try: del self.jobqueue[0]
        except: pass
        # run next
        if len(self.jobqueue) > 0:
            jobid=self.jobqueue[0][0]
            prg=self.jobqueue[0][1]
            arg=self.jobqueue[0][2]
            plt=self.jobqueue[0][3]
            pdir=self.jobqueue[0][4]
            outfile=self.jobqueue[0][5]
            #del(self.jobqueue[0])
            self.ExecuteProgram(jobid,prg,arg,plt,pdir,outfile)

    def ListWaitingJobs(self):
        mess=""
        if len(self.jobdone) > 0:
            mess="Jobs done: "+"\n"
            for m0,m1,m2 in self.jobdone:
                mess=mess+m0+" "+m1+" "+m2+"\n"

        if len(self.jobqueue) <= 0:
            mess=mess+"No job is waiting."+"\n"
        else:
            mess=mess+"Running: "+"\n"
            np=len(self.prg)-1
            mess=mess+self.jobid+" "+self.prg[np]+" "+self.arg[np]+"\n"
            if len(self.jobqueue) > 1:
                mess="Waiting: "+"\n"
                for i in range(1,len(self.jobqueue)):
                    np=len(self.jobqueue[i][1])-1
                    m0=self.jobqueue[i][0]; m1=self.jobqueue[i][1][np]; m2=self.jobqueue[i][2][np]
                    mess=mess+m0+" "+m1+" "+m2+"\n"

        lib.MessageBoxOK(mess,"")
        #
    def SetJobInQueue(self,job):
        self.jobqueue.append(job)

    def CancelJobs(self):

        if len(self.jobqueue) > 1:
            for i in range(1,len(self.jobqueue)):
                np=len(self.jobqueue[i][1])-1
                m0=self.jobqueue[i][0]; m1=self.jobqueue[i][1][np]; m2=self.jobqueue[i][2][np]
                self.jobcancelled.append(m1+" "+m2)
        self.jobqueue=[]

    def GetDoneJobList(self):
        joblst=[]
        for m0,m1,m2 in self.jobdone:
            joblst.append(m1+" "+m2)
        return joblst

    def GetCancelledJobList(self):
        return self.self.jobcancelled

    def GetKilledJobList(self):
        return self.jobkilled

    def ClearJobQueue(self):
        self.jobqueue=[]

    def ChangeBackgroundColor(self):
        color=lib.ChooseColorOnPalette(self.panel,True,-1)
        #color=[255*col[0],255*col[1],255*col[2]]
        self.outtext.SetBackgroundColour(color)

    def SetOutputOnDisplay(self,on):
        """
        :param bool on: True for display, False for not display
        """
        self.disp=on
        #self.exmenu."Output on display"
        item=self.menuitemdic["Output on display"]
        item.Check(on)

    def GetComputeStatus(self):
        return self.running

    def GetWaitingJobList(self):
        return self.jobqueue

    def ChangeTextColor(self):
        color=lib.ChooseColorOnPalette(self.panel,True,-1)
        #color=[255*col[0],255*col[1],255*col[2]]
        self.outtext.SetForegroundColour(color)

    def ExecuteProgram(self,jobid,prg,arg,plt,pdir,outfile):
        # prg [list]: exe file name to be executed successively.
        # arg [list]: arguments for each program
        # plt [list]: plot data (dictionary) for each program
        # ex. pltdic={'winpos':[-1,-1],'winsize':[640,250],'every':0,
        #    'fromkw':"Iter",'tokw':"\n",'xitemno':0,'yitemno':1,
        #    'xform':'int','yform':'float','title':'Newton optimization',
        #    'xlabel':'iteratin','ylabel':'energy in kcal/mol'}
        # pdir (string): directory name of programs
        # outfile (string): output file name wich will be created in executions
        self.jobid=jobid
        self.njob=len(prg)
        self.prg=prg
        self.arg=arg
        self.plt=plt
        self.outfile=outfile
        self.pdir=pdir
        #self.disp=disp
        self.outtext.Clear()
        # plot data
        self.nstep=-1
        for i in range(len(self.plt)):
            if len(self.plt[i]) and self.disp> 0:
                cprg=self.prg[i]
                try:
                    self.OpenMplWin(self.plt[i],cprg)
                    self.openmplwin=True
                except: self.openmplwin=False
        try:
            if lib.GetPlatform() == 'WINDOWS':
                self.thread=threading.Thread(target=self.RunProg)
                ###self.thread.setDaemon(True)
                self.thread.start()
            else: self.RunProg()
            self.fout.close()
        except: pass

    def RunProg(self):
        self.running=True
        self.ended=False; self.killed=False
        # change directory
        if len(self.pdir) > 0: os.chdir(self.pdir)
        #
        for i in range(self.njob):
            cmd=self.prg[i]+" "+self.arg[i]
            self.SetTitle(self.title+"["+cmd+"]")
            self.curcmd=cmd
            self.curplt=self.plt[i]
            mess="Running "+self.curcmd+'. Elapsed time='
            # write date and time
            date=datetime.datetime.today()
            time1=time.clock()
            startmess='... '+self.prg[i]+' starts at '
            startmess=startmess+date.strftime("%Y/%m/%d %H:%M:%S")
            argmess='... arguments: '+self.arg[i]
            sa=[]
            if self.disp:
                ###self.AddText(sa,startmess); self.AddText(sa,argmess)
                self.outtext.AppendText(startmess+'\n')
                self.outtext.AppendText(argmess+'\n')

            if self.outfile != "":
                self.fout=open(self.outfile,"w")
                self.fout.write(startmess+'\n'+argmess+'\n')
                #self.fout.write(argmess+'\n')

            # execute cmd
            try:
                if lib.GetPlatform() == 'WINDOWS':
                    info = subprocess.STARTUPINFO()
                    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    info.wShowWindow = subprocess.SW_HIDE
                    #    proc = subprocess.Popen(..., startupinfo=info)
                    self.process=subprocess.Popen(cmd,bufsize=-1,
                               stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                               stdin=subprocess.PIPE,startupinfo=info)
                else:
                    cmd=cmd+' >> '+self.outfile
                    self.process=subprocess.Popen(cmd,bufsize=-1,shell=True,
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                # dispaly output text
                while True:
                    line=self.process.stdout.readline()
                    ###wx.Yield()
                    etime="%10.2f" % (time.clock()-time1)
                    self.SetStatusText(mess+etime+' sec',0)
                    line=self.DecodeStdout(line)
                    if line is None:
                        wx.MessageBox('stdout decode error in subwin.ExecProg_Frm.RunProg')
                        return
                    if self.disp:
                        try: self.outtext.AppendText(line+'\n')
                        except: pass
                        if self.openmplwin and len(self.plt[i]) > 0:
                            self.TrapDataAndPlot(line)
                    if self.outfile != "":
                        try: self.fout.write(line+'\n')
                        except: pass
                    if not line: break

            except OSError as err:
                mess='GAMESS execution failed. e=',err.strerror
                lib.MessageBoxOK(mess,'ExecProg_Frm(RunProg')
                return
            #
            date=datetime.datetime.today()
            endmess='... '+self.prg[i]+' ended at '+date.strftime("%Y/%m/%d %H:%M:%S")
            time2=time.clock()
            dtime="%12.2f" % (time2-time1)
            elpsmess='... elapsed time= '+dtime+' (sec)'
            if self.killed:
                mess=self.prg[i]+" "+self.arg[i]
                self.jobkilled.append(mess)
            if self.disp:
                text=endmess+'\n'+elpsmess+'\n'
                self.outtext.AppendText(text)
                if self.killed:
                    mess='... The job was killed by user.'
                    self.outtext.AppendText('\n'+mess+'\n')
            if self.outfile != "":
                try:
                    self.fout.write(endmess+'\n'); self.fout.write(elpsmess+'\n'); self.fout.write('\n')
                except: pass
                if self.killed:
                    try:
                        self.fout.write(mess+'\n'); self.fout.close()
                    except: pass
        # notify job-over to parent
        try:
            self.fout.close()
            self.process.stdout.close()
            self.process.stderr.close()
            self.process.kill()
        except: pass
        #
        #if os.path.exists(self.outfile):
        #    self.AppendTextFromFile(self.outfile)
        #
        date=datetime.datetime.today()
        endmess=self.prg[i]+' ended at '+date.strftime("%Y/%m/%d %H:%M:%S")
        self.SetStatusText(endmess,0)
        self.running=False
        wx.PostEvent(self.parent,ThreadEvent(self.jobid,self.curcmd,self.killed)) #jobid))
        self.JobManager()

    def DecodeStdout(self,line):
        jpcodecs=['shift_jis','cp932','euc_jp','iso2022_jp']
        for jpcode in jpcodecs:
            try:
                line=line.decode(jpcode)
                break
            except:
                pass
            line=None
        return line

    def AddText(self,sa,text):
        sa.append(text+'\n')
        self.last=self.outtext.GetLastPosition()

    def KillProcess(self):
        # close output file
        if self.killed: return

        try: del self.jobdone[-1]
        except: pass

        try: self.fout.close()
        except: pass
        #
        pid=os.getpid()
        try: parent = psutil.Process(pid)
        except: parent=None
        #try: self.fout.close()
        #except: pass
        try:
            nkil=0
            for child in parent.get_children(recursive=True):
                child.kill(); nkil += 1
            if nkil > 0:
                self.killed=True
                self.running=False
        except: pass

    def SaveLogOnFile(self,outfile):
        self.outtext.SaveFile(outfile)

    def TrapDataAndPlot(self,text):
        #if self.trapover: return
        if self.trap:
            if 'tokw' in self.curplt:
                if self.curplt['tokw'] == '':
                    if text.strip() == "": self.trap=False
                else:
                    if text.find(self.curplt['tokw']) >= 0: self.trap=False
                if not self.trap: return
        if not self.trap:
            if 'fromkw' not in self.curplt:
                self.trap=True
            else:
                if text.find(self.curplt['fromkw']) >= 0:
                    self.trap=True; return
        #
        if not self.trap: return
        #
        item=text.split()
        nitm=len(item)
        ix=-1
        if 'xitemno' in self.curplt: ix=self.curplt['xitemno']
        if nitm < ix or nitm < self.curplt['yitemno']: return
        self.nstep += 1
        if 'every' in self.curplt:
            if self.curplt['every'] != 0 and self.nstep % self.curplt['every'] != 0: return
        try:
            if 'xitemno' in self.curplt:
                x=item[self.curplt['xitemno']]; x=x.replace(",","")
                if 'xform' in self.curplt:
                    if self.curplt['xform'] == 'int': x=int(x)
                    elif self.curplt['xform'] == 'float': x=float(x)
                else:
                    if x.find('.') >=0: x=float(x)
                    else: x=int(x)
            else: x=self.nstep
            self.x.append(x)
            #
            y=item[self.curplt['yitemno']]; y=y.replace(",","")
            if 'yform' in self.curplt:
                if self.curplt['yform'] == 'int': y=int(y)
                elif self.curplt['yform'] == 'float': y=float(y)
            else:
                if y.find('.') >=0: y=float(y)
                else: y=int(y)
            self.y.append(y)
            # plot (x,y)
            self.Plot(True)

        except:
            pass

    def OpenMplWin(self,plt,cmd):
        # open Mpl window
        self.x=[]; self.y=[]
        if not self.openmplwin:
            frmpos=self.panel.GetPosition(); frmsiz=self.panel.GetSize()
            if 'winpos' not in plt:
                winpos=[frmpos[0]+frmsiz[0]-240,frmpos[1]]
            else:
                winpos=plt['winpos']
                if winpos[1] == -1: winpos[1]=frmpos[1]+frmsiz[1]+50
            if 'winsize' not in plt: winsize=[640,250]
            else: winsize=plt['winsize']
            # create Mpl panel
            winlabel='ExecProgWin'
            self.exempl=MatPlotLib_Frm(self.panel,-1,self.model,winpos,winsize,winlabel) #winpos) #,winsize)1
            self.exempl.Show()
            self.openmplwin=True
            #self.x=[]; self.y=[]
            self.curcmd=""
            self.curplt={}
        self.Plot(True)

    def Plot(self,single):
        if single:
            self.exempl.Clear(); self.exempl.NewPlot()
        if 'title' in self.curplt: title=self.curplt['title']
        else: title='no title'
        if 'xlabel' in self.curplt: xlabel=self.curplt['xlabel']
        else: xlabel='x'
        if 'ylabel' in self.curplt: ylabel=self.curplt['ylabel']
        else: ylabel='y'
        style=0
        if 'style' in self.curplt: style=self.curplt['style']
        if style > 1: style=0
        wtitle='No title'
        if len(self.curcmd) > 0: wtitle=self.curcmd
        if 'fromkw' in self.curplt: wtitle=wtitle+',kw1='+self.curplt['fromkw']
        if 'tokw' in self.curplt: wtitle=wtitle+',kw2='+self.curplt['tokw']
        self.exempl.SetTitle(wtitle) #self.curcmd)

        self.exempl.PlotTitle(title)
        self.exempl.PlotXLabel(xlabel)
        self.exempl.PlotYLabel(ylabel)
        #
        if len(self.x) <= 0: return
        # split data
        #print 'self.x',self.x
        #print 'self.y',self.y
        x0=self.x[0]; xrep=[]
        for i in range(len(self.x)):
            if self.x[i] == x0: xrep.append(i)
        nx=len(xrep); xrep.append(len(self.x))
        #print 'xrep',xrep
        for i in range(nx):
            ist=xrep[i]; ied=xrep[i+1]
            #print 'ist,ied',ist,ied
            x=[]; y=[]
            for j in range(ist,ied):
                #print 'j,x,y',j,x,y
                x.append(self.x[j]); y.append(self.y[j])
            #print 'x',x
            #print 'y',y
            if len(x) > 0:
                if nx > 1:
                    if style == 0: self.exempl.PlotXY2(x,y,str(i))
                    else:
                        mk=self.GetMarker(i)
                        self.exempl.PlotXY3(x,y,mk,str(i))
                else: self.exempl.PlotXY(x,y)

    def OnTextEntered(self,event):
        last=self.outtext.GetLastPosition()
        nl=self.outtext.GetNumberOfLines() # note: last pos exculuding '/n'
        #py3#text=self.outtext.GetString(last-nl+1,last-nl+1)
        text = self.outtext.GetRange(last - nl + 1, last - nl + 1)
        print(('text',text))

        self.outtext.ShowPosition(last)
        text=text.strip(); text=text.replace('\n','')
        print(('text[0:4]',text[0:4]))
        if len(text) <= 0: pass # still need get last line
        # cmmand
        elif text[0:4] == '>run':
            runprg=lib.PickUpValue(text,'run:')
            prg=[]; arg=[]; plt=[]; pdir=""; outfile=""
            print(('run',runprg))
            runprg="c:/gamess.64/rungms.bat"
            self.runarg="c:/gamess.64/exam01.inp 11-64 1 0"
            self.runpdir="c:/gamess.64"
            self.runoutfile=""
            self.runplt={}; plt.append(self.runplt)

            prg.append(runprg)
            #if len(self.runplt) >= 0: plt.append(self.runplt)
            #if len(self.runpdir) >= 0: pdir=self.runpdir
            #if len(self.runarg) >= 0: arg.append(self.runarg)
            #if len(self.runoutfile) >= 0: outfile=self.runoutfile
            plt.append(self.runplt)
            pdir=self.runpdir
            arg.append(self.runarg)
            outfile=self.runoutfile

            self.ExecuteProgram(prg,arg,plt,pdir,outfile)
        # run parameters
        elif text[0:4] == '>prm':
            self.SetRunParams(text[4:])
            #runset=lib.PickUpValue(text,'plt:')
            #self.cmdplt=self.cmdplt.strip()
        elif text[0:5] == '>rmprm':
            print('remove params')
        # print parametres
        elif text[0:4] == '?prm':
            self.PrintRunParams(text[:4])
        # stdin input
        else:
            try:
                self.process.stdin.write(text+'\n')
            except:
                lib.MessageBoxOK("Invalid input data. Reenter.","")

        # get cuttent last position
        self.outtext.AppendText('\n')
        self.last=self.outtext.GetLastPosition()

    def PrintRunParams(self,text):
        print('run paramters. prg')
        print('arg')
        print('plt...')

    def SetRunParams(self,text):
        print(('text in SetRun',text))
        # working directory
        # clear prg params
        self.runcle=lib.PickUpValue(text,'cle=')
        self.runcle=self.runprg.strip()
        print(('runcle',self.runcle))

        self.runprg=lib.PickUpValue(text,'prg=')
        self.runprg=self.runprg.strip()
        print(('runprg',self.runprg))

        self.runpdir=lib.PickUpValue(text,'pdir=')
        self.runpdir=self.runpdir.strip()
        print(('runpdir',self.runpdir))


    def GetMarker(self,i):
        marker=['-',# solid line style
        '--',# dashed line style
        '-.',# dash-dot line style
        ':',# dotted line style
        '.',# point marker
        ',',# pixel marker
        'o',# circle marker
        'v',# triangle_down marker
        '^',# triangle_up marker
        '<',# triangle_left marker
        '>',# triangle_right marker
        '1',# tri_down marker
        '2',# tri_up marker
        '3',# tri_left marker
        '4',# tri_right marker
        's',# square marker
        'p',# pentagon marker
        '*',# star marker
        'h',# hexagon1 marker
        'H',# hexagon2 marker
        '+',# plus marker
        'x',# x marker
        'D',# diamond marker
        'd',# thin_diamond marker
        '|',# vline marker
        '_' ]# hline marker
        nmark=27
        ii= i % nmark
        return marker[ii]

    def AppendTextFromFile(self,outfile):
        outfile=os.path.normcase(outfile)
        self.ClearText()
        retry=False
        self.outtext.LoadFile(outfile)
        rline=self.outtext.GetNumberOfLines()

        if rline <= 1: # try read file
            retry=True
            self.ClearText()
            f=open(outfile,'r')
            n=0; errline=''
            for text in f.readlines():
                n += 1
                try: self.outtext.AppendText(text)
                except: errline=errline+str(n)+','
            f.close()
        # Show line numbers ?
        #if self.menubar.IsChecked("Show line numbers"):
        #    self.ShowLineNumbers(True)
        rline=self.outtext.GetNumberOfLines()
        mess="Load file="+outfile+". Number of lines="+str(rline)
        self.SetStatusText(mess,0)
        if retry:
            try: self.model.ConsoleMessage('Filed utf-8 decode in lines: '+errline)
            except: pass

    def ClearText(self):
        self.outtext.Clear()

    def OnTextMaxLen(self,event):
        last=self.outtext.GetLastPosition()
        mess="Exceeded max. length="+str(last)
        lib.MessageBoxOK(mess,"")

        """ SetMaxLength(len) len=0 can change the max"""

    def OnClose(self,event):
        try: self.onclose()
        except: pass
        try:
            self.KillProcess()
            self.killed=True
        except: pass
        #try: self.winctrl.Close(self.winlabel)
        #except: pass
        #try:
        #    if self.winctrl.IsOpened('ExeProgWin'): self.winctrl.CloseWin('ExeProgWin')
        #except: pass
        try:
            if self.winctrl.IsOpened(self.winlabel): self.winctrl.Close(self.winlabel)
        except: pass
        #
        self.Destroy()

    def Find(self):
        style=(wx.FR_NOUPDOWN|wx.FR_NOMATCHCASE|wx.FR_NOWHOLEWORD)
        title='Find string'
        self.finddata=wx.FindReplaceData()
        self.fnddlg=wx.FindReplaceDialog(self.outtext,self.finddata,title,style)
        self.fnddlg.Bind(wx.EVT_FIND_CLOSE,self.OnFindClose)
        self.fnddlg.Bind(wx.EVT_FIND,self.OnFind)
        self.fnddlg.Bind(wx.EVT_FIND_NEXT,self.OnFindNext)
        self.fnddlg.Show()

    def MissingQuortError(self):
        mess='Missing quotation mark!'
        lib.MessageBoxOK(mess,'MissingQuotError')

    def Replace(self):
        stxt=""
        stxt=wx.GetTextFromUser('Enter "string1(old)","string2(new)" to replace.',parent=self.panel)
        if len(stxt) <= 0: return
        #items=stxt.split(',')
        items=lib.SplitStringAtSpacesOrCommas(stxt)
        if len(items) < 2: return
        oldstr=items[0].strip() #; oldstr=oldstr[1:]; oldstr=oldstr[:-1]
        oldstr=lib.GetStringBetweenQuotation(oldstr)
        if len(oldstr) <= 0: self.MissingQuortError()
        oldstr=oldstr[0]
        newstr=items[1].strip() #; newstr=newstr[1:]; newstr=newstr[:-1]
        newstr=lib.GetStringBetweenQuotation(newstr)
        if len(newstr) <= 0: self.MissingQuortError()
        newstr=newstr[0]
        #
        text=self.outtext.GetValue()
        if len(text) < 0: return
        text=text.replace(oldstr,newstr)
        self.outtext.Clear()
        self.outtext.AppendText(text)

    def PickupLines(self):
        stxt=""
        stxt=wx.GetTextFromUser('Enter string in line to be picked up; "string".',
                               'Input string for pickup.',parent=self.panel)
        stxt=stxt.strip()
        if len(stxt) <= 0: return
        stxt=lib.GetStringBetweenQuotation(stxt)
        if len(stxt) <= 0:
            self.MissingQuortError()
            return
        stxt=stxt[0]
        nlin=self.outtext.GetNumberOfLines()
        if self.org: self.orgtext=self.outtext.GetValue()
        seltxt=""
        nsel=0
        for i in range(nlin):
            s=self.outtext.GetLineText(i)
            #if self.org: self.orgtext=self.orgtext+s+'\n'
            if s.find(stxt) >=0:
                nsel += 1
                seltxt=seltxt+s+'\n'
        if len(seltxt) > 0:
            self.outtext.Clear()
            self.outtext.AppendText(seltxt)
            self.org=False
        mess='Pick up lines with "'+stxt+'"='+str(nsel)
        self.SetStatusText(mess,0)

    def RemoveLines(self):
        stxt=""
        stxt=wx.GetTextFromUser('Enter string in line to be Removeped; "string".',
                               'Input string for Remove.',parent=self.panel)
        if len(stxt) <=0: return
        stxt=lib.GetStringBetweenQuotation(stxt)
        if len(stxt) <= 0:
            self.MissingQuortError()
            return
        stxt=stxt[0]
        stxt.strip(); stxt=stxt.replace('\n','')
        nlin=self.outtext.GetNumberOfLines()
        if self.org: self.orgtext=self.outtext.GetValue()
        seltxt=""
        for i in range(nlin):
            s=self.outtext.GetLineText(i)
            #if self.org: self.orgtext=self.orgtext+s+'\n'
            if s.find(stxt) < 0: seltxt=seltxt+s+'\n'
        if len(seltxt) > 0:
            self.outtext.Clear()
            self.outtext.AppendText(seltxt)
            self.org=False

    def PickupLinesBetween(self):
        stxt=""
        stxt=wx.GetTextFromUser('Enter string start and end lines strings,"string 1","string2".',
                               'Input two string for pickup.',parent=self.panel)
        if len(stxt) <=0: return
        items=lib.SplitStringAtSpacesOrCommas(stxt)
        if len(items) < 2:
            lib.MessageBoxOK("Wrong input. Try again.","")
            return
        startstr=lib.GetStringBetweenQuotation(items[0])
        if len(startstr) <= 0:
            self.MissingQuortError()
            return
        stratstr=startstr[0]
        endstr=lib.GetStringBetweenQuotation(items[1])
        if len(endstr) <= 0:
            self.MissingQuortError()
            return
        endstr=endstr[0]
        nlin=self.outtext.GetNumberOfLines()
        if self.org: self.orgtext=self.outtext.GetValue()
        orgtext=self.orgtext.splitlines()
        #start=False; seltxt=""
        seltxt=lib.PickUpTextBetween(orgtext,startstr,endstr)
        if len(seltxt) > 0:
            self.outtext.Clear()
            self.outtext.AppendText(seltxt)
            self.org=False

    def InputDataAndPlot(self,graphtype):
        """

        :param str graphtype: 'line' or 'bar'
        """
        if graphtype == 'line': style=0
        else: style=1
        #
        self.curplt={}
        dat=wx.GetTextFromUser('Enter columns for x and y and t="title",x="xlabel", and y="ylabel".',
                              'Input date for plot.',parent=self) #.panel)

        title='no title'; xlabel='x'; ylabel='y'; style=0
        # find title
        val=lib.PickUpValue(dat,'t=') # title
        try:
            if val != "": title=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'x=') # x-label
        try:
            if val != "": xlabel=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'y=') # y-label
        try:
            if val != "": ylabel=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'s=') # s:style
        try:
            if val != "":
                style=val; style=int(style)
        except: pass
        #
        text=self.outtext.GetStringSelection()
        text=text.splitlines()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")

            return
        dat=dat.replace(',',' ')
        item=dat.split()
        itemx=0; itemy=0

        try:
            if item[0].isdigit() and item[1].isdigit():
                itemx=int(item[0])-1
                itemy=int(item[1])-1
                self.curplt["x"]=itemx
                self.curplt["y"]=itemy
            else:
                lib.MessageBoxOK("Please input column numbers in integers!","")
                return
        except: pass
        #
        self.x=[]; self.y=[]
        text=self.outtext.GetStringSelection()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")
            return
        text=text.splitlines()
        for s in text:
            if len(s) <= 0: continue
            item=s.split()
            nitm=len(item)
            if nitm < itemx or nitm < itemy: continue
            try:
                item[itemx]=item[itemx].replace(",","")
                item[itemy]=item[itemy].replace(",","")
                if item[itemx].isdigit(): self.x.append(int(item[itemx]))
                elif item[itemx].find('.') >= 0:
                    self.x.append(float(item[itemx]))
                else: continue
                if item[itemy].isdigit(): self.y.append(int(item[itemy]))
                elif item[itemy].find('.') >= 0:
                    self.y.append(float(item[itemy]))
                else: continue
            except: pass
        #if len(self.x) <= 0: self.x=numpy.arange(1,len(self.y),1)
        #
        winpos=[0,20]; winsize=lib.WinSize([640,245])
        winlabel='Open EasyPlotWin'
        self.exempl=MatPlotLib_Frm(self,-1,self.model,winpos,winsize,winlabel)
        self.exempl.Show()
        self.openmplwin=True
        #
        if graphtype == '': graphtype='line'
        self.exempl.SetGraphType(graphtype)
        self.curplt['title']=title; self.curplt['xlabel']=xlabel
        self.curplt['ylabel']=ylabel; self.curplt['style']=style

        self.Plot(True)

    def PlotGraph(self,curplt,formline,toline):
        """ not completed

        :param dic curplt:  curplt{'x':colmunx(int),'y':columny(int),'title':title(str),'xlabel':xlabel(str),
             'ylabel':ylabel(str),'style':style(int=0 for line,1=for bar)}
        :param str graphtype: 'line' or 'bar'
        """
        #
        self.curplt={}
        dat=wx.GetTextFromUser('Enter columns for x and y and t="title",x="xlabel", and y="ylabel".',
                              'Input date for plot.',parent=self) #.panel)

        title='no title'; xlabel='x'; ylabel='y'; style=0
        # find title
        val=lib.PickUpValue(dat,'t=') # title
        try:
            if val != "": title=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'x=') # x-label
        try:
            if val != "": xlabel=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'y=') # y-label
        try:
            if val != "": ylabel=lib.GetStringBetweenQuotation(val)[0]
        except: pass
        val=lib.PickUpValue(dat,'s=') # s:style
        try:
            if val != "":
                style=val; style=int(style)
        except: pass
        #
        text=self.outtext.GetStringSelection()
        text=text.splitlines()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")

            return
        dat=dat.replace(',',' ')
        item=dat.split()
        itemx=0; itemy=0

        try:
            if item[0].isdigit() and item[1].isdigit():
                itemx=int(item[0])-1
                itemy=int(item[1])-1
            else:
                lib.MessageBoxOK("Please input column numbers in integers!","")
                return
        except: pass

        self.x=[]; self.y=[]
        text=self.outtext.GetStringSelection()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")
            return
        text=text.splitlines()
        for s in text:
            if len(s) <= 0: continue
            item=s.split()
            nitm=len(item)
            if nitm < itemx or nitm < itemy: continue
            try:
                item[itemx]=item[itemx].replace(",","")
                item[itemy]=item[itemy].replace(",","")
                if item[itemx].isdigit(): self.x.append(int(item[itemx]))
                elif item[itemx].find('.') >= 0:
                    self.x.append(float(item[itemx]))
                else: continue
                if item[itemy].isdigit(): self.y.append(int(item[itemy]))
                elif item[itemy].find('.') >= 0:
                    self.y.append(float(item[itemy]))
                else: continue
            except: pass


        #if len(self.x) <= 0: self.x=numpy.arange(1,len(self.y),1)
        #
        winpos=[0,20]; winsize=lib.WinSize([640,245])
        winlabel='Open EasyPlotWin'
        self.exempl=MatPlotLib_Frm(self,-1,self.model,winpos,winsize,winlabel)
        self.exempl.Show()
        self.openmplwin=True
        #
        if graphtype == '': graphtype='line'
        self.exempl.SetGraphType(graphtype)
        self.curplt['title']=title; self.curplt['xlabel']=xlabel
        self.curplt['ylabel']=ylabel; self.curplt['style']=style

        self.Plot(True)

    def ShowLineNumbers(self,on):
        text=self.outtext.GetValue()
        if len(text) <= 1: return

        self.ClearText()
        items=text.split('\n')
        nlines=float(len(items))
        figs=int(log10(nlines))+1
        text=''
        if on:
            n=0; form='%0'+str(figs)+'d'
            for s in items:
                n += 1; text=text+(form % n)+':'+s+'\n'
        else:
            for s in items:
                n=s.find(':',1); s=s[n+1:]
                text=text+s+'\n'
        self.outtext.AppendText(text)

    def AddLineNumbers(self):
        text=self.outtext.GetStringSelection()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")
            return
        items=text.splitlines()
        self.ClearText()
        text=''
        nlines=float(len(items))
        figs=int(log10(nlines))+1
        text=''
        n=0; form='%0'+str(figs)+'d'
        for s in items:
            n += 1; text=text+(form % n)+' '+s+'\n'
        text=text[:-1]
        self.outtext.AppendText(text)

    def SelectLines(self,lfrom,lto):
        sfrom=self.outtext.XYToPosition(0,lfrom-1)
        sto=self.outtext.XYToPosition(0,lto-1)
        self.outtext.SetSelection(sfrom,sto)

    def RemoveLineNumbers(self):
        text=self.outtext.GetStringSelection()
        text=text.rstrip()
        if len(text) <= 0:
            lib.MessageBoxOK("No text selected.","")
            return
        items=text.splitlines()
        self.ClearText()
        text=''
        figs=items[0]
        figs=figs.split(' ',1)[0].strip()
        n=len(figs)
        if n <= 0: return
        try: ifig=int(figs)
        except: return
        #if figs.isdigit():
        for s in items:
            s=s[n+1:]
            text=text+s+'\n'
        text=text[:-1]
        self.outtext.AppendText(text)

    def OpenDropFiles(self,filenames):
        if len(filenames) <= 0: return
        outfile=filenames[0]
        if len(outfile) <= 0: return
        #
        self.outtext.AppendText("\n"+"... begin text in file="+outfile+"\n")
        self.AppendTextFromFile(outfile)
        #
        self.SetStatusText(outfile+' is loaded.',0)
        self.SetTitle(self.title+"[View output: "+outfile+"]")

    def OnMenu(self,event):
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        bChecked=self.menubar.IsChecked(menuid)
        if item == "Save log as":
            wcard='output file(*.log)|*.log'
            filename=lib.GetFileName(self.panel,wcard,"w",True,"")
            if len(filename) <= 0:
                self.outtext.AppendText('\n'+'... Filename is not given.\n')
            else: self.SaveLogOnFile(filename)

        elif item == "View output file":
            outfile=self.outfile
            if len(self.outfile) <= 0:
                wcard='output file(*.log,*.out)|*.log;*.out'
                outfile=lib.GetFileName(self.panel,wcard,"r",True,"")
                if len(outfile) <= 0: return
            #lib.Editor(outfile)
            #os.spawnv(os.P_NOWAIT,"C:\\Windows\\System32\\notepad.exe",
            #                      ["notepad.exe"+' '+outfile])
            title = 'View output file'
            winsize = [600, 400]
            viewout=TextEditor_Frm(self,-1,winsize=winsize,title=title, textfile=outfile,
                                   mode='View')

        elif item == "Output on display":
            if bChecked: self.disp=True
            else: self.disp=False

        elif item == "Load output file":
            outfile=self.outfile
            if len(self.outfile) <= 0:
                wcard='output file(*.log,*.out)|*.log;*.out'
                outfile=lib.GetFileName(self.panel,wcard,"r",True,"")
                if len(outfile) <= 0: return
            self.AppendTextFromFile(outfile)
            self.SetStatusText(outfile+' is loaded.',0)
            self.SetTitle(self.title+"[View output: "+outfile+"]")

        elif item == "Read output file":
            outfile=''
            wcard='output file(*.log,*.out)|*.log;*.out'
            outfile=lib.GetFileName(self.panel,wcard,"r",True,"")
            if len(outfile) <= 0: return

            self.outtext.AppendText("\n"+"... begin text in file="+outfile+"\n")
            self.AppendTextFromFile(outfile)

            self.SetStatusText(outfile+' is loaded.',0)
            self.SetTitle(self.title+"[View output: "+outfile+"]")

        elif item == "Background color": self.ChangeBackgroundColor()

        elif item == "Text color": self.ChangeTextColor()

        elif item == "Close": self.OnClose(1)

        elif item == "Find": self.Find()

        elif item == 'Replace': self.Replace()

        elif item == "Pickup lines": self.PickupLines()

        elif item == "Remove lines": self.RemoveLines()

        elif item == "Pickup lines between": self.PickupLinesBetween()

        elif item == "Restore all lines":
            if not self.orgtext:
                lib.MessageBoxOK("Restore is not possible.","")

                return
            self.outtext.Clear()
            self.outtext.AppendText(self.orgtext)
            self.org=True

        elif item == "Select all": self.outtext.SelectAll()

        elif item == "Show line numbers": self.ShowLineNumbers(bChecked)

        elif item == "Add line numbers": self.AddLineNumbers()

        elif item == "Remove line numbers": self.RemoveLineNumbers()

        elif item == "Clear":
            self.orgtext=self.outtext.GetValue()
            self.ClearText() #outtext.Clear()

        elif item == "Undo Clear":
            if not self.orgtext:
                lib.MessageBoxOK("Unable to undo","")
                return
            self.outtext.AppendText(self.orgtext)
            self.orgtext=None

        elif item == "Copy selected": self.outtext.Copy()

        elif item == "Paste": # does not work in READ_ONL+Y mode!
            self.outtext.Paste()

        elif item == "Plot(line)": self.InputDataAndPlot('line')

        elif item == "Plot(bar)": self.InputDataAndPlot('bar')

        elif item == "Execute program":
            jobid="test"; prg=[],arg=[],plt=True; pdir=""; oputfile=""
            print('read program and command. currently, input in the display does not work.')
            self.ExecuteProgram(jobid,prg,arg,plt,pdir,outfile)

        elif item == "List waiting jobs": self.ListWaitingJobs()

        elif item == "Cancel waiting jobs": self.ClearJobQueue()

        elif item == "Kill": self.KillProcess()

        elif item == "Setting":
            pass # write program on file
        elif item == "Document":
            self.HelpDocument()

    def HelpDocument(self):
        """ Document of ExecProg_Frm """
        helpname = 'ExecProg_Frm'
        self.model.helpctrl.Help(helpname)

    def OnFind(self,event):
        self.fndstr=self.finddata.GetFindString()
        self.line=0

    def OnFindNext(self,event):
        nstr=len(self.fndstr)
        nline=self.outtext.GetNumberOfLines()
        preline=self.line
        for i in range(self.line,nline):
            text=self.outtext.GetLineText(i)
            colmn=text.find(self.fndstr)
            if colmn >= 0:
                ipos=self.outtext.XYToPosition(colmn,i)
                self.outtext.SetSelection(ipos,ipos+nstr)
                self.outtext.ShowPosition(ipos)
                self.line=i+1
                break
            else:
                if i == nline-1: self.line=0

    def OnFindClose(self,event):
        self.fnddlg.Destroy()

    def MenuItems(self):
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        submenu.Append(-1,"Save log as","Save current data on file")
        submenu.AppendSeparator()
        iid=wx.NewId()
        submenu.Append(iid,"Output on display","Display output",
                       kind=wx.ITEM_CHECK)
        submenu.Check(iid,True)
        submenu.AppendSeparator()
        submenu.Append(-1,"Load output file","Resore output file from file")
        submenu.Append(-1,"View output file","Open output file for view")
        submenu.AppendSeparator()
        submenu.Append(-1,"Read output file","Read output file in dispaly")
        submenu.AppendSeparator()

        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Background color","Change background color")
        subsubmenu.Append(-1,"Text color","Change background color")
        #submenu.AppendMenu(-1,"Change color",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,'Change color',subsubmenu)
        submenu.AppendSeparator()
        submenu.Append(-1,"Close","Close")
        menubar.Append(submenu,"File")
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Select all","Select all")
        submenu.AppendSeparator()
        submenu.Append(-1,"Find","Find strings")
        submenu.Append(-1,"Replace","Replace strings")
        submenu.AppendSeparator()
        submenu.Append(-1,"Pickup lines","Pickup lines with string")
        submenu.Append(-1,"Remove lines","Remove lines")
        submenu.Append(-1,"Pickup lines between","Pickup line between lines")
        submenu.Append(-1,"Restore all lines","Restore all text")
        submenu.AppendSeparator()
        submenu.Append(-1,"Add line numbers","Show lione number")
        submenu.Append(-1,"Remove line numbers","Remove lione number")
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear","Clear all text")
        submenu.Append(-1,"Undo Clear","Undo clear")
        submenu.AppendSeparator()
        submenu.Append(-1,"Copy selected","Copy selcted to clipboad")
        submenu.Append(-1,"Paste","Paste data in clipboard")

        menubar.Append(submenu,"Edit")
        # Plot
        submenu=wx.Menu()
        submenu.Append(-1,"Plot(line)","Plot selected data")
        submenu.Append(-1,"Plot(bar)","Plot selected data")
        menubar.Append(submenu,"Plot")

        # Exec
        #submenu=wx.Menu()
        #submenu.Append(-1,"Execute program","")
        #menubar.Append(submenu,"Execute")
        # Status
        submenu=wx.Menu()
        submenu.Append(-1,"List waiting jobs")
        submenu.Append(-1,"Cancel waiting jobs","Cancel waiting jobs")
        menubar.Append(submenu,"Status")
        # Kill
        submenu=wx.Menu()
        submenu.Append(-1,"Kill","Kill process")
        menubar.Append(submenu,"Kill")
        # Setting
        #submenu=wx.Menu()
        #submenu.Append(-1,"Set prgram path and arg","Set prgram path")
        #menubar.Append(submenu,"Setting")
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,"Document",'Help document')
        menubar.Append(submenu,"Help")

        return menubar

class Message_Frm(wx.MiniFrame):
    """ Display message in wx.StaticText """
    def __init__(self,parent,id,winpos=[],winsize=[],winlabel='',message=''):
        title='Message panel'
        if len(winpos) <= 0:
            parpos=parent.GetPosition()
            parsize=parent.GetSize()
            winpos=[parpos[0]+100,parpos[1]+100]
        if len(winsize) <= 0: winsize=[250,100]
        winpos  = lib.SetWinPos(winpos)
        wx.MiniFrame.__init__(self,parent,id,title=title,pos=winpos,\
                              size=winsize,\
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|\
               wx.RESIZE_BORDER|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.bgcolor='white' #[255,208,255] #'light gray'
        self.fgcolor='blue'
        #self.size=winsize
        #self.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.winlabel=winlabel
        self.message=message
        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Show()

    def CreatePanel(self):
        #w=self.size[0]; h=self.size[1]
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=(0,0),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor)
        yloc=5
        #wx.StaticText(self.panel,-1,"Input, name=3-1-2..., \nor cat seleced (or all)",pos=(10,yloc),size=(w-10,46))
        self.text=wx.StaticText(self.panel,-1,self.message,pos=(10,yloc),
                                size=(w-20,h-10))
        self.text.SetForegroundColour(self.fgcolor)
        self.text.Refresh()

    def SetMessage(self,message):
        self.message=message
        self.text.SetLabel(self.message)
        self.text.SetForegroundColour(self.fgcolor)
        self.text.Refresh()

    def Clear(self):
        self.text.SetLabel('')

    def OnClose(self,event):
        self.Destroy()

class MessageBox_Frm(wx.Dialog):
    """ Display warning message in wx.StaticText """
    def __init__(self,parent=None,title='',winpos=[],winsize=[],winlabel='',
                 message='',model=None,retmethod=None,boxname='',
                 boxkind='Warning'):
        # set font
        self.font=lib.GetFont(5); self.font.SetPixelSize([7,13])
        if len(winsize) <= 0:
            winsize=self.ComputeWinSize(message)
            winsize=lib.WinSize(winsize)
        if len(winpos) <= 0: winpos=self.ComputeWinPos(parent)
        winpos  = lib.SetWinPos(winpos)
        if len(title) <= 0: title='Message panel'
        wx.Dialog.__init__(self,parent,-1,title=title,pos=winpos,
                              size=winsize) #,style=wx.STAY_ON_TOP)
        self.parent=parent
        self.model=model
        if self.model is None: self.model=const.MDLWIN.model
        self.retmethod=retmethod
        self.bgcolor0=[253,255,206] #'yellow' #'white' #upper panel
        self.bgcolor1='light gray' # lower panel
        self.title=title
        self.winlabel=winlabel
        self.message=message
        self.SetFont(self.font)
        self.boxname = boxname
        self.boxkind = 'Warning'
        if boxname != '': self.boxkind = 'Info'
        # warning icon
        """
        icondir=self.model.setctrl.GetDir('Icons')
        GetIconBmp(self,name,imgfrm='.png')
        warnpng=os.path.join(icondir,'warning.png')

        self.warnbmp=wx.Bitmap(warnpng,wx.BITMAP_TYPE_ANY)
        """
        self.warnbmp=self.model.setctrl.GetIconBmp('warning',imgfrm='.png')
        #
        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Show()
        #self.ShowModal()

    def ComputeWinSize(self,message):
        def yvalue(nmess,wfont,x):
            y=(nmess*wfont+20)/x+1
            return y
        xmin=300; ymin=250; ymax=400
        nmess=len(message)
        wfont,hfont=self.font.GetPixelSize()
        x=xmin
        y=yvalue(nmess,wfont,x)
        if y > ymax:
            x=400; y=yvalue(nmess,wfont,x)
        elif y < ymin: y=ymin
        winsize=[x,y]
        return winsize

    def ComputeWinPos(self,parent):
        if parent is None:
            return [-1,-1]
        else:
            parpos=parent.GetPosition()
            parsize=parent.GetSize()
            winpos=[parpos[0]+parsize[0]/2,parpos[1]+90]
            return winpos

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor0)
        yloc=30; xloc=40
        wx.StaticBitmap(self.panel,-1,self.warnbmp,pos=(xloc,10),size=(50,50))
        wx.StaticText(self.panel,-1,self.boxkind+":",pos=(xloc+80,yloc),size=(50,30))
        yloc=80; height=h-yloc-90
        # message
        self.text=wx.StaticText(self.panel,-1,'',pos=(10,yloc),
                                size=(w-20,height),style=wx.ST_NO_AUTORESIZE) #size=(w-20,height))
        self.SetMessage(self.message,w-20)
        # OK button
        yloc=h-80
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),
                      style=wx.LI_HORIZONTAL)
        yloc += 8; xloc=w/2-30; hpan=h-yloc
        #self.panbtn=wx.Panel(self,-1,pos=(0,ylocpanbtn),size=(w,hpan))
        #self.panbtn.SetBackgroundColour(self.bgcolor1)
        btnok=wx.Button(self.panel,-1,"OK",pos=(xloc,yloc),size=(60,25))
        btnok.Bind(wx.EVT_BUTTON,self.OnOK)
        yloc += 25
        self.ckbnot=wx.CheckBox(self.panel,-1,
                                "Do not show the panel hereafter.",
                                pos=(10,yloc),size=(250,20))
        yloc += 25
        mess='To revive, "File"->"Enable MessageBox".'
        sttxt=wx.StaticText(self.panel,-1,mess,pos=(10,yloc),size=(w-15,18))

    def SetMessage(self,message,width):
        import textwrap
        wfont,hfont=self.font.GetPixelSize()
        ns=width/wfont
        lst=textwrap.wrap(message,ns)
        mess='\n'.join(lst)
        self.text.SetLabel(mess)

    def OnOK(self,event):
        value=self.ckbnot.GetValue()
        if self.retmethod is not None:
            text=''
            try: self.retmethod(self.title,value)
            except: pass
        
        if self.boxname == "messbox_MMMinimizer":
            try: const.SETCTRL.SetParam(self.boxname,not(value))
            except: pass
        else:
            try: const.SETCTRL.SetMessageBoxFlag('',not(value))
            except: pass
        
        self.OnClose(1)

    def Clear(self):
        self.text.SetLabel('')

    def SetBgColor(self,color):
        self.bgcolor=color
        self.panel.SetBackgroundColour(self.bgcolor)

    def OnClose(self,event):
        #self.EndModal(0)
        self.Destroy()

    def Close(self):
        self.OnClose(1)

class TextInput_Frm(wx.MiniFrame):
    def __init__(self,parent,id,winpos,winsize,winlabel,comment,retmethod,
                 title='Text inputer'):
        if len(winsize) <= 0: winsize=[240,120]
        winsize=lib.WinSize(winsize,False)
        winpos  = lib.SetWinPos(winpos)
        wx.MiniFrame.__init__(self,parent,id,title=title,pos=winpos,size=winsize, #style=wx.CAPTION|wx.CLOSE_BOX) #wx.MINIMIZE_BOX ) #,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER) #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.bgcolor='light gray'
        self.size=winsize
        #self.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.winlabel=winlabel
        self.retmethod=retmethod
        self.comment=comment

        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreatePanel(self):
        self.size=self.GetClientSize()
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor)
        yloc=5
        #wx.StaticText(self.panel,-1,"Input, name=3-1-2..., \nor cat seleced (or all)",pos=(10,yloc),size=(w-10,46))
        wx.StaticText(self.panel,-1,self.comment,pos=(10,yloc),size=(w-20,46))
        yloc += 35
        self.tcinp=wx.TextCtrl(self.panel,-1,'',pos=(10,yloc),size=(w-20,22),
                               style=wx.TE_PROCESS_ENTER)
        self.tcinp.Bind(wx.EVT_TEXT_ENTER,self.OnTextEnter)
        #yloc += 30
        yloc=h-35
        xloc=w/2
        btcan=wx.Button(self.panel,-1,"Clear",pos=(xloc-90,yloc),size=(55,20))
        btcan.Bind(wx.EVT_BUTTON,self.OnClear)
        self.btapl=wx.Button(self.panel,-1,"Apply",pos=(xloc-20,yloc),size=(55,20))
        self.btapl.Bind(wx.EVT_BUTTON,self.OnApply)
        self.btcls=wx.Button(self.panel,-1,"OK",pos=(xloc+50,yloc),size=(35,20))
        self.btcls.Bind(wx.EVT_BUTTON,self.OnClose)

    def OnClear(self,event):
        self.tcinp.SetValue('')

    def OnTextEnter(self,event):
        self.OnClose(0)

    def OnClose(self,event):
        self.OnApply(0)
        self.parent.opendrvpan=False
        self.Destroy()

    def OnApply(self,event):
        #
        inputtext=self.tcinp.GetValue()
        self.retmethod(self.winlabel,inputtext)
        #

    def GetDerivedData(self):
        return self.drvtxt,self.drvnam,self.drvcmp

class DeriveDataInputX_Frm(wx.Frame):
    def __init__(self,parent,id,pos,winsize):
        wx.Frame.__init__(self,parent,id,pos=pos,size=winsize,style=wx.MINIMIZE_BOX ) #,
        #       style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.bgcolor='light gray'
        #
        self.size=winsize
        #self.Bind(wx.EVT_PAINT,self.OnPaint)
        #self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.drvtxt=''; self.drvnam=''; self.drvcmp=[]

        self.CreatePanel()

    def CreatePanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor)
        yloc=8
        wx.StaticText(self.panel,-1,"Input like, name=3-1-2...",pos=(10,yloc),size=(w-10,18))

        self.tcinp=wx.TextCtrl(self.panel,-1,'',pos=(10,yloc+20),size=(w-20,20),
                               style=wx.TE_PROCESS_ENTER)
        self.tcinp.Bind(wx.EVT_TEXT_ENTER,self.OnTextEnter)
        yloc=yloc+45
        xloc=w/2
        btcan=wx.Button(self.panel,wx.ID_ANY,"Cancel",pos=(xloc-50,yloc),size=(45,20))
        btcan.Bind(wx.EVT_BUTTON,self.OnCancel)
        self.btapl=wx.Button(self.panel,wx.ID_ANY,"Apply",pos=(xloc+10,yloc),size=(45,20))
        self.btapl.Bind(wx.EVT_BUTTON,self.OnApply)

    def OnCancel(self,event):
        self.tcinp.SetValue('')

    def OnTextEnter(self,event):
        self.OnApply(0)

    def OnApply(self,event):
        #
        inpt=self.tcinp.GetValue()
        #
        if len(inpt) <= 0: return
        drvtxt=inpt
        nc=inpt.find('=')
        if nc <= 0:
            lib.MessageBoxOK("No name. Try again. %s" % inpt,"")

            return
        drvnam=inpt[:nc]
        cmptxt=inpt[nc+1:]
        txt=''
        if cmptxt[0] != '-' or cmptxt != '+': cmptxt='+'+cmptxt
        #
        for i in range(len(cmptxt)):

            s=cmptxt[i]
            if s == ' ':continue
            if s == '-' or s == '+':
                txt=txt+' '+s
            else: txt=txt+s
        #
        cmpo=txt.split(' ')
        for sc in cmpo:
            if sc == '': continue
            sc.strip()
            drvcmp.append(sc)
        #
        if len(drvcmp[0]) <= 0:
            lib.MessageBoxOK("No components. Try again. %s" % inpt,"")

        # check data
        for s in drvcmp:
            try: s=int(s)
            except:
                lib.MessageBoxOK("Wrong input. %s" % inpt,"")

                drvtxt=''; drvnam=''; drvcmp=[]
                break
        if drvnam == '':
            return
        #
        self.parent.AddDrvativeData(drvnam,drvtxt)

    def GetDerivedData(self):
        return self.drvtxt,self.drvnam,self.drvcmp

class OpenMultipleFile_Frm(wx.Frame):
    def __init__(self,parent,id,form,directory,filterlist,namecnv):
        # directory: 'e:/', filter: ['*.*',....], namecnv:0.1,1,2,3e
        # form: 0: dir and files panels, 1:dir,files, and select panels
        # namecnv(name convention selection option):
        #    0=no,1=files with same basename, 2:files with same basename elements,3:both 2 and 3
        # usage: filopn=Openfile(1,directory,filter list, 1)
        self.title = "Open Multiple Files"
        winsize=lib.WinSize([510,360])
        if form == 0: winsize=lib.WinSize([340,360])
        wx.Frame.__init__(self,parent,id,title=self.title,size=winsize,
                          style=wx.SYSTEM_MENU|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.CAPTION \
                          |wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.size=self.GetClientSize()
        self.bgcolor='light gray'
        #
        self.form=form
        if form > 1 or form < 0: self.form=0
        self.npan=3
        if form == 0: self.npan=2

        if directory == None: self.directory=os.getcwd()
        #
        self.curdir=directory
        #
        self.openfiles=[]
        #
        self.filterlist=filterlist
        if len(filterlist) <= 0: self.filterlist=['*.* (all)']
        self.filter=self.filterlist[0]
        self.extdic=self.GetFileExt(self.filter)
        self.namecnv=namecnv
        if namecnv < 0 or namecnv > 3: self.namecnv=0

        self.CreateOpenFilePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)

    def CreateOpenFilePanel(self):
        #
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor)
        # Widget position and size
        hrem=24; hcmd=50; hcb=const.HCBOX
        self.wlc1=int((w-10)/self.npan)
        self.wlc2=self.wlc1; self.wlc3=self.wlc1
        self.hlc1=h-hrem; self.hlc2=h-hrem-hcmd; self.hlc3=h-hrem-hcmd
        xlc1=5; xlc2=xlc1+self.wlc1; xlc3=xlc2+self.wlc2
        xlc1c=xlc1+(self.wlc1)/2; xlc2c=xlc2+(self.wlc2)/2; xlc3c=xlc3+(self.wlc3)/2
        # remarks
        yloc=4
        wx.StaticText(self.panel,wx.ID_ANY,'Directory:',pos=(xlc1c-25,yloc),size=(50,20))
        wx.StaticText(self.panel,wx.ID_ANY,'Files',pos=(xlc2c+10-25,yloc),size=(50,20))
        if self.form == 1:
            wx.StaticText(self.panel,wx.ID_ANY,'Selected',pos=(xlc3c-25,yloc),size=(50,20))
        # list controls, directory, files, and seleced (optionally)
        self.lc1=wx.ListCtrl(self.panel,-1,pos=(-1,hrem),size=(self.wlc1,self.hlc1))
        self.lc2=wx.ListCtrl(self.panel,-1,pos=(self.wlc1+5,hrem),size=(self.wlc2,self.hlc2),
                             style=wx.SB_VERTICAL|wx.LC_SORT_ASCENDING) #wx.LC_LIST|wx.SB_VERTICAL)
        #self.lc2.Bind(wx.EVT_LIST_ITEM_LEFT_CLICK,self.OnFileSelect)
        self.lc2.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnFileSelect)
        #self.lc2.Bind(wx.EVT_LIST_ITEM_ACTIVATED,(id, func) #double click or enter
        self.lc2.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.OnDeleteFile)


        if self.form == 1:
            self.lc3=wx.ListCtrl(self.panel,-1,pos=(self.wlc1+self.wlc2+10,hrem),size=(self.wlc3,self.hlc3),
                                 style=wx.SB_VERTICAL|wx.LC_SORT_ASCENDING) #wx.LC_LIST)
            self.lc3.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.OnRemoveFile)
        self.dirctrl=wx.GenericDirCtrl(self.lc1,-1,pos=(-1,-1),size=(self.wlc1,h-hrem),
                                   dir=self.curdir,filter="",style=wx.DIRCTRL_DIR_ONLY)
        self.tree=self.dirctrl.GetTreeCtrl()
        self.panel.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnDirSelect,id=self.tree.GetId())
        self.ListDirInlc2()
        # files options
        wcmb=125; hcmb=const.HCBOX #22 #40
        yloc=self.hlc2+30
        xfil=xlc2c-(30+wcmb)/2
        st1=wx.StaticText(self.panel,-1,"Filter:",pos=(xfil,yloc),size=(30,18))
        st1.SetForegroundColour("black")
        self.cmbfil=wx.ComboBox(self.panel,-1,'',choices=self.filterlist, \
                               pos=(xfil+32,yloc-2), size=(wcmb,hcmb),style=wx.CB_READONLY)
        self.cmbfil.Bind(wx.EVT_COMBOBOX,self.OnFilter)
        self.cmbfil.SetStringSelection(self.filter)
        yloc=yloc+22
        self.ckbnam=wx.CheckBox(self.panel,-1,"Name convention",pos=(xlc2c-60,yloc),size=(120,18))
        self.ckbnam.Bind(wx.EVT_CHECKBOX,self.OnNameConvention)
        if self.namecnv == True:
            self.ckbnam.SetValue(self.namecnv)
        else: self.ckbnam.Disable()
        # select commands
        if self.form == 1:
            xopn=xlc3c; yloc=self.hlc2+30
            wx.StaticLine(self.panel,pos=(xlc3-1,yloc-8),size=(8,hcmd+5),style=wx.LI_VERTICAL)
            st2=wx.StaticText(self.panel,-1,"Select:",pos=(xopn-65,yloc),size=(40,18))
            self.btall=wx.Button(self.panel,wx.ID_ANY,"All",pos=(xopn-22,yloc-2),size=(50,20))
            self.btall.Bind(wx.EVT_BUTTON,self.OnSelectAll)
            self.btclr=wx.Button(self.panel,wx.ID_ANY,"Clear",pos=(xopn+32,yloc-2),size=(50,20))
            self.btclr.Bind(wx.EVT_BUTTON,self.OnSelectClear)
            #btok=wx.Button(self.panel,wx.ID_ANY,"OK",pos=(xopn-55,yloc+20),size=(30,20))
            #btok.Bind(wx.EVT_BUTTON,self.OnOpenOK)
            btcan=wx.Button(self.panel,wx.ID_ANY,"Cancel",pos=(xopn-45,yloc+20),size=(45,20))
            btcan.Bind(wx.EVT_BUTTON,self.OnOpenCancel)
            self.btapl=wx.Button(self.panel,wx.ID_ANY,"Open",pos=(xopn+10,yloc+20),size=(45,20))
            self.btapl.Bind(wx.EVT_BUTTON,self.OnOpenApply)

    def OnDeleteFile(self,event):
        # delete file...not completed.
        item=self.lc2.GetFirstSelected()
        path=self.lc2.GetItemText(item)

    def OnRemoveFile(self,event):
        # remove file in selected files
        item=self.lc3.GetFirstSelected()
        self.lc3.DeleteItem(item)
        selnamedic,selbasedic,selelemdic=self.MakeStringItemDic(self.lc3)
        self.lc3.ClearAll()
        lst=list(selnamedic.keys())
        lst.sort()
        for i in range(len(lst)):
            if lst[i][0] != '.':
                self.lc3.InsertStringItem(0,lst[i])

    def GetFileExt(self,filtr):
        extdic={}
        #ext=self.cmbfil.GetStringSelection()
        np=filtr.find('(')
        ext=filtr[:np]
        extlst=ext.split(',')
        for i in range(len(extlst)):
            ext=extlst[i].strip()
            if ext != '*.*': ext=ext[1:]
            extdic[ext]=1

        return extdic

    def OnFileSelect(self,event):
        # select file'
        extlst=list(self.extdic.keys())
        filnamedic,filbasedic,filelemdic=self.MakeStringItemDic(self.lc2)
        # make file name dictionary in selected files
        selnamedic,selbasedic,selelemdic=self.MakeStringItemDic(self.lc3)
        self.lc3.ClearAll()
        # get selected item list in Files panel
        item=-1
        while 1:
            item=self.lc2.GetNextItem(item,wx.LIST_NEXT_ALL,wx.LIST_STATE_SELECTED)
            if item == -1: break
            fil=self.lc2.GetItemText(item)
            selnamedic[fil]=1
            if self.namecnv > 0:
                base=os.path.basename(fil)
                base=os.path.splitext(base)[0]
                if self.namecnv == 1 or self.namecnv == 3: # files with commaon basename
                    for s in extlst:
                        if s == '.*': continue
                        fil=base+s
                        if self.IsFile(fil,filnamedic): selnamedic[fil]=1
                if self.namecnv == 2 or self.namecnv == 3:
                    elem=base.split('_')
                    for e in elem:
                        for s in extlst:
                            if s == '.*': continue
                            fil=e+s
                            if self.IsFile(fil,filnamedic): selnamedic[fil]=1
        lst=list(selnamedic.keys())
        self.DispSelectedList(self.lc3,lst)

    def DispSelectedList(self,lc,lst):
        lc.ClearAll()
        lst.sort()
        for i in range(len(lst)):
            if lst[i][0] != '.':
                lc.InsertStringItem(0,lst[i])

    def IsFile(self,name,dic):
        if name in dic: return True
        else: return False

    def MakeStringItemDic(self,lc):
        # lc: ListCtr instance
        namedic={}; basedic={}; elemdic={}
        item=-1
        while 1:
            item=lc.GetNextItem(item,wx.LIST_NEXT_ALL,wx.LIST_STATE_DONTCARE)
            if item == -1: break
            fil=lc.GetItemText(item)
            namedic[fil]=1
            base=os.path.basename(fil)
            basedic[base]=1
            elem=base.split('_')
            for s in elem:
                elemdic[s]=1

        return namedic,basedic,elemdic

    def OnSelectAll(self,event):
        selnamedic,selbasedic,selelemdic=self.MakeStringItemDic(self.lc2)
        lst=list(selnamedic.keys())
        self.DispSelectedList(self.lc3,lst)

    def OnSelectClear(self,event):
        # clear all selected
        self.lc3.ClearAll()

    def OnOpenCancel(self,event):
        self.lc3.ClearAll()
        curdir=''; openfiles=[]
        self.parent.SetOpenFiles(curdir,openfiles)

    def OnOpenApply(self,event):
        selnamedic,selbasedic,selelemdic=self.MakeStringItemDic(self.lc3)
        self.openfiles=list(selnamedic.keys())
        if len(self.openfiles) <= 0:
            lib.MessageBoxOK("No files selected for open.","")

        else:
            self.curdir=os.path.realpath(self.curdir)
            self.parent.GetOpenFiles(self.curdir,self.openfiles)
        self.Destroy()

    def OnOpenOK(self,event):
        self.OnOpenApply(0)
        self.Destroy()

    def OnFilter(self,event):
        self.filter=self.cmbfil.GetStringSelection()
        self.extdic=self.GetFileExt(self.filter)
        self.DirSelect()

    def OnNameConvention(self,event):
        self.namecnv=self.ckbnam.GetValue()

    def OnDirSelect(self,event):
        self.DirSelect()

    def DirSelect(self):
        if self.form == 1: self.lc3.ClearAll()
        item=self.tree.GetSelections()
        direct=self.tree.GetItemText(item[0])
        self.curdir=self.dirctrl.GetPath()
        os.chdir(self.curdir) #("..")

        self.ListDirInlc2()

    def ListDirInlc2(self):
        try:
            lst=os.listdir(self.dirctrl.GetPath())
            self.lc2.ClearAll()
            #if self.form == 1: self.lc3.ClearAll()
            for i in range(len(lst)):
                ext=os.path.splitext(lst[i])[1]
                if '*.*' not in self.extdic and ext not in self.extdic: continue
                if lst[i][0] != '.':
                    self.lc2.InsertStringItem(0,lst[i])
        except: pass

    def OnSize(self, event):
        self.panel.Destroy()
        self.size=self.GetClientSize()
        self.CreateOpenFilePanel()

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        self.Destroy()


class SelectData_Frm(wx.Frame):
    def __init__(self,parent,ID,title,itemname,model,ctrlflag,winpos):
        #title = "Join Molecule Choice"
        winsize=lib.WinSize((400,260))
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent,ID,title,size=winsize,pos=winpos, #(300,300),
                style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
                #style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU |wx.CAPTION | wx.CLOSE_BOX)
        self.parent=parent
        self.model=model
        self.winctrl=model.winctrl
        self.ctrlflag=ctrlflag
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.itemname=itemname
        self.itemlst=[]
        self.sellst=[]
        self.size=self.GetClientSize()
        #self.SetTitle('Join ['+molnam+']')
        #w=self.size[0]; h=self.size[1]
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.CreateSelectPanel()

    def CreateSelectPanel(self):
        w=self.size[0]; h=self.size[1]
        self.panjoin=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panjoin.SetBackgroundColour("light gray")
        plx2=(w-40)/2+25; plw=(w-20)/2; plh=h-55 #-95
        wx.StaticText(self.panjoin,wx.ID_ANY,self.itemname,pos=(20,5),size=(plw-20,20))
        wx.StaticText(self.panjoin,wx.ID_ANY,'Choosen',pos=(plx2+35,5),size=(50,20))

        self.lbxitm = wx.ListBox(self.panjoin,wx.ID_ANY,choices=self.itemlst,style=wx.LB_EXTENDED,
                               pos=(5,25),size=(plw,plh))
        lbxsel = wx.ListBox(self.panjoin,wx.ID_ANY,choices=self.sellst,style=wx.LB_SINGLE, #wx.LB_EXTENDED,
                               pos=(plx2,25),size=(plw,plh-30)) # -60
        self.lbxitm.Bind(wx.EVT_LISTBOX,self.LBX1Sel)
        lbxsel.Bind(wx.EVT_LISTBOX,self.LBX2Selected)

        bx1=plw/2-22; bx2=1.5*plw
        bt11=wx.Button(self.panjoin,wx.ID_ANY,"Choose all",pos=(bx1-40,plh+30),size=(65,20))
        bt11.Bind(wx.EVT_BUTTON,self.JoinBTSel)
        bt12=wx.Button(self.panjoin,wx.ID_ANY,"Choose",pos=(bx1+40,plh+30),size=(45,20))
        bt12.Bind(wx.EVT_BUTTON,self.JoinBTSelAll)

        lin1=wx.StaticLine(self.panjoin,pos=(plw+8,-1),size=(2,h),style=wx.LI_VERTICAL)
        bt2=wx.Button(self.panjoin,wx.ID_ANY,"Up",pos=(bx2-55,plh),size=(35,20))
        bt2.Bind(wx.EVT_BUTTON,self.ClickUpButton)
        bt3=wx.Button(self.panjoin,wx.ID_ANY,"Down",pos=(bx2-2,plh),size=(38,20))
        bt3.Bind(wx.EVT_BUTTON,self.ClickDownButton)
        bt4=wx.Button(self.panjoin,wx.ID_ANY,"Del",pos=(bx2+55,plh),size=(35,20))
        bt4.Bind(wx.EVT_BUTTON,self.ClickDelButton)

        wx.StaticLine(self.panjoin,pos=(w/2,plh+25),size=(plw+22,2),style=wx.LI_HORIZONTAL)
        #self.jintcl1=wx.TextCtrl(self.panjoin,-1,"name here",pos=(plx2,plh+4),
        #                         size=(plw,22))
        bt5=wx.Button(self.panjoin,wx.ID_ANY,"Apply",pos=(bx2-30,plh+30),size=(52,20))
        bt5.Bind(wx.EVT_BUTTON,self.OnApply)
        btnok=wx.Button(self.panjoin,wx.ID_ANY,"OK",pos=(bx2+30,plh+30),size=(30,20))
        btnok.Bind(wx.EVT_BUTTON,self.OnOK)

    def SetItemList(self,itemlst):
        self.itemlst=itemlst
        self.lbxitm.Set(self.itemlst)

    def OnApply(self,event):
        pass
    def OnOK(self,event):
        self.OnApply(1)
        self.Destroy()

    def JoinBTSelAll(self,event):
        print('joinBTselall')
    def JoinBTSel(self,event):
        print('joinBTsel')
    def JoinRBGroup(self,event):
        print('join rb group')
    def JoinRBMolecule(self,event):
        print('join rb molecule')

    def ClickSelButton(self,event):
        print('clicked sel button')
    def ClickDelButton(self,event):
        print('clicked del button')
    def ClickUpButton(self,event):
        print('clicked up button')
    def ClickDownButton(self,event):
        print('clicked down button')

    def ClickApplyButton(self,event):
        print('clicked apply button')
    def ClickOKButton(self,event):
        self.winctrl.Set('SelGmsInpWin',False)
        self.Destroy()

    def ClickCancelButton(self,event):
        print('clicked cancel button')

    def listbox_select(self,event):
        obj = event.GetEventObject()

    def LBX1Sel(self,event):
        print('lbx1sel')
    def LBX2Selected(self,event):
        print('lbx2sel')

    def OnSize(self, event):
        self.panjoin.Destroy()
        self.size=self.GetClientSize()
        self.CreateSelectPanel()

    def OnClose(self,event):
        print('join sel  onclose')
        self.winctrl.Close('SelGmsInpWin')
        self.Destroy()

class GroupJoin_Frm(wx.Frame):
    def __init__(self, parent, ID, model): #, ctrlflag, molnam):
        self.title = "Join Molecule Choice"
        winsize=lib.WinSize((300,260))
        wx.Frame.__init__(self, parent, ID, self.title, size=winsize, #(300,300),
                style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
                #style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU |wx.CAPTION | wx.CLOSE_BOX)
        self.parent=parent
        self.mdlwin=parent
        self.model=model
        self.winctrl=model.winctrl
        #xxself.ctrlflag=model.ctrlflag
        molnam=model.mol.name #wrkmolnam
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        #
        self.mollst=model.molnam
        self.sellst=[]
        self.size=self.GetClientSize()
        self.SetTitle('Join ['+molnam+']')
        #w=self.size[0]; h=self.size[1]
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.CreateJoinPanel()

    def CreateJoinPanel(self):
        w=self.size[0]; h=self.size[1]
        self.panjoin=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panjoin.SetBackgroundColour("light gray")
        #element_array = ("element_1","element_2","element_4","element_3","element_5")
        plx2=(w-40)/2+25; plw=(w-20)/2; plh=h-55 #-95
        #st1=wx.StaticText(self.panjoin,wx.ID_ANY,text1,pos=(10,5),size=(55,20))
        self.jinrbt1=wx.RadioButton(self.panjoin,wx.ID_ANY,'Group',pos=(5,5))
        self.jinrbt2=wx.RadioButton(self.panjoin,wx.ID_ANY,'Molecule',pos=(60,5))
        self.jinrbt1.Bind(wx.EVT_RADIOBUTTON,self.JoinRBGroup)
        self.jinrbt2.Bind(wx.EVT_RADIOBUTTON,self.JoinRBMolecule)
        self.jinrbt1.SetValue(True)
        st1=wx.StaticText(self.panjoin,wx.ID_ANY,'Choosen',pos=(plx2+35,5),size=(50,20))

        lbx1 = wx.ListBox(self.panjoin,wx.ID_ANY,choices=self.mollst,style=wx.LB_EXTENDED,
                               pos=(5,25),size=(plw,plh))
        lbx2 = wx.ListBox(self.panjoin,wx.ID_ANY,choices=self.sellst,style=wx.LB_SINGLE, #wx.LB_EXTENDED,
                               pos=(plx2,25),size=(plw,plh-60))
        lbx1.Bind(wx.EVT_LISTBOX,self.LBX1Sel)
        lbx2.Bind(wx.EVT_LISTBOX,self.LBX2Selected)

        bx1=plw/2-22; bx2=1.5*plw
        bt11=wx.Button(self.panjoin,wx.ID_ANY,"Choose all",pos=(bx1-28,plh+30),size=(60,20))
        bt11.Bind(wx.EVT_BUTTON,self.JoinBTSel)
        bt12=wx.Button(self.panjoin,wx.ID_ANY,"Choose",pos=(bx1+40,plh+30),size=(45,20))
        bt12.Bind(wx.EVT_BUTTON,self.JoinBTSelAll)

        lin1=wx.StaticLine(self.panjoin,pos=(plw+8,-1),size=(2,h),style=wx.LI_VERTICAL)
        bt2=wx.Button(self.panjoin,wx.ID_ANY,"Up",pos=(bx2-40,plh-30),size=(35,20))
        bt2.Bind(wx.EVT_BUTTON,self.ClickUpButton)
        bt3=wx.Button(self.panjoin,wx.ID_ANY,"Down",pos=(bx2-2,plh-30),size=(38,20))
        bt3.Bind(wx.EVT_BUTTON,self.ClickDownButton)
        bt4=wx.Button(self.panjoin,wx.ID_ANY,"Del",pos=(bx2+40,plh-30),size=(35,20))
        bt4.Bind(wx.EVT_BUTTON,self.ClickDelButton)
        lin2=wx.StaticLine(self.panjoin,pos=(w/2,plh-3),size=(plw+22,2),style=wx.LI_HORIZONTAL)
        self.jintcl1=wx.TextCtrl(self.panjoin,-1,"name here",pos=(plx2,plh+4),
                                 size=(plw,22))
        bt5=wx.Button(self.panjoin,wx.ID_ANY,"Create",pos=(bx2-10,plh+30),size=(52,20))
        bt5.Bind(wx.EVT_BUTTON,self.ClickDelButton)
        #self.jintcl1.Disable()

    def JoinBTSelAll(self,event):
        print('joinBTselall')
    def JoinBTSel(self,event):
        print('joinBTsel')
    def JoinRBGroup(self,event):
        print('join rb group')
    def JoinRBMolecule(self,event):
        print('join rb molecule')

    def ClickSelButton(self,event):
        print('clicked sel button')
    def ClickDelButton(self,event):
        print('clicked del button')
    def ClickUpButton(self,event):
        print('clicked up button')
    def ClickDownButton(self,event):
        print('clicked down button')

    def ClickApplyButton(self,event):
        print('clicked apply button')
    def ClickOKButton(self,event):
        self.winctrl.Set('RenameGrpWin',False)
        self.Destroy()

    def ClickCancelButton(self,event):
        print('clicked cancel button')

    def listbox_select(self,event):
        obj = event.GetEventObject()

    def LBX1Sel(self,event):
        print('lbx1sel')
    def LBX2Selected(self,event):
        print('lbx2sel')

    def OnSize(self, event):
        self.panjoin.Destroy()
        self.size=self.GetClientSize()
        self.CreateJoinPanel()

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        self.winctrl.Close('JoinGrpWin')
        self.Destroy()

class GroupRename_Frm(wx.Frame):
    def __init__(self, parent, ID,model): #,ctrlflag,molnam):
        self.title = "Ren/Rmv "
        winsize=lib.WinSize((160,260)) #(300,260)
        wx.Frame.__init__(self, parent, ID, self.title, size=winsize, #(300,300),
                style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
                #style=wx.MINIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU |wx.CAPTION | wx.CLOSE_BOX)
        self.model=model #parent.model
        self.winctrl=model.winctrl
        #xxself.ctrlflag=model.ctrlflag
        molnam=model.mol.name #wrkmolnam
        #
        self.grpmollst=self.model.molnam
        self.sellst=[]
        self.size=self.GetClientSize()
        self.SetTitle('Ren ['+molnam+']')
        self.winwidth=self.size[0]; self.winminheight=122
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.CreateRenRmvPanel()

    def CreateRenRmvPanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        #
        plx2=(w-40)/2+25; plw=w-5; plh=h-100 #-95
        self.renrbt1=wx.RadioButton(self.panel,wx.ID_ANY,'Group',pos=(5,5))
        self.renrbt2=wx.RadioButton(self.panel,wx.ID_ANY,'Molecule',pos=(65,5))
        self.renrbt1.Bind(wx.EVT_RADIOBUTTON,self.RenRBGroup)
        self.renrbt2.Bind(wx.EVT_RADIOBUTTON,self.RenRBMolecule)
        self.renrbt1.SetValue(True)
        lbx1 = wx.ListBox(self.panel,wx.ID_ANY,choices=self.grpmollst,style=wx.LB_EXTENDED,
                               pos=(5,25),size=(plw-5,plh))
        lbx1.Bind(wx.EVT_LISTBOX,self.RenLBXLst)
        #bx1=plw/2-22; bx2=1.5*plw
        lin=wx.StaticLine(self.panel,pos=(-1,plh+28),size=(w,2),style=wx.LI_HORIZONTAL)
        self.renrbt3=wx.RadioButton(self.panel,wx.ID_ANY,'Rename',pos=(5,plh+33),
                                    style=wx.RB_GROUP)
        self.renrbt4=wx.RadioButton(self.panel,wx.ID_ANY,'Remove',pos=(72,plh+33))
        self.renrbt3.Bind(wx.EVT_RADIOBUTTON,self.RenRBRename)
        self.renrbt4.Bind(wx.EVT_RADIOBUTTON,self.RenRBRemove)
        self.renrbt3.SetValue(True)
        self.rentcl=wx.TextCtrl(self.panel,-1,"new name here",pos=(5,plh+50),
                                 size=(plw-5,22))
        value=self.renrbt3.GetValue()
        if not value: self.rentcl.Disable()
        pbx=w/2
        btok=wx.Button(self.panel,wx.ID_ANY,"OK",pos=(pbx-65,h-22),size=(38,20))
        btok.Bind(wx.EVT_BUTTON,self.OKButton)
        btcn=wx.Button(self.panel,wx.ID_ANY,"Clear",pos=(pbx-22,h-22),size=(42,20))
        btcn.Bind(wx.EVT_BUTTON,self.CancelButton)
        btap=wx.Button(self.panel,wx.ID_ANY,"Apply",pos=(pbx+25,h-22),size=(40,20))
        btap.Bind(wx.EVT_BUTTON,self.ApplyButton)

    def RenRBGroup(self,event):
        print('join rb group')
    def RenRBMolecule(self,event):
        print('join rb molecule')
    def RenRBRename(self,event):
        print('join rb rename')
        self.rentcl.Enable()
    def RenRBRemove(self,event):
        print('join rb remove')
        self.rentcl.Disable()
    def ApplyButton(self,event):
        print('clicked apply button')
    def OKButton(self,event):
        print('clicked close button')
        self.winctrl.Set('RenameGrpWin',False)
        self.Destroy()
    def CancelButton(self,event):
        print('clicked cancel button')

    def listbox_select(self,event):
        obj = event.GetEventObject()

    def RenLBXLst(self,event):
        print('lbx1sel')

    def OnSize(self, event):
        self.panel.Destroy()
        #
        self.CreateRenRmvPanel()
        self.size=self.GetClientSize(); winheight=self.size[1]
        if winheight < self.winminheight: winheight=self.winminheight
        tmp=[]; tmp.append(self.winwidth); tmp.append(winheight)
        self.size=tuple(tmp)
        self.SetClientSize(self.size)

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        self.Destroy()
        self.winctrl.Close('RenameGrpWin')


class TreeSelector_Frm(wx.Frame):
    def __init__(self,parent,iD,model,winpos,winlabel): #,ctrlflag,molnam):
        self.title='Tree Selector'
        winsize=lib.WinSize((160,380),False) # ((160, 600))
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent, iD, self.title, pos=winpos, size=winsize,
                          style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|\
                          wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.winctrl=parent.winctrl
        self.mdlwin=parent
        #xxself.ctrlflag=model.ctrlflag
        self.model=model #parent.model
        self.winlabel=winlabel
        try: self.molnam=self.model.mol.name #wrkmolnam
        except: self.molnam='UNK'
        #self.molnam=parent.wrkmolnam
        self.SetTitle('Tree['+self.molnam+']')
        #
        self.selflg=1
        self.chainitemdic={}
        self.resitemdic={}
        self.atomitemdic={}
        #self.Bind(wx.EVT_SET_FOCUS,self.OnFocus)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.size=self.GetClientSize()
        #
        self.CreateTreeSelPanel()
        #
        ExecProg_Frm.EVT_THREADNOTIFY(self,self.OnNotify)

    def CreateTreeSelPanel(self):
        w=self.size[0]; h=self.size[1]
        self.pantree=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.pantree.SetBackgroundColour('light gray') # ("light gray")
        # Reset button
        btnrset=Reset_Button(self.pantree,-1,self.OnReset)
        yloc=5
        wx.StaticText(self.pantree,-1,"Selection:",pos=(5,yloc),size=(80,18))
        yloc += 20
        self.trrbt1=wx.RadioButton(self.pantree,wx.ID_ANY,'single',
                                   pos=(10,yloc))
        self.trrbt2=wx.RadioButton(self.pantree,wx.ID_ANY,'pile up',
                                   pos=(70,yloc))
        self.trrbt1.Bind(wx.EVT_RADIOBUTTON,self.OnSelSingle)
        self.trrbt2.Bind(wx.EVT_RADIOBUTTON,self.OnSelPileUp)
        self.trrbt1.SetValue(True)
        #wx.StaticLine(self.pantree,pos=(70,0),size=(2,50),style=wx.LI_VERTICAL)
        #trsl1=wx.StaticLine(self.pantree,pos=(-1,yloc+20),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 20
        self.tree = wx.TreeCtrl(self.pantree,1,pos=(-1,yloc),size=(w,h-yloc),
                           style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|\
                           wx.TR_HAS_BUTTONS|wx.TR_MULTIPLE) #|wx.TR_EXTENDED)
        #font=wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
        #             wx.FONTWEIGHT_NORMAL, False, 'Courier 10 Pitch')
        self.saveitems=None
        font=self.GetFont()
        self.tree.SetFont(font)
        self.MakeItemLst()
        self.tree.Expand(self.expanditemid) #self.tree.ExpandAll()
        # Bind the OnSelChanged method to the tree
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelChanged, id=1)
        self.tree.Bind(wx.EVT_SET_FOCUS,self.OnFocus)

    def MakeItemLst(self):
        # make chain,res,atm name list
        self.chainlst=self.model.ListChain()
        self.reslst=self.model.ListResidue(True)
        self.atmlst=self.model.ListAtom()
        self.chainitemdic={}
        self.resitemdic={}
        self.atomitemdic={}
        root=self.tree.AddRoot(self.molnam)
        ires=-1
        for i in range(len(self.chainlst)):
            cname=self.chainlst[i][0]
            if cname == '': cname=' '
            cname=cname+'_'+str(self.chainlst[i][1])
            chain=self.tree.AppendItem(root,cname)
            self.chainitemdic[cname]=chain
            if i == 0: self.expanditemid=chain
            resi=[]
            for j in range(len(self.reslst[i])):
                res=self.reslst[i][j][0]+'_'+str(self.reslst[i][j][1])
                rs=self.tree.AppendItem(chain,res)
                self.resitemdic[res]=rs
                ires += 1
                for k in range(len(self.atmlst[ires])):
                    aname=self.atmlst[ires][k][0]+'_'+str(self.atmlst[ires][k][1])
                    treeitem=self.tree.AppendItem(rs,aname) #self.atmlst[j][k][0])
                    self.atomitemdic[aname]=treeitem

    def OnSelSingle(self,event):
        self.selflg=1

    def OnSelPileUp(self,event):
        self.selflg=0

    def OnNotify(self,event):
        #if event.jobid != self.winlabel: return
        try: item=event.message
        except: return
        if item == 'SwitchMol' or item == 'ReadFiles':
            self.model.ConsoleMessage('Reset mol object in "TreeSelector"')
            self.Reset()

    def OnReset(self,event):
        self.Reset()
        #lib.MessageBoxOK('Restored molecule object','')
        self.model.Message2('Restored molecule object')

    def Reset(self):
        self.pantree.Destroy()
        self.molname=self.model.mol.name
        self.SetTitle('Tree['+self.molnam+']')
        #
        self.selflg=1
        self.chainitemdic={}
        self.resitemdic={}
        self.atomitemdic={}

        self.CreateTreeSelPanel()

    def OnTreeSelChanged(self,event):
        """ Event handler for change selection """
        try:
            items=self.tree.GetSelections()
            # node?
            label=self.tree.GetItemText(items[0])
            loc=label.find('_');
            node=0
            if loc == 3: node=1
            if loc == 4: node=2
            self.SelectByTree(node,items,self.selflg)
        except: pass

    def OnFocus(self,event):
        if self.saveitems:
            for item in self.saveitems:
                self.tree.UnselectItem(item)
                self.tree.SetItemBold(item,False)

    def OnResize(self, event):
        self.pantree.Destroy()
        self.SetMinSize([160,100])
        self.SetMaxSize([160,2000])
        self.size=self.GetClientSize()
        self.CreateTreeSelPanel()

    def OnPaint(self,event):
        event.Skip()

    def SelectByTree(self,node,items,selflg):
        """

        :param int node: node number, 0(chain),1(residue), or 2(atom)
        :param obj items: treeobjectitem
        :param bool selflg: True for select, False for deselect
        """
        #???if self.ctrlflag.GetCtrlFlag('busy'): return
        if len(items) < 0: return
        if self.saveitems:
            for item in self.saveitems:
                self.tree.SetItemBold(item,False)
        for item in items:
            self.tree.SetItemBold(item,True)
        self.saveitems=items
        lstsel=[]
        for i in items:
            label=self.tree.GetItemText(i)
            namnmb=label.split('_')
            nam=namnmb[0]; nmb=int(namnmb[1])
            if node == 0:
                lstsel.append(nam)
            elif node == 1: # residue
                chaid=self.tree.GetItemParent(i)
                chalabel=self.tree.GetItemText(chaid)
                chain=chalabel.split('_')[0]
                lstsel.append([chain,nam,nmb])
            elif node == 2: # atom
                lstsel.append(nmb-1)
        #
        if len(lstsel) > 0 and selflg == 1: self.model.SetSelectAll(False)
        if node == 0:
            nsel=self.model.SelectChainByList(lstsel,True)
        elif node == 1:
            nsel=self.model.SelectResidueByList(lstsel,True)
        elif node == 2:
            nsel=self.model.SelectAtomBySeqNmb(lstsel,True)
        self.model.Message('Number of selected atom(s): '+str(nsel),0,'black')

    def XXSelectChainByNames(self,chainlst,on):
        """ Select chian by name

        :param lst chainlst: chain name list, e.g., "A_1" (1-char_number)
        :param bool on: True for select, False for deselect
        """
        items=[]
        for chain in chainlst:
            if chain not in self.chainitemdic:
                mess='Not found chain name='+chain
                self.model.ConsoleMessage(mess)
                continue
            treeitem=self.chainitemdic[chain]
            self.tree.SelectItem(treeitem,on)
            items.append(treeitem)
        self.SelectByTree(0,items,on)

    def XXSelectAtomByNames(self,atmlst,on):
        """ Select atom by name

        :param lst atmlst: atom name list, e.g., " N  _314" (4-char_number)
        :param bool on: True for select, False for deselect
        """
        items=[]
        for atom in atmlst:
            if atom not in self.atomitemdic:
                mess='Not found atom name='+atom
                self.model.ConsoleMessage(mess)
                continue
            treeitem=self.atomitemdic[atom]
            self.tree.SelectItem(treeitem,on)
            items.append(treeitem)
        self.SelectByTree(2,items,on)

    def XXSelectResidueByNames(self,reslst,on):
        """ Select residue by name

        :param lst reslst: residue name,list e.g., "TYR_44" (3-chars_number)
        :param bool on: True for select, False for deselect
        """
        items=[]
        for residue in reslst:
            if residue not in self.resitemdic:
                mess='Not found residue name='+residue
                self.model.ConsoleMessage(mess)
                continue
            treeitem=self.resitemdic[residue]
            self.tree.SelectItem(treeitem,on)
            items.append(treeitem)
        self.SelectByTree(1,items,on)

    def GetSelectedItemNames(self):
        """

        :return: selname(lst) - Selected item names list
        """
        selitemlst=self.tree.GetSelections()
        selname=[]
        for obj in selitemlst:
            selname.append(self.tree.GetItemText(obj))
        return selname

    def OnClose(self,event):
        try: self.winctrl.Close(self.winlabel) #Win('TreeSelWin')
        except: pass
        self.Destroy()

class NameSelector_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos,winlabel): #,model,ctrlflag,molnam):
        self.title='Name/Number Selector'
        #pltfrm=lib.GetPlatform()
        #if pltfrm == 'WINDOWS': winsize=lib.WinSize((130,320)) #((168,330))
        #else: winsize=(170,340)
        winsize=lib.WinSize([180,360],False)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent, id, self.title,pos=winpos,size=winsize,
                          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
        #self.Bind(wx.EVT_SIZE,self.OnSize)
        self.parent=parent
        self.winctrl=parent.winctrl
        self.mdlwin=parent
        #xxself.ctrlflag=model.ctrlflag
        self.model=model #parent.model
        self.winlabel=winlabel
        self.molnam=model.mol.name #wrkmolnam
        #
        self.SetTitle('NamSel ['+self.molnam+']')

        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.size=self.GetClientSize()
        self.selelmnamlst=['']; self.selatmnamlst=['']; self.selresnamlst=['']
        self.selchainnamlst=['']; self.selgrpnamlst=['']; self.selfrgnamlst=['']
        self.reskindlst=['','Charged','Polar','Non-polar']
        self.reskinddic={'Charged':['LYS','ARG','GLU','ASP'],
                         'Polar':['GLY','SER','THR','ASN','TYR','CYS','HIS'],
                         'Non-polar':['ALA','VAL','LEU','ILE','MET','PRO','PHE',
                                      'TRP']}
        self.curmol=self.model.curmol # name, # of atoms, # of residues
        self.selectsingle=1 # 0:multiple selection, 1:single selection
        self.selectatm=1 # 0: select residue, 1:select atom
        #
        self.SetListItems()
        #
        self.CreatePanel()
        #
        ExecProg_Frm.EVT_THREADNOTIFY(self,self.OnNotify)

    def CreatePanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        xsize=w; ysize=h; wnmb=95; wtxt=140-wnmb; xtcl0=155; xtcl1=260; htcl=22
        #
        hckb=24; hcmb=const.HCBOX; wtxt=60; wcmb=80; xcmb=75
        # Reset button
        btnrset=Reset_Button(self.panel,-1,self.OnReset)

        yloc=5
        wx.StaticText(self.panel,-1,"Selection:",pos=(5,yloc),size=(80,18))
        yloc += 20
        self.rbtsgl=wx.RadioButton(self.panel,wx.ID_ANY,'single',pos=(10,yloc))


        self.rbtmul=wx.RadioButton(self.panel,wx.ID_ANY,'pile up',pos=(70,yloc))
        self.rbtsgl.Bind(wx.EVT_RADIOBUTTON,self.SelSingle)
        self.rbtmul.Bind(wx.EVT_RADIOBUTTON,self.SelMulti)
        self.rbtsgl.SetValue(True)

        #wx.StaticLine(self.panel,pos=(85,0),size=(2,45),style=wx.LI_VERTICAL)

        #btnrset=wx.Button(self.panel,-1,"Reset",pos=(100,yloc-15),size=(50,22))
        #btnrset.Bind(wx.EVT_BUTTON,self.OnReset)


        sellin=wx.StaticLine(self.panel,pos=(-1,yloc+18),size=(w,2),
                             style=wx.LI_HORIZONTAL)
        yloc += 25
        #self.ckbnam = wx.CheckBox(self.panel,-1,"Name selection",pos=(5,yloc+3),size=(120,18))
        wx.StaticText(self.panel,-1,"Name selection",pos=(5,yloc+3),
                      size=(120,18))
        #self.ckbnam.Bind(wx.EVT_CHECKBOX,self.NameSel)
        #self.ckbnam.SetValue(True)

        txtelm=wx.StaticText(self.panel,-1,"Element:",pos=(15,yloc+hckb+2),
                             size=(wtxt,18))
        self.cmbelm=wx.ComboBox(self.panel,-1,'',choices=self.elmnamlst, \
                               pos=(xcmb,yloc+hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        self.cmbelm.Bind(wx.EVT_COMBOBOX,self.OnElement)
        if len(self.elmnamlst) <= 1:
            self.cmbelm.Disable()

        txtatm=wx.StaticText(self.panel,-1,"Atom:",pos=(15,yloc+2*hckb+2),
                             size=(wtxt,18))
        self.cmbatm=wx.ComboBox(self.panel,-1,'',choices=self.atmnamlst, \
                               pos=(xcmb,yloc+2*hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        self.cmbatm.Bind(wx.EVT_COMBOBOX,self.OnAtom)
        if len(self.atmnamlst) <= 1:
            self.cmbatm.Disable()

        txtres=wx.StaticText(self.panel,-1,"Residue:",pos=(15,yloc+3*hckb+2),
                             size=(wtxt,18))
        self.cmbres=wx.ComboBox(self.panel,-1,'',choices=self.resnamlst, \
                               pos=(xcmb,yloc+3*hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        self.cmbres.Bind(wx.EVT_COMBOBOX,self.OnResName)
        if len(self.resnamlst) <= 1:
            self.cmbres.Disable()

        txtres=wx.StaticText(self.panel,-1,"ResKind:",pos=(15,yloc+4*hckb+2),
                             size=(wtxt,18))
        self.cmbresknd=wx.ComboBox(self.panel,-1,'',choices=self.reskindlst, \
                               pos=(xcmb,yloc+4*hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        self.cmbresknd.Bind(wx.EVT_COMBOBOX,self.OnResKind)

        txtcha=wx.StaticText(self.panel,-1,"Chain:",pos=(15,yloc+5*hckb+2),
                             size=(wtxt,18))
        self.cmbcha=wx.ComboBox(self.panel,-1,'',choices=self.chanamlst, \
                               pos=(xcmb,yloc+5*hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        self.cmbcha.Bind(wx.EVT_COMBOBOX,self.OnCahin)
        if len(self.chanamlst) <= 1:
            self.cmbcha.Disable()

        txtgrp=wx.StaticText(self.panel,-1,"Group:",pos=(15,yloc+6*hckb+2),
                             size=(wtxt,18))
        self.cmbgrp=wx.ComboBox(self.panel,-1,'',choices=self.grpnamlst, \
                               pos=(xcmb,yloc+6*hckb), size=(wcmb,hcmb),
                               style=wx.CB_READONLY)
        #self.selcmb5.Bind(wx.EVT_COMBOBOX,self.PopUpSelPanGrpNam)
        self.cmbgrp.Bind(wx.EVT_COMBOBOX,self.OnGroup)
        if len(self.grpnamlst) <= 1:
            self.cmbgrp.Disable();

        txtfrg=wx.StaticText(self.panel,-1,"Fragment:",pos=(15,yloc+7*hckb+2),
                             size=(wtxt,18))
        self.cmbfrg=wx.ComboBox(self.panel,-1,'',choices=self.frgnamlst, \
                                   pos=(xcmb,yloc+7*hckb), size=(wcmb,hcmb), \
                                   style=wx.CB_READONLY)
        self.cmbfrg.Bind(wx.EVT_COMBOBOX,self.OnFragment)
        if len(self.frgnamlst) <= 1:
            self.cmbfrg.Disable()
        lina=wx.StaticLine(self.panel,pos=(-1,yloc+8*hckb+2),size=(xsize,2),
                           style=wx.LI_HORIZONTAL)
        #
        yloc=250
        #self.ckbnmb = wx.CheckBox(self.panel,-1,"Number selection",pos=(5,yloc),size=(155,18))
        #self.ckbnmb.Bind(wx.EVT_CHECKBOX,self.NumberSel)
        #self.ckbnmb.SetValue(False)
        wx.StaticText(self.panel,-1,"Number selection",pos=(5,yloc),
                      size=(155,18))
        self.rbtatm=wx.RadioButton(self.panel,wx.ID_ANY,'Atom',pos=(10,yloc+18)
                                   ,style=wx.RB_GROUP)
        self.rbtres=wx.RadioButton(self.panel,wx.ID_ANY,'Residue',
                                   pos=(65,yloc+18))
        self.rbtatm.Bind(wx.EVT_RADIOBUTTON,self.OnSelectAtom)
        self.rbtres.Bind(wx.EVT_RADIOBUTTON,self.OnSelectRes)
        self.rbtatm.SetValue(True)
        label=str(self.maxatm)
        self.nmbtcl=wx.TextCtrl(self.panel,-1,"",pos=(10,yloc+38),size=(105,20),
                                style=wx.TE_PROCESS_ENTER)
        self.nmbtcl.Bind(wx.EVT_TEXT_ENTER,self.OnApply)
        self.txtmax=wx.StaticText(self.panel,-1,label,pos=(122,yloc+40),
                                  size=(40,18))
        #self.nmbtcl.Disable()
        # OK,Cancel,Apply button
        #linf=wx.StaticLine(self.panel,pos=(-1,ysize-28),size=(xsize,2),style=wx.LI_HORIZONTAL)
        up=30
        apbt=wx.Button(self.panel,wx.ID_ANY,"Apply",pos=(110,ysize-up),
                       size=(50,20))
        apbt.Bind(wx.EVT_BUTTON,self.OnApply) # 10,105,53
        cnbt=wx.Button(self.panel,wx.ID_ANY,"Clear",pos=(53,ysize-up),
                       size=(50,20))
        cnbt.Bind(wx.EVT_BUTTON,self.OnClear)
        okbt=wx.Button(self.panel,wx.ID_ANY,"OK",pos=(10,ysize-up),size=(35,20))
        okbt.Bind(wx.EVT_BUTTON,self.OnOK)

    def SetListItems(self):

        self.elmnamlst=['']+self.model.ListElement()
        self.atmnamlst=['']+self.model.ListAtomName()
        self.resnamlst=['']+self.model.ListResidueName()
        self.chanamlst=['']+self.model.ListChainName()
        self.grpnamlst=['']+self.model.ListGroupName()
        self.frgnamlst=['']+self.model.frag.ListFragmentName()
        try:
            self.maxatm=self.model.GetMaxAtmNmb()
            self.maxres=self.model.GetMaxResNmb()
        except:
            self.maxatm=0; self.maxres=0

    def SelSingle(self,event):
        self.selectsingle=1

    def SelMulti(self,event):
        self.selectsingle=0

    def OnSelectAtom(self,event):
        #if self.ctrlflag.GetCtrlFlag('busy'): return
        self.txtmax.SetLabel(str(self.maxatm))
        self.selectatm=1

    def OnSelectRes(self,event):
        #if self.ctrlflag.GetCtrlFlag('busy'): return
        self.txtmax.SetLabel(str(self.maxres))
        self.selectatm=0

    def OnElement(self,event):
        #???if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        elmnam=self.cmbelm.GetStringSelection()
        if elmnam != '':
            self.model.SelectElmNam(elmnam,1)
            self.model.Message('Select element(s): '+elmnam,0,'black')
        self.cmbelm.SetStringSelection('')

    def OnAtom(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        atmnam=self.cmbatm.GetStringSelection()
        if atmnam != '':
            self.model.SelectAtmNam(atmnam,1)
            self.model.Message('Select atoms(s): '+atmnam,0,'black')
        self.cmbatm.SetStringSelection('')

    def OnResName(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        resnam=self.cmbres.GetStringSelection()
        if resnam != '':
            self.model.SelectResNam(resnam,1)
            self.model.Message('Select residue(s): '+resnam,0,'black')
        self.cmbres.SetStringSelection('')

    def OnResKind(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        resknd=self.cmbresknd.GetStringSelection()
        if resknd == '': return
        reslst=self.reskinddic[resknd]
        selreslst=[]
        for resnam in reslst:
            if resnam in self.resnamlst: selreslst.append(resnam)
        if len(selreslst) > 0:
            self.model.SelectResNam1(selreslst,True)
            self.model.Message('Select residue kind: '+resknd,0,'black')
        self.cmbresknd.SetStringSelection('')

    def OnCahin(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        chanam=self.cmbcha.GetStringSelection()
        if chanam != '':
            self.model.SelectChainNam(chanam,1)
            self.model.Message('Select chain(s): '+chanam,0,'black')
        self.cmbcha.SetStringSelection('')

    def OnGroup(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        grpnam=self.cmbgrp.GetStringSelection()
        if grpnam != '':
            self.model.SelectGroup(grpnam,True)
            self.model.Message('Select group(s): '+grpnam,0,'black')
        self.cmbgrp.SetStringSelection('')

    def OnFragment(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        frgnam=self.cmbfrg.GetStringSelection()
        if frgnam != '':
            self.model.frag.SelectFragmentByName([frgnam],1) #SelectFragNam(frgnam,1)
            self.model.Message('Select fragment(s): '+frgnam,0,'black')
        self.cmbfrg.SetStringSelection('')

    def OnOK(self,event):
        self.OnApply(event)
        self.OnClose(1)
        #self.ctrlflag.Set('NameSelWin',False)
        #self.Destroy()
    def OnNotify(self,event):
        #if event.jobid != self.winlabel: return
        try: item=event.message
        except: return
        if item == 'SwitchMol' or item == 'ReadFiles':
            self.model.ConsoleMessage('Reset mol object in "NameSelector"')
            self.Reset()

    def OnReset(self,event):
        #lib.MessageBoxOK('Restored molecule object','')
        self.model.Message('Restored molecule object',0,'')
        self.Reset()

    def Reset(self):
        self.panel.Destroy()
        self.curmol=self.model.curmol # name, # of atoms, # of residues
        self.selectsingle=1 # 0:multiple selection, 1:single selection
        self.selectatm=1 # 0: select residue, 1:select atom

        self.SetListItems()
        self.CreatePanel()

    def OnApply(self,event):
        #??if self.ctrlflag.GetCtrlFlag('busy'): return
        if self.selectsingle: self.model.SetSelectAll(0)
        txt='No input data.'
        data=[]; lst=[]
        if self.selectatm:
            maxvalue=self.maxatm-1; obj='atom(s)'
        else:
            maxvalue=self.maxres; obj='residue(s)'
        data=self.nmbtcl.GetValue()
        #self.model.Message('Input data='+data,0,'black')
        if len(data) <= 0:
            lib.MessageBoxOK(txt,"")
            #self.model.Message(txt,0,'black')
            return
        else:
            if len(data) < 0:
                self.model.Message(txt,0,'black')
                return
            else:
                lst=lib.StringToInteger(data)
                if len(lst) <= 0:
                    self.model.Message('Error in input data='+data,0,'blue')
                    return
                for i in range(len(lst)):
                    if self.selectatm: lst[i] -= 1
                    if lst[i] < 0 or lst[i] > maxvalue:
                        mess='Error: Exceeds maxvalue. data='+data,0,'black'
                        self.model.Message(mess)
                        return
        self.model.Message('Select '+obj+':'+data,0,'black')
        if self.selectatm: self.model.SelectAtomByList(lst,1)
        else: self.model.SelectResByNmb(lst,1)
        self.nmbtcl.Clear()

    def OnClear(self,event):
        self.cmbelm.SetStringSelection('')
        self.cmbatm.SetStringSelection('')
        self.cmbres.SetStringSelection('')
        self.cmbresknd.SetStringSelection('')
        self.cmbcha.SetStringSelection('')
        self.cmbgrp.SetStringSelection('')
        self.cmbfrg.SetStringSelection('')
        self.nmbtcl.SetValue("")
        self.rbtsgl.SetValue(True)
        self.SelSingle(event)
        self.rbtatm.SetValue(True)
        self.OnSelectAtom(event)
        #self.ckbnam.SetValue(True)
        #self.ckbnmb.SetValue(False)
        self.nmbtcl.SetLabel('')

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        try: self.winctrl.Close(self.winlabel) #Win('NameSelWin')
        except: pass
        self.Destroy()

class CheckListCtrl(wx.ListCtrl,CheckListCtrlMixin):
    def __init__(self,parent,id,winpos=[0,0],winsize=[100,50],
                 oncheckbox=None):
        wx.ListCtrl.__init__(self,parent,id,pos=winpos,size=winsize,
                             style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        self.oncheckbox=oncheckbox

    def OnCheckItem(self,boxnmb,value):
        if self.oncheckbox is not None: self.oncheckbox(boxnmb,value)


class CheckListCtrl_old(wx.ListCtrl,CheckListCtrlMixin):
    def __init__(self,parent,winpos,winsize,oncheckbox):
        wx.ListCtrl.__init__(self,parent,-1,pos=winpos,size=winsize,
                             style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        self.oncheckbox=oncheckbox

    def OnCheckItem(self,boxnmb,value):
        self.oncheckbox(boxnmb,value)

class ChildMolView_Frm(wx.Frame):
    def __init__(self,parent,id,model):
        self.title='Child molecule Viewer '
        winsize=lib.WinSize((212,212)) # (400,300)
        winpos=parent.GetPosition()
        winpos[0] -= 50; winpos[1] += 75
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize, #wx.Size(400, 300),
             style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.mdlwin=parent
        self.winctrl=model.winctrl
        self.view=parent.view
        self.canvas=parent.canvas
        self.molnam=model.mol.name #wrkmolnam
        #xxself.ctrlflag=model.ctrlflag
        self.model=model # parent.model
        self.winctrl=model.winctrl
        #
        self.SetBackgroundColour('black') #("light gray")

        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.drwflg={}
        self.mol=[]
        self.ratio=1.0
        self.atmdat=[]; self.bnddat=[]

        self.canvaschild=self.CreateChildCanvas()
        self.canvaschild.SetBackgroundColour('black')

        self.CreateButton() # if you want to use menu, replace this by self.CreateMenu()
        self.CreateSlider()

        self.viewchild=fuview.fuView(self,self.canvaschild)
        self.viewchild.getatmpos=False

        self.Redraw() # if remove this statement, "zoom" does not work!

    def CreateChildCanvas(self):
        size=self.GetSize()
        w=size.width; h=size.height

        attribList = (wx.glcanvas.WX_GL_RGBA,  # RGBA
                      wx.glcanvas.WX_GL_DOUBLEBUFFER,  # Double Buffered
                      wx.glcanvas.WX_GL_DEPTH_SIZE, 24)  # 32 bit
        canvas=wx.glcanvas.GLCanvas(self,-1, pos=(-1,-1), size=(w,h),
                                    attribList=attribList)
        canvas.Bind(wx.EVT_SIZE,self.OnResize)
        canvas.Bind(wx.EVT_SET_FOCUS,self.OnFocus)

        return canvas

    def CreateButton(self):
        self.hideh=wx.ToggleButton(self.canvaschild,label='hide H',pos=(2,2),
                                   size=(40,18))
        self.hidew=wx.ToggleButton(self.canvaschild,label='hide W',pos=(46,2),
                                   size=(44,18))
        self.bkbone=wx.ToggleButton(self.canvaschild,label='Chain',pos=(94,2),
                                    size=(48,18))
        redrw=wx.Button(self.canvaschild,label='redraw',pos=(148,2),
                        size=(45,18))

        self.hideh.SetValue(True); self.bkbone.SetValue(True)
        self.hidew.SetValue(False)
        #
        self.hideh.Bind(wx.EVT_TOGGLEBUTTON,self.OnHideHydrogen)
        self.bkbone.Bind(wx.EVT_TOGGLEBUTTON,self.OnChainOn)
        self.hidew.Bind(wx.EVT_TOGGLEBUTTON,self.OnHideWater)
        redrw.Bind(wx.EVT_BUTTON,self.OnRedraw)

    def CreateSlider(self):
        size=self.GetSize()
        w=size.width; h=size.height
        self.st01=wx.StaticText(self.canvaschild,-1," zoom: ",pos=(2,h-58),
                                size=(38,18))
        #st01.SetBackgroundColour('light gray')
        self.st01.SetForegroundColour('light gray')
        self.slmag=wx.Slider(self.canvaschild,pos=(42,h-56),size=(150,18),
                             style=wx.SL_HORIZONTAL)
        self.slmag.Bind(wx.EVT_SLIDER,self.OnZoom)

        self.slmag.SetMin(-10); self.slmag.SetMax(10)
        self.slmag.SetValue(0)

    def DestroySlider(self):
        self.st01.Destroy()
        self.slmag.Destroy()

    def OnHideHydrogen(self,event):
        obj=event.GetEventObject()
        ispressed=obj.GetValue()

        self.SetHideHyd(ispressed)

        self.canvaschild.SetFocus()
        self.DrawMolChild(True)

    def OnHideWater(self,event):
        obj=event.GetEventObject()
        ispressed=obj.GetValue()

        self.SetHideWat(ispressed)

        self.canvaschild.SetFocus()
        self.DrawMolChild(True)

    def OnChainOn(self,event):
        obj=event.GetEventObject()
        ispressed=obj.GetValue()

        if ispressed: self.SetChainOn()
        else: self.SetChainOff()

        self.canvaschild.SetFocus()
        self.DrawMolChild(True)

    def OnZoom(self,event):
        value=self.slmag.GetValue()
        ratio=1.0-0.05*value
        if ratio < 0.1: ratio=0.1
        self.viewchild.ratio=self.ratio*ratio
        self.DrawMolChild(False)

    def DrawMolChild(self,drw):
        self.viewchild.updated=False
        if drw:
            #self.canvas.SetCurrent()
            self.viewchild.updated=True
        self.viewchild.OnPaint()
        #self.view.canvas.SetFocus()

    def SetUpDrawChild(self):
        #
        self.SetMol()
        self.SetTitle(self.title+' ['+self.molnam+']')
        for i in range(len(self.mol)):
            if self.mol[i].elm == 'XX': continue
            self.mol[i].show=True

        self.SetHideWat(self.hidew.GetValue())
        if self.bkbone.GetValue(): self.SetChainOn()
        else: self.SetChainOff()
        self.SetHideHyd(self.hideh.GetValue())

        self.DrawMolChild(True)

    def UpdateView(self):
        #
        self.SetUpDrawChild()
        self.view.canvas.SetFocus()

    def ChangeMol(self):
        self.canvaschild.SetCurrent()
        self.Redraw()

    def SetChainOn(self):
        chaindat=self.model.MakeDrawChainTubeData(self.mol)
        if len(chaindat) > 0: self.viewchild.SetDrawChainTubeData(True,chaindat)
        else: self.viewchild.SetDrawChainTubeData(False,[])

    def SetChainOff(self):
        self.viewchild.SetDrawChainTubeData(False,[])

    def Message(self,mess,loc,color):
        self.model.Message(mess,loc,color)

    def OnRedraw(self,event):
        self.canvaschild.SetCurrent()
        self.Redraw()
        #self.canvaschild.SetFocus()

    def Redraw(self):
        self.SetUpDrawChild()

        self.viewchild.eyepos=self.view.eyepos
        self.viewchild.center=self.view.center
        self.viewchild.upward=self.view.upward
        #
        self.viewchild.InitGL()
        self.viewchild.OnResize()
        self.slmag.SetValue(0)

    def SetMol(self):
        molnam=self.model.mol.name #wrkmolnam
        self.mol=self.DeepCopyMol() #copy.deepcopy(self.model.mol.atm)
        if molnam != self.molnam:
            self.molnam=molnam
        for atom in self.mol: atom.show=True

    def DeepCopyMol(self):
        cpy=molec.Molecule(self.model)
        cpy.mol=copy.deepcopy(self.model.mol.atm)
        return cpy.mol

    def SetHideHyd(self,on):
        # value=True: hide, =False: show
        hidewat=self.hidew.GetValue()
        value=0
        if not on: value=1
        for atom in self.mol:
            if atom.elm == 'XX': continue
            res=atom.resnam
            if not hidewat:
                if res == 'HOH' or res == 'DOD' or res == 'WAT': continue
            if atom.elm == ' H': atom.show=value
        atmdat=self.model.MakeDrawAtomData(self.mol)
        bnddat=self.model.MakeDrawBondData(self.mol)
        if len(atmdat) > 0: self.viewchild.SetDrawAtomData(True,atmdat)
        else: self.viewchild.SetDrawAtomData(False,[])
        if len(bnddat) > 0: self.viewchild.SetDrawBondData(True,bnddat)
        else: self.viewchild.SetDrawBondData(False,[])

    def SetHideWat(self,on):
        # value=True: hide, =False: show
        value=0
        if not on: value=1
        for i in range(len(self.mol)):
            if self.mol[i].elm == 'XX': continue
            res=self.mol[i].resnam
            if res == 'HOH' or res == 'WAT' or res == 'DOD':
                self.mol[i].show=value
        atmdat=self.model.MakeDrawAtomData(self.mol)
        bnddat=self.model.MakeDrawBondData(self.mol)
        if len(atmdat) > 0: self.viewchild.SetDrawAtomData(True,atmdat)
        else: self.viewchild.SetDrawAtomData(False,[])
        if len(bnddat) > 0: self.viewchild.SetDrawBondData(True,bnddat)
        else: self.viewchild.SetDrawBondData(False,[])

    def SetDrwFlg(self):
        self.drwflg=copy.deepcopy(self.model.mol.drwflg)

    def OnResize(self, event):
        self.DestroySlider()
        self.CreateSlider()

        self.viewchild.OnResize()

        self.slmag.SetValue(0)
        self.ratio=self.viewchild.ratio

    def OnPaint(self,event):
        event.Skip()

    def OnFocus(self,event):
        print('on eneter child win')
        #self.canvaschild.SetCurrent()

    def OnClose(self,event):
        self.winctrl.Close('ChildViewWin')
        self.winctrl.Close('MolViewWin')
        self.Destroy()


class RadiusSelector_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos): #,model,ctrlflag,molnam):
        self.title='Radius Selection'
        winsize=lib.WinSize((155,125))
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent,id,self.title,pos=winpos,size=winsize,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
        self.parent=parent
        self.mdlwin=parent
        #xxself.ctrlflag=model.ctrlflag
        self.model=model #parent.model
        self.winctrl=model.winctrl
        molnam=self.model.mol.name #wrkmolnam

        self.SetTitle('RadSel ['+molnam+']')

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        #
        self.xsize=winsize[0]; self.ysize=winsize[1]
        #self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.nsel,self.selectedlst=self.model.ListSelectedAtom()
        self.popupradsel=self.model.popupradsel
        self.mol=self.model.mol.atm
        self.size=self.GetClientSize()

        self.select=True; self.selatm=False; self.radius=5.0
        self.CreateRadiusSelPanel()

    def CreateRadiusSelPanel(self):
        w=self.size[0]; h=self.size[1]

        self.radpan=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.radpan.SetBackgroundColour("light gray")
        yloc=5
        self.radrbt1=wx.RadioButton(self.radpan,wx.ID_ANY,'Select',
                                    pos=(5,yloc),style=wx.RB_GROUP)
        self.radrbt2=wx.RadioButton(self.radpan,wx.ID_ANY,'Deselect',
                                    pos=(60,yloc))
        self.radrbt1.Bind(wx.EVT_RADIOBUTTON,self.RadiusSelPanSel)
        self.radrbt2.Bind(wx.EVT_RADIOBUTTON,self.RadiusSelPanUnsel)
        self.radrbt2.SetValue(False)
        sl1=wx.StaticLine(self.radpan,pos=(-1,yloc+17),size=(w,2),
                          style=wx.LI_HORIZONTAL)
        yloc=28
        self.st1 = wx.StaticText(self.radpan,wx.ID_ANY,"Radius:",
                                 pos=(5,yloc),size=(45,18))
        self.st2 = wx.StaticText(self.radpan,wx.ID_ANY,"A",pos=(90,yloc),
                                 size=(40,18))
        rad=str(self.radius)
        self.radtcl1=wx.TextCtrl(self.radpan,-1,'5.0',pos=(50,yloc-2),
                                 size=(35,18))
        #self.radtcl1.Bind(wx.EVT_TEXT,self.RadiusSelPanRad)
        yloc=46
        self.radrbt3=wx.RadioButton(self.radpan,wx.ID_ANY,'atom',pos=(10,yloc),
                               style=wx.RB_GROUP)
        self.radrbt4=wx.RadioButton(self.radpan,wx.ID_ANY,'residue',
                                    pos=(66,yloc))
        self.radrbt3.Bind(wx.EVT_RADIOBUTTON,self.RadiusSelPanAtm)
        self.radrbt4.Bind(wx.EVT_RADIOBUTTON,self.RadiusSelPanRes)
        self.radrbt4.SetValue(True)
        # OK, Cancel button
        slf=wx.StaticLine(self.radpan,pos=(-1,h-32),size=(w,2),
                          style=wx.LI_HORIZONTAL)
        pbx=w/2-50; wsize=40; hwsize=wsize/2
        bt1=wx.Button(self.radpan,wx.ID_ANY,"OK",pos=(pbx-hwsize+6,h-25),
                      size=(wsize,20))
        bt1.Bind(wx.EVT_BUTTON,self.RadiusSelPanOK)
        bt2=wx.Button(self.radpan,wx.ID_ANY,"Cancel",pos=(pbx+hwsize+9,h-25),
                      size=(wsize,20))
        bt2.Bind(wx.EVT_BUTTON,self.RadiusSelPanCancel)
        bt3=wx.Button(self.radpan,wx.ID_ANY,"Apply",
                      pos=(pbx+wsize+hwsize+12,h-25),size=(wsize,20))
        bt3.Bind(wx.EVT_BUTTON,self.RadiusSelPanApply)

    def OnFocus(self,event):
        self.Show()
    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        self.winctrl.Close('RadiusSelWin')
        self.Destroy()

    def RadiusSelPanSel(self,event):
        self.select=False
        if self.radrbt1: self.select=True
    def RadiusSelPanUnsel(self,event):
        self.select=True
        if self.radrbt2: self.select=False
    """
    def RadiusSelPanRad(self,event):
        print ' selrad rad'
        self.radius=float(self.radtcl1.GetValue())

        print 'rad',self.radius
    """
    def RadiusSelPanAtm(self,event):
        self.selatm=False
        if self.radrbt3: self.selatm=True

    def RadiusSelPanRes(self,event):
        self.selatm=True
        if self.radrbt4: self.selatm=False

    def RadiusSelPanOK(self,event):
        self.RadiusSelPanApply(event)
        self.winctrl.Set('RadiusSelWin',False)
        self.Destroy()

    def RadiusSelPanCancel(self,event):
        self.model.SetSelectAll(False)()
        self.model.SelectByList(self.savesellst,1)
        self.winctrl.Set('RadiusSelWin',False)
        self.Destroy()

    def RadiusSelPanApply(self,event):
        nsel,lst=self.model.ListSelectedAtom()
        self.savesellst=lst[:]
        radius=float(self.radtcl1.GetValue())

        nadd=0
        if self.radius > 0.5: nadd,addlst=self.SelectRadius(radius)
        if nadd > 0: self.model.SelectByList(addlst,1)

    def SelectRadius(self,radius):
        nadd=0
        nsel,lst=self.model.ListSelectedAtom()
        if nsel <= 0:
            mess='No selected atoms.'
            self.model.Message(mess,0,'')
            return
        nadd,addlst=self.model.FindRadiusAtm(radius)
        return nadd,addlst

class AtomChargeInput_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos):
        self.title='Input Atom Charge'
        winsize=lib.WinSize((145,40))
        winpos  = lib.SetWinPos(winpos)
        #if const.SYSTEM == const.MACOSX: winsize=(145,40)
        wx.Frame.__init__(self, parent, id, self.title,size=winsize,pos=winpos,
          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.mdlwin=parent
        self.model=model #self.parent.model
        self.winctrl=model.winctrl
        #xxself.ctrlflag=model.ctrlflag
        self.menuctrl=model.menuctrl
        #
        self.size=self.GetSize()
        #
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.CreatePanel()
        self.err=False

    def CreatePanel(self):
        w=self.size[0]; h=self.size[1]
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        yloc=8
        wx.StaticText(self.panel,-1,"Charge:",pos=(5,yloc),size=(40,18))
        self.tclchg=wx.TextCtrl(self.panel,-1,"1.0",pos=(50,yloc-2),
                                size=(32,18))
        #self.tclchg.Bind(wx.EVT_TEXT,self.ControlPanBall)

        aplybt=wx.Button(self.panel,wx.ID_ANY,"Apply",pos=(90,yloc-2),
                         size=(45,20))
        aplybt.Bind(wx.EVT_BUTTON,self.OnApply)

    def OnApply(self,event):
        self.tclchg.GetValue()
        try:
            atmchg=float(self.tclchg.GetValue())
            self.model.AssignIonChg(atmchg)
            if self.err:
                self.model.Message('',0,'black'); self.err=False
        except:
            self.err=True
            mess='Wrong charge.'
            self.model.Message(mess,0,'black')

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        self.model.DrawFormalCharge(False)
        #self.parent.fumenuitemdic["Formal charge"].Check(False)
        self.menuctrl.Check("Formal charge",False)
        self.winctrl.Close('AtomChargeWin')
        self.Destroy()

class AssignAtomType_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos):
        self.title='Atom type assign'
        winsize=lib.WinSize([800,400]); winpos=[0,20]
        #wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
        #       style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,pos=winpos,size=winsize) #,
        #                  style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|\
        #                  wx.CLOSE_BOX)
        self.parent=parent
        self.winctrl=model.winctrl
        self.draw=parent.draw
        #xxself.ctrlflag=model.ctrlflag
        self.model=model
        wrkmolnam=model.mol.name #wrkmolnam
        #
        [w,h]=self.GetClientSize()
        self.sashposition=0.55*w
        hcmd=170
        self.yloctypmess=h-hcmd
        self.yloclstmess=h-25
        self.xloctgtmess=90; self.yloctgtmess=0
        self.xlocunasgn=245; self.ylocunasgn=0
        #
        self.SetTitle(self.title+' ['+wrkmolnam+']')
        # Menu
        menud=self.MenuItems()
        self.menubar=lib.fuMenu(menud)
        self.SetMenuBar(self.menubar.menuitem)
        lib.InsertTitleMenu(self.menubar,'[AtomType]')
        self.plotmenu=self.menubar.menuitem
        self.Bind(wx.EVT_MENU,self.OnMenu)
        # load force field name and its file name
        self.SetFFNamesAndFiles()
        self.atmtyplst=[]
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        #

        #self.size=self.GetClientSize()
        # atom list options
        self.atmtypdatnmbdic={}
        self.actatm=[]
        self.all=True # list all atoms
        self.elmlst=['all']+self.model.ListElement()
        self.elm='all'
        #self.valedic=self.MakeValeDic()
        self.vale='all'
        self.valelst=['all','0','1','2','3','4','5','6']
        self.reslst=[]
        self.res='all'
        #self.atmlst=[]
        #self.atm='all'
        self.conlst=[]
        self.con='all'
        self.typ='all'
        self.typlst=['all','0']
        self.targetdic={}
        self.updateddic={}
        self.ffatmtyp=''
        self.acttyp=[]
        #self.ffacttyp=[]
        self.ffgrp='all'
        self.ffgrplst=[]
        self.atmtyp=''
        self.ffvale='all'
        self.ffelm='all'
        self.ffelmlst=['all']
        self.ffvalelst=['all','0','1','2','3','4','5','6']
        self.colorlst=['black','red','yellow','blue','green']
        self.ffcls='all'
        self.ffclslst=['all']
        self.changedcolor='red'
        self.batch=True
        self.cantyp=[]
        self.tgtatm=-1
        # force field options
        self.ffname=''

        self.tablelst=['none','all'] # look up table for atmtyp
        self.tbl='none'

        self.atmtypsav=0
        self.targetdicsav={}
        self.tgtatmsav=-1
        self.atmtypselected=False

        self.CreateSplitterWindow()

        self.Bind(wx.EVT_SIZE,self.OnSize)

    def CreateSplitterWindow(self):
        # create splitwindow
        size=self.GetClientSize()
        w=size[0]; h=size[1]
        self.splwin=wx.SplitterWindow(self,-1,size=(w,h), style=wx.SP_3D)
        # panel on left window
        xpos=0; ypos=0; ysize=h #ysize=self.size[1] # ; xsize=self.size[0]
        xsize=self.sashposition
        xpanlst=xsize-5 #550
        self.panlst=wx.Panel(self.splwin,-1,pos=(xpos,ypos),
                             size=(xpanlst,ysize)) #ysize))
        self.panlst.SetBackgroundColour("light gray")
        # panel on right window
        xpos=self.sashposition+5
        hcmd=170
        ypos=0; ysize=h  #-hcmd #; xsize=self.size[0]; ysize=self.size[1]; xpos=555;
        xpansize=w-xpos #xsize-xpos
        self.pantyp=wx.Panel(self.splwin,-1,pos=(xpos,ypos),
                             size=(xpansize,ysize)) #ysize))
        self.pantyp.SetBackgroundColour("light gray")
        #
        self.splwin.SplitVertically(self.panlst,self.pantyp,
                                    sashPosition=self.sashposition) #w-150)
        self.splwin.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
                         self.OnSplitWinChanged)
        # left panel
        self.CreateAtomPanel()
        self.ListAtoms('black')
        # right panel
        self.CreateAtomTypePanel()
        self.ListFFAtomTypes()

    def CreateAtomPanel(self):
        [w,h]=self.GetClientSize()
        xsize=self.sashposition
        ysize=h
        xpanlst=xsize-10 #550
        hcb=const.HCBOX
        # put weget
        yloc=5
        wx.StaticText(self.panlst,-1,"Target atom list for:",pos=(5,yloc),
                      size=(120,18))
        #self.rbtprm=wx.RadioButton(self.panlst,wx.ID_ANY,'missing atom type only',pos=(110,yloc), \
        #                            style=wx.RB_GROUP)
        #self.rbtall=wx.RadioButton(self.panlst,wx.ID_ANY,'all',pos=(280,yloc))
        wx.StaticText(self.panlst,-1,"atmtyp:",pos=(125,yloc),size=(50,18))
        self.cmbtyp=wx.ComboBox(self.panlst,-1,'',choices=[], \
                               pos=(175,yloc-2),
                               size=(70,hcb),style=wx.CB_READONLY)
        self.cmbtyp.Bind(wx.EVT_COMBOBOX,self.OnAtmTyp)
        self.SetAtmTypLst()

        wx.StaticText(self.panlst,-1,"residue:",pos=(260,yloc),size=(50,18))
        self.cmbres=wx.ComboBox(self.panlst,-1,'',choices=self.reslst, \
                               pos=(310,yloc-2),
                               size=(50,hcb),style=wx.CB_READONLY)
        self.cmbres.Bind(wx.EVT_COMBOBOX,self.OnResidue)
        #self.SetResLst()
        #self.cmbres.SetStringSelection(self.res)
        btnsetall=wx.Button(self.panlst,wx.ID_ANY,"Set all",pos=(xsize-55,yloc),
                            size=(45,22))
        btnsetall.Bind(wx.EVT_BUTTON,self.OnSetAll)

        #wx.StaticText(self.panlst,-1,"atmnam:",pos=(300,yloc),size=(50,18))
        #self.cmbres=wx.ComboBox(self.panlst,-1,'',choices=self.atmlst, \
        #                       pos=(355,yloc-2),size=(60,20),style=wx.CB_READONLY)
        #self.cmbres.Bind(wx.EVT_COMBOBOX,self.OnAtmNam)
        #self.cmbres.SetStringSelection(self.atm)

        yloc=yloc+22
        wx.StaticText(self.panlst,-1,"element:",pos=(40,yloc+2),size=(50,18))
        self.cmbelm=wx.ComboBox(self.panlst,-1,'',choices=self.elmlst, \
                               pos=(95,yloc-2),size=(40,hcb),
                               style=wx.CB_READONLY)
        self.cmbelm.Bind(wx.EVT_COMBOBOX,self.OnElement)
        #self.SetElmLst()

        #self.cmbelm.SetStringSelection(self.elm)
        wx.StaticText(self.panlst,-1,"vale:",pos=(145,yloc+2),size=(25,18))
        self.cmbvale=wx.ComboBox(self.panlst,-1,'',choices=[],
                               pos=(175,yloc-2),size=(40,hcb),
                               style=wx.CB_READONLY)
        #self.SetValeLst()
        self.cmbvale.Bind(wx.EVT_COMBOBOX,self.OnVale)

        wx.StaticText(self.panlst,-1,"bonded:",pos=(225,yloc+2),size=(50,18))
        self.cmbcon=wx.ComboBox(self.panlst,-1,'',choices=self.conlst,
                           pos=(280,yloc-2),size=(80,hcb),style=wx.CB_READONLY)
        #self.SetConLst()
        #self.cmbcon.SetStringSelection(self.con)
        self.cmbcon.Bind(wx.EVT_COMBOBOX,self.OnConect)

        self.SetResLst()
        self.SetElmLst()
        self.SetValeLst()
        self.SetConLst()
        self.cmbres.SetStringSelection(self.res)
        self.cmbelm.SetStringSelection(self.elm)
        self.cmbvale.SetStringSelection(str(self.vale))
        self.cmbcon.SetStringSelection(self.con)

        yloc=yloc+25; ybtn=30 # 25
        self.lstctrl=wx.ListCtrl(self.panlst,-1,pos=(5,yloc),
                             size=(xpanlst,ysize-yloc-ybtn),style=wx.LC_REPORT)
        self.lstctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnAtomSelected)

        self.lstctrl.InsertColumn(0,'seq.',width=50)
        self.lstctrl.InsertColumn(1,'elm',width=35)
        self.lstctrl.InsertColumn(2,'residue',width=60)
        self.lstctrl.InsertColumn(3,'atmnam',width=65)
        self.lstctrl.InsertColumn(4,'vale',width=38)
        self.lstctrl.InsertColumn(5,'bonded',width=70)
        #self.lstctrl.InsertColumn(6,'charge',width=55)
        self.lstctrl.InsertColumn(6,'atmtyp',width=55)
        self.lstctrl.InsertColumn(7,'ff name',width=70)
        # OK, Cancel button
        yloc=ysize-ybtn # 25
        btncol=wx.Button(self.panlst,wx.ID_ANY,"Clear color",
                         pos=(xsize-200,yloc+3),size=(80,22))
        btncol.Bind(wx.EVT_BUTTON,self.OnClearColor)
        btnclr=wx.Button(self.panlst,wx.ID_ANY,"Clear atmtyp",
                         pos=(xsize-100,yloc+3),size=(80,22))
        btnclr.Bind(wx.EVT_BUTTON,self.OnClearAtmtyp)
        #btnapl=wx.Button(self.panlst,wx.ID_ANY,"Clear charge",pos=(xsize-100,yloc+3),size=(80,22))
        #btnapl.Bind(wx.EVT_BUTTON,self.OnClearCharge)

        self.yloclstmess=yloc

    def CreateAtomTypePanel(self):
        # popup control panel
        [w,h]=self.GetClientSize()
        xpos=self.sashposition+5
        hcmd=180; hcb=const.HCBOX
        ypos=0; ysize=h #h-hcmd #; xsize=self.size[0]; ysize=self.size[1]; xpos=555;
        xpansize=w-xpos #xsize-xpos
        yopt=165; ychg=5 #40
        yloc=5
        wx.StaticText(self.pantyp,-1,"Force field:",pos=(5,yloc),size=(65,18))
        self.cmbff=wx.ComboBox(self.pantyp,-1,'',choices=[],pos=(75,yloc-2),
                               size=(100,hcb),style=wx.CB_READONLY)
        self.SetForceField()
        self.cmbff.SetStringSelection(self.ffname)
        self.cmbff.Bind(wx.EVT_COMBOBOX,self.OnFFChoice)

        #wx.StaticText(self.pantyp,-1,"residue:",pos=(195,yloc),size=(50,18))
        self.cmbffgrp=wx.ComboBox(self.pantyp,-1,'',choices=[],pos=(195,yloc-2),
                               size=(90,hcb),style=wx.CB_READONLY)
        self.cmbffgrp.Bind(wx.EVT_COMBOBOX,self.OnFFGroup)
        #self.SetFFGroupLst()

        yloc=yloc+22
        wx.StaticText(self.pantyp,-1,"Atom types for",pos=(5,yloc+2),
                      size=(100,18))
        #self.cmbvale.Bind(wx.EVT_COMBOBOX,self.OnVale)
        wx.StaticText(self.pantyp,-1,"element:",pos=(95,yloc+2),size=(50,18))
        self.cmbffelm=wx.ComboBox(self.pantyp,-1,'',choices=self.ffelmlst, \
                            pos=(148,yloc-2),size=(38,hcb),style=wx.CB_READONLY)
        self.cmbffelm.Bind(wx.EVT_COMBOBOX,self.OnFFElement)
        #self.cmbffelm.SetStringSelection(self.ffelm)
        wx.StaticText(self.pantyp,-1,"vale:",pos=(193,yloc+2),size=(25,18))
        self.cmbffvale=wx.ComboBox(self.pantyp,-1,'',choices=self.ffvalelst, \
                            pos=(223,yloc-2),size=(35,hcb),style=wx.CB_READONLY)
        self.cmbffvale.SetStringSelection(self.ffvale)

        self.cmbffvale.Bind(wx.EVT_COMBOBOX,self.OnFFVale)
        wx.StaticText(self.pantyp,-1,"atmcls:",pos=(263,yloc+2),size=(42,18))
        self.cmbffcls=wx.ComboBox(self.pantyp,-1,'',choices=self.ffclslst, \
                            pos=(305,yloc-2),size=(40,hcb),style=wx.CB_READONLY)
        self.cmbffcls.SetStringSelection(str(self.ffcls))
        self.cmbffcls.Bind(wx.EVT_COMBOBOX,self.OnFFClass)

        self.SetFFGroupLst()
        self.SetFFElementLst()
        self.cmbffelm.SetStringSelection(self.ffelm)
        self.SetFFAtmClassLst()

        yloc=yloc+25 # 25
        xchg=xpansize-10 #540
        ylst=ysize-hcmd-5 #yopt-ychg-5
        self.lstctyp=wx.ListCtrl(self.pantyp,-1,pos=(5,yloc),size=(xchg,ylst),
                                 style=wx.LC_REPORT) #wx.LC_SINGLE_SEL|
        self.lstctyp.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnAtmTypSelected)
        self.lstctyp.InsertColumn(0,'atmtyp',width=55)
        self.lstctyp.InsertColumn(1,'vale',width=38)
        self.lstctyp.InsertColumn(2,'atmcls',width=55)
        self.lstctyp.InsertColumn(3,'ffatm',width=45)
        self.lstctyp.InsertColumn(4,'comment',width=180) #xchg-45-45-10)

        self.lowerpanloc=ylst+yloc+10

        #if self.batch:
        # Atom type assignment
        yloc=yloc+ylst+5
        wx.StaticText(self.pantyp,-1,"Target atoms:",pos=(5,yloc),size=(80,18))
        btntgtall=wx.Button(self.pantyp,wx.ID_ANY,"all",pos=(140,yloc-2),
                            size=(35,22))
        btntgtall.Bind(wx.EVT_BUTTON,self.OnTargetAll)
        self.btntgtclr=wx.Button(self.pantyp,wx.ID_ANY,"clear",pos=(185,yloc-2),
                                 size=(35,22))
        self.btntgtclr.Bind(wx.EVT_BUTTON,self.OnTargetClear)

        self.yloctgtmess=yloc
        yloc=yloc+20; xtgt=xpansize-25
        self.tcltgt=wx.TextCtrl(self.pantyp,-1,"",pos=(20,yloc),size=(xtgt,20))
        self.SetTargetAtoms([])
        yloc=yloc+25
        wx.StaticText(self.pantyp,-1,"Specified atmtyp:",pos=(5,yloc+2),
                      size=(100,18))
        self.tcltyp=wx.TextCtrl(self.pantyp,-1,"",pos=(110,yloc),size=(55,20))
        #self.tcltyp.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnFFAtmTyp)
        self.tcltyp.SetValue(str(self.atmtyp))

        self.btnapl=wx.Button(self.pantyp,wx.ID_ANY,"Apply",pos=(200,yloc),
                              size=(50,22))
        self.btnapl.Bind(wx.EVT_BUTTON,self.OnFFApply)
        self.btnund=wx.Button(self.pantyp,wx.ID_ANY,"Undo",pos=(265,yloc),
                              size=(50,22))
        self.btnund.Bind(wx.EVT_BUTTON,self.OnFFUndo)

        yloc=yloc+25
        wx.StaticText(self.pantyp,-1,"Show applied in:",pos=(10,yloc+2),
                      size=(95,18))
        self.cmbcol=wx.ComboBox(self.pantyp,-1,'',choices=self.colorlst, \
                              pos=(110,yloc),size=(55,hcb),style=wx.CB_READONLY)
        self.cmbcol.SetStringSelection(self.changedcolor)
        wx.StaticText(self.pantyp,-1,"Unassiged:",pos=(180,yloc+2),size=(60,18))
        self.ylocunasgn=yloc+2
        #
        yloc=yloc+26
        wx.StaticLine(self.pantyp,pos=(-1,yloc),size=(xpansize,2),
                      style=wx.LI_HORIZONTAL)
        yloc=yloc+5
        self.btnapl=wx.Button(self.pantyp,wx.ID_ANY,"Assign in batch",
                              pos=(10,yloc),size=(100,22))
        self.btnapl.Bind(wx.EVT_BUTTON,self.OnFFBatch)
        wx.StaticText(self.pantyp,-1,"table:",pos=(130,yloc+4),size=(35,18))
        self.cmbtbl=wx.ComboBox(self.pantyp,-1,'',choices=self.tablelst, \
                             pos=(170,yloc),size=(120,hcb),style=wx.CB_READONLY)
        self.cmbtbl.Bind(wx.EVT_BUTTON,self.OnFFTable)
        self.cmbtbl.SetValue(self.tbl)
        if len(self.tablelst) <= 2: self.cmbtbl.Disable()

        self.DispUnassign()
        #else: # sequential mode
        """
        #print 'else, self.batch',self.batch

        yloc=yloc+ylst+10#
        #yloc=self.lowerpanloc
        # Atom type assignment
        #yloc=5 #yloc=yloc+ylst+10
        wx.StaticText(self.pantyp,-1,"Target atom:",pos=(5,yloc),size=(80,18))
        self.tcltgtcan=wx.TextCtrl(self.pantyp,-1,"",pos=(90,yloc-2),size=(40,20))
        #self.SetTargetAtomCan('')
        btntgtskp=wx.Button(self.pantyp,wx.ID_ANY,"skip",pos=(150,yloc-2),size=(40,22))
        btntgtskp.Bind(wx.EVT_BUTTON,self.OnTargetSkip)
        self.btntgtbak=wx.Button(self.pantyp,wx.ID_ANY,"back",pos=(200,yloc-2),size=(40,22))
        self.btntgtbak.Bind(wx.EVT_BUTTON,self.OnTargetBack)
        xcan=xpansize-90
        yloc=yloc+25; hcan=85
        wx.StaticText(self.pantyp,-1,"Candidates:",pos=(5,yloc+2),size=(75,18))
        self.lstccan=wx.ListCtrl(self.pantyp,-1,pos=(80,yloc),size=(xcan,hcan),
                                 style=wx.LC_SINGLE_SEL|wx.LC_REPORT)
        self.lstccan.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnFFCandidateSelected)
        self.lstccan.InsertColumn(0,'atmtyp',width=55)
        self.lstccan.InsertColumn(1,'comment',width=180)
        yloc=yloc+hcan+5
        self.btnqit=wx.Button(self.pantyp,wx.ID_ANY,"Quit",pos=(140,yloc),size=(40,22))
        self.btnqit.Bind(wx.EVT_BUTTON,self.OnFFQuit)
        self.btnund=wx.Button(self.pantyp,wx.ID_ANY,"Undo",pos=(210,yloc),size=(40,22))
        self.btnund.Bind(wx.EVT_BUTTON,self.OnFFUndo)
        self.yloctypmess=yloc
        # compute charge section
        #yloc=ysize-ychg+5
        #wx.StaticLine(self.pantyp,pos=(-1,yloc),size=(xpansize,4),style=wx.LI_HORIZONTAL)
        #yloc=ysize-ychg+15
        #wx.StaticText(self.pantyp,-1,"Compute charges:",pos=(5,yloc),size=(100,18))
        #self.btnmul=wx.Button(self.pantyp,wx.ID_ANY,"Mulliken",pos=(120,yloc-2),size=(50,22))
        #self.btnmul.Bind(wx.EVT_BUTTON,self.OnFFMulliken)
        #self.btnrsp=wx.Button(self.pantyp,wx.ID_ANY,"RESP",pos=(180,yloc-2),size=(40,22))
        #self.btnrsp.Bind(wx.EVT_BUTTON,self.OnFFRESP)
        """
    def DispUnassign(self):
        mess=str(self.NumberOfUnassigned())
        wx.StaticText(self.pantyp,-1,mess,pos=(self.xlocunasgn,self.ylocunasgn),
                      size=(60,18))

    def DispTargetted(self):
        strnmb=str(len(list(self.targetdic.keys())))
        wx.StaticText(self.pantyp,-1,strnmb,pos=(self.xloctgtmess,
                                                 self.yloctgtmess),size=(45,18))

    def ListAtoms(self,col):
        self.lstctrl.DeleteAllItems()
        self.actatm=[]; color=col
        try: len(self.model.mol.atm)
        except:
            lib.MessageBoxOK("No atoms.","")

            return
        self.condic={}; self.resdic={}
        #if self.all:
        for atom in self.model.mol.atm:
            if atom.elm == 'XX': continue
            #if self.typ != 'all' and self.typ != atom.ffatmtyp: continue
            if self.typ == 'unassigned' and atom.ffatmtyp != 0: continue
            if self.typ == 'assigned' and atom.ffatmtyp == 0: continue
            if self.typ != 'all' and self.typ != 'unassigned' \
                and self.typ != 'assigned' and self.typ != atom.ffatmtyp:
                continue
            if self.res != 'all' and self.res != atom.resnam: continue
            if self.elm != 'all' and self.elm != atom.elm: continue
            if self.vale != 'all' and len(atom.conect) != self.vale: continue
            scon=self.BondedElm(atom.conect)
            if self.con != 'all' and self.con != scon: continue

            index=self.lstctrl.InsertStringItem(sys.maxsize,str(atom.seqnmb+1))
            self.lstctrl.SetStringItem(index,1,atom.elm)
            self.lstctrl.SetStringItem(index,2,atom.resnam+str(atom.resnmb))
            self.lstctrl.SetStringItem(index,3,atom.atmnam)
            self.lstctrl.SetStringItem(index,4,str(len(atom.conect)))
            #scon=self.BondedElm(atom.conect)
            self.lstctrl.SetStringItem(index,5,scon)
            #self.lstctrl.SetStringItem(index,6,str(atom.ffcharge))
            self.lstctrl.SetStringItem(index,6,str(atom.ffatmtyp))
            if atom.seqnmb+1 in self.updateddic:
                if col == '': color=self.lstctrl.GetItemTextColour(index)
                self.lstctrl.SetItemTextColour(index,color)
            self.lstctrl.SetStringItem(index,7,str(atom.ffname))

            self.actatm.append(atom.seqnmb+1)

        mess='listed atoms: '+str(len(self.actatm))
        wx.StaticText(self.panlst,-1,mess,pos=(20,self.yloclstmess+5),
                      size=(100,18))

    def BondedElm(self,conect):
        elmlst=[]
        for i in conect: elmlst.append(self.model.mol.atm[i].elm)
        chemlst,formula=lib.ChemFormula(elmlst)
        return formula

    def SetAtmTypLst(self):
        nmbdic={}; lst=[]; typlst=[]
        for atom in self.model.mol.atm:
            if self.res != 'all' and self.res != atom.resnam: continue
            if self.elm != 'all' and self.elm != atom.elm: continue
            if self.typ == 'unassigned' and atom.ffatmtyp != 0: continue
            if self.typ == 'assigned' and atom.ffatmtyp == 0: continue
            nmbdic[int(atom.ffatmtyp)]=1
        lst=list(nmbdic.keys())
        lst.sort()
        for i in lst: typlst.append(str(i))
        typlst=['all','unassigned','assigned']+typlst
        self.cmbtyp.SetItems(typlst)
        #if len(typlst) == 1:
        #    self.typ='all'
        self.cmbtyp.SetValue(str(self.typ))

    def SetValeLst(self):
        nmbdic={}
        if self.elm == 'all':
            for atom in self.model.mol.atm:
                nmbdic[len(atom.conect)]=1
        else:
            for atom in self.model.mol.atm:
                if atom.elm != self.elm: continue
                nmbdic[len(atom.conect)]=1
        valelst=list(nmbdic.keys())
        valelst.sort()
        for i in range(len(valelst)): valelst[i]=str(valelst[i])
        valelst=['all']+valelst
        self.cmbvale.SetItems(valelst)
        #if len(valelst) == 1:
        #    self.vale='all'
        self.cmbvale.SetValue(str(self.vale))

        self.SetConLst()

    def SetConLst(self):
        condic={}
        for atom in self.model.mol.atm:
            if atom.elm == 'XX': continue
            if self.elm != 'all' and self.elm != atom.elm: continue
            if self.vale != 'all' and self.vale != len(atom.conect): continue
            condic[self.BondedElm(atom.conect)]=1
        self.conlst=list(condic.keys())
        self.conlst.sort()
        self.conlst=['all']+self.conlst
        self.cmbcon.SetItems(self.conlst)
        try: self.cmbcon.SetValue(self.con)
        except: self.cmbcon.SetValue('all')

    def SetResLst(self):
        resdic={}
        for atom in self.model.mol.atm:
            resdic[atom.resnam]=1
        self.reslst=list(resdic.keys())
        self.reslst.sort()
        self.reslst=['all']+self.reslst
        self.cmbres.SetItems(self.reslst)
        self.cmbres.SetValue(self.res)

    def SetElmLst(self):
        elmdic={}
        for atom in self.model.mol.atm:
            if self.res != 'all' and self.res != atom.resnam: continue
            elmdic[atom.elm]=1
        self.elmlst=list(elmdic.keys())
        self.elmlst.sort()
        self.elmlst=['all']+self.elmlst
        self.cmbelm.SetItems(self.elmlst)
        try: self.cmbelm.SetValue(self.elm)
        except:
            self.cmbelm.SetValue('all')
            self.elm='all'

    def XXSetFFValeLst(self):
        if len(self.atmtyplst) <= 0: return
        ffvalelst=[]
        valedic={}
        if self.ffelm == 'all':
            for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
                if val == self.ffvale: self.valedic[elm]=1
        else:
            for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
                if elm == self.ffelm and val == self.ffvale:
                    self.valedic[elm]=1
        ffvalelst=list(valedic.keys())
        ffvalelst.sort()

        #print 'ffvalelst',ffvalelst

        self.cmbffvale.SetItems(ffvalelst)

        if len(self.ffvalelst) == 1:
            self.ffvale='all'; self.cmbffvale.SetValue(self.ffvale)

    def ListFFAtomTypes(self):
        self.lstctyp.DeleteAllItems()
        self.acttyp=[]

        if len(self.ffname) == '':
            lib.MessageBoxOK("No force files is specified.","")

            return
        if len(self.atmtyplst) <= 0: return
        ###self.ffelm=self.cmbffelm.GetStringSelection()

        for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
            #print 'elm','"'+elm+'"'
            #print 'ffelm','"'+self.ffelm+'"'
            keywd=com.split()
            if self.ffgrp != 'all' and self.ffgrp != keywd[0]: continue
            if self.ffelm != "all" and self.ffelm != elm: continue
            if self.ffvale != 'all' and self.ffvale != val: continue
            if self.ffcls != 'all' and self.ffcls != clsn: continue
            index=self.lstctyp.InsertStringItem(sys.maxsize,str(typn))
            self.lstctyp.SetStringItem(index,1,str(val))
            self.lstctyp.SetStringItem(index,2,str(clsn))
            self.lstctyp.SetStringItem(index,3,nam)
            self.lstctyp.SetStringItem(index,4,com)

            self.acttyp.append(str(typn))

        #if self.atmtyp != 'all': self.lstctyp.Focus(int(self.atmtyp))

    def ListFFCandidates(self):
        self.cantyp=[]
        try:
            self.lstccan.DeleteAllItems()
            if len(self.candidatedic[self.tgtatm]) > 0:
                for i in self.candidatedic[self.tgtatm]:
                    #ii=self.FindDatNmbInAtmTypLst(i)
                    ii=self.atmtypdatnmbdic[i]
                    typn=self.atmtyplst[ii][0]
                    com=self.atmtyplst[ii][3]
                    index=self.lstccan.InsertStringItem(sys.maxsize,str(typn))
                    self.lstccan.SetStringItem(index,1,com)
                    self.cantyp.append(typn)

        except:
            mess="No candidate data is created. Try after auto assignment."
            lib.MessageBoxOK(mess,"")


    def SetTargetAtoms(self,sel):
        targtxt=''; targ=[]
        for i in sel: self.targetdic[i]=1
        targ=list(self.targetdic.keys())
        #for s in self.actatm: targ.append(int(s))
        if len(targ) > 0:
            targ.sort()
            compint=lib.CompressIntData(targ)
            #for i in compint: targtxt=targtxt+str(i)+' '
            nint=len(compint); nd=nint % 2
            for i in range(0,nint-1,2):
                ii=compint[i]; iii=compint[i+1]
                if iii < 0: targtxt=targtxt+str(ii)+str(iii)+','
                else: targtxt=targtxt+str(ii)+','+str(iii)+','
            ns=len(targtxt); targtxt=targtxt[:ns-1]
            if nd != 0:
                if compint[nint-1] < 0:
                    targtxt=targtxt+str(compint[nint-1])
                else:
                    if targtxt == '': targtxt=str(compint[nint-1])
                    else: targtxt=targtxt+','+str(compint[nint-1])

        try: self.tcltgt.SetValue(targtxt)
        except: pass

        self.DispTargetted()
        #strnmb=str(len(self.targetdic.keys()))
        #wx.StaticText(self.pantyp,-1,strnmb,pos=(self.xloctgtmess,self.yloctgtmess),size=(45,18))

    def OnTargetAll(self,event):
        targtxt=''
        targ=[]
        for i in self.actatm:
            targ.append(i); self.targetdic[i]=1
        if len(targ) >  0:
            targ.sort()
            compint=lib.CompressIntData(targ)
            for i in compint: targtxt=targtxt+str(i)+' '
        self.tcltgt.SetValue(targtxt)

        self.DispTargetted()
        #strnmb=str(len(self.targetdic.keys()))
        #wx.StaticText(self.pantyp,-1,strnmb,pos=(self.xloctgtmess,self.yloctgtmess),size=(45,18))

    def OnTargetClear(self,event):
        try:
            self.tcltgt.SetValue('')
            self.targetdic={}
            self.DispTargetted()
            #wx.StaticText(self.pantyp,-1,'0',pos=(self.xloctgtmess,self.yloctgtmess),size=(45,18))
        except: pass

    def XXOnFFAtmTyp(self,event):
        self.ffatmtyp=self.tcltyp.GetValue()

    def GetTargetAtoms(self):
        self.targetdic={}
        targtxt=self.tcltgt.GetValue()
        targ=lib.StringToInteger(targtxt)
        for i in targ: self.targetdic[i]=1

    def OnFFApply(self,event):
        if self.ffname == "":
            lib.MessageBoxOK("No Force filed specified.","")

            return

        self.atmtyp=self.tcltyp.GetValue()
        self.changedcolor=self.cmbcol.GetValue()
        self.GetTargetAtoms()
        #self.batch=True; self.rbtbat.SetValue(True)

        if self.atmtyp == 'all' or self.atmtyp == '':
            if len(self.targetdic) <= 0:
                for i in self.actatm: self.targetdic[i]=1
            self.FindAndAssignAtmTyp()

        else:
            if len(self.atmtyp) <= 0:
                lib.MessageBoxOK("No atmtyp specified.","")

                return

            if len(self.targetdic) <= 0:
                mess="No target atoms are set. Select all?"
                yesno=lib.MessageBoxYesNo(mess,"")
                if yesno:
                    for i in self.actatm: self.targetdic[i]=1
                else: return

            self.AssignAtmTyp()

        lst=list(self.targetdic.keys())
        self.lstctrl.Focus(max(lst))

        self.OnTargetClear(0)

        self.DispUnassign()
        #mess=str(self.NumberOfUnassigned())
        #wx.StaticText(self.pantyp,-1,mess,pos=(self.xlocunasgn,self.ylocunasgn),size=(60,18))
    def OnFFBatch(self,event):
        if len(self.targetdic) <= 0:
            for i in self.actatm: self.targetdic[i]=1
        lst=list(self.targetdic.keys())
        maxlst=max(lst)

        self.FindAndAssignAtmTyp()

        self.OnTargetClear(0)

        self.DispUnassign()
        self.lstctrl.Focus(maxlst)

    def NumberOfUnassigned(self):
        nmb=0
        for atom in self.model.mol.atm:
            if atom.ffatmtyp == 0: nmb += 1
        return nmb

    def AssignAtmTyp(self):

        self.atmtyp=self.tcltyp.GetValue()
        self.changedcolor=self.cmbcol.GetValue()

        self.atmtypsav=self.atmtyp
        self.targetdicsav=self.targetdic
        self.updateddic={}

        targ=list(self.targetdic.keys())
        targ.sort()
        for i in targ:
            ffatmtypold=self.model.mol.atm[i-1].ffatmtyp
            self.model.mol.atm[i-1].ffatmtyp=int(self.atmtyp)
            ffnameold=self.model.mol.atm[i-1].ffname
            self.model.mol.atm[i-1].ffname=self.ffname
            ffatmnamold=self.model.mol.atm[i-1].ffatmnam

            #ii=self.FindDatNmbInAtmTypLst(int(self.atmtyp))
            ii=self.atmtypdatnmbdic[int(self.atmtyp)]
            self.model.mol.atm[i-1].ffatmnam=self.atmtyplst[ii][2]
            self.targetdicsav[i]=[ffatmtypold,ffnameold,ffatmnamold]

            self.updateddic[i]=True
        #print 'targetdicsav',self.targetdicsav
        self.ListAtoms(self.changedcolor)


    def FindAndAssignAtmTyp(self):
        self.atmtyp=self.tcltyp.GetValue()
        self.changedcolor=self.cmbcol.GetValue()

        self.atmtypsav=self.atmtyp
        self.targetdicsav=self.targetdic
        for i in self.targetdicsav: self.targetdicsav[i]=[]

        self.candidatedic={}
        self.updateddic={}

        targ=list(self.targetdic.keys())
        targ.sort(); ntag=len(targ)
        ndon=0; nmul=0; nund=0
        for i in targ:
            elm=self.model.mol.atm[i-1].elm
            vale=len(self.model.mol.atm[i-1].conect)
            for j in self.acttyp:
                #jj=self.FindDatNmbInAtmTypLst(j)
                jj=self.atmtypdatnmbdic[int(j)]
                if jj < 0:
                    print(('atmtyp not found',jj))
                    continue
                if elm != self.atmtyplst[jj][4]: continue
                if vale != int(self.atmtyplst[jj][6]): continue
                if i in self.candidatedic:
                    self.candidatedic[i].append(j)
                else:
                    self.candidatedic[i]=[j]

            mul=True
            if i in self.candidatedic:
                if len(self.candidatedic[i]) == 1: mul=False
                    #ffatmtypold=self.model.mol.atm[i-1].ffatmtyp
                    #ffnameold=self.model.mol.atm[i-1].ffname
                    #self.targetdicsav[i]=[ffatmtypold,ffnameold]
                    #self.model.mol.atm[i-1].ffname=self.ffname
                    #self.model.mol.atm[i-1].ffatmtyp=self.candidatedic[i][0]
                    #self.model.mol.atm[i-1].ffatmnam=self.atmtyplst[jj][2]
                    #self.updateddic[i]=True; ndon += 1
                else:
                    dat=self.atmtypdatnmbdic[int(self.candidatedic[i][0])]
                    cls=self.atmtyplst[dat][1]
                    #cls=self.atmtyplst[int(self.candidatedic[i][0])][1]
                    if cls != -1:
                        mul=False
                        for j in range(1,len(self.candidatedic[i])):
                            varnam=int(self.candidatedic[i][j])
                            jj=self.atmtypdatnmbdic[varnam]
                            if cls != self.atmtyplst[jj][1]:
                                mul=True; break
                if not mul:
                    ffatmtypold=self.model.mol.atm[i-1].ffatmtyp
                    ffnameold=self.model.mol.atm[i-1].ffname
                    ffatmnamold=self.model.mol.atm[i-1].ffatmnam
                    self.targetdicsav[i]=[ffatmtypold,ffnameold,ffatmnamold]
                    self.model.mol.atm[i-1].ffname=self.ffname
                    cand=self.candidatedic[i][0]
                    self.model.mol.atm[i-1].ffatmtyp=int(cand)

                    #print 'i,candic',i,self.candidatedic[i]
                    #print 'atmtyplst',self.atmtyplst

                    #ii=self.FindDatNmbInAtmTypLst(int(self.candidatedic[i][0]))
                    ii=self.atmtypdatnmbdic[int(self.candidatedic[i][0])]
                    ffatmnam=self.atmtyplst[ii][2]
                    # print "ffatmnam",ffatmnam
                    self.model.mol.atm[i-1].ffatmnam=ffatmnam
                    self.updateddic[i]=True; ndon += 1

                    self.candidatedic[i]=[]
                else: nmul += 1
            else: nund += 1

        self.ListAtoms(self.changedcolor)
        #mess="succeeded="+str(ndon)+", multiple candidates="+str(nmul)+",  candidate not found="+str(nund)
        #mess=mess+" out of toral targets="+str(ntag)+".\n"
        #mess=mess+"Do you continue the assignment in interactive mode?"
        #msg=wx.MessageBox(mess,"Result of atom type assignment.",style=wx.YES_NO|wx.ICON_EXCLAMATION)
        #if msg == wx.YES:
        #    self.OnFFSequential(0)

    def OpenInteractivePanel(self):
        print('open InteractiveAssignmentPanel')
        pass

    def XXFindDatNmbInAtmTypLst(self,typnmb):
        i=-1; nmb=int(typnmb)
        for i in range(len(self.atmtyplst)):
            if self.atmtyplst[i][0] == nmb:
                return i; break
        return i
    def XXOnTargetBack(self,event):
        pass

    def OnTargetSkip(self,event):
        pass

    def XXFindNextTargetAtom(self):
        try:
            ncan=0; found=False
            for i in list(self.candidatedic.keys()):
                if i > self.tgtatm and len(self.candidatedic[i]) >= 2:

                    ncan += 1
                    if not found and self.model.mol.atm[i-1].ffatmtyp == 0:
                        self.tgtatm=i; found=True
            yloc=self.yloctypmess
            mess='remaining:'+str(ncan)
            wx.StaticText(self.pantyp,-1,mess,pos=(20,yloc+5),size=(120,18))
            if self.tgtatm < 0:
                self.OnFFBatch(0)
                return

            self.lstctrl.Select(self.tgtatm-1,1)
            self.lstctrl.Focus(self.tgtatm-1)
            self.tcltgtcan.SetValue(str(self.tgtatm))
        except: pass

    def XXOnFFCandidateSelected(self,event):
        # key == 1 from selcted atmtyp list
        if self.tgtatm < 0: return

        if not self.atmtypselected:
            for i in range(len(self.cantyp)):
                if self.lstccan.IsSelected(i):
                    self.atmtyp=self.cantyp[i]; break
        else:
            self.atmtypselected=False
            if self.atmtyp == '': return

        self.atmtypsav=self.atmtyp
        self.updateddic={}
        self.targetdicsav={}
        self.tgtatmsav=self.tgtatm
        i=self.tgtatm
        ffatmtypold=self.model.mol.atm[i-1].ffatmtyp
        self.model.mol.atm[i-1].ffatmtyp=int(self.atmtyp)
        ffnameold=self.model.mol.atm[i-1].ffname
        self.model.mol.atm[i-1].ffname=self.ffname
        self.targetdicsav[i]=[ffatmtypold,ffnameold]
        self.updateddic[i]=True

        self.ListAtoms(self.changedcolor)

        self.FindNextTargetAtom()
        self.ListFFCandidates()

        self.lstctrl.Focus(int(self.tgtatm))

    def XXOnFFQuit(self,event):
        self.batch=True
        #self.pantyp.Destroy()
        #self.CreateAtomTypePanel()
        self.OnSize(0)

        #self.rbtbat.SetValue(True)
        self.tcltgt.SetValue('')
        self.tcltyp.SetValue('')

        self.OnTargetClear(0)

    def XXOnFFSequential(self,event):

        """
        self.tgtatm=-1
        lst=self.candidatedic.keys()
        lst.sort()
        for i in lst:
            if len(self.candidatedic[i]) >= 2: self.tgtatm=i
        if self.tgtatm < 0:
            wx.MessageBox("No candidate atmtyp is set.","",
            style=wx.OK|wx.ICON_EXCLAMATION)
            return
        """
        self.batch=False
        #print 'batch off'
        self.OnSize(0)

        #self.tcltgtcan.SetValue(str(self.tgtatm))
        try:
            self.tgtatm=-1

            self.FindNextTargetAtom()

            self.ListFFCandidates()

        except: pass

    def XXOnFFMulliken(self,event):
        pass

    def XXOnFFRESP(self,event):
        self.btnrsp

    def OnFFUndo(self,event):
        #if self.batch:
        sel=[]
        targ=list(self.targetdicsav.keys())
        targ.sort()
        for i in targ:
            #ffatmtypold=self.model.mol.atm[i-1].ffatmtyp
            #print 'i,sav',i,self.targetdicsav[i][0]
            if len(self.targetdicsav[i]) < 3: continue
            self.model.mol.atm[i-1].ffatmtyp=self.targetdicsav[i][0]
            #ffnameold=self.model.mol.atm[i-1].ffname
            self.model.mol.atm[i-1].ffname=self.targetdicsav[i][1]
            #self.targetdicsav[i]=[ffatmtypold,ffnameold]
            self.model.mol.atm[i-1].ffatmnam=self.targetdicsav[i][2]
            sel.append(i)

        self.ListAtoms('black')

        lst=list(self.targetdicsav.keys())
        maxlst=max(lst)


        self.atmtypsav=0
        self.targetdicsav={}

        self.OnTargetClear(0)
        self.SetTargetAtoms(sel)

        self.lstctrl.Focus(maxlst)
        #else:
        #    i=self.tgtatmsav
        #    self.model.mol.atm[i-1].ffatmtyp=self.targetdicsav[i][0]
        #    self.model.mol.atm[i-1].ffname=self.targetdicsav[i][1]
        #    self.tgtatm=self.tgtatmsav
        #    self.tcltgtcan.SetValue(str(self.tgtatm))
        #    self.ListAtoms('black')

        #    self.lstctrl.Focus(int(self.tgtatm))

        self.DispUnassign()

    def OnFFGroup(self,event):
        self.ffgrp=self.cmbffgrp.GetValue()
        print(('onffgroup',self.ffgrp))

        self.ffelm='all'
        self.ffvale='all'
        self.cmbffvale.SetStringSelection('all')
        self.ffcls='all'
        self.cmbffcls.SetStringSelection('all')

        self.SetFFElementLst()

        self.ListFFAtomTypes()

    def OnFFTable(self,event):
        self.tbl=self.cmbtbl.GetValue()
        if self.tbl != 'none':
            self.atmtyp=''; self.tcltyp.SetValue(self.atmtyp)
        #if self.tbl == 'none': return

    def SetForceField(self):
        self.cmbff.SetItems(self.ffnamelst)

    def SetFFGroupLst(self):
        grpdic={}
        self.ffgrplst=[]
        for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
            keywd=com.split()
            if self.ffgrp != 'all' and self.ffgrp != keywd[0]: continue
            grpdic[keywd[0]]=1
        self.ffgrplst=list(grpdic.keys())
        self.ffgrplst.sort()
        self.ffgrplst=['all']+self.ffgrplst
        self.cmbffgrp.SetItems(self.ffgrplst)
        self.cmbffgrp.SetStringSelection(self.ffgrp)

    def SetFFElementLst(self):
        elmdic={}
        self.ffgrplst=[]
        for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
            keywd=com.split()
            if self.ffgrp != 'all' and self.ffgrp != keywd[0]: continue
            elmdic[elm]=1
        self.ffelmlst=list(elmdic.keys())
        self.ffelmlst.sort()
        self.ffelmlst=['all']+self.ffelmlst
        self.cmbffelm.SetItems(self.ffelmlst)
        self.ffelm='all'
        self.cmbffelm.SetStringSelection(self.ffelm)

        self.SetFFAtmClassLst()

    def SetFFAtmClassLst(self):
        clsdic={}; clslst=[]
        self.ffclslst=[]
        for typn,clsn,nam,com,elm,mass,val in self.atmtyplst:
            keywd=com.split()
            if self.ffgrp != 'all' and self.ffgrp != keywd[0]: continue
            if self.ffelm != 'all' and self.ffelm != elm: continue
            if self.ffvale != 'all' and self.ffvale != val: continue
            clsdic[int(clsn)]=1
        clslst=list(clsdic.keys())
        clslst.sort()
        for i in clslst: self.ffclslst.append(str(i))
        self.ffclslst=['all']+self.ffclslst
        self.cmbffcls.SetItems(self.ffclslst)
        self.ffcls='all'
        self.cmbffcls.SetStringSelection(self.ffcls)

    def SetFFNamesAndFiles(self):
        self.ffnamelst=['TINY','AMBER94','AMBER96','AMBER98','AMBER99',
                        'AMBER99SB','CHARMM19','CHARMM22','CHARMM22CMAP',
                        'DANG','HOCH','MM2','MM3','MM3PRO',
                        'OPLSAA','OPLSAAL','OPLSUA',
                        'SMOOTHAA','SMOOTHUA','WATER']
        self.fffiledic={'TINY':"e:/winfort/tinker/params/tiny.prm",
                        'AMBER94':"e:/winfort/tinker/params/amber94.prm",
                        'AMBER96':"e:/winfort/tinker/params/amber96.prm",
                        'AMBER98':"e:/winfort/tinker/params/amber98.prm",
                        'AMBER99':"e:/winfort/tinker/params/amber99.prm",
                        'AMBER99SB':"e:/winfort/tinker/params/amber99sb.prm",
                        'CHARMM19':"e:/winfort/tinker/params/charmm19.prm",
                        'CHARMM22':"e:/winfort/tinker/params/charmm22.prm",
                        'CHARMM22CMAP':"e:/winfort/tinker/params/charmm22cmap.prm",
                        'DANG':"e:/winfort/tinker/params/dang.prm",
                        'HOCH':"e:/winfort/tinker/params/hoch.prm",
                        'MM2':"e:/winfort/tinker/params/mm2.prm",
                        'MM3':"e:/winfort/tinker/params/mm3.prm",
                        'MM3PRO':"e:/winfort/tinker/params/mm2.prm",
                        'OPLSAA':"e:/winfort/tinker/params/oplsaa.prm",
                        'OPLSAAL':"e:/winfort/tinker/params/oplsaal.prm",
                        'OPLSUA':"e:/winfort/tinker/params/oplsua.prm",
                        'SMOOTHAA':"e:/winfort/tinker/params/smoothaa.prm",
                        'SMOOTHUA':"e:/winfort/tinker/params/smoothua.prm",
                        'WATER':"e:/winfort/tinker/params/water.prm",
                        }
        #self.ffnamelst=self.fffiledic.keys()

    def OnFFChoice(self,event):
        self.ffname=self.cmbff.GetStringSelection()
        self.fffile=self.fffiledic[self.ffname]
        # atmtyplst.append([typnmb,atmnam,coment,elm,mass,valence])
        self.atmtyplst=lib.ReadTinkerAtomType(self.ffname,self.fffile)

        self.AtmTypeDatNumDic()
        self.ffgrp='all'
        self.SetFFGroupLst()
        self.ffelm='all'
        self.SetFFElementLst()
        self.ffcls='all'
        self.SetFFAtmClassLst()

        self.ListFFAtomTypes()

    def AtmTypeDatNumDic(self):
        self.atmtypdatnmbdic={}
        for i in range(len(self.atmtyplst)):
            atmtypnmb=self.atmtyplst[i][0]
            self.atmtypdatnmbdic[int(atmtypnmb)]=i

    def OnVale(self,event):
        self.vale=self.cmbvale.GetStringSelection()
        if self.vale != 'all': self.vale=int(self.vale)

        self.SetConLst()
        try: self.cmbcon.SetStringSelection(self.con)
        except:
            self.cmbcon.SetStringSelection('all')
            self.con='all'
        self.ListAtoms('')

    def OnElement(self,event):
        self.elm=self.cmbelm.GetStringSelection()
        if len(self.elm) == 1: self.elm=' '+self.elm

        self.SetValeLst()
        #try: self.cmbvale.SetStringSelection(self.vale)
        #except:
        self.cmbvale.SetStringSelection('all')
        self.vale='all'

        self.SetConLst()
        #try: self.cmbcon.SetStringSelection(self.con)
        #except:
        self.cmbcon.SetStringSelection('all')
        self.con='all'

        self.SetAtmTypLst()
        try: self.cmbtyp.SetStringSelection(self.typ)
        except:
            self.cmbtyp.SetStringSelection('all')
            self.typ='all'

        self.ListAtoms('')

    def XXOnFFTypAll(self,event):
        self.tcltyp.SetValue('all')

    def OnFFVale(self,event):
        self.ffvale=self.cmbffvale.GetStringSelection()
        if self.ffvale != 'all': self.ffvale=int(self.ffvale)

        self.SetFFAtmClassLst()

        self.ListFFAtomTypes()

    def OnFFElement(self,event):
        self.ffelm=self.cmbffelm.GetStringSelection()
        if len(self.ffelm) == 1: self.ffelm=' '+self.ffelm
        self.ffvale='all'
        self.cmbffvale.SetStringSelection('all')
        self.ffcls='all'
        self.SetFFAtmClassLst()
        self.cmbffcls.SetStringSelection('all')

        self.ListFFAtomTypes()

    def OnFFClass(self,event):
        self.ffcls=self.cmbffcls.GetStringSelection()
        #if self.ffcls != 'all': self.ffcls=self.ffcls
        #self.SetFFAtmClassLst()
        self.ListFFAtomTypes()

    def OnAtomSelected(self,event):
        #print 'selected count',self.lstctrl.GetSelectedItemCount()
        ###if not self.batch: return

        nmb=self.lstctrl.GetSelectedItemCount()
        sel=[]
        for i in range(len(self.actatm)):
            if self.lstctrl.IsSelected(i):
                sel.append(self.actatm[i])
                ###self.lstctrl.Select(i,False)
        #print 'sel',sel
        if len(sel) > 0 and self.batch: self.SetTargetAtoms(sel)

    def OnAtmTypSelected(self,event):
        #try:
        #    self.lstctyp.Focus(int(self.atmtyp))
        #    print 'atmtyp',self.atmtyp
        #except: pass

        nmb=self.lstctyp.GetSelectedItemCount()
        if nmb <= 0:
            if self.batch:self.tcltyp.SetValue('')
            else: self.atmtypinseq=-1
            return
        self.atmtyp=''
        for i in range(len(self.acttyp)):
            if self.lstctyp.IsSelected(i): self.atmtyp=self.acttyp[i]

        self.tcltyp.SetValue(self.atmtyp)
        #else:
        #    self.atmtypselected=True
        #    self.OnFFCandidateSelected(0)

    def OnResidue(self,event):
        self.res=self.cmbres.GetValue()

        self.SetElmLst()
        try: self.cmbelm.SetStringSelection(self.elm)
        except:
            self.cmbelm.SetStringSelection('all')
            self.elm='all'

        self.ListAtoms('')

    def OnSetAll(self,event):
        self.typ='all'; self.res='all'; self.elm='all'; self.vale='all'
        self.con='all'
        self.cmbtyp.SetValue(self.typ)
        self.cmbres.SetValue(self.res)
        self.cmbelm.SetValue(self.elm)
        self.cmbvale.SetValue(self.vale)
        self.cmbcon.SetValue(self.con)

        self.SetElmLst()
        self.SetValeLst()
        #self.SetConLst()
        self.ListAtoms('')

    def OnConect(self,event):
        self.con=self.cmbcon.GetValue()
        self.ListAtoms('')

    def OnAtmTyp(self,event):
        self.typ=self.cmbtyp.GetValue()
        #if self.typ != 'all' and self.typ != 'unassigned' and self.typ != 'assigned':
        if self.typ.isdigit(): self.typ=int(self.typ)
        self.SetAtmTypLst()

        self.ListAtoms('')

    def OnClearColor(self,event):
        self.ListAtoms('black')

    def OnClearAtmtyp(self,event):
        for i in self.actatm:
            self.model.mol.atm[i-1].ffatmtyp=0
            self.model.mol.atm[i-1].ffname=''
        self.ListAtoms('')
        self.DispUnassign()

    def XXOnClearCharge(self,event):
        for i in self.actatm:
            self.model.mol.atm[i-1].ffcharge=0.0
        self.ListAtoms('')

    def OnClose(self,event):
        self.winctrl.Close('AtmtypWin')
        self.Destroy()

    def OnSplitWinChanged(self,event):
        self.sashposition=self.splwin.GetSashPosition()
        self.OnSize(0)

    def OnSize(self,event):
        self.splwin.Destroy()
        self.CreateSplitterWindow()

    def MenuItems(self):
        # Menu items
        mfil= ("File", (
                  ("Open","Open",0),
                  ("Save","",False),
                  ("Save as","",False),
                  ("Print","Unfinished",0),
                  ("Quit","Close plot panel",0)))
        mprm= ("Set parameter directory", (
                  ("ff param","",0),
                  ("ff internal","",0)))
        # msel= ("Select", (

        menud=[mfil,mprm]
        return menud


    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        item=self.plotmenu.GetLabel(menuid)
        bChecked=self.plotmenu.IsChecked(menuid)
        if item == "Open":
            print('open')

        if item == "Save": #xxx.ffp (force field parameter
            pass
        if item == "Save as":
            pass
        if item == "Quit":
            self.OnClose(0)


class OneByOneViewer_Frm(wx.Frame):
    """ modified at 14Dec2015 """
    def __init__(self,parent,id,winpos=[],winsize=[],winlabel='One-by-One',
                 menu=True): #,model,ctrlflag,molnam):
        self.title='One-by-One Viewer'
        #if lib.GetPlatform() == 'MACOSX': winsize=lib.WinSize((215,230)) #(215,180)
        #elif lib.GetPlatform() == 'WINDOWS': winsize=lib.WinSize((215,210)) #(215,180)
        #else: winsize=(215,230)
        self.model=parent; self.mdlwin=self.model.mdlwin
        if len(winpos) <= 0: winpos=lib.WinPos(self.mdlwin) #winpos=[100,100]
        winpos  = lib.SetWinPos(winpos)
        if len(winsize) <= 0: winsize=[230,250] #((215,260)
        winsize = lib.WinSize(winsize)
        wx.Frame.__init__(self,self.mdlwin,id,self.title,pos=winpos,size=winsize,
                          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        #self.parent=parent
        #self.mdlwin=parent
        #self.model=model
        self.winctrl=self.model.winctrl
        self.molnam=self.model.mol.name #wrkmolnam
        #self.SetTitle('OneByOne viewer')
        self.winlabel=winlabel
        self.helpname='OneByOneViewer'
        #
        xsize=winsize[0]; ysize=winsize[1]
        # Create Menu
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            lib.InsertTitleMenu(self.menubar,'[OneByOneViewer]')
            self.Bind(wx.EVT_MENU,self.OnMenu)
        #self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        #self.resetbmp=self.model.setctrl.GetIconBmp('reset')

        self.labellst=['element','atmnam','atmnam+nmb','resnam','resnam+nmb',
                       'frgnam','grpnam']
        self.objlst=[]
        #self.objlst=['residue','chain','group','fragment','all']

        self.objlstdic={}
        self.itemlst=[]
        self.infodic={}
        self.iniobj=''
        #
        self.selshwmode=1 # 0:select, 1:show
        self.focusratio=-1
        self.unfocusratio=-1
        self.shwbda=False
        self.hideh=False
        #self.selectedobj='residue'; self.itemlst=[]; self.curritem=0; self.emptyobj=1

        self.SetObjectList('all')
        self.CreatePanel() #winpos[0],winpos[1],self.size[1],self.size[1])
        self.objcmb.SetItems(self.objlst)
        self.curobj=self.objlst[0]
        self.cunmb=0
        self.SetCurrentObject(self.objlst[0])
        self.DispTotalNumberOfItems()
        self.SetObjectItems()
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Show()

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        hcb=25 #const.HCBOX
        # Reset button
        btnrset=Reset_Button(self.panel,-1,self.OnReset)
        #
        yloc=10
        st2=wx.StaticText(self.panel,-1,"object:",pos=(5,yloc+3),size=(40,18))
        self.objcmb=wx.ComboBox(self.panel,-1,'',choices=self.objlst, \
                              pos=(50,yloc),size=(80,hcb),style=wx.CB_READONLY)
        self.objcmb.Bind(wx.EVT_COMBOBOX,self.OnObject)
        self.objcmb.SetStringSelection('residue')
        self.btnaddto=wx.Button(self.panel,-1,"extract",pos=(140,yloc+2),
                                size=(60,20))
        self.btnaddto.Bind(wx.EVT_BUTTON,self.OnAddObject)
        #btnrset=wx.Button(self.panel,wx.ID_ANY,"Reset",pos=(165,yloc+2),size=(40,20))
        #btnrset.Bind(wx.EVT_BUTTON,self.OnReset)
        #btnrset.SetToolTipString('Restore object data')
        yloc += 30
        self.ckbbnd=wx.CheckBox(self.panel,-1,"add temporary bonds",
                                pos=(15,yloc),size=(150,18))
        self.ckbbnd.Bind(wx.EVT_CHECKBOX,self.OnAddBonds)
        yloc += 25
        self.ckbenv=wx.CheckBox(self.panel,-1,"with env.residues(A)",
                                pos=(15,yloc),size=(145,20))
        self.tclenv=wx.TextCtrl(self.panel,-1,'4.0',pos=(175,yloc),size=(40,20),
                                style=wx.TE_PROCESS_ENTER) # size x 28 <-30
        #self.ckbenv.SetToolTipString('Show object with surrounding atoms')# not supported yet
        lib.SetTipString(self.ckbenv,'Show object with surrounding atoms')#
        #self.ckbenv.Disable()

        yloc += 25
        self.ckblbl=wx.CheckBox(self.panel,-1,"show label",pos=(15,yloc),
                                size=(90,18))
        #self.ckblsl.Bind(wx.EVT_CHECKBOX,self.OnLabel)
        self.ckblbl.Bind(wx.EVT_CHECKBOX,self.OnShowLabel)
        self.cmbshw=wx.ComboBox(self.panel,-1,'',choices=self.labellst, \
                             pos=(110,yloc), size=(110,hcb),style=wx.CB_READONLY)
        yloc += 20
        self.cmbshw.SetStringSelection('resnam+nmb')
        yloc += 8
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),
                      style=wx.LI_HORIZONTAL)
        yloc += 10
        bt1=wx.Button(self.panel,-1,"<",pos=(25,yloc-2),size=(25,20))
        bt1.Bind(wx.EVT_BUTTON,self.OnBackward)
        bt2=wx.Button(self.panel,-1,">",pos=(65,yloc-2),size=(25,20))
        bt2.Bind(wx.EVT_BUTTON,self.OnForward)
        self.stlnmb=wx.StaticText(self.panel,-1,"1",pos=(160,yloc),size=(40,20))
        self.tclnmb=wx.TextCtrl(self.panel,-1,'1',pos=(110,yloc-2),size=(40,20),
                                style=wx.TE_PROCESS_ENTER) # size x 28 <-30
        self.tclnmb.Bind(wx.EVT_TEXT_ENTER ,self.OnDataNumber)
        yloc += 25
        st3=wx.StaticText(self.panel,-1,"item:",pos=(15,yloc+3),size=(35,20))
        self.itmcmb=wx.ComboBox(self.panel,-1,'',choices=self.itemlst, \
                              pos=(50,yloc), size=(100,hcb),style=wx.CB_READONLY)
        self.itmcmb.Bind(wx.EVT_COMBOBOX,self.OnItem)
        #self.itmcmb.SetStringSelection('residue')
        self.btnfcs=wx.ToggleButton(self.panel,wx.ID_ANY,"Focus",
                                    pos=(w-60,yloc+2),size=(50,22))
        self.btnfcs.Bind(wx.EVT_TOGGLEBUTTON,self.OnFocusView)
        self.btnfcs.SetValue(True)
        yloc += 30
        btsize=wx.Button(self.panel,wx.ID_ANY,"Keep view",pos=(25,yloc),
                         size=(80,25))
        btsize.Bind(wx.EVT_BUTTON,self.OnKeepView)
        #btsize.SetToolTipString('Keep view size for focused and unfocused view')
        lib.SetTipString(btsize,'Keep view size for focused and unfocused view')
        self.btncalp=wx.ToggleButton(self.panel,wx.ID_ANY,"Show chain",
                                     pos=(130,yloc),size=(85,25))
        self.btncalp.Bind(wx.EVT_TOGGLEBUTTON,self.OnShowCAlpha)
        self.btncalp.SetValue(False)
        #self.OnShowCAlpha(1)
        #self.btncalp.SetToolTipString('Show C-Alpha chain')
        lib.SetTipString(self.btncalp,'Show C-Alpha chain')

    def OnShowCAlpha(self,event):
        if self.btncalp.GetValue(): self.model.DrawChainCAlpha(True)
        else: self.model.DrawChainCAlpha(False)

    def OnKeepView(self,event):
        focusview=self.btnfcs.GetValue()
        ratio=self.model.mdlwin.draw.GetRatio()
        if focusview: self.focusratio=ratio
        else: self.unfocusratio=ratio

        event.Skip()

    def OnAddBonds(self,event):
        self.DrawCurrentObject()
        event.Skip()

    def AddBonds(self,on):
        self.ckbbnd.SetValue(on)

    def OnShowLabel(self,event):
        self.DrawCurrentObject()
        event.Skip()

    def OnFocusView(self,event):
        self.focusview=self.btnfcs.GetValue()
        self.DrawCurrentObject()
        event.Skip()

    def OnItem(self,event):
        item=self.itmcmb.GetValue()
        try: idx=self.objlstdic[self.curobj].index(item)
        except: return
        self.curnmb=idx
        self.tclnmb.SetValue(str(self.curnmb+1))
        #
        self.DrawCurrentObject()

        event.Skip()

    def OnReset(self,event):
        self.Reset(True)
        event.Skip()
        self.model.Message('Restored molecule object',0,'')
        #lib.MessageBoxOK('Restored molecule object','')

    def Reset(self,drw):
        self.UnsetEnvGrp()

        self.SetObjectList('all')
        self.objcmb.SetValue(self.curobj)
        self.SetObjectItems()
        self.curnmb=0
        self.tclnmb.SetValue(str(self.curnmb+1))
        self.DispTotalNumberOfItems()
        #
        if drw: self.DrawCurrentObject()

    def RemoveObjectInList(self,rmvlst):
        if len(rmvlst) <= 0:
            rmvlst=['residue','chain','group','fragment','all']
        for obj in rmvlst:
            if obj in self.objlst: self.objlst.remove(obj)

    def SetObjectList(self,curobj):
        """
        :param str curobj: 'residue','chain','group','fragment', or 'all'
        """
        object=['residue','chain','group','fragment','all']
        #residue
        obj='residue'
        if curobj == obj or curobj == 'all':
            reslst=self.model.ListResidue3('all')
            if len(reslst) >= 1: self.objlstdic[obj]=reslst
                #if not obj in self.objlst: self.objlst.append(obj)
        # chain
        obj='chain'
        if curobj == obj or curobj == 'all':
            chainlst=self.model.ListChainName()
            if len(chainlst) >= 1: self.objlstdic[obj]=chainlst
                #if not obj in self.objlst: self.objlst.append(obj)
        # group
        obj='group'
        if curobj == obj or curobj == 'all':
            grplst=self.model.ListGroupName()
            if len(grplst) >= 1: self.objlstdic[obj]=grplst
                #if not obj in self.objlst: self.objlst.append(obj)
        # fragment
        obj='fragment'
        if curobj == obj or curobj == 'all':
            frglst=self.model.frag.ListFragmentName()
            ndum=frglst.count('')
            for i in range(ndum): frglst.remove('')
            if len(frglst) >= 1:
                self.objlstdic[obj]=frglst
                #if not obj in self.objlst: self.objlst.append(obj)
        obj='all'
        if curobj == 'all': self.objlstdic[obj]=['all']
        #
        self.objlst=[]
        for obj in object:
            if obj in self.objlstdic: self.objlst.append(obj)
        #
        try:
            self.objcmb.SetItems(self.objlst)
            self.objcmb.SetValue(self.curobj)
        except: pass
        try: self.DispDataNumber()
        except: pass
        self.curnmb=0
        try: self.tclnmb.SetValue(str(self.curnmb+1))
        except: pass
        try: self.DispTotalNumberOfItems()
        except: pass

    def SetCurrentObject(self,curobj):
        if not curobj in self.objlst: return
        self.objcmb.SetValue(curobj)
        self.curobj=curobj
        self.SetObjectItems()

    def SetObjectItems(self):
        #if not self.objlstdic.has_key(self.curobj): return
        itemlst=self.objlstdic[self.curobj]
        if len(itemlst) <= 0: return
            #mess='No items for object='+self.curobj
            #lib.MessageBoxOK(mess,'One-By-OneViewer(SetObjectItems')
            #return
        self.itmcmb.SetItems(itemlst)
        item=itemlst[self.curnmb]
        self.itmcmb.SetValue(item)
        self.DispTotalNumberOfItems()

    def OnDataNumber(self,event):
        self.curobj=self.objcmb.GetStringSelection()
        maxnmb=len(self.objlstdic[self.curobj])
        curnmb=int(self.tclnmb.GetValue())
        if curnmb < 0 or curnmb > maxnmb-1:
            self.curnmb=maxnmb-1
        else: self.curnmb=int(self.tclnmb.GetValue())-1
        self.DataNumber(self.curnmb)

        event.Skip()

    def DataNumber(self,curnmb):
        self.curnmb=curnmb
        item=self.objlstdic[self.curobj][self.curnmb]
        self.itmcmb.SetValue(item)
        self.tclnmb.SetValue(str(self.curnmb+1))
        self.tclnmb.Refresh()
        #
        self.DrawCurrentObject()

    def GetCurObj(self):
        return self.curobj

    def GetCurItemNumber(self):
        return self.curnmb

    def GetCurObjItemNumber(self):
        return len(self.objlstdic[self.curobj])

    def GetCurrentItem(self):
        return self.objlstdic[self.curobj][self.curnmb]

    def SetCurrentItem(self):
        self.curobj=self.objcmb.GetStringSelection()
        maxnmb=len(self.objlstdic[self.curobj])
        curnmb=int(self.tclnmb.GetValue())
        if curnmb < 0 or curnmb > maxnmb-1:
            lib.MessageBoxOK('Larger than the maximum item number!',
                             'OneByOne selector')
            return
        self.curnmb=int(self.tclnmb.GetValue())-1
        self.DispTotalNumberOfItems()
        #
        self.DrawCurrentObject()

    def DrawCurrentObject(self):

        object=self.objlstdic[self.curobj]
        obj=object[self.curnmb]
        # mode self.selshwmode=0 select, 1show
        renv=0.0
        if self.ckbenv.GetValue():
            try: renv=float(self.tclenv.GetValue())
            except: pass
        lbl=''
        if self.ckblbl.GetValue():
            lbl=self.cmbshw.GetStringSelection()
        bnd=False
        if self.ckbbnd.GetValue(): bnd=True
        # fucus view
        focusview=self.btnfcs.GetValue()
        # select
        self.ResetDraw()
        if self.curobj == 'residue': self.model.SetSelectResidue(obj,True)
        elif self.curobj == 'chain': self.model.SetSelectChainNam(obj,True)
        elif self.curobj == 'fragment': self.model.frag.SetSelectFrg(obj,True)
        elif self.curobj == 'group': self.model.SetSelectGroup(obj,True)
        else:
            objnam,resnam=lib.SplitVariableAndValue(self.curobj)
            if objnam == 'res': self.model.SetSelectResidue(obj,True)
            else: pass
        #elif self.curobj == 'all': self.model.SetSelectAtmNam(obj,True)
        mess='Selected '+self.curobj+': '+obj
        # env atoms
        nadd=0; lstenv=[]
        if renv == 0.0: self.UnsetEnvGrp()

        elif renv > 0.0: # set env atoms/residues?
            #nadd,lstenv=self.model.FindRadiusAtoms(renv)
            if self.curobj == 'fragment':
                nadd,lstenv=self.model.FindRadiusFragment(renv)
            else: nadd,lstenv=self.model.FindRadiusResidue1(renv)
            if nadd > 0:
                for i in lstenv: self.model.mol.atm[i].select=True
        # hide hydrogens
        if self.hideh: self.model.SelectHydrogens(False,drw=False)
        # temp bonds
        if bnd: self.model.SetBonds()

        if self.selshwmode == 1:  # show
            self.model.SetShowSelectedOnly(True)
            self.model.SetChangeAtomColor('by element')
            if focusview: self.model.FitToScreen(True,False)
            mess='Shown only '+self.curobj+', '+obj
        savemodel=[]
        if renv > 0.0 and nadd > 0:
            for i in lstenv:
                self.model.mol.atm[i].color=const.RGBColor['yellow']
                savemodel.append(self.model.mol.atm[i].model)
                self.model.mol.atm[i].model=0
                #self.model.SetEnvGrpAtom(i,True)
        # BDA points
        if self.shwbda: self.model.frag.DrawBDAPoint(True)
        else: self.model.frag.DrawBDAPoint(False)
        # set view size
        if focusview and self.focusratio > 0:
            self.model.mdlwin.draw.SetRatio(self.focusratio)
        elif not focusview and self.unfocusratio > 0:
            self.model.mdlwin.draw.SetRatio(self.unfocusratio)
        self.model.Message(mess,0,'')
        if lbl == '': self.model.DrawMol(True)
        else: self.DrawLabel(lbl)
        # recover model
        if len(savemodel) > 0:
            ii=-1
            for i in lstenv:
                ii += 1
                self.model.mol.atm[i].model=savemodel[ii]

    def UnsetEnvGrp(self):
        for atom in self.model.mol.atm:
            atom.envflag=False
            atom.grpnam='base'
            atom.SetElmColor(atom.elm)
            #self.model.SetEnvGrpAtom(i,False)

    def ResetDraw(self):
        self.model.SetSelectAll(False)
        self.model.DrawLabelRemoveAll(False)
        self.model.SetShowAll(True)
        self.model.FitToScreen(True,False)

    def DrawLabel(self,label):
        if label == 'resnam': self.model.DrawLabelRes(True,0)
        elif label == 'resnam+nmb': self.model.DrawLabelRes(True,1)
        elif label == 'element': self.model.DrawLabelElm(True,0)
        elif label == 'atmnam': self.model.DrawLabelAtm(True,1)
        elif label == 'atmnam+nmb': self.model.DrawLabelAtm(True,2)
        elif label == 'frgnam': self.model.frag.DrawLabelFrgNam(True)
        elif label == 'grpnam': self.model.DrawLabelGrpNam(True)

    def OnBackward(self,event):
        self.curobj=self.objcmb.GetStringSelection()
        maxnmb=len(self.objlstdic[self.curobj])
        if self.curnmb == 0: self.curnmb=maxnmb-1
        else: self.curnmb -= 1
        self.tclnmb.SetValue(str(self.curnmb+1))
        item=self.objlstdic[self.curobj][self.curnmb]
        self.itmcmb.SetValue(item)
        #
        self.DrawCurrentObject()

        self.model.NotifyToSubWin(self.winlabel)

        event.Skip()

    def OnForward(self,event):
        self.curobj=self.objcmb.GetStringSelection()
        maxnmb=len(self.objlstdic[self.curobj])
        if self.curnmb == maxnmb-1: self.curnmb=0
        else: self.curnmb += 1
        self.tclnmb.SetValue(str(self.curnmb+1))
        item=self.objlstdic[self.curobj][self.curnmb]
        self.itmcmb.SetValue(item)
        #
        self.DrawCurrentObject()

        self.model.NotifyToSubWin(self.winlabel)

        event.Skip()

    def OnSelectMode(self,event):
        self.selshwmode=0

    def OnShowMode(self,event):
        self.selshwmode=1

    def OnObject(self,event):
        self.curobj=self.objcmb.GetStringSelection()
        self.nitems=len(self.objlstdic[self.curobj])
        self.DispTotalNumberOfItems()
        self.curnmb=0
        self.tclnmb.SetValue(str(self.cunmb+1))
        self.SetObjectItems()
        item=self.objlstdic[self.curobj][self.curnmb]
        self.itmcmb.SetValue(item)
        #
        self.DrawCurrentObject()

        self.model.NotifyToSubWin(self.winlabel)

    def DispTotalNumberOfItems(self):
        maxnmb=len(self.objlstdic[self.curobj])
        self.stlnmb.SetLabel(str(maxnmb))

    def SetInfoText(self,objectname,text):
        self.infodic[objectname]=text

    def OnAddObject(self,event):
        mess='Enter objnam=value, e.g.,"res=HIS"\n or "res=selected".'
        text=wx.GetTextFromUser(mess,caption='Add object')
        if len(text) <= 0: return
        #objnam,value=lib.SplitVariableAndValue(text)
        text=text.strip()
        objnam,resnam=lib.SplitVariableAndValue(text)
        if resnam == 'Selected' or resnam == 'selected' or \
                                                   resnam == 'SELECTED':
            reslst=self.model.ListSelectedResidues()
        else:
            reslst=self.model.ListResidue4(resnam)
        if len(reslst) <= 0:
            mess='No items of object='+text
            lib.MessageBoxOK(mess,'OneByOneViewer(OnAddObject)')
            return
        self.objlstdic[text]=reslst
        curobj=self.objcmb.GetStringSelection()
        self.objlst.append(text)
        self.objcmb.SetItems(self.objlst)
        self.objcmb.SetStringSelection(curobj)

    def ResetObjectList(self,objlst,objlstdic):
        if len(objlst) <= 0:
            mess='subwin.One-by-One(ResetObjectList): Object list is empty.'
            self.model.ConsoleMessage(mess)
            return
        self.objlst=objlst
        self.objlstdic=objlstdic
        self.objcmb.SetItems(self.objlst)
        self.objcmb.SetStringSelection(self.objlst[0])
        self.curobj=self.objlst[0]
        self.SetObjectItems()
        self.SetCurrentItem()

    def AddObjectToList(self,objnam,objlstfordic):
        if len(objnam) <= 0 or len(objlstfordic) <= 0:
            mess='subwin.One-by-One(AddObjectToList): missing object name or'
            mess=mess+' empty objectlst.'
            self.model.ConsoleMessage(mess)
            return
        self.objlst.append(objnam)
        self.objlstdic[objnam]=objlstfordic
        self.objcmb.SetItems(self.objlst)
        self.objcmb.SetStringSelection(objnam)

    def OnInfo(self,event):
        object=self.objcmb.GetValue()
        if object in self.objlstdic:
            nmb=len(self.objlstdic[object])
        else: nmb=0
        if object in self.infodic:
            text=self.infodic[object]
        else: text='no info available'
        mess='number of data='+str(nmb)+'\n'
        mess=mess+text
        lib.MessageBoxOK(mess,'OneByOne viewer')

    def OnClose(self,event):
        self.UnsetEnvGrp()
        self.ResetDraw()
        self.model.DrawMol(True)
        self.Close()

    def Close(self):
        try: self.model.frag.DrawBDAPoint(False)
        except: pass
        self.model.Message('Closed '+self.winlabel,0,'')
        try: self.winctrl.Close(self.winlabel)
        except: pass
        try: self.winctrl.Close('HisFormChanger')
        except: pass


        self.Destroy()

    def OpenMutateResidue(self):
        pass

    def HelpDocument(self):
        self.model.helpctrl.Help(self.helpname)

    def Tutorial(self):
        self.model.helpctrl.Tutorial(self.helpname)

    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        submenu.Append(-1,"Show BDA points",kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        submenu.Append(-1,'Close','Close the window')
        menubar.Append(submenu,'Option')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        # Related functions
        #submenu.AppendSeparator()
        #subsubmenu=wx.Menu()
        #subsubmenu.Append(-1,"ZmtViewer",
        #                  "View geometrical paramters in z-matrix form")
        #subsubmenu.AppendSeparator()
        #subsubmenu.Append(-1,"MutateResidue","Open MutateResidue panel")
        #subsubmenu.Append(-1,"RotCnfEditor",
        #                  "Open Rotate bond conformation editor")
        #subsubmenu.Append(-1,"ZmtCnfEditor",
        #                  "Open Z-matrix conformation editor")
        #subsubmenu.AppendSeparator()
        #subsubmenu.Append(-1,"TINKER","Minimization with TINKER")
        #subsubmenu.Append(-1,"GAMESS","Minimization with GAMESS")
        #submenu.AppendMenu(-1,'Related functions',subsubmenu)
        menubar.Append(submenu,'Help')
        #
        return menubar

    def OnMenu(self,event):
        """ Menu event handler """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        bChecked=self.menubar.IsChecked(menuid)
        # File menu items
        if item == 'Open':
            pass
        if item == "Show BDA points":
            if self.shwbda: self.shwbda=False
            else: self.shwbda=True
        if item == "Hide hydrogens":
            if self.hideh: self.hideh=False
            else: self.hideh=True
        elif item == 'Save ini file':
            pass

        elif item == "Close":
            self.OnClose(1)
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()
        elif item == "ZmtViewer": self.OpenZmtViewer()
        elif item == "MutateResidue": self.OpenMutateResidue()
        elif item == "RotCnfEditor": self.OpenRotCnfEditor()
        elif item == "ZmtCnfEditor": self.OpenZmtcnfEditor()
        elif item == "TINKER": self.ExecTinker()
        elif item == 'GAMESS': self.ExecGAMESS()


class PopupWindow_Frm(wx.Frame):
    def __init__(self,parent,id,model,winpos,winlabel,menulst,tipslst):
        self.title='Popup Window'
        #winsize=(155,135)
        # get item list
        self.mdlwin=parent
        self.model=self.mdlwin.model
        self.menuctrl=self.model.menuctrl
        self.winctrl=self.mdlwin.model.winctrl
        # the menu items are defined in 'MouseManage' class
        self.menulst=menulst
        self.tipslst=tipslst
        nitems=len(self.menulst)
        #winsize=lib.WinSize((155,25*nitems+5))
        winsize=(155,25*nitems+5)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
                          style=wx.MINIMIZE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.winlabel=winlabel

        self.curitem=self.menuctrl.GetMouseOperationMode()

        # create panel
        self.btn=None
        #
        self.CreatePanel()

        self.Bind(wx.EVT_LEAVE_WINDOW,self.OnClose)

    def CreatePanel(self):
        buttons=[]
        # model mode radio buttons
        self.btn=wx.RadioBox(self,wx.ID_ANY,"",choices=self.menulst,
                             style=wx.RA_VERTICAL)
        for i in range(len(self.tipslst)):
            self.btn.SetItemToolTip(i,self.tipslst[i])
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.btn)
        self.SetSizer(layout)
        self.btn.Bind(wx.EVT_RADIOBOX,self.OnButton)
        if len(self.curitem) >= 0: self.btn.SetStringSelection(self.curitem)

    def OnButton(self,event):
        # get object
        obj=event.GetEventObject()
        label=obj.GetStringSelection()
        if label == 'Cancel': label='Off'
        self.menuctrl.OnPopupWindow(self.winlabel,label)
        self.OnClose(1)

    def GetButtonObject(self):
        return self.btn

    def OnClose(self,event):
        self.winctrl.Close(self.winlabel)
        try: self.Destroy()
        except: pass

class ControlPanel_Frm(wx.MiniFrame):
    def __init__(self,parent,id,model,winpos,winlabel): #,ctrlflag,molnam,winpos):
        self.title='Control Panel'
        winsize=(210,460)
        winpos  = lib.SetWinPos(winpos)
        #if const.SYSTEM == const.MACOSX: winsize=(165,400) #375) #380)
        wx.MiniFrame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
          style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent
        self.draw=parent.draw
        self.model=model
        self.mdlwin=model.mdlwin
        self.winctrl=model.winctrl
        self.menuctrl=model.menuctrl

        self.winlabel=winlabel
        #xxself.ctrlflag=model.ctrlflag
        self.stickbold=str(const.DefaultAtomParam["BondThickness"])
        self.sldrbt1=None
        self.fogscale=self.draw.fogscale
        self.fogscale_max=100 # fixed
        self.secscale_max=100 # fixed
        self.stereo=False
        self.prvopacity=100
        self.section=2 # 0: x, 1:y, 2:z-direction
        self.secmod=self.menuctrl.secmod

        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        #self.Bind(wx.EVT_LEAVE_WINDOW,self.OnLeaveControlWin)
        # set menuitems
        self.size=self.GetClientSize()
        # menu items
        menuitemlst=self.model.setctrl.GetParam('control-win-menu')
        self.menulst,self.menudic,self.menustat=self.MakeMenuDic(menuitemlst)
        #
        self.CreatePanel()
        self.Show()

    def MakeMenuDic(self,menuitemlst):
        menulst=[]; menudic={}; menustat={}
        for label,menuitem in menuitemlst:
            menulst.append(label); menudic[label]=menuitem
            items=menuitem.split('-')
            if len(items) == 1: continue
            menulabel=items[1]; menustat[menulabel]=False
        return menulst,menudic,menustat

    def CreatePanel(self):
        # popup control panel
        xpos=0; ypos=0; xsize=self.size[0]; ysize=self.size[1]; pupper=290 #250 #75
        # upper panel
        self.mdlpan=wx.Panel(self,-1,pos=(xpos,ypos),size=(xsize,pupper)) #ysize))
        self.mdlpan.SetBackgroundColour("light gray")
        # Menu
        hcb=const.HCBOX
        xloc = 5
        yloc=10 #5
        st0=wx.StaticText(self.mdlpan,-1,"Menu:",pos=(xloc+5,yloc),size=(35,18))
        self.mdlcmb0=wx.ComboBox(self.mdlpan,-1,'',choices=self.menulst,
                                 pos=(xloc+50,yloc-3), size=(125,hcb),
                                 style=wx.CB_READONLY)   # 22 <-30
        self.mdlcmb0.Bind(wx.EVT_COMBOBOX,self.OnMenu)
        #
        yloc += 22
        lin0=wx.StaticLine(self.mdlpan,pos=(-1,yloc),size=(xsize,2),
                           style=wx.LI_HORIZONTAL)
        # Color
        yloc += 5 #=30 #32
        st01=wx.StaticText(self.mdlpan,-1,"Fog:",pos=(xloc+5,yloc),size=(35,18))
        #st01.SetBackgroundColour('light gray')
        st01.SetForegroundColour('black')
        self.slfog=wx.Slider(self.mdlpan,pos=(xloc+38,yloc),size=(130,18),
                             style=wx.SL_HORIZONTAL)
        self.slfog.Bind(wx.EVT_SLIDER,self.OnFogSlider)
        #fog,scale=self.draw.GetFogScale() #self.ctrlflag.GetCtrlFlag('gradientscale')
        self.slfog.SetMin(0); self.slfog.SetMax(self.fogscale_max)
        self.slfog.SetValue(self.fogscale)

        yloc += 20 # 36
        wx.StaticLine(self.mdlpan,pos=(-1,yloc),size=(xsize,2),
                      style=wx.LI_HORIZONTAL)

        yloc += 5 #73
        st1=wx.StaticText(self.mdlpan,-1,"Color:",pos=(xloc+5,yloc+4),size=(35,18))
        st1.SetForegroundColour("black")
        yloc += 5
        coltext=['','by element','by residue','by chain','by fragment',
                 'by group',
                 '---','red','magenta',
                 'yellow','orange','brown','blue','cyan','green','purple',
                 'white','gray','black','---','on color palette']
        self.mdlcmb1=wx.ComboBox(self.mdlpan,-1,'',choices=coltext, \
                            pos=(xloc+55,yloc-3), size=(120,hcb),style=wx.CB_READONLY)
        self.mdlcmb1.Bind(wx.EVT_COMBOBOX,self.OnColor)
        yloc += 25
        wx.StaticText(self.mdlpan,-1,"Opacity:",pos=(xloc+5,yloc),size=(50,18))
        self.opatcl=wx.TextCtrl(self.mdlpan,-1,'1.0',pos=(xloc+75,yloc-2),
                                size=(40,20),style=wx.TE_PROCESS_ENTER) # size x 28 <-30
        self.opatcl.Bind(wx.EVT_TEXT_ENTER ,self.OnOpacity)

        self.colsampleposx=45;self.colsampleposy=yloc+2
        yloc += 25
        lin1=wx.StaticLine(self.mdlpan,pos=(-1,yloc),size=(200,2),
                           style=wx.LI_HORIZONTAL)
        # Atom Label
        yloc += 5 #=106 #118
        st2=wx.StaticText(self.mdlpan,-1,"Label:",pos=(xloc+5,yloc),size=(35,18))
        st2.SetForegroundColour("black")
        self.mdlckb1 = wx.CheckBox(self.mdlpan,wx.ID_ANY,"atom",
                                   pos=(xloc+50,yloc-2),size=(55,18))
        self.mdlckb1.Bind(wx.EVT_CHECKBOX,self.OnAtmLbl) #ControlPanAtmLbl)
        self.mdlckb2 = wx.CheckBox(self.mdlpan,wx.ID_ANY,"residue",
                                   pos=(xloc+110,yloc-2),size=(70,18))
        self.mdlckb2.Bind(wx.EVT_CHECKBOX,self.OnResLbl)
        lin2=wx.StaticLine(self.mdlpan,pos=(-1,yloc+18),size=(200,2),
                           style=wx.LI_HORIZONTAL)
        # Molecular model
        yloc += 30 #=138 # 147
        st4=wx.StaticText(self.mdlpan,-1,"Model:",pos=(xloc+5,yloc),
                          size=(40,18))
        st4.SetForegroundColour("black")
        mdltxt=["","line","stick","ball & stick","CPK",
                '---',"stereo"] #vdW surface","SA surface","Remove surface"]
        self.mdlcmb2=wx.ComboBox(self.mdlpan,-1,'',choices=mdltxt, \
                            pos=(xloc+55,yloc-6), size=(120,hcb),style=wx.CB_READONLY) # 28<-22
        self.mdlcmb2.Bind(wx.EVT_COMBOBOX,self.OnModel) #ControlPanMdl)

        st5=wx.StaticText(self.mdlpan,-1,"line/stick size",
                          pos=(xloc+15,yloc+20),size=(80,20))
        st5.SetForegroundColour("black")
        self.mdltcl5=wx.TextCtrl(self.mdlpan,-1,self.stickbold,
                       pos=(xloc+120,yloc+20),size=(30,20),style=wx.TE_PROCESS_ENTER)
        self.mdltcl5.Bind(wx.EVT_TEXT_ENTER,self.OnModelStick) #ControlPanStick)
        st6=wx.StaticText(self.mdlpan,-1,"circle/ball scale",
                          pos=(xloc+15,yloc+40),size=(80,20))
        st6.SetForegroundColour("black")
        self.mdltcl6=wx.TextCtrl(self.mdlpan,-1,"1.0",pos=(xloc+120,yloc+40),
                                 size=(30,20),style=wx.TE_PROCESS_ENTER)
        self.mdltcl6.Bind(wx.EVT_TEXT_ENTER,self.OnModelBall) #ControlPanBall)
        self.mdltcl6.Disable()
        st7=wx.StaticText(self.mdlpan,-1,"vdW/SA scale",pos=(xloc+15,yloc+60),
                          size=(80,20))
        st7.SetForegroundColour("black")
        self.mdltcl7=wx.TextCtrl(self.mdlpan,-1,"1.0",pos=(xloc+120,yloc+60),
                                 size=(30,20),style=wx.TE_PROCESS_ENTER)
        self.mdltcl7.Bind(wx.EVT_TEXT_ENTER,self.OnModelVdw) #ControlPanVdw)
        self.mdltcl7.Disable()
        wx.StaticLine(self.mdlpan,pos=(-1,yloc+85),size=(200,2),
                      style=wx.LI_HORIZONTAL)
        # Selection
        yloc += 95 # 80 #218 #24
        self.ckbsec = wx.CheckBox(self.mdlpan,wx.ID_ANY,"Section mode",
                                  pos=(xloc+5,yloc),size=(120,18)) #(70,18))
        self.ckbsec.Bind(wx.EVT_CHECKBOX,self.OnSection)
        self.ckbsec.SetValue(self.secmod)
        yloc += 20
        self.slsec=wx.Slider(self.mdlpan,pos=(xloc+20,yloc),size=(145,18),
                             style=wx.SL_HORIZONTAL)
        self.slsec.Bind(wx.EVT_SLIDER,self.OnSecSlider)
        self.slsec.SetMin(0); self.slfog.SetMax(self.secscale_max)
        self.slsec.SetValue(0)
        yloc += 30
        wx.StaticLine(self.mdlpan,pos=(-1,yloc),size=(200,2),
                      style=wx.LI_HORIZONTAL)
        # lowe command panel
        ysize1=ysize-pupper
        self.cmdpan=wx.Panel(self,-1,pos=(0,pupper),size=(xsize,ysize1),
                             style=wx.DOUBLE_BORDER)
        #self.cmdpan=wx.Panel(self,-1,pos=(xpos,ypos+yupper),size=(xsize,ysize-yupper),style=wx.DOUBLE_BORDER)
        self.cmdpan.SetBackgroundColour("light gray")
        wx.StaticLine(self.cmdpan,pos=(-1,0),size=(200,2),
                      style=wx.LI_HORIZONTAL)
        yloc=8
        self.ckbrad = wx.CheckBox(self.cmdpan,-1,"Select distance(A)",
                                  pos=(xloc+5,yloc),size=(140,18))
        mess='Select atoms/residues within distance from selected atoms'
        #self.ckbrad.SetToolTipString(mess)
        lib.SetTipString(self.ckbrad,mess)
        self.ckbrad.Bind(wx.EVT_CHECKBOX,self.OnSelect) #ControlPanSel)
        self.ckbrad.SetValue(False)
        self.rbtrad1=wx.RadioButton(self.cmdpan,-1,'atom',pos=(20,yloc+18), \
                               style=wx.RB_GROUP)
        self.rbtrad2=wx.RadioButton(self.cmdpan,-1,'residue',pos=(75,yloc+18))
        self.rbtrad1.Bind(wx.EVT_RADIOBUTTON,self.OnSelectAtm) #ControlSelAtm)
        self.rbtrad2.Bind(wx.EVT_RADIOBUTTON,self.OnSelectRes) #ControlSelRes)
        self.rbtrad2.SetValue(True)
        self.tclrad=wx.TextCtrl(self.cmdpan,-1,'4.0',pos=(xloc+145,yloc+18),
                                size=(30,20)) # size x 28 <-30
        self.tclrad.Bind(wx.EVT_TEXT,self.OnSelectRadius)
        self.tclrad.Disable()

        yloc=45 #yloc=174
        self.mdlckb5 = wx.CheckBox(self.cmdpan,wx.ID_ANY,"Make group",
                                   pos=(xloc+5,yloc),size=(150,18))
        self.mdlckb5.Bind(wx.EVT_CHECKBOX,self.OnGroup) #ControlPanMakGrp)
        self.mdltcl9=wx.TextCtrl(self.cmdpan,-1,"group name here",
                                 pos=(xloc+20,yloc+20),size=(150,22)) #22))
        self.mdltcl9.Disable() # not suported  yet
        # OK, Cancel button
        mdlapbt=wx.Button(self.cmdpan,wx.ID_ANY,"Apply",
                          pos=(xloc+125,ysize1-35),size=(50,22))
        mdlapbt.Bind(wx.EVT_BUTTON,self.OnApply)
        mdlcnbt=wx.Button(self.cmdpan,wx.ID_ANY,"Cancel",
                          pos=(xloc+60,ysize1-35),size=(55,22))
        mdlcnbt.Bind(wx.EVT_BUTTON,self.OnCancel)
        mdlokbt=wx.Button(self.cmdpan,wx.ID_ANY,"OK",pos=(xloc+10,ysize1-35),
                          size=(40,22))
        mdlokbt.Bind(wx.EVT_BUTTON,self.OnOK)

    def OnOpacity(self,event):
        try: opacity=float(self.opatcl.GetValue())
        except: return
        if opacity > 1.0: opacity=1.0
        if opacity < 0.0: opacity=0.0
        self.opatcl.SetValue(str(opacity))
        self.model.ChangeOpacity(opacity)
        mess='Opacity was set to '+str(opacity)
        self.model.Message(mess,0,'')
        self.model.DrawMol(True)

    def XXFogScale(self,event):
        self.sliderfog=True

    def DispGroupName(self,grpnam):
        self.mdltcl9.SetValue(grpnam)

    def OnSection(self,event):
        value=self.ckbsec.GetValue()
        #if value:
        #self.model.mousectrl.SetSectionMode(value) #True)
        self.model.SetSection(value)
        self.menuctrl.OnSelect('Section mode',value)
        #self.model.SaveShwAtm(value) #True)
        #self.model.SaveRasPosZ(value) #True)
            #self.ctrlflag.SetCtrlFlag('sectionmode',True)
        #else:
        #    self.model.mousectrl.SetSectionMode(False)
        #    self.model.SaveShwAtm(False)
        #    self.model.SaveRasPosZ(False)
            #self.ctrlflag.SetCtrlFlag('sectionmode',False)
    def SetSectionMode(self,on):
        self.ckbsec.SetValue(on)

    def OnSectionX(self,event):
        self.section=0

    def OnSectionY(self,event):
        self.section=1

    def OnSectionZ(self,event):
        self.section=2

    def OnGroup(self,event): #ControlPanMakGrp(self,event):
        vl=self.mdlckb5.GetValue()
        if vl:
            self.mdltcl9.Enable(); self.mdltcl9.SetValue('')
            self.ckbrad.SetValue(False)
            #self.mdlckb3.SetValue(False)
        else:
            self.mdltcl9.Disable(); self.mdltcl9.SetValue('group name here')

    def OnMenu(self,event):
    #def ControlPanMenu(self,event):
        item=self.mdlcmb0.GetStringSelection()
        if len(item) <= 0: return
        menuitem=self.menudic[item]
        items=menuitem.split('-'); topmenu=items[0]; menulabel=items[1]
        #bChecked=True
        #if self.checkdic.has_key(menulabel):
        #    if self.checkdic[menulabel]: bChecked=False
        #    else: bChecked=True
        #self.checkdic[menulabel]=bChecked
        if self.menustat[menulabel]: self.menustat[menulabel]=False
        else: self.menustat[menulabel]=True
        bChecked=self.menustat[menulabel]
        if topmenu == 'Select':
            self.model.menuctrl.OnSelect(menulabel,bChecked)
        elif topmenu == 'Show':
            self.model.menuctrl.OnShow(menulabel,bChecked)

        self.mdlcmb0.SetStringSelection('')

    def OnSelect(self,event): #ControlPanSel(self,event):
        vl=self.ckbrad.GetValue()
        self.tclrad.SetValue('4.0')
        if vl:
            self.tclrad.Enable()
            #self.mdlckb3.SetValue(False)
            self.mdlckb5.SetValue(False)

    def OnSelectRes(self,event): #ControlSelRes(self,event):
        pass

    def OnSelectAtm(self,event): #ControlSelAtm(self,event):
        pass

    def OnSelectRadius(self,event):
        #print 'mdl sel dis'
        try: self.radius=float(self.tclrad.GetValue())
        except: pass

    def OnModelStick(self,event): #ControlPanStick(self,event):
        try:
            stickbold=float(self.mdltcl5.GetValue())
        except: stickbold=self.stickbold
        self.model.ChangeStickBold(stickbold)

    def OnModelBall(self,event): #ControlPanBall(self,event):
        try:
            atmradsc=float(self.mdltcl6.GetValue())
        except: atmradsc=1.0
        self.model.ChangeAtmRad(atmradsc)

    def OnModelVdw(self,event): #ControlPanVdw(self,event):
        try: vdwradsc=float(self.mdltcl7.GetValue())
        except: vdwradsc=1.0
        self.model.ChangeVdwRad(vdwradsc)

    def OnColor(self,event):
        item=self.mdlcmb1.GetStringSelection()
        if item == '' or item == '---': return
        self.model.ChangeAtomColor(item)
        self.mdlcmb1.SetStringSelection('')

    def OnModel(self,event): #ControlPanMdl(self,event):
        # 0:line, 1:stick, 2:ball-stick, 3:CPK
        mdl=0
        val=self.mdlcmb2.GetValue()

        if val == 'line' or val == 'stick':
            mdl=0
            if val == 'stick': mdl=1
            self.mdltcl5.Enable(); self.mdltcl6.Disable()
            self.mdltcl7.Disable()
        elif val == 'ball & stick':
            mdl=2
            self.mdltcl5.Enable(); self.mdltcl6.Enable(); self.mdltcl7.Disable()
        elif val == 'CPK' or val == 'vdW surface' or val == 'SA surface':
            mdl=3
            self.mdltcl5.Disable(); self.mdltcl6.Disable()
            self.mdltcl7.Enable()
        elif val == 'stereo':
            mdl=4
            self.mdltcl5.Disable(); self.mdltcl6.Disable()
            self.mdltcl7.Disable()
        else:
            self.mdltcl5.Disable(); self.mdltcl6.Disable()
            self.mdltcl7.Disable()
        if mdl == 4:
            if self.stereo:
                self.model.SetStereo(False); self.stereo=False
            else: self.model.SetStereo(True); self.stereo=True
        else: self.model.ChangeDrawModel(mdl)
        self.mdlcmb2.SetStringSelection('')

    #def ControlPanAtmLbl(self,event):
    def OnAtmLbl(self,event):
        on=self.mdlckb1.GetValue()
        if on: self.model.DrawLabelElm(True,1)
        else: self.model.DrawLabelElm(False,1)
        self.model.DrawMol(True)

    def OnResLbl(self,event):
        on=self.mdlckb2.GetValue()
        if on: self.model.DrawLabelRes(True,1)
        else: self.model.DrawLabelRes(False,1)
        self.model.DrawMol(True)

    def OnOK(self,event):
        self.OnApply(event)
        self.OnClose(1)

    def OnCancel(self,event):
        #self.ctrlflag.SetCtrlFlag('controlpanel',False)
        #self.parent.viewmol.DrawMol(True)
        #self.Destroy()
        self.OnClose(1)

    def OnApply(self,event):
        # show commans
        #self.mdlmenutxt=['','show selected only','show all','show distance','show angle',
        #         'add 1H','add 2H','add 3H']
        cmb0chosen=self.mdlcmb0.GetStringSelection()
        # set environment
        #if self.mdlckb3.GetValue(): # Add environment atoms
        #    selobj=0
        #    if self.mdlrbt4.GetValue(): selobj=1
        #    radius=float(self.tclenv.GetValue())
        #    nenv=self.model.MakeEnvGrpByRadius(selobj,radius)
        #    self.model.Message('Number of atom(s) in environment group:'+str(nenv),0,'black')
        nsel,lst=self.model.ListSelectedAtom()
        if nsel <= 0:
            mess='Please select atoms'
            lib.MessageBoxOK(mess,'ControlPanel_Frm(OnApply)')
            return
        if self.ckbrad.GetValue(): # Add selected atoms
            #nsel,lst=self.model.ListSelectedAtom()
            self.savesellst=lst[:]
            selobj=0
            if self.rbtrad2.GetValue(): selobj=1

            radius=float(self.tclrad.GetValue())
            nadd=self.model.SelectByRadius(selobj,radius,1)
            #self.model.Message('Number of selected atom(s):'+str(nsel+nadd),
            #                   0,'black')
        if self.mdlckb5.GetValue(): # make group
            grpnam=self.mdltcl9.GetValue()
            self.model.MakeGroup(grpnam)
            return
        #
        self.SetDefaultValue()

    def SetDefaultValue(self):
        # envcheck box
        #self.mdlckb3.SetValue(False); self.tclenv.Disable()
        #self.mdlrbt4.SetValue(True)
        self.ckbrad.SetValue(False); self.tclrad.Disable()
        self.rbtrad2.SetValue(True)
        # group/molecule name
        self.mdlckb5.SetValue(False)
        self.mdltcl9.Disable()

    def SetFogScale(self,scale):
        self.fogscale=scale
        self.slfog.SetValue(self.fogscale)

    def SetSecScale(self,scale):
        self.slsec.SetValue(scale)

    def OnFogSlider(self,event):
        scale=self.slfog.GetValue()
        self.model.SetFogScale(scale)
        if scale > self.fogscale_max: scale=self.fogscale_max

    def OnSecSlider(self,event):
        #print 'scale',self.slfog.GetValue()
        scale=self.slsec.GetValue()
        scale=float(scale)/float(self.secscale_max) # 0.0-1.0
        self.model.SetSectionZScale(scale)

    def OnPaint(self,event):
        event.Skip()

    def OnClose(self,event):
        #self.ctrlflag.secmod=False
        #self.OnApply(event)
        #self.ctrlflag.SetCtrlFlag('controlpanel',False)
        self.winctrl.Close(self.winlabel)
        try: self.Destroy()
        except: pass

class FragmentByBDA_Frm(wx.Frame):
    """ Not completed yet. 28Feb1024 KK """
    def __init__(self,parent,id,winpos=[],winsize=[]):
        title='Fragment by BDA data'
        if len(winsize) == 0: winsize=lib.WinSize([300,400])
        if len(winpos) == 0: winpos=lib.WinPos(parent)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self, parent,-1, title, size=winsize, #(300,300),
                style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        #
        self.model=parent.model
        self.exedir=parent.model.curdir
        self.winlabel='FragBDAWin'
        # set icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        # Create Menu
        menud=self.MenuDat()
        self.menubar=lib.fuMenu(menud)
        self.SetMenuBar(self.menubar.menuitem)
        lib.InsertTitleMenu(self.menubar,'[FragByBDA]')
        self.menuitem=self.menubar.menuitem
        self.menuitemdic=self.menubar.menuitemdic
        self.Bind(wx.EVT_MENU,self.OnMenu)
        # create panel
        self.bgcolor='light gray'
        self.CreatePanel()
        #
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.Show()

    def CreatePanel(self):
        # create panel
        [w,h]=self.GetClientSize() #self.GetSize()
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour(self.bgcolor)
        #
        hbtn=20; htxt=20
        xloc=10
        yloc=5
        self.stbda=wx.StaticText(self.panel,wx.ID_ANY,'BDA file: ',
                                 pos=(xloc,yloc),size=(w-20,htxt))
        yloc += 25; htcbda=60
        self.tcbda=wx.TextCtrl(self.panel,-1,"",pos=(xloc,yloc),
                size=(w-20,htcbda),style=wx.TE_READONLY|wx.TE_MULTILINE) #|wx.HSCROLL)
        self.SetBDAInfo()
        yloc += htcbda+5
        self.sttrg=wx.StaticText(self.panel,wx.ID_ANY,'Target: ',
                                 pos=(xloc,yloc),size=(w-20,htxt))
        yloc += 25
        self.stcom=wx.StaticText(self.panel,-1,
                                 'Number of unfragmented atoms/total: ',
                                 pos=(xloc,yloc),size=(w-20,htxt))
        yloc += 25; hchklc=h-yloc-60; wchklc=w-20
        self.chklc=CheckListCtrl(self.panel,(xloc,yloc),(wchklc,hchklc),
                                 self.OnCheckList)
        self.chklc.InsertColumn(0,'res1',width=80)
        self.chklc.InsertColumn(1,'res2')
        index=self.chklc.InsertStringItem(sys.maxsize,'ALA001')
        index=self.chklc.InsertStringItem(1,'PHE002')
        yloc=yloc+hchklc+5
        btnsel=wx.Button(self.panel,wx.ID_ANY,"Choose all",pos=(xloc,yloc),
                         size=(70,hbtn))
        btndes=wx.Button(self.panel,wx.ID_ANY,"Unchoose",pos=(xloc+90,yloc),
                         size=(60,hbtn))
        btnshw=wx.Button(self.panel,wx.ID_ANY,"Show in view",pos=(185,yloc),
                         size=(80,hbtn))
        yloc=h-30
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),
                      style=wx.LI_HORIZONTAL)
        yloc += 5
        btncle=wx.Button(self.panel,wx.ID_ANY,"Clear all BDA",pos=(xloc,yloc),
                         size=(75,hbtn))
        btnfrg=wx.Button(self.panel,wx.ID_ANY,"Fragment",pos=(xloc+110,yloc),
                         size=(60,hbtn))
        btnund=wx.Button(self.panel,wx.ID_ANY,"Undo",pos=(200,yloc),
                         size=(40,hbtn))

        #btplt.Bind(wx.EVT_BUTTON,self.OnPlot)
    def OnCheckList(self,boxnmb,value):
        pass

    def SetBDAInfo(self):
        pass

    def OnSize(self,event):
        #self.SavePropChoice(True)
        self.panel.Destroy()
        self.CreatePanel()

    def OnClose(self,event):
        self.model.winctrl.Close(self.winlabel)
        self.Destroy()

    def MenuDat(self):
        # Menu items

        mfil= ("File", (
                  ("Open","Open GAMESS-FMO input/output file",False),
                  ("","",False),
                  #("*Save bitmap","Save bitmap on file",False),
                  #("*Print bitmap","Unfinished",False),
                  ("Quit","Close plot panel",False)))
        mwin= ("Edit/View", (
                  #("Mol viewer","molecule viewer",False),
                  #("","",False),
                  ("BDA data file","BDA data file",False),
                  ("","",False),
                  ("MatPlotLib","MatPlotLib",False)))
        mhlp= ("Help", (
                  ("About","licence remark",False),
                  ("Version","Version",False)))

        #menud=[mfil,mplt,mrep,mwin]
        menud=[mfil,mwin,mhlp]
        return menud

    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        item=self.menuitem.GetLabel(menuid)
        bChecked=self.menuitem.IsChecked(menuid)
        # File menu items
        if item == "Open":
            wcard=['*.bda(BDA data)','*.* (all)']
            direc=self.curdir
            filename=lib.GetFileName(self,wcard,"r",False,"")
            print(('filename',filename))

        if item == "Save log":
            print('save log file')

        if item == "Quit":
            self.OnClose(0)
        # plot menu items

class TipString():
    def __init__(self,parent,string,retmethod=None,font=None,winpos=[],
                 leaveclose=True,bgcolor='white'):
        """ Display tip string. See ListBoxMenu_Frm class for the usage.

        :param obj parent: window object
        :param str string: tip string
        :return: obej - method executed on Close
        """
        self.retmethod=retmethod
        self.tipwinopen=True
        #
        if len(winpos) <= 0: winpos=wx.GetMousePosition()
        if font is None: font=lib.GetFont(5); font.SetPixelSize([7,13])

        textwidth,textheight=lib.GetTextPixelSize(font,string)
        winposx=winpos[1]-10
        winposy=winpos[0]-20
        if winpos[1]-10 <= 0: winposy=20
        if winpos[0]-20 <= 0: winposx=0
        winpos=[winposx,winposy]
        winpos  = lib.SetWinPos(winpos)
        #winwidth=len(string)*fontwidth+5
        winwidth=textwidth+10; winheight=textheight+2
        winsize=[winwidth,winheight]
        self.tipwin=wx.Frame(parent,-1,pos=winpos,size=winsize,
                          style=wx.MINIMIZE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        tipsize=[winwidth-2,winheight-2]
        self.tipwin.SetFont(font)

        string=' '+string
        self.sttip=wx.StaticText(self.tipwin,-1,string,pos=(2,0),size=tipsize) #(winwidth-15,18))
        self.sttip.SetBackgroundColour(bgcolor) #'white')
        self.leaveclose=leaveclose


        if lib.GetPlatform() == 'WINDOWS':
            self.sttip.Bind(wx.EVT_LEAVE_WINDOW,self.OnClose)
        else:
            self.sttip.Bind(wx.EVT_LEFT_DOWN,self.OnClose)
            self.sttip.Bind(wx.EVT_RIGHT_DOWN,self.OnClose)
        self.tipwin.Show()

    def OnClose(self,event):
        if not self.leaveclose: return
        self.Close()
        event.Skip()

    def Close(self):
        if self.retmethod is not None:
            try: self.retmethod('DisplayTipString:closed')
            except: pass

        self.tipwinopen=False
        try: self.tipwin.Destroy()
        except: pass
        try: self.Destroy()
        except: pass

    def SetText(self,text):
        self.sttip.SetLabel(text)

    def IsOpen(self):
        return self.tipwinopen

class ListBoxMenu_Frm(wx.Frame):
    """ An alternative to popup menu.

    :function: Select a menu item by mouse Left button click and show tip by right button click.

    :param obj retmethod: the method will be called after item selection
    :param lst menulst: menu items list
    :param lst tiplst=: tips list
    :param str menulabel=: menu label
    :param bool isthissubmenu: used for internal submenu control
    :return: call retmethod object with selected item and menulabel, retmethod(item,menulabel)
    """

    def __init__(self, parent, id, winpos, winsize, retmethod, menulst, tiplst=[],
                 submenudic={}, subtipdic={}, font=None,
                 select='', menulabel='', menuselected='', dummylst=[], bgcolor=[],
                 winwidth=-1):  # ,ctrlflag,molnam,winpos):
        if len(winpos) <= 0:
            [x, y] = wx.GetMousePosition()
            winposx = x - 20
            winposy = y - 10
            if winposx <= 0: winposx = 0
            if winposy <= 20: winposy = 20
            winpos = [winposx, winposy]
        #winpos = lib.SetWinPos(winpos)
        maxs = 0;
        maxtext = ''
        for s in menulst:
            #s=str(s)
            if len(s) > maxs:
                maxs = len(s);
                maxtext = s
        if font == None:
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            if lib.GetPlatform() == 'WINDOWS':
                hspace=1.0
            else:
                hspace=1.6
        self.textwidth, self.textheight = lib.GetTextPixelSize(font, maxtext, hspace)
        if len(winsize) <= 0:
            maxlistboxheight = 400
            winheight = len(menulst) * self.textheight + 20  # 10
            if lib.GetPlatform() == 'LINUX':
                winheight += self.textheight
            if winheight > maxlistboxheight:
                winheight = maxlistboxheight
            if winwidth <= 0: winwidth = self.textwidth + 30  # 10
            winsize = [winwidth, winheight]
        #                  style=wx.MINIMIZE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, parent, id, pos=winpos, size=winsize,
                          style=wx.MINIMIZE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        self.retmethod = retmethod
        self.menulabel = menulabel
        self.menulst = menulst
        self.tiplst = tiplst
        self.submenudic = submenudic
        self.subtipdic = subtipdic
        self.menuselected = menuselected
        self.submenu = None
        self.tipwin = None
        self.dummylst = dummylst
        if len(dummylst) <= 0: self.dummylst = ['<']
        self.tipwinopen = False
        # self.fontheight=16 #16
        self.maxlistboxmenuheight = 400
        if len(bgcolor) <= 0:
            self.bgcolor = [255,255,150] #'yellow'
        self.SetFont(font) #  GetFont(3, size=12))  # 10))
        #
        # create panel
        self.panel = wx.Panel(self, -1, pos=[0, 0], size=winsize)
        self.panel.SetBackgroundColour('light gray')
        lcsize = [winsize[0] - 4, winsize[1] - 4]
        lcpos = [1, 2]
        if lib.GetPlatform() == 'LINUX':
            if self.menulst[0] != 'CLICK AN ITEM':
                self.menulst.insert(0, 'CLICK AN ITEM')

        self.lcmenu = wx.ListBox(self.panel, -1, choices=self.menulst, pos=lcpos,
                                 size=lcsize, style=wx.LB_SINGLE | wx.LB_HSCROLL)

        self.Bind(wx.EVT_LISTBOX, self.OnSelected)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.lcmenu.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.lcmenu.SetFont(font)
        # self.lcmenu.Bind(wx.EVT_ENTER_WINDOW,self.OnRightClick)
        self.SetBGColor(self.bgcolor)
        # set default selection
        #####if len(select) >= 0: self.SetSelection(select)
        #
        #if lib.GetPlatform() == 'WINDOWS':
        #    self.lcmenu.Bind(wx.EVT_LEAVE_WINDOW, self.OnClose)
        #else:
        self.Bind(wx.EVT_LEFT_DOWN, self.OnClose)
        #
        self.Show()
        # self.SetFocus()

    def SetBGColor(self, bgcolor):
        self.bgcolor = bgcolor
        self.lcmenu.SetBackgroundColour(self.bgcolor)

    def SetSelection(self, item):
        """ Set selection

        :param str item: menu item
        """
        try:
            self.lcmenu.SetStringSelection(item)
        except:
            pass

    def OnSelected(self, event):
        """ Event handler to Return selected item

        :return: call retmethod(selected-item,menulabel)
        """
        self.selected = self.lcmenu.GetStringSelection()
        if self.selected == 'CLICK AN ITEM': return
        if len(self.selected) <= 0: return
        #if selected[:1] in self.dummylst:
        #    self.Close()
        #    return
        if len(self.menuselected) > 0:
            self.selected = self.menuselected + ':' + self.selected
        #
        if self.menulst[0] == 'CLICK AN ITEM': del self.menulst[0]
        if self.selected not in self.submenudic:
            if self.retmethod != None:
                self.retmethod(self.selected, self.menulabel)
            try:
                self.Close()
            except:
                pass
            try:
                if len(self.menuselected) > 0: self.parent.Destroy()
            except:
                pass
        elif self.selected in self.dummylst:
            if self.retmethod != None:
                self.retmethod(self.selected, self.menulabel)
            try:
                self.Close()
            except:
                pass

        else:
            #print('self.selected=',self.selected)

            menulst = self.submenudic[self.selected]
            #print('menulst=',menulst)
            #print('submenudic=',self.submenudic)

            tiplst = []
            for i in range(len(menulst)):
                if menulst[i] in self.submenudic:
                    tiplst.append(self.submenudic[menulst[i]])
                else:
                    tiplst.append('')
            [x, y] = self.GetPosition()
            winpos = [x + 20, y]
            """
            winheight=len(menulst)*self.fontheight+10
            if winheight > self.maxlistboxmenuheight:
                winheight=self.maxlistboxmenuheight
            winsize=[100,winheight]
            """
            winsize = []
            self.submenu = ListBoxMenu_Frm(self, -1, winpos, winsize,
                                           self.retmethod, menulst, tiplst=tiplst,
                                           submenudic=self.submenudic, subtipdic=self.subtipdic,
                                           menulabel=self.menulabel, menuselected=self.selected)
            #print('submenu is created. submenu=',self.submenu)
            self.submenu.Show()

        event.Skip()

    def OnRightClick(self, event):
        """ Open tip string window at mouse position

        """

        return

        if len(self.tiplst) <= 0: return

        pos = self.GetPosition()
        idx = self.lcmenu.HitTest(pos)
        valnam = self.menulst[idx]
        mess = ''
        if idx >= 0 and idx < len(self.menulst):
            try:
                mess = self.tiplst[idx]
            except:
                pass
            # self.lcmenu.SetSelection(idx)
        if len(mess) <= 0: mess = 'No description available.'
        ###self.ShowTipString(mess)
        tipwin = TipString(self, mess, winpos=pos, retmethod=self.Notify)
        self.tipwinopen = True

    def Notify(self, mess):
        self.tipwinopen = False

    def OnClose(self, event):
        self.Close()
        try:
            event.Skip()
        except:
            pass

    def Close(self):
        try:
            if self.tipwinopen: return
        except:
            pass
        try:
            self.tipwin.Destroy()
        except:
            pass
        if self.menulst[0] == 'CLICK AN ITEM': del self.menulst[0]
        try:
            self.Destroy()
        except:
            pass

class XXListBoxMenu_Frm(wx.Frame):
    """ An alternative to popup menu.

    :function: Select a menu item by mouse Left button click and show tip by right button click.

    :param obj retmethod: the method will be called after item selection
    :param lst menulst: menu items list
    :param lst tiplst=: tips list
    :param str menulabel=: menu label
    :param bool isthissubmenu: used for internal submenu control
    :return: call retmethod object with selected item and menulabel, retmethod(item,menulabel)
    """

    def __init__(self, parent, id, winpos, winsize, retmethod, menulst, tiplst=[],
                 submenudic={}, subtipdic={}, font=None,
                 select='', menulabel='', menuselected='', dummylst=[], bgcolor=[],
                 winwidth=-1):  # ,ctrlflag,molnam,winpos):
        if len(winpos) <= 0:
            [x, y] = wx.GetMousePosition()
            winposx = x - 20
            winposy = y - 10
            if winposx <= 0: winposx = 0
            if winposy <= 20: winposy = 20
            winpos = [winposx, winposy]
        #winpos = lib.SetWinPos(winpos)
        maxs = 0;
        maxtext = ''
        for s in menulst:
            if len(s) > maxs:
                maxs = len(s);
                maxtext = s
        if font == None:
            font = GetFont(5);
            font.SetPixelSize([7, 13])
        self.textwidth, self.textheight = GetTextPixelSize(font, maxtext)
        if len(winsize) <= 0:
            maxlistboxheight = 400
            winheight = len(menulst) * self.textheight + 20  # 10
            if GetPlatform() == 'LINUX':
                winheight += self.textheight
            if winheight > maxlistboxheight:
                winheight = maxlistboxheight
            if winwidth <= 0: winwidth = self.textwidth + 30  # 10
            winsize = [winwidth, winheight]
        #                  style=wx.MINIMIZE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        wx.Frame.__init__(self, parent, id, pos=winpos, size=winsize,
                          style=wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        self.retmethod = retmethod
        self.menulabel = menulabel
        self.menulst = menulst
        self.tiplst = tiplst
        self.submenudic = submenudic
        self.subtipdic = subtipdic
        self.menuselected = menuselected
        self.submenu = None
        self.tipwin = None
        self.dummylst = dummylst
        if len(dummylst) <= 0: self.dummylst = ['<']
        self.tipwinopen = False
        # self.fontheight=16 #16
        self.maxlistboxmenuheight = 400
        if len(bgcolor) <= 0:
            # self.bgcolor=[255,255,153,1.0] #'yellow'
            self.bgcolor = 'yellow'
        self.SetFont(GetFont(3, size=12))  # 10))
        #
        # create panel
        self.panel = wx.Panel(self, -1, pos=[0, 0], size=winsize)
        self.panel.SetBackgroundColour('light gray')
        lcsize = [winsize[0] - 4, winsize[1] - 4]
        lcpos = [1, 2]
        if GetPlatform() == 'LINUX':
            if self.menulst[0] != 'CLICK AN ITEM':
                self.menulst.insert(0, 'CLICK AN ITEM')

        self.lcmenu = wx.ListBox(self.panel, -1, choices=self.menulst, pos=lcpos,
                                 size=lcsize, style=wx.LB_SINGLE | wx.LB_HSCROLL)

        self.Bind(wx.EVT_LISTBOX, self.OnSelected)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.lcmenu.Bind(wx.EVT_RIGHT_DOWN, self.OnRightClick)
        self.lcmenu.SetFont(font)
        # self.lcmenu.Bind(wx.EVT_ENTER_WINDOW,self.OnRightClick)
        self.SetBGColor(self.bgcolor)
        # set default selection
        #####if len(select) >= 0: self.SetSelection(select)
        #
        if GetPlatform() == 'WINDOWS':
            self.lcmenu.Bind(wx.EVT_LEAVE_WINDOW, self.OnClose)
        else:
            self.Bind(wx.EVT_LEFT_DOWN, self.OnClose)
        #
        self.Show()
        # self.SetFocus()

    def SetBGColor(self, bgcolor):
        self.bgcolor = bgcolor
        self.lcmenu.SetBackgroundColour(self.bgcolor)

    def SetSelection(self, item):
        """ Set selection

        :param str item: menu item
        """
        try:
            self.lcmenu.SetStringSelection(item)
        except:
            pass

    def OnSelected(self, event):
        """ Event handler to Return selected item

        :return: call retmethod(selected-item,menulabel)
        """
        selected = self.lcmenu.GetStringSelection()
        if selected == 'CLICK AN ITEM': return
        if len(selected) <= 0: return
        #if selected[:1] in self.dummylst:
        #    self.Close()
        #    return
        if len(self.menuselected) > 0:
            selected = self.menuselected + ':' + selected
        #
        if self.menulst[0] == 'CLICK AN ITEM': del self.menulst[0]
        if selected not in self.submenudic:
            if self.retmethod != None:
                self.retmethod(selected, self.menulabel)
            try:
                self.Close()
            except:
                pass
            try:
                if len(self.menuselected) > 0: self.parent.Destroy()
            except:
                pass
        elif self.selected in self.dummylst:
            if self.retmethod != None:
                self.retmethod(selected, self.menulabel)
            try:
                self.Close()
            except:
                pass

        else:
            menulst = self.submenudic[selected]
            tiplst = []
            for i in range(len(menulst)):
                if menulst[i] in self.submenudic:
                    tiplst.append(self.submenudic[menulst[i]])
                else:
                    tiplst.append('')
            [x, y] = self.GetPosition()
            winpos = [x + 20, y]
            """
            winheight=len(menulst)*self.fontheight+10
            if winheight > self.maxlistboxmenuheight:
                winheight=self.maxlistboxmenuheight
            winsize=[100,winheight]
            """
            winsize = []
            self.submenu = ListBoxMenu_Frm(self, -1, winpos, winsize,
                                           self.retmethod, menulst, tiplst=tiplst,
                                           submenudic=self.submenudic, subtipdic=self.subtipdic,
                                           menulabel=self.menulabel, menuselected=selected)
            self.submenu.Show()
        event.Skip()

    def OnRightClick(self, event):
        """ Open tip string window at mouse position

        """

        return

        if len(self.tiplst) <= 0: return

        pos = self.GetPosition()
        idx = self.lcmenu.HitTest(pos)
        valnam = self.menulst[idx]
        mess = ''
        if idx >= 0 and idx < len(self.menulst):
            try:
                mess = self.tiplst[idx]
            except:
                pass
            # self.lcmenu.SetSelection(idx)
        if len(mess) <= 0: mess = 'No description available.'
        ###self.ShowTipString(mess)
        tipwin = TipString(self, mess, winpos=pos, retmethod=self.Notify)
        self.tipwinopen = True

    def Notify(self, mess):
        self.tipwinopen = False

    def OnClose(self, event):
        self.Close()
        try:
            event.Skip()
        except:
            pass

    def Close(self):
        try:
            if self.tipwinopen: return
        except:
            pass
        try:
            self.tipwin.Destroy()
        except:
            pass
        if self.menulst[0] == 'CLICK AN ITEM': del self.menulst[0]
        try:
            self.Destroy()
        except:
            pass


class MemoryFiler(wx.MiniFrame):
    def __init__(self,parent,id,winpos,winsize,title,model,mode,wildcard='',
                 presetname=''):
        # mode: 'read','save','saveas','rename',or 'delete'
        self.title=title
        if len(winsize) > 0: self.winsize=winsize
        else: self.winsize=[200,250]
        winpos  = lib.SetWinPos(winpos)
        wx.MiniFrame.__init__(self,parent,id,title,pos=winpos,size=self.winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.texteditor=parent # text editor
        self.model=model # Model instance
        self.mode=mode
        #
        self.textbuffobj=self.model.textbuff
        self.petitscriptfile=''
        #
        if wildcard == '': self.widlcard=['All']
        else: self.wildcard=wildcard
        self.nameext=self.wildcard[0]
        if self.nameext.find('Python') >= 0: self.nameext='.py'
        self.presetname=presetname
        # memory file acrchive
        scriptdir=self.model.setctrl.GetDir('Scripts')
        archfile='petit-scripts.pyarch'
        self.archfile=os.path.join(scriptdir,archfile)
        self.archfile=lib.ReplaceBackslash(self.archfile)
        #
        self.curtextnam=''
        self.textnamlst=self.RecoverTextInArchiveFile()

        self.CreatePanel()

        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Show()

    def CreatePanel(self):
        # create select panel on left hand side
        [w,h]=self.GetClientSize()
        ysize=h; hbtn=30; btnloc=h-hbtn+5
        xpos=0; ypos=0
        self.panel=wx.Panel(self,-1,pos=(xpos,ypos),size=(w,h))
        self.panel.SetBackgroundColour("light gray")
        xloc=10; yloc=5
        wx.StaticText(self.panel,wx.ID_ANY,'Text name list:',pos=(xloc+5,yloc),
                      size=(100,20))
        yloc += 20
        hclb=h-yloc-hbtn-90 #120 #50;
        wclb=w-20
        self.lbdat=wx.ListBox(self.panel,-1,pos=(xloc,yloc),size=(wclb,hclb),
                                      style=wx.LB_HSCROLL|wx.LB_SORT) #
        self.lbdat.Bind(wx.EVT_LISTBOX,self.OnSelectText)
        #self.lbdat.Bind(wx.EVT_RIGHT_DOWN,self.OnDataRightClick)
        self.lbdat.Set(self.textnamlst)
        #self.lbdat.SetToolTipString('List of text name in TextBuffer')
        lib.SetTipString(self.lbdat,'List of text name in TextBuffer')
        yloc += hclb+10; xsize=w-20
        yloc=h-110 #140 #75
        wx.StaticText(self.panel,wx.ID_ANY,'Text name:',pos=(xloc,yloc+5),
                      size=(80,20))
        self.cmbwcd=wx.ComboBox(self.panel,-1,'',choices=self.wildcard, \
              pos=(w-90,yloc-4), size=(80,20),style=wx.CB_READONLY|wx.LB_SINGLE)
        self.cmbwcd.Bind(wx.EVT_COMBOBOX,self.OnWildCard)
        self.cmbwcd.SetStringSelection(self.wildcard[0])
        yloc += 25
        self.tclnam=wx.TextCtrl(self.panel,-1,self.presetname,pos=(xloc,yloc),
                                size=(wclb,20))
        yloc += 25
        xloc=15
        btndel=wx.Button(self.panel,wx.ID_ANY,'Del',pos=(xloc,yloc),
                         size=(40,20))
        btndel.Bind(wx.EVT_BUTTON,self.OnDelText)
        #btndel.SetToolTipString('Delete text from memory')
        lib.SetTipString(btndel,'Delete text from memory')
        btnlod=wx.Button(self.panel,wx.ID_ANY,'Save',pos=(xloc+50,yloc),
                         size=(50,20))
        btnlod.Bind(wx.EVT_BUTTON,self.OnSaveText)
        #btnlod.SetToolTipString('Save text on memory')
        lib.SetTipString(btnlod,'Save text on memory')
        btnopn=wx.Button(self.panel,wx.ID_ANY,'Open',pos=(xloc+110,yloc),
                         size=(50,20))
        btnopn.Bind(wx.EVT_BUTTON,self.OnOpenText)
        #btnopn.SetToolTipString('Open text')
        lib.SetTipString(btnopn,'Open text')
        yloc += 25
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),
                      style=wx.LI_HORIZONTAL)
        yloc += 8
        btnlod=wx.Button(self.panel,-1,'Load',pos=(xloc,yloc),size=(45,20))
        btnlod.Bind(wx.EVT_BUTTON,self.OnLoad)
        #btnlod.SetToolTipString('Load text from archive file')
        lib.SetTipString(btnlod,'Load text from archive file')
        btnstr=wx.Button(self.panel,-1,'Store',pos=(xloc+55,yloc),size=(45,20))
        btnstr.Bind(wx.EVT_BUTTON,self.OnStore)
        #btnstr.SetToolTipString('Store text on archive file')
        lib.SetTipString(btnstr,'Store text on archive file')
        btncan=wx.Button(self.panel,-1,'Close',pos=(xloc+110,yloc),size=(45,20))
        btncan.Bind(wx.EVT_BUTTON,self.OnClose)
        #btncan.SetToolTipString('Close the panel')
        lib.SetTipString(btncan,'Close the panel')
        """
        yloc += 25
        wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        xloc=10
        btnpus=wx.Button(self.panel,wx.ID_ANY,'Push',pos=(xloc,yloc),size=(40,20))
        btnpus.Bind(wx.EVT_BUTTON,self.OnPush)
        btnpus.SetToolTipString('Send command to the interpreter for execution')
        btnrun=wx.Button(self.panel,wx.ID_ANY,'Run',pos=(xloc+50,yloc),size=(40,20))
        btnrun.Bind(wx.EVT_BUTTON,self.OnRun)
        btnrun.SetToolTipString('Run')
        btncan=wx.Button(self.panel,wx.ID_ANY,'Cancel',pos=(xloc+110,yloc),size=(50,20))
        btncan.Bind(wx.EVT_BUTTON,self.OnCancel)
        btncan.SetToolTipString('Cancel')
        """
    def GetPyShellObj(self):
        pyshell=self.model.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='PyShell is not active.'
            lib.MessageBoxOK(mess,'Memory filer')
        return pyshell

    def OnRun(self,event):
        """runfile(filename) :Execute all commands in file as if they were typed
         into the shell.
        run(command,prompt,verbos):Execute command as if it was typed in
        directly.
        """
        textnam=self.GetTextNameInput()
        if textnam == '': return
        self.curtextnam=textnam
        pyshell=self.GetPyShellObj()
        if not pyshell: return
        script=self.textbuffobj.GetText(self.curtextnam)
        print(('script',script))
        pyshell.shell.run(script)
        #pyshell.shell.prompt()
        pyshell.shell.insertLineBreak()

    def OnPush(self,event):
        textnam=self.GetTextNameInput()
        if textnam == '': return
        self.curtextnam=textnam
        pyshell=self.GetPyShellObj()
        if not pyshell: return
        cmd=self.textbuffobj.GetText(self.curtextnam)
        pyshell.shell.push(cmd,silent=False)
        pyshell.shell.insertLineBreak()
        #pyshell.shell.addHistory(cmd)
        #pyshell.shell.propmt() #write(cmd)
    def OnSelectText(self,event):
        self.curtextnam=self.lbdat.GetStringSelection()
        self.tclnam.SetValue(self.curtextnam)

    def OnLoad(self,event):
        self.textnamlst=self.RecoverTextInArchiveFile()
        print(('textnamlst',self.textnamlst))
        self.ResetTextNameList()
        mess='Loaded from text archive file='+self.archfile
        self.texteditor.SetStatusText(mess,0)

        #self.lbdat.Set(self.textnamlst)
    def OnStore(self,event):
        if not os.path.exists(self.archfile):
            mess='Archive file not found. file='+self.archfile
            lib.MessageBoxOK(mess,'MomoryFiler(OnStore)')
            return
        self.textbuffobj.SaveTextOnArchiveFile(self.archfile)
        mess='Stored on archive file='+self.archfile
        self.texteditor.SetStatusText(mess,0)

    def ResetTextNameList(self):
        self.textnamlst=self.textbuffobj.ListTextNames()
        lst=[]
        if self.nameext == 'All': lst=self.textnamlst
        else:
            for nam in self.textnamlst:
                items=nam.split('.')
                if len(items) == 1: ext=''
                else: ext=items[1].strip()
                if self.nameext == '.py':
                    if ext == 'py': lst.append(nam)
                else:
                    if ext != 'py': lst.append(nam)
        self.lbdat.Set(lst)

    def RecoverTextInArchiveFile(self):
        textnamlst=[]
        if not os.path.exists(self.archfile):
            mess='Archive file not found. file='+self.archfile
            lib.MessageBoxOK(mess,'MomoryFiler(RecoverTextInArchiveFile)')
            return textnamlst
        self.textbuffobj.StoreTextInArchiveFile(self.archfile)
        textnamlst=self.textbuffobj.ListTextNames()
        mess='Loaded from text archive file='+self.archfile
        self.texteditor.SetStatusText(mess,0)
        return textnamlst

    def ReadArchFile(self,filename):
        textdic={}
        f=open(filename,'r')

        f.close()
        return textidc

    def RestoreTextNames(self):
        self.textnamlst=self.textbuffobj.ListTextNames()

    def OnWildCard(self,event):
        self.nameext=self.cmbwcd.GetValue()
        if self.nameext.find('Python') >= 0: self.nameext='.py'
        self.ResetTextNameList()

    def OnCancel(self,event):
        pass

    def GetTextNameInput(self):
        textnam=self.tclnam.GetValue()
        textnam=textnam.strip()
        if len(textnam) <= 0:
            mess='Select or input a text name in "Text name".'
            lib.MessageBoxOK(mess,'Memory Filer')
        return textnam

    def OnOpenText(self,event):
        textnam=self.GetTextNameInput()
        if textnam == '': return
        self.curtextnam=textnam
        text=self.textbuffobj.GetText(self.curtextnam)
        self.texteditor.ClearText()
        self.texteditor.AppendTo(text)
        mess='Opened '+self.curtextnam
        self.texteditor.SetStatusText(mess,0)
        #self.OnClose(1)
    def OnSaveText(self,event):
        textnam=self.GetTextNameInput()
        if textnam == '': return
        #textnam=self.tclnam.GetValue()
        text=self.texteditor.GetText()
        if textnam != self.curtextnam:
            self.textbuffobj.SaveTextAs(textnam,text)
            self.curtextnam=textnam
            self.ResetTextNameList()
            mess='Saved as'+self.curtextnam
        else:
            self.textbuffobj.SaveText(text)
            mess='Saved '+self.curtextnam
        self.texteditor.SetStatusText(mess,0)
        #self.OnClose(1)

    def OnSaveTextAs(self,event):
        textnam=self.GetTextNameInput()
        if textnam == '': return
        self.curtextnam=textnam
        text=self.texteditor.GetText()
        textname='' # get from panel
        self.textbuffobj.SaveTextAs(textname,text)
        self.ResetTextNameList()
        mess='Saved as '+self.curtextnam
        self.texteditor.SetStatusText(mess,0)
        #self.OnClose(1)

    def OnDelText(self,event):
        textnam=self.GetTextNameInput()
        if textnam == '': return
        self.textbuffobj.DeleteText(textnam)
        self.ResetTextNameList()
        mess='Deleted '+textnam
        self.texteditor.SetStatusText(mess,0)

    def OnResize(self,event):
        self.panel.Destroy()
        self.SetMinSize([200,250])
        self.SetMaxSize([600,2000])
        self.CreatePanel()

    def OnClose(self,event):
        self.Destroy()

class TextEditor_Frm(wx.Frame):
    def __init__(self,parent,id,winpos=[],winsize=[],title='TextEditor',
                 text='',textfile=None,retmethod=None, mode='Edit',
                 scriptmode=False,filemenu=True,bgcolor=[255,255,255]):

        self.title=title
        self.winlabel=title
        if len(winsize) <= 0: winsize  = lib.WinSized([400,200])
        if len(winpos) <= 0: winpos  = [0,20]
        wx.Frame.__init__(self,parent,id,title,pos=winpos,size=winsize)
        """ Editor/Script editor supprting memory file

        :param str mode: 'Edit', 'View or 'Simple'
        :param str title: title
        :param str text: text data
        :param obj retmethod: method object
        :return: title and text by callingretmethod(title,text)
        """
        self.parent=parent # mdlwin
        self.bgcolor=bgcolor
        try: self.model=self.parent.model
        except: self.model=None
        self.mode=mode
        self.scriptmode=scriptmode
        #if self.mode == '': self.mode='Edit'
        self.retmethod=retmethod
        self.filemenu=filemenu
        if textfile is not None:
            if os.path.exists(textfile):
                with open(textfile,'r') as f:
                    text=f.read()
            else:
                text=''
        self.text=text
        self.newtext=text
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        #if self.parent:
        #    try: self.SetIcon(self.parent.icon)
        #    except: pass
        # Menu
        self.stepmenuid=wx.NewId()
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'['+self.title+']')
        #
        #
        #self.panel=None
        #self.input=None
        #self.CreatePanel()
        # accept drop files
        droptarget=lib.DropFileTarget(self)
        self.SetDropTarget(droptarget)
        #
        self.inpfile=textfile
        self.savetext=''
        #self.input.SetValue(self.newtext)
        self.loadfile=''
        self.savefile=''
        self.cancel=False
        self.curtextname=''
        self.curpos=0
        self.stepnmb=0
        self.stepbystep=False
        self.expanded=False
        self.savtext=''
        self.findpos=0
        #
        self.panel=None
        self.input=None
        self.CreatePanel()
        self.input.SetValue(self.newtext)
        #self.input.Bind(wx.EVT_TEXT_ENTER,self.OnTextEntered)
        self.Bind(wx.EVT_TEXT,self.OnTextEntered)
        self.input.Bind(wx.EVT_TEXT_MAXLEN,self.OnTextMaxLen)
        self.input.Bind(wx.EVT_TEXT_PASTE,self.OnTextPaste)
        #self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)
        #self.input.Bind(wx.EVT_KEY_DOWN,self.OnKeyDown)

        self.input.SetMaxLength(0) # too late to be practical!

        self.input.SetBackgroundColour("white")
        self.input.SetForegroundColour("black")
        #
        self.statusbar=self.CreateStatusBar()
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-4,-6])
        if not self.retmethod: retmethod='None'
        else: retmethod=self.retmethod.__name__
        mess='Mode='+self.mode+', Return method='+retmethod
        self.statusbar.SetStatusText(mess,1)
        # Event handlers
        self.Bind(wx.EVT_MENU,self.OnMenu)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        #
        self.Show()

    def XXOnLeftDown(self,event):
        self.curpos=self.input.GetInsertionPosition()
        print(('leftdownat ',self.curpos))
        event.Skip()

    def CreatePanel(self):
        size=self.GetClientSize()
        self.panel=wx.Panel(self,pos=[0,0],size=size)
        # buttons
        btnheight=0
        if self.mode == 'Edit': btnheight=30
        pansize=[size[0],size[1]-btnheight]
        self.input=wx.TextCtrl(self.panel,pos=[0,0],size=pansize,
                              style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_NOHIDESEL)
        self.input.SetEditable(True)
        self.input.SetBackgroundColour(self.bgcolor)
        #self.input.SetEditable(False)
        pos=[0,size[1]-btnheight]
        pansize=[size[0],btnheight]
        yloc=pos[1]+5
        if self.scriptmode:
            xloc=pansize[0]-260
            self.btnexp=wx.Button(self.panel,-1,"Expand",pos=[xloc,yloc],
                                  size=(60,20))
            self.btnexp.Bind(wx.EVT_BUTTON,self.OnExpandFile)
            mess='Inline expand all or selected file names'
            #self.btnexp.SetToolTipString(mess)
            lib.SetTipString(self.btnexp,mess)
            self.ckbstp=wx.CheckBox(self.panel,-1,"Step-by-step",
                                    pos=(xloc+90,yloc),size=(100,18))
            self.ckbstp.Bind(wx.EVT_CHECKBOX,self.OnStepByStep)
            self.ckbstp.SetValue(self.stepbystep)
            btnrun=wx.Button(self.panel,-1,"Run",pos=[xloc+190,yloc],
                             size=(50,20))
            btnrun.Bind(wx.EVT_BUTTON,self.OnRun)
            #btnrun.SetToolTipString('Run text(python script) in "PyShell" console')
        else:
            #xloc += 60
            xloc=pansize[0]-160
            btnapl=wx.Button(self.panel,-1,"Apply",pos=[xloc,yloc],size=(50,22))
            btnapl.Bind(wx.EVT_BUTTON,self.OnApply)
            mess='Return text to parent return method and close the panel'
            #btnapl.SetToolTipString(mess)
            lib.SetTipString(btnapl,mess)
            if self.mode == 'Edit' and self.retmethod is None: btnapl.Disable()
            btncan=wx.Button(self.panel,-1,"Close",pos=[xloc+70,yloc],
                             size=(60,22))
            btncan.Bind(wx.EVT_BUTTON,self.OnCancel)
            #btncan.SetToolTipString('Cancel edit and close the panel')
            lib.SetTipString(btncan,'Cancel edit and close the panel')

    def SetWinTitle(self,title):
        self.title=title
        self.SetTitle(title)

    def GetSaveFileName(self):
        return self.savefile

    def GetLoadFileName(self):
        return self.loadfile

    def OnExpandFile(self,event):
        self.savetext=''; self.expanded=False
        [frompos,topos]=self.input.GetSelection()
        if frompos == topos: # no selection
            text=self.input.GetValue()
            frompos=0; topos=self.input.GetLastPosition()
        else:
            [frompos,topos]=self.input.GetSelection()
            if lib.IsWxVersion2():
                lineno=self.input.PositionToXY(frompos)
            else:
                [retcode,lineno]=self.input.PositionToXY(frompos)
            if lib.IsWxVersion2():
                text=self.input.GetString(frompos,topos)
            else:
                text = self.input.GetValue()[frompos:topos]
        text=self.ExpandFile(text)
        if len(text) > 0:
            self.savtext=self.input.GetValue()
            self.expanded=True
            self.input.Remove(frompos,topos)
            self.input.SetInsertionPoint(frompos)
            self.input.WriteText(text)
        else:
            lib.MessageBoxOK('Failed to expand','ScriptEditor(OnExpand)')

    def ExpandFile(self,text):
        """ Expand file in text """
        fileindicator='#file#'
        filenamedic={}
        textlst=text.split('\n')
        lineno=-1
        for s in textlst:
            lineno += 1
            if s[:6] == '#file#':
                filename=s[6:].strip()
                filename=lib.RemoveQuots(filename)
                if os.path.exists(filename): filenamedic[lineno]=filename
        if len(filenamedic) <= 0: return text
        #
        lineno=-1; curtext=-1; newtextlst=[]
        for s in textlst:
            lineno += 1; curtext += 1
            if lineno in filenamedic:
                filename=filenamedic[lineno]
                if os.path.exists(filename):
                    newtextlst.append('# begin expand file='+filename)
                    f=open(filename,'r')
                    for s in f.readlines(): newtextlst.append(s.rstrip())
                    newtextlst.append('# end expand file='+filename)
                    f.close()
                else: continue
            else: newtextlst.append(s)
            #newtextlst.append(s)
        #
        newtext=''
        for s in newtextlst: newtext=newtext+s+'\n'
        newtext=newtext[:-1]
        return newtext

    def OnStepByStep(self,event):
        value=self.ckbstp.GetValue()
        self.SetStepByStep(value)

    def SetStepByStep(self,on):
        self.stepbystep=on
        self.prvpos=-1; self.curpos=-1
        if on:
            mess='ScriptEditor: Step-by-step execution starts'
            self.model.ConsoleMessage(mess)
            self.statusbar.SetStatusText('Step-by-step run=ON',0)
            self.stepnmb=0
        else:
            nchars=self.input.GetLastPosition()
            self.input.SetStyle(0,nchars,wx.TextAttr("black","white"))
            self.statusbar.SetStatusText('Step-by-step run=OFF',0)
            mess='ScriptEditor: Step-by-step execution ends. Number of blocks='
            mess=mess+str(self.stepnmb)
            self.model.ConsoleMessage(mess)

    def OnApply(self,event):
        self.cancel=False
        if self.retmethod is not None:
            self.ReturnText()
        #self.OnClose(1)

    def OnRun(self,event):
        if self.stepbystep:
            nc=self.SetSelectBlock()
            if nc <= 0: return
        #
        text=self.input.GetStringSelection()
        if self.stepbystep:
            mess='# Script block number='+str(self.stepnmb)
            self.model.ConsoleMessage(mess)
        #
        if len(text) <= 0:
            text=self.input.GetValue()
        text=self.ExpandFile(text)
        if len(text.strip()) <= 0:
            mess='No text is opened.'
            self.SetStatusText(mess,0)
            return
        pyshell=self.model.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='PyShell is not active.'
            lib.MessageBoxOK(mess,'Text editor')
        #
        self.model.mdlwin.SetFocus()
        #
        tempfile=self.MakeTempFile(text)
        tempfile=tempfile.replace('\\','//')
        # pyshell.shell.runfile(tempfile) # do not work as expected!
        #py3#method='execfile('+"'"+tempfile+"'"+')'
        method = 'exec(open(' + "'" + tempfile + "'" + ').read())'
        pyshell.shell.run(method)
        #pyshell.shell.prompt()
        #pyshell.shell.insertLineBreak()
    def SetSelectBlock(self):
        """ SetSelect text between '#-#' marks (step-by-step excution block)


        """
        nc=0
        nchars=self.input.GetLastPosition()
        if nchars <= 0: return
        self.input.SetStyle(0,nchars,wx.TextAttr("black","white"))
        if self.prvpos >= nchars:
            self.prvpos=-1
            mess='End of script. Would you like to repeat?'
            dlg=lib.MessageBoxYesNo(mess,'ScriptEditor(Run step-by-step')
            #if dlg.ShowModal() == wx.ID_NO:
            if not dlg:
                self.SetStepByStep(False)
            #else: self.prvpos=-1
            return nc
        #
        text=self.input.GetValue()
        if self.prvpos < 0:
            self.prvpos=text.find('\n#-#')
            if self.prvpos < 0:
                mess='Step-by-step indicator,"#-#", not found'
                lib.MessageBoxOK(mess,'Script Editor(SetSelectBlock)')
                return nc
            else: self.prvpos += 5
        #
        text=text[self.prvpos:] #self.input.GetRange(self.prvpos,nchars)
        curpos=text.find('\n#-#')
        if curpos < 0:  self.curpos=nchars
        else: self.curpos=curpos+self.prvpos
        #
        nc=self.curpos-self.prvpos
        if nc > 0:
            self.input.SetSelection(self.prvpos,self.curpos)
            #self.input.Refresh()
            color=[51,153,255] # [0.2,0.6,1.0]
            self.input.SetStyle(self.prvpos,self.curpos-1,
                                wx.TextAttr("white",color))
            self.prvpos=self.curpos+5
            if curpos < 0: self.prvpos=nchars
            self.stepnmb += 1
        return nc

    def OnKeyDown(self,event):
        self.inpt.EmulateKeyPress(event)
        keycode=event.GetKeyCode()
        print(('keycode',keycode))
        event.Skip()

    def ClearSelection(self):
        self.input.SetSelction=(-1,0)

    def MakeTempFile(self,text):
        scrdir=self.model.setctrl.GetDir('Scratch')
        if not os.path.isdir(scrdir):
            mess='Not found "Scratchs" directory.'
            lib.MessageBoxOK(mess,'TextEditor(MakeTempFile)')
            return
        tempfile='texteditor-temp.py'
        tempfile=os.path.join(scrdir,tempfile)
        f=open(tempfile,'w')
        f.write(text)
        f.close()
        return tempfile

    def SupressRotate(self):
        """  Supress Model.Rotate() method calls """
        text=self.input.GetValue()
        newtext=''
        textlst=text.split('\n')
        find=False; rotx=0; roty=0; rotmode='free'; rotm=rotmode
        for s in textlst:
            if s[:10] == 'fum.Rotate':
                xy=lib.GetStringBetweenChars(s[10:],'[',']')
                items=xy.split(',')
                try:
                    x=int(items[0]); y=int(items[1])
                except:
                    x=0; y=0
                rotm=lib.GetStringBetweenChars(s[10:],'(',')')
                items=rotm.split(',')
                rotm=items[0].strip()
                if rotm != rotmode:
                    find=False
                    if rotx != 0 and roty != 0:
                        newtext=newtext+'fum.Rotate('+rotmode+', ['+str(rotx)
                        newtext=newtext+','+str(roty)+'])\n'
                if not find:
                    rotmode=rotm; rotx=x; roty=y
                else:
                    rotx += x; roty += y
                find=True
            else:
                if find:
                    newtext=newtext+'fum.Rotate('+rotmode+', ['+str(rotx)+','
                    newtext=newtext+str(roty)+'])\n'
                    find=False
                    rotx=0; rotx=0
                newtext=newtext+s+'\n'
        newtext=newtext[:-1]
        self.input.SetValue(newtext)

    def SupressZoom(self):
        """  Supress Model.Zoom() method calls """
        text=self.input.GetValue()
        newtext=''
        textlst=text.split('\n')
        find=False; zoom=0; z=0
        for s in textlst:
            if s[:8] == 'fum.Zoom':
                z=0
                try: z=int(lib.GetStringBetweenChars(s[8:],'(',')'))
                except: pass
                if not find: zoom=z
                else: zoom += z
                find=True
            else:
                if find:
                    newtext=newtext+'fum.Zoom('+str(zoom)+')\n'
                    find=False
                    zoom=0; z=0
                newtext=newtext+s+'\n'
        newtext=newtext[:-1]
        self.input.SetValue(newtext)

    def AddFileNameList(self):
        """ Add filename list """
        text=self.input.GetValue()
        textlst=text.split('\n')
        filenamelst=[]
        find=False; filename=''; line=-1; insline=-1
        for s in textlst:
            line += 1
            if s[:8] == 'filename':
                items=s.split('=')
                name=items[0].strip()
                filenamelst.append(name)
                insline=line
            #newtext=newtext+s+'\n'
        if insline >= 0:
            filenamelst.sort()
            text=lib.ListToString(filenamelst)
            text=text.replace('"','')
            text='filenamelst='+text
            textlst.insert(insline+1,text)
        newtext=''
        for s in textlst: newtext=newtext+s+'\n'
        newtext=newtext[:-1]
        self.input.SetValue(newtext)

    def AddLineNumbers(self):
        text=self.input.GetValue()
        newtext=''
        textlst=text.split('\n')
        nlines=float(len(textlst))
        figs=int(log10(nlines))+1
        n=0; form='%0'+str(figs)+'d'
        for s in textlst:
            n += 1; newtext=newtext+(form % n)+' '+s+'\n'
        newtext=newtext[:-1]
        self.input.SetValue(newtext)

    def DelLineNumbers(self):
        text=self.input.GetValue()
        newtext=''
        textlst=text.split('\n')
        figs=textlst[0]
        figs=figs.split(' ',1)[0].strip()
        n=len(figs)

        if n <= 0: return
        try: ifig=int(figs)
        except: return
        #if figs.isdigit():
        for s in textlst:
            s=s[n+1:]
            newtext=newtext+s+'\n'
        newtext=newtext[:-1]
        self.input.SetValue(newtext)

    def AddDelFourSpaces(self,add):
        """ Add/Delete four spaces at line head

        :params bool add: True for add, False for delete
        """
        text=self.input.GetStringSelection()
        if len(text) <= 0:
            text=self.input.GetValue()
            self.input.Clear()
        textlst=text.split('\n')
        textlst=textlst[:-1]
        newtext=''
        if add: # add '#'
            for s in textlst: newtext=newtext+4*' '+s+'\n'
        else: # del #
            for s in textlst: newtext=newtext+s[4:]+'\n'
        self.input.WriteText(newtext)

    def CommentOutLines(self,on):
        text=self.input.GetStringSelection()
        if len(text) <= 0:
            text=self.input.GetValue()
            self.input.Clear()
        textlst=text.split('\n')
        textlst=textlst[:-1]
        newtext=''
        if on: # add '#'
            for s in textlst: newtext=newtext+'#'+s+'\n'
        else: # del #
            for s in textlst:
                if s[:1] == '#':
                    newtext=newtext+s[1:]+'\n'
                else: newtext=newtext+s+'\n'
        self.input.WriteText(newtext)

    def OnCancel(self,event):
        self.cancel=True
        self.OnClose(1)

    def SetLoadFile(self,filename):
        if not os.path.exists(filename):
            mess='file "'+filename+'" is not found.'
            lib.MessageBoxOK(mess,'TextEditor_Frm:SetLoadFile')
            return
        self.loadfile=filename

    def ChangeBackgroundColor(self):
        color=lib.ChooseColorOnPalette(self.panel,True,-1)
        #color=[255*col[0],255*col[1],255*col[2]]
        self.input.SetBackgroundColour(color)

    def ChangeTextColor(self):
        color=lib.ChooseColorOnPalette(self.panel,True,-1)
        #color=[255*col[0],255*col[1],255*col[2]]
        self.input.SetForegroundColour(color)

    def AddText(self,sa,text):
        #try: self.input.AppendText(text+'\n')
        #except: pass
        sa.append(text+'\n')
        self.last=self.input.GetLastPosition()

    def AppendTo(self,text):
        self.input.AppendText(text)

    def OnTextEntered(self,event):
        if self.mode == 'Edit':
            self.newtext=self.input.GetValue()
        else:
            pass
            ###mess='You can not change the text in "View" mode.'
            #self.statusbar.SetStatusText(mess)
            ###lib.MessageBoxOK(mess,'TextEditor')

    def OnTextPaste(self,event):
        self.newtext=self.input.GetValue()

    def AppendTextFromFile(self,filename):
        """ not completed """

        self.ClearText()

        mess="\n"+"... append file="+filename+"\n"
        self.input.AppendText(mess)

        self.input.LoadFile(filename)
        rline=self.input.GetNumberOfLines()
        #if rline < nline:
        #    mess="\n"+"... read "+str(rline)+" lines of total "+str(nline)+" lines in file="+filename+"\n"
        #    self.input.AppendText(mess)
        #else:
        mess="\n"+"... end of "+editor+". number of lines="+str(rline)+"\n"
        self.input.AppendText(mess)

    def LoadTextFromFile(self,filename):
        if not os.path.exists(filename):
            mess='File not found. file='+filename
            self.statusbar.SetStatusText(mess,0)
            #lib.MessageBox(mess,'LoadTextFromfile')
            return
        self.savetext=self.input.GetValue()
        self.input.LoadFile(filename)
        self.newtext=self.input.GetValue()

    def ClearText(self):
        self.input.Clear()
        self.savetext=self.newtext
        self.newtext=''

    def GetText(self):
        text=self.input.GetValue()
        return text

    def OpenMemoryFiler(self):
        """
        :paam str mode: 'Restore','Read','Save','SaveAs','Rename',or 'Delete'
        """
        if not self.model: return
        if not self.model.textbuff:
            mess='TextBuffer object is not availabel.'
            lib.MessageBoxOK(mess,'TextEditor(OpenMemoryFile)')
            return
        title='Memory filer'
        pos=self.GetPosition()
        size=self.GetClientSize()
        winpos=[pos[0]+size[0],pos[1]+20]
        winsize=[]
        wcard=['Python(*.py)','Others','All']
        presetname=''; mode=''
        #if mode == 'Save': presetname=self.curtextname
        memfiler=MemoryFiler(self,-1,winpos,winsize,title,self.model,mode,
                        wildcard=wcard,presetname=presetname)
        #
    def InputFileNames(self):
        wcard='python(*.py,*.fupy)|*.py;*.fupy|All(*.*)|*.*'
        filenames=lib.GetFileNames(self.panel,wcard,"r",True,"")
        if len(filenames) <= 0: return
        text=''
        for name in filenames:
            head,ext=os.path.splitext(name)
            if ext == '.fupy':
                if os.path.exists(name):
                    f=open(name,'r')
                    for file in f.readlines():
                        file=file.strip()
                        nc=file.find('#')
                        if nc >= 0: file=file[:nc].strip()
                        if len(file) <= 0: continue #file[:1] == '#': continue
                        file=lib.RemoveQuots(file)
                        if file[:6] == '#file#': file=file[6:].strip()
                        if not os.path.exists(file): continue
                        file=file.replace('\\','//')
                        text=text+'#file# "'+file+'"\n'
                    f.close()
            else:
                file=name.replace('\\','//')
                text=text+'#file# "'+name+'"\n'
        #text='#file#'+text
        pos=self.input.GetInsertionPoint()
        self.input.SetInsertionPoint(pos)
        self.input.WriteText(text)

    def Undo(self):
        if self.input.CanUndo(): self.input.Undo()
        if self.expanded and len(self.savtext) > 0:
            self.input.SetValue(self.savtext)
            self.savtext=''; self.expanded=False

    def OnTextMaxLen(self,event):
        last=self.input.GetLastPosition()
        mess="Exceeded max. length="+str(last)
        #self.statusbar.SetStatusText(mess)
        lib.MessageBoxOK(mess,"")

        """ SetMaxLength(len) len=0 can change the max"""

    def OnMove(self,event):
        try:
            self.panel.Destroy()
            self.CreatePanel()
            self.input.SetValue(self.newtext)
        except: pass
        self.FileNameMess()

    def OnResize(self,event):
        self.OnMove(1)

    def GetScratchDir(self):
        try: scrdir=self.model.setctrl.GetDir('Scratch')
        except: scrdir=os.getcwd()
        return scrdir

    def GetTempFileName(self):
        tmpfile=''
        scrdir=self.GetScratchDir()
        tmpfile=os.path.join(scrdir,'ScriptEditor.tmp')
        return tmpfile

    def FileNameMess(self):
        if self.inpfile is not None:
            if len(self.inpfile) > 0: self.SetLabel(self.inpfile)

    def Help(self):
        if self.scriptmode:
            helpdir=self.model.setctrl.GetDir('FUdocs')
            helpfile='ScriptEditor//html//ScriptEditor.html'
            helpfile=os.path.join(helpdir,helpfile)
            title='ScriptEditor Help'
            #HelpTextWin_Frm(self,title=title,textfile=helpfile,fumodel=self.model)
            [x,y]=self.GetPosition()
            winpos=[x+20,y+20]
            HelpMessage(helpfile,title=title,winpos=winpos,parent=self)
        else:
            mess='Not available.'
            lib.MessageBoxOK(mess,'Text editor')

    def OpenDropFiles(self,filenames):
        if len(filenames) <= 0: return
        else: filename=filenames[0]
        self.OpenFile(filename)

    def OpenFile(self,filename):
        if len(filename) <= 0: return
        self.savetext=self.input.GetValue()
        base,ext=os.path.splitext(filename)
        if ext == '.gz':
            unzipfile=base
            retcode=lib.ZipFile(unzipfile,filename,False)
            if not retcode:
                mess='Failed to unzip file='+filename
                lib.MessageBoxOK(mess,'ScriptEditor(Open file)')
                return
            filename=unzipfile
        self.input.LoadFile(filename)
        self.inpfile=filename
        self.FileNameMess()

    def OnMenu(self,event):
        """ Menu handler
        """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        # File menu
        curdir=os.getcwd()
        testdir=self.model.setctrl.GetDir('Tests')
        if item == "Open file":
            if self.scriptmode: os.chdir(testdir)
            wcard='all(*.*)|*.*'
            if self.scriptmode:
                wcard='pycode(*.py;*.logging)|*.py;*.logging|all(*.*)|*.*'
            filename=lib.GetFileName(self.panel,wcard,"r",True,"")
            self.OpenFile(filename)
            if self.scriptmode: os.chdir(curdir)
        elif item == 'Save':
            if self.inpfile is None:
                mess='No input file. Use "Save As" menu'
                lib.MessageBoxOK(mess,'Text(Script) Editor')
                return
            filename=self.inpfile
            head,tail=os.path.split(filename)
            base,ext=os.path.splitext(tail)
            if ext == '.gz':
                tmpfile=self.GetTempFileName()
                self.input.SaveFile(tmpfile)
                retcode=lib.ZipFile(tmpfile,filename,True)
                os.remove(tmpfile)
                if not retcode:
                    mess='Failed to make zip file='+filename
                    lib.MessageBoxOK(mess,'ScriptEditor(Save file as)')
                    return
            else: self.input.SaveFile(filename)
            self.savefile=filename
            self.input.SaveFile(filename)
        elif item == "Save file as":
            if self.scriptmode: os.chdir(testdir)
            wcard='all(*.*)|*.*'
            filename=lib.GetFileName(self.panel,wcard,"w",True,"")
            if len(filename) <= 0: return
            head,tail=os.path.split(filename)
            base,ext=os.path.splitext(tail)
            if ext == '.gz':
                tmpfile=self.GetTempFileName()
                self.input.SaveFile(tmpfile)
                retcode=lib.ZipFile(tmpfile,filename,True)
                os.remove(tmpfile)
                if not retcode:
                    mess='Failed to make zip file='+filename
                    lib.MessageBoxOK(mess,'ScriptEditor(Save file as)')
                    return
            else: self.input.SaveFile(filename)
            self.savefile=filename
            self.ReturnText()
            if self.scriptmode: os.chdir(curdir)
        # momory files
        elif item == 'Open memory filer': self.OpenMemoryFiler()
        elif item == 'Input file names': self.InputFileNames()
        #
        elif item == "Quit": self.OnClose(1)
        # Edit menu
        elif item == "Undo edit": self.Undo()
        elif item == "Redo edit": self.input.Redo()
        elif item == "Find":  self.Find()
        elif item == "Replace": self.Replace()
        elif item == "Select all": self.input.SelectAll()
        elif item == "Clear Selection": self.ClearSelection()
        elif item == "Add line numbers": self.AddLineNumbers()
        elif item == "Del line numbers": self.DelLineNumbers()
        elif item == "Add 4-spaces at line head":
            self.AddDelFourSpaces(True)
        elif item == "Del 4-spaces at line head":
            self.AddDelFourSpaces(False)
        elif item == "Clear":
            self.savetext=self.input.GetValue()
            self.ClearText() #editor.Clear()
        if self.mode == "Edit" and item == "Undo Clear":
            if len(self.savetext) <= 0:
                try: self.statusbar.SetStatusText("Unable to undo")
                except:
                    try: lib.MessageBoxOK("Unable to undo","")
                    except: pass
                return
            self.input.SetValue(self.savetext)
            self.newtext=self.savetext
            self.savetext=''
        if item == "Copy": self.input.Copy()
        if item == "Paste": # does not work in READ_ONL+Y mode!
            self.input.Paste()
            self.newtext=self.input.GetValue()
        # modify menu
        if item == "Supress Rotate": self.SupressRotate()
        if item == "Supress Zoom": self.SupressZoom()
        if item == "Add filename list": self.AddFileNameList()
        if item == "Comment out lines": self.CommentOutLines(True)
        if item == "Uncomment out lines": self.CommentOutLines(False)
        # Help menu
        elif item == "Help": self.Help()

    def OnFind(self,event):
        self.lenstr=len(self.finddata.GetFindString())

    def OnReplace(self,event):
       self.lenstr=len(self.replacedata.GetFindString())

    def ReturnText(self):
        if self.cancel: self.newtext=self.text
        else: self.newtext=self.input.GetValue()

        if self.retmethod is not None:
            try: self.retmethod(self.title,self.newtext,self.cancel)
            except:
                mess='Failed to execute return method.'
                mess=mess+'Save text data on file?'
                ans=lib.MessageBoxYesNo(mess,'TextEditor_Frm')
                if ans:
                    filename=lib.GetFileName(None,'','w',True,'')
                    self.input.SaveFile(filename)
        else: pass

    def OnClose(self,event):
        """
        if self.cancel: self.newtext=self.text
        else: self.newtext=self.input.GetValue()

        try: self.retmethod(self.title,self.newtext,self.cancel)
        except:
            mess='Failed to execute return method.'
            mess=mess+'Save text data on file?'
            ans=lib.MessageBoxYesNo(mess,'TextEditor_Frm')
            if ans == wx.YES:
                filename=lib.GetFileName(None,'','w',True,'')
                self.input.SaveFile(fileName)
        """
        #if self.retmethod is not None: self.ReturnText()
        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        try: self.Destroy()
        except: pass

    def Find(self):
        self.lenstr=0
        style=0
        title='Find string'
        self.finddata=wx.FindReplaceData()
        flags=wx.FD_DEFAULT_STYLE
        self.finddata.SetFlags(flags)
        self.fnddlg=wx.FindReplaceDialog(self.input,self.finddata,title,style)
        self.fnddlg.Bind(wx.EVT_FIND_CLOSE,self.OnFindClose)
        self.fnddlg.Bind(wx.EVT_FIND,self.OnFind)
        if lib.IsWxVersion2():
            self.fnddlg.Bind(wx.EVT_COMMAND_FIND_NEXT,self.OnFindNext)
        else:
            self.fnddlg.Bind(wx.EVT_FIND_NEXT, self.OnFindNext)
        self.fnddlg.Show()

    def Replace(self):
        self.lenstr = 0
        title = 'Replace string'
        style = wx.FR_REPLACEDIALOG
        self.replacedata = wx.FindReplaceData()
        flags = wx.FD_DEFAULT_STYLE
        self.replacedata.SetFlags(flags)
        self.rpldlg = wx.FindReplaceDialog(self.input, self.replacedata, title,
                                           style)
        self.rpldlg.Bind(wx.EVT_FIND_CLOSE, self.OnReplaceClose)
        if lib.IsWxVersion2():
            self.rpldlg.Bind(wx.EVT_COMMAND_FIND_NEXT, self.OnFindNextForReplace)
            self.rpldlg.Bind(wx.EVT_COMMAND_FIND_REPLACE, self.OnFindReplace)
            self.rpldlg.Bind(wx.EVT_COMMAND_FIND_REPLACE_ALL, self.OnReplaceAll)
        else:
            self.rpldlg.Bind(wx.EVT_FIND_NEXT, self.OnFindNextForReplace)
            self.rpldlg.Bind(wx.EVT_FIND_REPLACE, self.OnFindReplace)
            self.rpldlg.Bind(wx.EVT_FIND_REPLACE_ALL, self.OnReplaceAll)
        self.rpldlg.Show()

    def OnFindNext(self,event):
        finddata=event.GetEventObject().GetData()
        findstr=finddata.GetFindString()
        flags=finddata.GetFlags()
        downward=False
        if (flags & wx.FR_DOWN) == wx.FR_DOWN: downward=True
        nstr=len(findstr)
        lastpos=self.input.GetLastPosition()
        loop=True
        if downward:
            if self.input.GetInsertionPoint() >= lastpos:
                self.statusbar.SetStatusText('Reached at the last')
                self.input.SetInsertionPoint(0)
                return
            while loop:
                end=self.input.GetLastPosition()
                start=self.input.GetInsertionPoint()+self.lenstr
                if lib.IsWxVersion2():
                    text=self.input.GetString(start,end)
                else:
                    text=self.input.GetValue()[start:end]
                found=text.find(findstr)
                if found >= 0:
                    foundlast=start+found+nstr
                    self.input.SetSelection(start+found,foundlast)
                    if lib.IsWxVersion2():
                        [colmn,line]=self.input.PositionToXY(start+found)
                    else:
                        # print('self.input.PositionToXY(start+found)=',self.input.PositionToXY(start+found))
                        [retcode,colmn, line] = self.input.PositionToXY(start + found)
                    mess='found at ['+str(colmn)+','+str(line-1)+']'
                    self.statusbar.SetStatusText(mess)
                    self.lenstr=nstr
                else: self.input.SetInsertionPoint(lastpos)
                break
        else:
            if self.input.GetInsertionPoint()-self.lenstr <= 0:
                self.statusbar.SetStatusText('Reached at the top')
                #self.input.SetInsertionPoint(lastpos)
                return
            while loop:
                start=self.input.GetInsertionPoint()-self.lenstr-1
                end=0
                if lib.IsWxVersion2():
                    text=self.input.GetString(end,start)
                else:
                    text = self.input.GetValue()[end:start]
                found=text.rfind(findstr)
                if found >= 0:
                    foundlast=end+found+nstr
                    self.input.SetSelection(end+found,foundlast)
                    if lib.IsWxVersion2():
                        [colmn,line]=self.input.PositionToXY(end+found)
                    else:
                        [retcode,colmn, line] = self.input.PositionToXY(end+found)

                    mess='found at ['+str(colmn)+','+str(line-1)+']'
                    self.statusbar.SetStatusText(mess)
                    self.lenstr=nstr
                else: self.input.SetInsertionPoint(0)
                break

    def OnFindNextForReplace(self,event):
        self.OnFindNext(event)

    def OnFindReplace(self,event):
        self.OnFindNext(event)
        replacestr=self.replacedata.GetReplaceString()
        lenfindstr=len(self.replacedata.GetFindString())
        lendel=len(replacestr)-lenfindstr
        #nstr=len(findstr); nrplstr=len(replacestr)
        [start,end]=self.input.GetSelection()
        if start == end:
            self.statusbar.SetStatusText('No find string')
            return
        self.input.Replace(start,end,replacestr)
        self.input.SetSelection(start,end+lendel)
        if lib.IsWxVersion2():
            [colmn,line]=self.input.PositionToXY(start)
        else:
            [retcode, colmn, line] = self.input.PositionToXY(start)

        mess='found at ['+str(colmn)+','+str(line-1)+']'
        self.statusbar.SetStatusText(mess)

    def OnReplaceAll(self,event):
        findstr=self.replacedata.GetFindString()
        replacestr=self.replacedata.GetReplaceString()
        #if replacestr == '': return
        nstr=len(findstr)
        nline=self.input.GetNumberOfLines()
        nrpl=0
        for i in range(nline):
            text=self.input.GetLineText(i)
            colmn=text.find(findstr)
            if colmn >= 0:
                start=self.input.XYToPosition(colmn,i)
                end=start+nstr
                self.input.SetSelection(start,end)
                self.input.Replace(start,end,replacestr)
                nrpl += 1
        self.statusbar.SetStatusText(str(nrpl)+' were replaced')

    def OnFindClose(self,event):
        self.fnddlg.Destroy()
        self.statusbar.SetStatusText('')

    def OnReplaceClose(self,event):
        self.rpldlg.Destroy()
        self.statusbar.SetStatusText('')

    def MenuItems(self):
        menubar=wx.MenuBar()
        submenu=wx.Menu()
        # if self.mode != 'Simple':
        # File menu
        if self.filemenu:
            subsubmenu=wx.Menu()
            submenu.Append(-1,'Open file','Open file.')
            submenu.Append(-1,'Input file names','Input file names.')
            ###submenu.Append(-1,'Load file','Load preset file')
            submenu.AppendSeparator()
            if self.mode == 'Edit' or self.scriptmode:
                submenu.Append(-1,'Save','Save file')
                submenu.Append(-1,'Save file as','Save file as')
                submenu.AppendSeparator()
            if self.scriptmode:
                submenu.Append(-1,'Open memory filer','Open memory filer.')
                submenu.AppendSeparator()
            submenu.Append(-1,'Quit','Close this panel')
            menubar.Append(submenu,'File')
        # Edit menu
        submenu=wx.Menu()
        #if self.mode != 'Simple':
        if self.mode == 'Edit' or self.scriptmode:
            submenu.Append(-1,"Undo edit","Undo")
            submenu.Append(-1,"Redo edit","Redo")
            submenu.AppendSeparator()
        submenu.Append(-1,"Find","Find strings")
        if self.mode == 'Edit' or self.scriptmode:
           submenu.Append(-1,"Replace","Replace strings")
        submenu.AppendSeparator()
        submenu.Append(-1,"Select all","Select all")
        submenu.Append(-1,"Clear Selection","Clear selection")
        submenu.AppendSeparator()
        submenu.Append(-1,"Add line numbers","Add line number")
        submenu.Append(-1,"Del line numbers","Delet line number")
        if self.mode == 'Edit' or self.scriptmode:
            submenu.AppendSeparator()
            submenu.Append(-1,"Add 4-spaces at line head","Add 4-spaces")
            submenu.Append(-1,"Del 4-spaces at line head","Delet 4-spaces")
            submenu.AppendSeparator()
            submenu.Append(-1,"Clear","Clear all text")
            submenu.Append(-1,"Undo Clear","Undo clear")
            submenu.AppendSeparator()
            submenu.Append(-1,"Copy","Copy selcted to clipboad")
            submenu.Append(-1,"Paste","Paste data in clipboard")
        menubar.Append(submenu,'Edit')
        # modyfy menu
        if self.scriptmode:
            submenu=wx.Menu()
            submenu.Append(-1,"Supress Rotate","Suppress fum.Rotate methods")
            submenu.Append(-1,"Supress Zoom","Suppress fum.zoom methods")
            submenu.AppendSeparator()
            submenu.Append(-1,"Add filename list","Add filename list")
            submenu.AppendSeparator()
            submenu.Append(-1,"Comment out lines",
                           "Add '#' in the first column(comment out")
            submenu.Append(-1,"Uncomment out lines",
                           "Del '#' in the first column(uncomment out")
            menubar.Append(submenu,'ForLogfile')
            # Help
            submenu=wx.Menu()
            submenu.Append(-1,"Help","Usage")
            menubar.Append(submenu,'Help')

        return menubar

class BatchJob_Frm(wx.Frame):
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,id,winpos=[],winsize=[],joblst=[], #prgname='',
                 onclose=None): #winsize=[300,400]):
        """

        :param int mode: 0 for with manue, 1 for without menu
        :param lst gmsdoc: gamess inputdoc data.
        :seealso: ReadGMSInputDocText() static method for gmsdoc
        """
        title='ExecBatchJobWin'

        if len(winpos) <= 0: winpos=[0,20]
        if len(winsize) <= 0:
            height=(len(joblst)+1)*20+120
            if height > 400: height=400
            if height < 250: height=250
            winsize=[300,height]
        winsize=lib.WinSize(winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)        #
        #
        self.parent=parent
        #self.mode=mode
        #self.oncompute=oncompute
        self.onclose=onclose
        self.joblst=joblst
        #self.prgname=prgname
        self.jobchkboxdic={}
        self.jobcheckdic={}
        #self.SetJobCheckDic()

        self.SetBackgroundColour('light gray')

        #if len(joblst) <= 0:
        # Menu
        #self.menubar=self.MenuItems()
        #self.SetMenuBar(self.menubar)
        # accept drop files
        #droptarget=lib.DropFileTarget(self)
        #self.SetDropTarget(droptarget)

        self.leftdown=False
        self.moveobjname=''
        self.moveobj=None
        self.prvobj=None
        self.leftdownpos=[-100,-100]
        self.CreatePanel()

        self.Show()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        #self.Bind(wx.EVT_SIZE,self.OnResize)
        #self.Bind(wx.EVT_MOVE,self.OnMove)
        #self.Bind(wx.EVT_MENU,self.OnMenu)

    def OnClose(self,event):
        self.Destroy()
    def OnResize(self,event):
        pass
    def OnMove(self,event):
        pass
    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")

        yloc=10
        # create file button
        #title=self.prgname+' input files(check for compute):'
        title='TEST'
        sttip=wx.StaticText(self.panel,-1,title,pos=(10,yloc),size=(w-20,18))
        #
        yloc += 25
        width=w-10 #self.sashposition
        height=h-60
        if lib.GetPlatform() == 'WINDOWS': height=h-70

        self.jobpan=CheckBoxPanel(self.panel,-1,pos=[10,yloc],size=[width,height])
        """
        self.jobpan=wx.ScrolledWindow(self.panel,-1,pos=[10,yloc],size=[width,height]) #,
                                       #style=wx.HSCROLL|wx.VSCROLL)

        self.jobpan.SetScrollbars(1,1,2*width,height+10) #(len(self.joblst)+1)*20)
        self.jobpan.SetBackgroundColour('white')
        self.CreateCheckBoxes()
        self.jobpan.SetScrollRate(5,20)

        yloc=h-25; xloc=w-180
        self.btnchk=wx.ToggleButton(self.panel,wx.ID_ANY,"CheckAll",pos=(xloc,yloc),size=(70,20))
        self.btnchk.Bind(wx.EVT_TOGGLEBUTTON,self.OnCheckAll)
        self.btnchk.SetToolTipString('Toggle to check and uncheck')
        self.btncmp=wx.Button(self.panel,wx.ID_ANY,"Compute",pos=(xloc+90,yloc),size=(70,20))
        self.btncmp.Bind(wx.EVT_BUTTON,self.OnCompute)
        self.btncmp.SetToolTipString('Execute checked scripts sequentially')
        """

class CheckBoxPanel(wx.ScrolledWindow):
    def __init__(self,parent,id,pos=[],size=[],itemlst=[],cbheight=20,
                 name='CheckBoxPanel'):
        wx.ScrolledWindow.__init__(self,parent,id,pos=pos,size=size,name=name)
        #
        self.parent=parent # wx.Panel instance
        self.title=name
        self.winpos=pos
        self.winsize=size
        self.cbheight=cbheight
        self.cbiniposy=8

        self.itemlst=itemlst
        self.checkboxdic={}
        if len(self.itemlst) > 0: self.CreateCheckBoxes()
        width=self.winsize[0]; height=self.winsize[1]
        self.SetScrollbars(1,1,2*width,height+10)
        self.SetBackgroundColour('white')
        self.SetScrollRate(5,20)

        self.leftdown=False
        self.leftdownpos=[-100,-100]
        self.moveidx=-1
        self.newitemlst=[]

    def CreateCheckBoxes(self):
        #self.panel=panel
        #size=panel.GetSize(); w=size[0]; h=size[1]
        [w,h]=self.GetClientSize()
        self.checkboxdic={}
        yloc=self.cbiniposy
        for name in self.itemlst:
            chkbox=wx.CheckBox(self,-1,name,pos=[10,yloc]) #,size=[w-20,28])
            #chkbox.Bind(wx.EVT_CHECKBOX,self.OnCheck)
            chkbox.Bind(wx.EVT_LEFT_DOWN,self.OnMouseLeftDown)
            chkbox.Bind(wx.EVT_LEFT_UP,self.OnMouseLeftUp)
            chkbox.Bind(wx.EVT_MOTION,self.OnMouseMove)
            self.checkboxdic[name]=chkbox
            chkbox.SetLabel(name)
            yloc += self.cbheight
        self.Refresh()

    def SetCheckBoxHeight(self,cbheight):
        self.cbheight
        if len(self.itemlst) > 0:
            self.DestroyCheckBoxes()
            self.CreateCheckBoxes()

    def SetItemList(self,itemlst):
        self.itemlst=itemlst
        self.DestroyCheckBoxes()
        if len(self.itemlst) > 0: self.CreateCheckBoxes()

    def AppendItems(self,itemlst):
        self.itemlst=self.itemlst+itemlst
        self.DestroyCheckBoxes()
        if len(self.itemlst) > 0: self.CreateCheckBoxes()

    def DelItems(self,itemlst):
        for item in itemlst:
            if item in self.itemlst: self.itemlst.remove(item)
        self.DestroyCheckBoxes()
        if len(self.itemlst) > 0: self.CreateCheckBoxes()

    def OnMouseLeftDown(self,event):
        pos=self.ScreenToClient(wx.GetMousePosition())
        objidx=self.GetCheckBoxIdFromPos(pos)
        objname=self.itemlst[objidx]
        obj=self.checkboxdic[objname]
        #
        if pos[0] < 20: # check/uncheck
            chk=obj.GetValue()
            if chk: obj.SetValue(False)
            else: obj.SetValue(True)
            self.leftdown=False
        else: # move item
            self.moveobj=obj
            self.moveidx=objidx
            self.olditemlst=self.itemlst[:]
            self.newitemlst=[]
            self.leftdownpos=pos
            self.leftdown=True
            self.moveobj.SetBackgroundColour('light blue')
            self.moveobj.Refresh()
            ###event.Skip()
    def OnMouseMove(self,event):
        if not self.leftdown: return
        if self.moveidx < 0: return
        pos=self.ScreenToClient(wx.GetMousePosition())
        newidx=self.GetCheckBoxIdFromPos(pos)
        newname=self.olditemlst[newidx]
        newobj=self.checkboxdic[newname]
        if newidx != self.moveidx:
            self.newitemlst=self.olditemlst[:]
            movename=self.newitemlst[self.moveidx]
            moveobj=self.checkboxdic[movename]
            if newidx > self.moveidx: chg=1
            else: chg=-1
            for i in range(self.moveidx,newidx,chg):
                newname=self.olditemlst[i+chg]
                self.newitemlst[i]=newname
            self.newitemlst[newidx]=movename
            checkboxdic={}
            for i in range(len(self.olditemlst)):
                newnam=self.newitemlst[i]
                oldnam=self.olditemlst[i]
                checkboxdic[newnam]=self.checkboxdic[oldnam]
                checkboxdic[newnam].SetLabel(newnam)
                checkboxdic[newnam].SetBackgroundColour('white')

        newobj.SetBackgroundColour('light blue')
        self.moveobj.SetBackgroundColour('white')
        self.Refresh()
        ###event.Skip()
    def GetCheckBoxIdFromPos(self,pos):
        """ Return checkbox id (zero based sequence number)

        :param lst pos: position in the panel, [x(int),y(int)] obtained by
        self.ScreenToClient(wx.GetMousePosition())
        """
        posy=pos[1]-self.cbiniposy
        cbid=int(float(posy)/float(self.cbheight))
        ncb=len(self.itemlst)
        if cbid < 0: cbid=0
        elif cbid > ncb-1: cbid=ncb-1
        return cbid

    def OnMouseLeftUp(self,event):
        if not self.leftdown: return
        self.leftdown=False
        self.moveobj.SetBackgroundColour('white')
        self.moveidx=-1
        if len(self.newitemlst) <= 0: return
        self.itemlst=self.newitemlst[:]
        checkboxdic={}
        for i in range(len(self.olditemlst)):
            newnam=self.newitemlst[i]
            oldnam=self.olditemlst[i]
            checkboxdic[newnam]=self.checkboxdic[oldnam]
            checkboxdic[newnam].SetLabel(newnam)
            self.checkboxdic[newnam].SetBackgroundColour('white')
        self.checkboxdic=checkboxdic
        self.Refresh()
        ###event.Skip()

    def CheckAllItems(self,on):
        """ Check item on/off

        :param bool on: True for check, False for uncheck
        """
        for name,cbobj in list(self.checkboxdic.items()):
            cbobj.SetValue(on)
        self.Refresh()

    def CheckItem(self,item,on):
        """ Check on/off of item

        :param str or lst item: item name or 'all'
        :param bool on: True for check, False for uncheck
        """
        if item == 'all':
            for name,cbobj in list(self.checkboxdic.items()): cbobj.SetValue(on)
        else:
            if item in self.checkboxdic:
                self.checkboxdic[item].SetValue(on)
        self.Refresh()

    def CheckItemsByList(self,itemlst,on):
        """ Check items in itemlst on/off

        :param lst or itemlst: item name list
        :param bool on: True for check, False for uncheck
        """
        for item in itemlst:
            if item in self.checkboxdic:
                self.checkboxdic[item].SetValue(on)
        self.Refresh()

    def GetCheckedItems(self):
        """ Return checked item list

        :return: checked item list - [item1(str),item2(str),...]
        """
        checkedlst=[]
        for name,cbobj in list(self.checkboxdic.items()):
            if cbobj.GetValue(): checkedlst.append(name)
        return checkedlst

    def IsItemChecked(self,item):
        """ Get check status of item

        :return: - True for checed, False for unchecked
        """
        if item in self.checkboxdic:
            return self.checkboxdic[item].GetValue()

    def OnCheck(self,event):
        """ not used """
        cbobj=event.GetEventObject()
        value=cbobj.GetValue()
        event.Skip()

    def GetItemList(self):
        """ Return checkbox item list

        :return: itemlst(lst) - [name1(str),name2(str),...]
        """
        return self.itemlst

    def GetCheckBoxObjects(self):
        """ Return CheckBox object

        :return dic checkboxobj - {'name1(str)': checkbox object(obj),...}
        """
        return self.checkboxdic

    def DestroyCheckBoxes(self):
        if len(self.checkboxdic) <= 0: return
        try:
            for name,cbobj in list(self.checkboxdic.items()): cbobj.Destroy()
        except: pass
        self.checkboxdic={}

class ExecuteBatchJob_Frm(wx.Frame):
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,oncompute,winpos=[],winsize=[],prgname='',
                 joblst=[],onclose=None): #winsize=[300,400]):
        """

        :param int mode: 0 for with manue, 1 for without menu
        :param lst gmsdoc: gamess inputdoc data.
        :seealso: ReadGMSInputDocText() static method for gmsdoc
        """
        title='ExecBatchJobWin'

        if len(winpos) <= 0: winpos=[0,20]
        if len(winsize) <= 0:
            height=(len(joblst)+1)*20+120
            if height > 400: height=400
            if height < 200: height=200
            winsize=[400,height]
        winsize=lib.WinSize(winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent=parent
        #self.mode=mode
        self.oncompute=oncompute
        self.onclose=onclose
        self.joblst=joblst
        self.prgname=prgname
        #
        self.SetBackgroundColour('light gray')
        # Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[ExecBatch]')
        # accept drop files
        droptarget=lib.DropFileTarget(self)
        self.SetDropTarget(droptarget)

        self.CreatePanel()

        self.Show()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_MENU,self.OnMenu)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        yloc=0
        width=w-20 #self.sashposition
        height=h-60
        self.panel=wx.Panel(self,wx.ID_ANY,pos=[0,0],size=[w,h])
        self.panel.SetBackgroundColour("light gray")
        yloc += 10
        # create file button
        title=self.prgname+' input files(check for compute):'
        sttip=wx.StaticText(self.panel,-1,title,pos=(10,yloc),size=(w-20,18))
        #
        if lib.GetPlatform() == 'WINDOWS': height=h-70
        inpwidth=w-20; inpheight=h-70
        yloc += 25
        self.inppan=CheckBoxPanel(self.panel,-1,pos=[10,yloc],
                                  size=[inpwidth,inpheight])
        yloc=h-25; xloc=w-245 #180
        self.btnview=wx.Button(self.panel,-1,"View",pos=(xloc,yloc),
                               size=(45,20))
        self.btnview.Bind(wx.EVT_BUTTON,self.OnView)
        #self.btnview.SetToolTipString('View a checked input file')
        lib.SetTipString(self.btnview,'View a checked input file')
        self.btnchk=wx.ToggleButton(self.panel,-1,"CheckAll",pos=(xloc+65,yloc),
                                    size=(70,20))
        self.btnchk.Bind(wx.EVT_TOGGLEBUTTON,self.OnCheckAll)
        #self.btnchk.SetToolTipString('Tgggle button to check/uncheck all files')
        lib.SetTipString(self.btnchk,'Tgggle button to check/uncheck all files')
        self.btncmp=wx.Button(self.panel,-1,"Compute",pos=(xloc+155,yloc),
                              size=(70,20))
        self.btncmp.Bind(wx.EVT_BUTTON,self.OnCompute)
        #self.btncmp.SetToolTipString('Execute GAMESS')
        lib.SetTipString(self.btncmp,'Execute GAMESS')

    def OnView(self,event):
        checkeditems=self.inppan.GetCheckedItems()
        if len(checkeditems) <= 0:
            mess='No checked item'
            lib.MessageBoxOK(mess,'ExecuteBatch(OnView)')
            return
        elif len(checkeditems) > 1:
            mess='Check one data for view'
            lib.MessageBoxOK(mess,'ExecuteBatch(OnView)')
            return
        filename=checkeditems[0]
        if filename == '': return
        lib.Editor(filename)

    def OnCompute(self,event):
        filelst=self.inppan.GetCheckedItems()
        self.oncompute(filelst)

    def OnCheckAll(self,event):
        value=self.btnchk.GetValue()
        self.inppan.CheckAllItems(value)

    def OpenDropFiles(self,filelst):
        if len(filelst) <= 0: return
        self.SetOpenFiles(filelst)

    def OpenInputFiles(self):
        wildcard='input file(*.inp)|*.inp|All(*.*)|*.*'
        filelst=lib.GetFileNames(self,wildcard,"r",True,"")
        if len(filelst) <= 0: return
        self.SetOpenFiles(filelst)

    def SetOpenFiles(self,filelst):
        self.gmsinputfile=filelst[0]
        #
        filelst=self.RemoveDuplicate(filelst)
        self.joblst=self.joblst+filelst
        ###self.SetJobCheckDic()
        self.inppan.SetItemList(self.joblst)
        self.inppan.CheckItem('all',True)
        #self.CreateCheckBoxes()

    def GetInputFilesInDirecory(self):
        self.dirnam=lib.GetDirectoryName(self)
        filelst=lib.GetFilesInDirectory(self.dirnam,['.inp'])
        if len(filelst) <= 0: return
        #
        self.joblst=self.joblst+filelst
        self.SetOpenFiles(self.joblst)

    def RemoveDuplicate(self,filelst):
        dup=False; replace=False
        if len(filelst) <= 0: return
        inputlst=[]
        for file in filelst:
            if file in self.joblst:
                mess='Duplicated filename "'+file
                mess=mess+'". Would you like to replace it?'
                dlg=lib.MessageBoxYesNo(mess,'')
                #if dlg.ShowModal() == wx.ID_YES:
                if dlg:
                    self.joblst.remove(file)
                    self.inputlst.append(file)
                #dlg.Destroy()
            else: inputlst.append(file)
        return inputlst

    def ClearJobFileList(self):
        self.joblst=[]
        self.inppan.SetItemList(self.joblst)

    def OpenSettingGAMESSPanel(self):
        print('OpenSettingGAMESSPanel')
    def ViewGAMESSDocument(self):
        print('ViewGAMESSDocument')
    def DeleteGAMESSScratch(selfself):
        print('DeleteGAMESSScratch')

    def OnClose(self,event):
        try: self.onclose()
        except: pass

        self.Destroy()

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):
        try: checkedlst=self.inppan.GetCheckedItems()
        except: pass
        self.panel.Destroy()
        self.CreatePanel()
        try:
            self.inppan.SetItemList(self.joblst)
            self.inppan.CheckItemsByList(checkedlst,True)
        except: pass

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        #submenu.Append(-1,"Open default","Open default value file")
        #submenu.Append(-1,"Open input file","Open GAMESS input file")
        submenu.Append(-1,"Open input files","Open multiple GAMESS input files")
        submenu.Append(-1,"Open files in directory",
                       "Open GAMESS input files in directory")
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear file list","Clear file list for compute")
        submenu.AppendSeparator()
        #submenu.Append(-1,"Delete gamess scratch","Delete GAMESS $DATA")
        #submenu.AppendSeparator()
        submenu.Append(-1,"Close","Close this panel")
        menubar.Append(submenu,'File')
        # View/Edit menu
        # Help menu
        submenu=wx.Menu()
        submenu.Append(-1,"About","Open about message")
        #submenu.AppendSeparator()
        #submenu.Append(-1,"Games input document","Open GAMESS INPUT document")
        #submenu.AppendSeparator()
        #submenu.Append(-1,"Setting","Set GAMESS program path")
        menubar.Append(submenu,'Help')
        return menubar

    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        menuitem=self.menubar.FindItemById(menuid)
        item=menuitem.GetItemLabel()
        #
        if item == "Close":
            self.OnClose(1)
        #elif item == "Open input file":
        #    self.OpenInputFiles(False)

        elif item == "Open input files":
            self.OpenInputFiles()

        elif item == "Open files in directory":

            self.GetInputFilesInDirecory()

        elif item == "Clear file list":
            self.ClearJobFileList()

        elif item == "Close":
            self.OnClose(0)
         # Help menu items
        elif item == 'About':
            title='Execute Batch in FU v.'
            lib.About(title,const.FUMODELLOGO)
        # Setting
        elif item == "Setting":
            self.OpenSettingGAMESSPanel()

        elif item == "Games input document":
            self.ViewGAMESSDocument()

        elif item == "Delete all in gamess/scr":
            self.DeleteGAMESSScratch()


class TextBox_Frm(wx.MiniFrame):
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,winpos=[],winsize=[],title='Text Box',text='',
                 ok=True,cancel=True,yes=False,no=False,retmethod=None):
        #title='Text viewer'
        """
        :param obj parent: window obj
        :param lst winpos: position of this window
        :param lst winsize: size of this window
        :param lst text: text to show
        """
        self.winlabel='TextBox'
        if len(winpos) <= 0: winpos=wx.GetMousePosition()
        winpos  = lib.SetWinPos(winpos)
        if len(winsize) <= 0: winsize=[400,200]
        wx.MiniFrame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent=parent # Window instance
        self.retmethod=retmethod
        self.text=text
        self.ok=ok
        self.cancel=cancel
        self.yes=yes
        self.no=no
        # model: Model instance
        self.bgcolor=[255,255,175] #'yellow'
        self.fgcolor=[0,0,0] #'black'

        self.CreatePanel()

        #if len(text) > 0: self.SetText(self.text)

        self.Show()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_SIZE,self.OnResize)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=[0,0],size=[w,h])
        height=h; btn=False
        #btn=True
        #btn=self.yes or self.no or self.cancel or self.ok
        #if btn: height=h-30
        btn=True
        height=h-30
        self.tcltext=wx.TextCtrl(self.panel,-1,pos=[0,0],size=[w,height],
                               value=self.text,style=wx.TE_MULTILINE)
        self.tcltext.SetBackgroundColour(self.bgcolor)
        self.tcltext.SetForegroundColour(self.fgcolor)
        #self.SetText(self.text)
        #self.tcltext.Refresh()
        yloc = h - 25
        if btn:
            xloc = 0
            if self.ok and not self.cancel and not self.yes and not self.no:
                xloc=w/2-105
                btnok=wx.Button(self.panel,-1,"OK",pos=[xloc,yloc],size=(50,20))
                btnok.Bind(wx.EVT_BUTTON,self.OnOK)
                xloc=xloc+50+20
            elif self.ok and self.cancel and not self.yes and not self.no:
                xloc=w-240
                btnok=wx.Button(self.panel,-1,"OK",pos=[xloc,yloc],size=(50,20))
                btnok.Bind(wx.EVT_BUTTON,self.OnOK)
                btncan=wx.Button(self.panel,-1,"Cancel",pos=[xloc+70,yloc],
                                 size=(60,20))
                btncan.Bind(wx.EVT_BUTTON,self.OnCancel)
                xloc=xloc+130+20
            elif not self.ok and not self.cancel and self.yes and self.no:
                xloc=w-240
                btnyes=wx.Button(self.panel,-1,"Yes",pos=[xloc,yloc],
                                 size=(50,20))
                btnyes.Bind(wx.EVT_BUTTON,self.OnYes)
                btnno=wx.Button(self.panel,-1,"No",pos=[xloc+70,yloc],
                                size=(50,20))
                btnno.Bind(wx.EVT_BUTTON,self.OnNo)
                xloc=xloc+140
            
            if xloc == 0: xloc = w/2 - 30
            btncls=wx.Button(self.panel,-1,"Close",pos=[xloc,yloc],size=(60,20))
            btncls.Bind(wx.EVT_BUTTON,self.OnClose)

    def OnOK(self,event):
        try: self.retmethod('ok')
        except: pass

    def OnCancel(self,event):
        self.retmethod('cancel')

    def OnYes(self,event):
        self.retmethod('yes')

    def OnNo(self,event):
        self.retmethod('no')

    def SetBackgroundColor(self,color):
        self.bgcolor=color
        self.tcltext.SetBackgroundColour(self.bgcolor)
        self.tcltext.Refresh()

    def SetForegroundColor(self,color):
        self.fgcolor=color
        self.tcltext.SetForegroundColour(self.fgcolor)
        self.tcltext.Refresh()

    def SetText(self,text):
        self.text=text
        self.tcltext.SetValue(self.text)
        self.tcltext.Refresh()

    def ClearText(self):
        self.tcltext.Clear()

    def OnClose(self,event):
        try: self.retmethod('close')
        except: pass
        self.Destroy()

    def OnMove(self,event):
        self.panel.Destroy()
        self.CreatePanel()
        self.SetText(self.text)
        self.tcltext.Refresh()

    def OnResize(self,event):
        self.OnMove(1)

class TextViewer_Frm(wx.Frame):
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,winpos=[],winsize=[],title='Text viewer',text='',
                 textfile='',model=None,menu=False):
        #title='Text viewer'
        """
        :param obj parent: window obj
        :param lst winpos: position of this window
        :param lst winsize: size of this window
        """
        self.winlabel='TextViewerWin'
        if len(winpos) <= 0: winpos=wx.GetMousePosition()
        winpos  = lib.SetWinPos(winpos)
        if len(winsize) <= 0: winsize=[400,200]
        #winsize=lib.WinSize(winsize)
        wx.Frame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent=parent # Window instance
        # model: Model instance
        if model:
            self.bgcolor=model.setctrl.GetParam('helpwin-bgcolor')
            self.fgcolor=model.setctrl.GetParam('helpwin-fgcolor')
        else:
            self.bgcolor=[253,255,206]
            self.fgcolor='black'
        # font
        font=lib.GetFont(5,10)
        self.SetFont(font)
        #
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            lib.InsertTitleMenu(self.menubar,'['+title+']')
            self.Bind(wx.EVT_MENU,self.OnMenu)
        #
        self.CreatePanel()
        #
        self.text=text
        if len(textfile) > 0:
            with open(textfile,'r') as f:
                self.text = f.read()
            self.text=self.text.replace('\r\n','\n')

        self.SetText(self.text)

        self.appendfile=None

        self.Show()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_SIZE,self.OnResize)

    def CreatePanel(self):
        winsize=self.GetClientSize()
        self.tcltext=wx.TextCtrl(self,-1,pos=[0,0],size=winsize,
                               style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)
        self.tcltext.SetBackgroundColour(self.bgcolor)
        self.tcltext.SetForegroundColour(self.fgcolor)

    def SetBackgroundColor(self,color):
        self.bgcolor=color
        self.tcltext.SetBackgroundColour(self.bgcolor)

    def SetForegroundColor(self,color):
        self.fgcolor=color
        self.tcltext.SetForeGroundColour(self.color)

    def xxReadText(self,textfile):
        self.tcltext.LoadFile(textfile)
        self.text=self.tcltext.GetValue()
        """
        self.text=''
        if not os.path.exists(textfile): return self.text
        f=open(textfile,'r')
        textlst=f.readlines()
        f.close()
        self.text=''
        for s in textlst: self.text=self.text+s
        """
    def SetText(self,text):
        self.text=text
        self.tcltext.SetValue(self.text)

    def SetTextFont(self,font):
        """Set font

        :param obj font: wx.font object
        """
        self.SetFont(font)

    def GetText(self):
        return self.tcltext.GetValue()

    def ClearText(self):
        self.tcltext.Clear()

    def OnClose(self,event):
        self.Destroy()

    def OnMove(self,event):
        self.tcltext.Destroy()
        self.CreatePanel()
        self.SetText(self.text)

    def OnResize(self,event):
        self.OnMove(1)

    def OpenFile(self):
        wildcard='All(*.*)|*.*'
        filename=lib.GetFileName(self,wildcard,"r",True,"")
        if len(filename) <= 0: return
        if not os.path.exists(filename):
            mess='Not found file='+filename
            lib.MessageBoxOK(mess,'TextViewer(OpenFile)')
            return
        self.tcltext.LoadFile(filename)
        mess='Saved text on file='+filename
        const.CONSOLEMESSAGE(mess)

    def SaveFileAs(self):
        wildcard='All(*.*)|*.*'
        filename=lib.GetFileName(self,wildcard,"w",True,"")
        if len(filename) <= 0: return
        ret=self.tcltext.SaveFile(filename)
        if ret: mess='Saved text on file='+filename
        else: mess='Failed to save text on file='+filename
        const.CONSOLEMESSAGE(mess)

    def AppendToFile(self):
        wildcard='All(*.*)|*.*'
        defnam=''
        if self.appendfile is not None: defnam=self.appendfile
        filename=lib.GetFileName(self,wildcard,"r",False,defaultname=defnam)
        if len(filename) <= 0: return
        self.AppendTo(filename)

    def AppendTo(self,filename):
        """ Append text to file """
        f=open(filename,'a')
        f.write(self.tcltext.GetValue())
        f.close()
        mess='Appended text on file='+filename
        const.CONSOLEMESSAGE(mess)
        self.appendfile=filename

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        submenu.Append(-1,"Open","Open file")
        submenu.Append(-1,"Save as","Save file as")
        submenu.Append(-1,"Append to file","Append text to file")
        submenu.AppendSeparator()
        submenu.Append(-1,"Close","Close this panel")
        menubar.Append(submenu,'File')
         # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Select all","Select all")
        submenu.Append(-1,"Copy","Copy text to clipboad")
        #submenu.Append(-1,"Paste","Paste text from cipboad")
        menubar.Append(submenu,'Edit')

        return menubar

    def RemoveOpenMenu(self):
        menu=self.menubar.GetMenu(0)
        menuid=menu.FindItem('Open')
        menu.Remove(menuid)

    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        menuitem=self.menubar.FindItemById(menuid)
        item=menuitem.GetItemLabel()
        #
        if item == "Close":
            self.OnClose(1)
        elif item == "Open": self.OpenFile()
        elif item == "Save as": self.SaveFileAs()
        elif item == "Append to file": self.AppendToFile()
        elif item == "Close": self.OnClose(0)
         # Edit menu items
        elif item == "Select all": self.tcltext.SelectAll()
        elif item == "Copy": self.tcltext.Copy()
        elif item == "Paste": # does not work in "read only mode"
            self.tcltext.Paste()
        else:
            try: pass
            except: pass

class HelpMessage(object):
    def __init__(self,helpdata,title='Help message',winpos=[],winsize=[],
                 parent=None,datatype='file',viewer='Html'):

        #def HelpMessage(helpdata,title='Help message',parent=None,winpos=[],winsize=[],
        #            datatype='file',viewer='Html'):
        """ Show help message by HtmlViwer_Frm, TextViewer_Frm or wx.MessageBoX

        :param str helpdata: help data. file name(datatype='file')
         or text('text')
        :param str title: title of the panel
        :param obj parent: window type object
        :param str datatype: help data type, 'file' or 'text'
        :param str viewer: viewwer, 'Html','Text' or 'MessageBox'
        """
        if not parent: viewer='Messagebox'
        #    mess='Error: Window type parent is required'
        #    lib.MessageBoxOK(mess,'lib.HelpMessage')
        #    return
        if datatype == 'file':
            helpfile=helpdata
            if not os.path.exists(helpfile):
                mess='Not found help file='+helpfile
                lib.MessageBoxOK(mess,'lib.HelpMessage')
                return
        else:
            text=helpdata # datatype='text'
            helpfile=''
        #
        if len(winpos) <= 0:
            [x,y]=parent.GetPosition()
            winpos=[x+20,y+20]
        winpos  = lib.SetWinPos(winpos)

        if len(winsize) <= 0: winsize=[400,200]
        #
        if viewer == 'Html':
            if datatype == 'file':
                if lib.GetPlatform() == 'WINDOWS':
                    helpfile=helpfile.replace('//','\\')
                HtmlViewer_Frm(parent,winpos=winpos,winsize=winsize,title=title,
                               htmlfile=helpfile)
            else: # 'Text'
                HtmlViewer_Frm(parent,winpos=winpos,winsize=winsize,text=helpdata)
        elif viewer== 'Text':
            TextViewer_Frm(parent,winpos=winpos,winsize=winsize,title=title,
                                  textfile=helpfile,text=helpdata)
        else:
            mess=text
            if datatype == 'file':
                mess=''
                f=open(helpfile,'r')
                for s in f.readlines(): mess=mess+s
                f.close()
            lib.MessageBoxOK(mess,title)

class HtmlViewer_Frm(wx.Frame):
    """

    :param obj parent: window obj
    :param lst winpos: position of this window
    :param lst winsize: size of this window
    """
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,winpos=[],winsize=[],title='HtmlViewer',
                 winlabel='',htmlfile='',htmltext='',fumodel=None):
        self.winlabel=winlabel
        if self.winlabel == '': self.winlabel='HtmlViewer'
        #winpos=wx.GetMousePosition()
        if len(winsize) <= 0: winsize=[400,200]
        #winsize=lib.WinSize(winsize)
        if len(winpos) < 0: winpos=wx.GetMousePosition()
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent=parent # Window instance
        self.model=fumodel # model: Model instance

        self.bgcolor='white'

        self.SetBackgroundColour(self.bgcolor)
        self.htmlfile=htmlfile
        self.htmltext=htmltext
        self.CreatePanel()

        self.Show()

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        #self.Bind(wx.EVT_LEFT_DOWN,self.OnLeftClick)

    def CreatePanel(self):
        winsize=self.GetClientSize()
        self.htmlview=wx.html.HtmlWindow(self,-1,pos=[0,0],size=winsize,
                                   style=wx.NO_BORDER|wx.html.HW_SCROLLBAR_AUTO)
        #self.htmlview.Bind(wx.html.EVT_HTML_LINK_CLICKED,self.OnLink)
        self.htmlview.Bind(wx.EVT_LEFT_UP,self.OnMouseLeftUp)
        if os.path.exists(self.htmlfile):
            curdir = os.getcwd()
            hdir = lib.GetFileNameDir(self.htmlfile)
            os.chdir(hdir)
            #
            if lib.IsPython2():
                mess = '(python2) Errors occured in "HtmlViewer_Frm".'
                with open(self.htmlfile, 'r') as f:
                    string = f.read()
            else:
                mess = '(not python2) Errors occured in "HtmlViewer_Frm".'
                with open(self.htmlfile, 'r', encoding='utf-8') as f:
                    string = f.read()
            #
            try:
                self.htmlview.SetPage(string)
            except:
                wx.MessageBox(mess, "HTMLViewer_Frm.CreatePanel")
            os.chdir(curdir)
        else:
            self.htmlview.SetPage(self.htmltext)

    def OnMouseLeftUp(self,event):
        self.htmlview.HistoryBack()
        event.Skip()

    def SetHtmlText(self,htmltext):
        """ Set html page

        :param str htmltext: html ,body text, '<html><body>Hello,
        world!</body></html>'
        """
        self.htmltext=htmltext
        self.htmlview.SetPage(htmltext)

    def SetHtmlFile(self,htmlfile):
        """ Load html file

        :param str htmlfile: html file name
        """
        self.htmlfile=htmlfile
        self.htmlview.LoadFile(self.htmlfile)

    def SetBackgroundColor(self,color):
        self.bgcolor=color
        self.htmlview.SetBackgroundColour(self.bgcolor)

    def OnClose(self,event):
        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        self.Destroy()

    def OnMove(self,event):
        self.htmlview.Destroy()
        self.CreatePanel()

    def OnResize(self,event):
        self.OnMove(1)


class ExecuteScript_Frm(wx.Frame):
    #def __init__(self,mdlwin,id,gmsuser,mode,namvarlst,inputvaldic,textvaldic,gmsdoc,
    def __init__(self,parent,winpos=[],winsize=[]):
        title='Execute script'
        """
        :param obj parent: window obj
        :param lst winpos: position of this window
        :param lst winsize: size of this window
        """
        self.winlabel='Open ExecScriptWin'

        if len(winpos) <= 0: winpos=[0,20]
        if len(winsize) <= 0: winsize=[325,200]
        winsize=lib.WinSize(winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,-1,title,pos=winpos,size=winsize,
                  style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.parent=parent # assume 'mdlwin'
        self.mdlwin=parent
        self.model=self.mdlwin.model
        try:
            self.winctrl=self.model.winctrl
        except: self.winctrl=None

        self.SetBackgroundColour('light gray')
        #self.mode=mode
        #self.oncompute=oncompute
        self.scriptdic={}
        self.scriptlst=[]
        self.curscript=''
        #
        self.stepbystep=False
        self.curblock=0
        self.blockscriptlst=[]
        # Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[ExecScript]')
        # accept drop files
        droptarget=lib.DropFileTarget(self)
        self.SetDropTarget(droptarget)
        #
        self.CreatePanel()
        #
        self.Show()
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)
        self.Bind(wx.EVT_MENU,self.OnMenu)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,wx.ID_ANY,pos=(-1,-1),size=(w,h))
        self.panel.SetBackgroundColour("light gray")

        yloc=5; xloc=10
        # create file button
        sttip=wx.StaticText(self.panel,-1,'Scripts(check items for run):',
                            pos=(xloc,yloc),size=(w-20,18))
        #
        yloc += 20; width=w-20; height=h-55
        self.scrpan=CheckBoxPanel(self.panel,-1,pos=[10,yloc],
                                  size=[width,height])
        """
        self.cmbscr=wx.ComboBox(self.panel,wx.ID_ANY,'',pos=(xloc,yloc),size=(190,18))
        #self.cmbscr.Bind(wx.EVT_COMBOBOX,self.OnScript)
        self.cmbscr.SetItems(self.scriptlst)
        self.cmbscr.SetValue(self.curscript)
        """
        yloc=h-25; xloc=10
        btnview=wx.Button(self.panel,-1,"View",pos=(xloc,yloc),size=(45,20))
        btnview.Bind(wx.EVT_BUTTON,self.OnView)
        #btnview.SetToolTipString('View a checked script file')
        lib.SetTipString(btnview,'View a checked script file')
        self.btnchk=wx.ToggleButton(self.panel,-1,"CheckAll",pos=(xloc+55,yloc),
                                    size=(70,20))
        self.btnchk.Bind(wx.EVT_TOGGLEBUTTON,self.OnCheckAll)
        mess='Tgggle button to check/uncheck all scripts'
        #self.btnchk.SetToolTipString(mess)
        lib.SetTipString(self.btnchk,mess)
        self.ckbstp=wx.CheckBox(self.panel,-1,"Step-by-step",
                                pos=(xloc+140,yloc),size=(90,18))
        self.ckbstp.Bind(wx.EVT_CHECKBOX,self.OnStepByStep)
        #self.ckbstp.SetToolTipString('Execute a script file step-by-step')
        lib.SetTipString(self.ckbstp,'Execute a script file step-by-step')
        self.btnrun=wx.Button(self.panel,-1,"Run",pos=(xloc+240,yloc),
                              size=(40,20))
        self.btnrun.Bind(wx.EVT_BUTTON,self.OnRun)
        mess='Run scripts or a block of a script (step-by-step)'
        #self.btnrun.SetToolTipString(mess)
        lib.SetTipString(self.btnrun,mess)

    def OnCheckAll(self,event):
        value=self.btnchk.GetValue()
        self.scrpan.CheckAllItems(value)

    def OpenDropFiles(self,filenames):
        """ Event handler for drag-and-drop files"""
        if len(filenames) <= 0: return
        self.SetScripts(filenames)
        self.curblock=0

    def OnStepByStep(self,event):
        self.stepbystep=self.ckbstp.GetValue()
        self.curblock=0

    def ExecStepByStep(self):
        pyshell=self.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='"PyShell" is not active.'
            lib.MessageBoxOK(mess,'ExecuteScript')
            return
        # one script at a time
        checkeditems=self.scrpan.GetCheckedItems()
        if len(checkeditems) > 1:
            mess='Check one script for step-by-setp run'
            lib.MessageBoxOK(mess,'ExecScriptWin(ExecStepByStep')
            return
            #self.scrpan.CheckAllItems(False)
            #self.scrpan.CheckItem(self.curscript,True)

        self.curscript=checkeditems[0]
        #
        if self.curblock == 0:
            self.blockscriptlst=[]
            #self.curscript=self.cmbscr.GetValue()
            scrfile=self.scriptdic[self.curscript]
            scripttext=self.SkipAppliedScript(scrfile)
            blocklst=self.BlockScripts(scripttext)
            self.blockscriptlst=self.MakeTempScripts(blocklst)
        if self.curblock >= len(self.blockscriptlst):
            mess='Ends step-by-step run. script='+self.curscript+', block='
            mess=mess+str(self.curblock)
            self.model.ConsoleMessage(mess)
            self.curblock=0
            return
        #
        blockscrfile=self.blockscriptlst[self.curblock]
        lib.ExecuteScript1(pyshell.shell,blockscrfile)
        mess='Run step-by-step script. script='+self.curscript+', block='
        mess=mess+str(self.curblock)
        self.model.ConsoleMessage(mess)
        self.curblock += 1

    def SkipAppliedScript(self,scriptfile):
        scripttext=''
        f=open(scriptfile)
        text=f.readlines()
        f.close()
        lines=text #.split('\n')
        skiplst=[]
        # find skip methdo
        for s in lines:
            if s[:6] == '#skip#':
                ss=s[6:]
                ns=ss.find('#')
                if ns >= 0: ss=ss[:ns]
                ss=ss.strip()
                skiplst.append(ss)
        print(('skiplst',skiplst))
        if len(skiplst) > 0:
            for s in lines:
                find=False
                for skp in skiplst:
                    if s.find(skp) >= 0: find=True
                if not find: scripttext=scripttext+s+'\n'
        else:
            for s in lines: scripttext=scripttext+s+'\n'
        return scripttext

    def BlockScripts(self,text):
        blocklst=[]
        lines=text.split('\n')
        block=''
        for s in lines:
            if s[:3] == '#-#':
                if block != '': blocklst.append(block)
                block=''; continue
            else:
                ss=s.strip()
                if ss[:1] == '#': continue
                if ss == '': continue
                if len(ss) <= 0: continue
                block=block+s+'\n'
        if block != '': blocklst.append(block)
        return blocklst

    def MakeTempScripts(self,blocklst):
        tempscriptfilelst=[]
        scrdir=self.model.setctrl.GetDir('Scratch')
        iblock=-1
        for block in blocklst:
            iblock += 1
            filename='Execute-Script-'+str(iblock)+'.py'
            filename=os.path.join(scrdir,filename)
            f=open(filename,'w')
            f.write(block)
            f.close()
            tempscriptfilelst.append(filename)
        return tempscriptfilelst

    def RenameLogFile(self,scrfile):
        ispyfile=True
        base,ext=os.path.splitext(scrfile)
        if ext == '.logging':
             ispyfile=False
             oldfilename=scrfile
             scrfile=scrfile.replace(ext,'.py')
             if os.path.exists(scrfile):
                 mess='The file='+scrfile+ 'exists. May i delete it?'
                 dlg=lib.MessageBoxYesNo(mess,'ExecuteScript')
                 #if dlg.ShowModal() == wx.ID_NO: return
                 if not dlg: return
                 #dlg.Destroy()
             os.rename(oldfilename,scrfile)

             print(('oldfilename,scrfile',oldfilename,scrfile))

        return ispyfile

    def OnRun(self,event):
        self.stepbystep=self.ckbstp.GetValue()
        if self.stepbystep:
            self.ExecStepByStep()
        else: self.Execute()

    def Execute(self):
        pyshell=self.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='"PyShell" is not active.'
            lib.MessageBoxOK(mess,'ExecuteScript')
            return
        checkeditems=self.scrpan.GetCheckedItems()
        if len(checkeditems) <= 0:
            mess='No checked items'
            lib.MessageBoxOK(mess,'ExecuteScript(Execute)')
            return
        for script in checkeditems:
            self.curscript=script #self.cmbscr.GetValue()
            scrfile=self.scriptdic[self.curscript]
            savefilename=scrfile
            mess='Run script. script='+self.curscript
            self.model.ConsoleMessage(mess)
            lib.ExecuteScript1(pyshell.shell,scrfile)

    def OnView(self,event):
        checkeditems=self.scrpan.GetCheckedItems()
        if len(checkeditems) <= 0:
            mess='No checked item'
            lib.MessageBoxOK(mess,'ExecuteScript(OnView)')
            return
        self.curscript=checkeditems[0]
        if len(self.curscript) <= 0:
            mess='No script file is opened.'
            lib.MessageBoxOK(mess,'ExecuteScript(OnView)')
        filename=self.scriptdic[self.curscript]
        if filename == '': return
        lib.Editor(filename)

    def SaveFupyFileAs(self):
        wildcard='fupy file(*.fupy)|*.fupy|All(*.*)|*.*'
        filename=lib.GetFileName(self,wildcard,"w",True,"")
        if len(filename) <= 0: return
        #
        checkeditems=self.scrpan.GetCheckedItems()
        if len(checkeditems) > 0:
            f=open(filename,'w')
            for item in checkeditems:
                text='#file# '+self.scriptdic[item]+'\n'
                f.write(text)
            f.close()
            #
            mess='Save .fupy file='+filename
            self.model.ConsoleMessage(mess)

    def OpenScripts(self):
        wildcard='script file(*.py;*.fupy)|*.py;*.fupy|All(*.*)|*.*'
        filelst=lib.GetFileNames(self,wildcard,"r",True,"")
        if len(filelst) <= 0: return
        self.SetScripts(filelst)
        self.curblock=0

    def OpenLogFiles(self):
        wildcard='log file(*.log)|*.log|All(*.*)|*.*'
        filelst=lib.GetFileNames(self,wildcard,"r",True,"")
        if len(filelst) <= 0: return
        self.SetScripts(filelst)

    def SetScripts(self,filelst):
        # *.fupy file
        files=[]
        for file in filelst:
            if not os.path.exists(file): continue
            base,ext=os.path.splitext(file)
            if ext == '.fupy':
                f=open(file,'r')
                for s in f.readlines():
                     if s[:6] != '#file#': continue
                     s=s[6:].strip()
                     if not os.path.exists(s): continue
                     files.append(s)
                f.close()
            elif ext == '.py': files.append(file)
            else: continue
        for scrfile in files:
            head,tail=os.path.split(scrfile)
            scrnam=tail
            if scrnam in self.scriptlst: continue
            self.scriptlst.append(scrnam)
            scrfile=lib.ReplaceBackslash(scrfile)
            self.scriptdic[scrnam]=scrfile
        #
        nscr=len(self.scriptlst)
        try: self.curscript=self.scriptlst[nscr-1]
        except: pass
        ###self.cmbscr.SetItems(self.scriptlst)
        ###self.cmbscr.SetValue(self.curscript)
        ###self.scrpan.AppendItems(self.scriptlst)
        self.scrpan.SetItemList(self.scriptlst)
        self.scrpan.CheckItem('all',True)
        self.curblock=0

    def ClearScripts(self):
        self.scriptdic={}
        self.scriptlst=[]
        #
        self.scrpan.SetItemList(self.scriptlst)
        self.curblock=0

    def SetCurrentScript(self,script):
        if script in self.scriptdic:
            self.curscript=script
        else: pass
        self.curblock=0

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):
        try:
            itemlst=self.scrpan.GetItemList()
            checkedlst=self.scrpan.GetCheckedItems()
        except: pass
        self.panel.Destroy()
        self.CreatePanel()
        try:
            self.scrpan.SetItemList(itemlst)
            self.scrpan.CheckItemsByList(checkedlst,True)
        except: pass
        #

    def OnClose(self,event):
        try: self.winctrl.Close(self.winlabel)
        except: pass
        #
        self.Destroy()

    def Help(self):
        helpdir=self.model.setctrl.GetDir('FUdocs')
        helpfile='subwindoc//ExecuteScript//executescriptdoc.html'
        helpfile=lib.PathJoin(helpdir,helpfile)
        title='Help ExecuteScript'
        [x,y]=self.GetPosition()
        winpos=[x+20,y+20]
        HelpMessage(helpfile,'ExecuteScript',winpos=winpos,parent=self)
        ###if lib.GetPlatform() == 'WINDOWS': helpfile=helpfile.replace('//','\\')
        #TextViwer_Frm(self,title=title,textfile=helpfile,fumodel=self.model)
        ###pos=self.GetPosition()
        ###winpos=[pos[0]+20,pos[1]+20]
        #HtmlViewer_Frm(self,winpos=winpos,title=title,htmlfile=helpfile,fumodel=self.model)

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        #submenu.Append(-1,"Open default","Open default value file")
        submenu.Append(-1,"Open script files","Open script files")
        submenu.AppendSeparator()
        submenu.Append(-1,"Clear script files","Clear script file lits")
        submenu.AppendSeparator()
        #submenu.Append(-1,"Open log files","Open log files")
        #submenu.AppendSeparator()
        #submenu.Append(-1,"Delete gamess scratch","Delete GAMESS $DATA")
        #submenu.AppendSeparator()
        submenu.Append(-1,"Save fupy as","Save fupy file as")
        submenu.AppendSeparator()

        submenu.Append(-1,"Close","Close this panel")
        menubar.Append(submenu,'File')
        # Pause menu # not used, use step-by-step instead
        #submenu=wx.Menu()
        #self.idpause=wx.NewId()
        #submenu.Append(self.idpause,"Pause after","Pause after executing a script")
        #menubar.Append(submenu,'Pause')
        # Help menu
        submenu=wx.Menu()
        submenu.Append(-1,"Help","Open help message")
        menubar.Append(submenu,'Help')
        return menubar

    def OnMenu(self,event):
        # Menu event handler
        menuid=event.GetId()
        menuitem=self.menubar.FindItemById(menuid)
        item=menuitem.GetItemLabel()
        # File
        if item == "Open script files": self.OpenScripts()
        #elif item == "Open log files": self.OpenLogFiles()
        elif item == "Clear script files": self.ClearScripts()
        elif item == "Save .fupy as": self.SaveFupyFileAs()
        elif item == "Close": self.OnClose(1)
        # Help menu items
        elif item == 'Help': self.Help()

        elif item == 'About':
            title='Execute Scripts'
            lib.About(title,const.FUMODELLOGO)

class HtmlViewerWithTreeIndex_Frm(wx.Frame):
    """ Html Help Viewer
    'Search' is not suported
    """
    title='Html viewer with index'
    def __init__(self,parent,id,winpos=[],winsize=[],title=title,winlabel='',
                 treewidth=-1,contentsfile='',expandall=True,rootname='root',
                 search=False,printmenu=True,statusbar=True):
        self.title=title
        self.winpos=winpos
        if len(winpos) <= 0:
            [x,y]=parent.GetPosition()
            self.winpos=[x+20,y+20]
        self.winpos  = lib.SetWinPos(self.winpos)
        self.winsize=winsize
        if len(winsize) <= 0: self.winsize=[640,400]
        #self.winsize=lib.WinSize(self.winsize)
        wx.Frame.__init__(self, parent, id, self.title, pos=self.winpos,
                  size=self.winsize,
                  style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)
        self.parent=parent # futool
        self.model=self.parent.model
        self.winctrl=self.model.winctrl
        self.winlabel=winlabel
        # print menu
        if printmenu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            lib.InsertTitleMenu(self.menubar,'[HtmlViewer]')
            self.Bind(wx.EVT_MENU,self.OnMenu)
        # statusbar
        if statusbar:
            self.statusbar=self.CreateStatusBar()
        #
        [w,h]=self.GetClientSize()
        self.treewidth=treewidth
        if treewidth <= 0: self.treewidth=120
        if self.treewidth > w: self.treewidth=w-80
        self.expandall=expandall
        self.search=search
        self.lenstr=0
        self.bgcolor='white'
        self.searchall=False
        #
        self.rootname=rootname
        self.treeitemlst=[]
        self.htmldic={}
        self.textdic={}
        self.expanditemid=None
        self.expandedlst=[]
        self.curname=''
        #self.saveitems=None
        font=self.GetFont()
        self.SetFont(font)
        self.prvname=None
        self.curpos=0
        self.searchstr=''
        self.searhcall=False
        #self.MakeItemLst()
        # Bind the OnSelChanged method to the tree
        #self.doctype=doctype
        self.contentsfile=contentsfile
        #self.textpan=None
        self.panel=None
        self.treepan=None
        self.htmlpan=None
        self.ready=False
        self.CreatePanel()
        self.Show()
        # read contentsfile
        self.nameitemdic={}
        self.curname=''
        if self.contentsfile != '':
            self.treeitemlst,self.textdic,self.htmldic= \
                     rwfile.ReadContentsFile(self.contentsfile,retscript=False)
        if len(self.treeitemlst) > 0:
            self.SetTreeItemList(self.rootname,self.treeitemlst)
        self.ready=True
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        # tree panel
        yloc=4
        if self.search:
            ypos=2; xloc=w-300
            self.panel=wx.Panel(self,-1,pos=[0,0],size=[w,25])
            self.panel.SetBackgroundColour('white')
            sttxt=wx.StaticText(self.panel,-1,"Search:",pos=(xloc,ypos+2),
                                size=(60,18))
            sttxt.SetBackgroundColour('white')
            self.tclinp=wx.TextCtrl(self.panel,-1,pos=[xloc+60,ypos],
                                    size=[150,20],style=wx.TE_PROCESS_ENTER)
            self.tclinp.Bind(wx.EVT_TEXT,self.OnSearchText)
            #self.alltext=wx.CheckBox(self.panel,-1,"all",pos=[220,ypos],size=[30,20])
            #self.alltext.Bind(wx.EVT_CHECKBOX,self.OnSearchAll)
            #self.alltext.Disable()
            btnprev=wx.Button(self.panel,-1,"<",pos=(xloc+225,ypos),
                              size=(20,20))
            btnprev.Bind(wx.EVT_BUTTON,self.OnPrevSearch)
            btnnext=wx.Button(self.panel,-1,">",pos=(xloc+260,ypos),
                              size=(20,20))
            btnnext.Bind(wx.EVT_BUTTON,self.OnNextSearch)
            yloc += 20
        treepos=[0,yloc]
        tw=self.treewidth
        treesize=[tw,h-yloc]
        self.treepan=wx.TreeCtrl(self,-1,pos=treepos,size=treesize) #,
                                 #style=wx.TR_HIDE_ROOT)
        self.treepan.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelChanged)
        self.treepan.Bind(wx.EVT_TREE_ITEM_EXPANDED,self.OnExpanded)
        self.treepan.Bind(wx.EVT_TREE_ITEM_COLLAPSED,self.OnCollapsed)
        self.treepan.Refresh()
        self.treepan.Bind(wx.EVT_RIGHT_DOWN,self.OnRightClick)
        # descripton panel
        textpos=[tw+5,yloc]
        textsize=[w-tw-5,h-yloc]
        #if self.doctype == 'text':
        #    self.textpan=wx.TextCtrl(self,-1,pos=textpos,size=textsize,
        #                             style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2|wx.TE_NOHIDESEL) #|wx.HSCROLL
        #    self.textpan.SetBackgroundColour(self.bgcolor)
        # this option is not tested
        #elif self.doctype == 'html':
        #self.htmlpan=wx.html.HtmlWindow(self,-1,pos=textpos,size=textsize,style=wx.NO_BORDER)
        #self.htmlpan.LoadPage('help.html') #http://zetcode.com/wxpython/advanced/
        #if lib.GetPlatform() == 'WINDOWS':
        #    helpfile=helpfile.replace('//','\\')
        winsize=self.GetClientSize()
        self.htmlpan=wx.html.HtmlWindow(self,-1,pos=textpos,size=textsize,
                                   style=wx.NO_BORDER|wx.html.HW_SCROLLBAR_AUTO)
        #self.htmlview.Bind(wx.html.EVT_HTML_LINK_CLICKED,self.OnLink)
        ### Do not activate the following event handler. it hinders to display
        ### text file in file-format link!
        ###self.htmlpan.Bind(wx.EVT_LEFT_UP,self.OnMouseLeftUp)
        self.htmlpan.Bind(wx.EVT_RIGHT_UP,self.OnMouseRightUp)
        ###if wx.version()[0:2] == '2.': self.htmlpan.AddFilter(wx.html.HtmlFilter())
        self.htmlpan.Refresh()
        #if len(self.htmlfile) > 0:
            #self.htmlpan.AddFilter(wx.html.HtmlFilter())

            #retcode=self.htmlpan.LoadFile(self.htmlfile)
            #if not retcode:
            #    mess='Failed to load htmlfile='+self.htmlfile
            #    lib.MessageBoxOK(mess,'HtmlViewer(CreatePanel)')
        #else:
            #self.htmlpan.SetPage(self.htmltext)
    def OnExpanded(self,event):
        item=event.GetEventObject()
        self.expandedlst.append(item)

    def OnCollapsed(self,event):
        item=event.GetEventObject()
        if item in self.expandedlst: self.expandedlst.remove(item)

    def ExpandAllItems(self):
        rootid=self.treepan.GetRootItem()
        self.treepan.Expand(rootid)
        self.treepan.ExpandAll()

    def CollapseAllItems(self):
        rootid=self.treepan.GetRootItem()
        self.treepan.Expand(rootid)
        self.treepan.CollapseAll()

    def OnRightClick(self,event):
        const.CONSOLEMESSAGE('Entered in OnLeftClick')
        rootid=self.treepan.GetRootItem()
        #self.treepan.SelectItem(rootid,True)
        #self.treepan.SetItemBold(rootid,True)
        self.treepan.CollapseAllChildren(rootid)
        event.Skip()

    def OnMouseLeftUp(self,event):
        self.htmlpan.HistoryForward()
        event.Skip()

    def OnMouseRightUp(self,event):
        self.htmlpan.HistoryBack()
        event.Skip()

    def SetBGColor(self,color):
        self.bgcolor=color
        self.textpan.SetBackgroundColour(self.bgcolor)

    def OnPrevSearch(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchstr=self.tclinp.GetValue().strip()
        start=0
        end=self.textpan.GetInsertionPoint()-self.lenstr
        text=self.textpan.GetString(start,end)
        self.lenstr=len(self.searchstr)
        found=text.rfind(self.searchstr)
        if found >= 0:
            self.textpan.SetSelection(found,found+self.lenstr)
        else: pass

    def OnNextSearch(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchstr=self.tclinp.GetValue().strip()
        start=self.textpan.GetInsertionPoint()+self.lenstr
        end=self.textpan.GetLastPosition()
        text=self.textpan.GetString(start,end)
        self.lenstr=len(self.searchstr)
        found=text.find(self.searchstr)
        if found >= 0:
            self.textpan.SetSelection(start+found,start+found+self.lenstr)
        else: pass

    def OnSearchText(self,event):
        self.searchstr=self.tclinp.GetValue().strip()
        self.lenstr=0

    def OnSearchAll(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchall=False

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):

        #self.treepan.GetSelection()
        #curname=self.curname
        try: self.panel.Destroy()
        except: pass
        self.treepan.Destroy()
        self.htmlpan.Destroy()
        self.CreatePanel()
        self.SetItemsToTree(False)
        ###self.tclinp.SetValue(self.searchstr)
        #selitem=self.nameitemdic[curname]
        #self.TreeSelChanged(selitem)
        #self.alltext.SetValue(self.searchall)

    def SetTreeItemList(self,rootname,treeitemlst):
        self.rootname=rootname
        self.treeitemlst=treeitemlst
        self.SetItemsToTree(True)

    def SetItemsToTree(self,init):
        """ Set items to tree menu """
        self.nameitemdic={}
        expanditemid=None
        root=self.treepan.AddRoot(self.rootname)
        self.nameitemdic[self.rootname]=root
        for i in range(len(self.treeitemlst)):
            name=self.treeitemlst[i][0]
            if name == '': name=' '
            first=self.treepan.AppendItem(root,name)
            self.nameitemdic[name]=first
            if i == 0: expanditemid=first
            for j in range(len(self.treeitemlst[i][1])):
                second=self.treeitemlst[i][1][j]
                obj=self.treepan.AppendItem(first,second)
                self.nameitemdic[self.treeitemlst[i][1][j]]=obj
        if init:
            rootid=self.treepan.GetRootItem()
            self.treepan.SelectItem(rootid,True)
            self.treepan.SetItemBold(rootid,True)
            self.treepan.CollapseAndReset(rootid)
        else:
            name=self.curname
            #if self.curname == self.rootname: name='root'
            if self.curname == '': name=self.rootname
            selitem=self.nameitemdic[name]
            self.treepan.SelectItem(selitem,True)
            self.treepan.SetItemBold(selitem,True)
            #####self.ExpandItems()
            rootid=self.treepan.GetRootItem()
            self.treepan.Expand(rootid)

        lib.ChangeCursor(self,0)

    def GetExpandedItems(self):
        expandedlst=[]
        for name,itemobj in list(self.nameitemdic.items()):
            if itemobj.IsExpanded(itemobj): expandedlst.append(itemobj)
        return expandedlst

    def ExpandItems(self):
        if self.curname == '': return
        if self.rootname in self.expandedlst:
            self.treepan.ExpandAll()
            return
        if self.curname == self.rootname:
            self.treepan.ExpandAll()
            return
        #try:
        #    for itemobj in self.expandedlst: itemobj.Expand(itemobj)
        #except: pass

    def SetHtmlText(self,htmltext):
        """ Set html page

        :param str htmltext: html ,body text,
        '<html><body>Hello, world!</body></html>'
        """
        self.htmltext=htmltext
        self.htmlpan.SetPage(htmltext)

    def SetHtmlFile(self,htmlfile):
        """ Load html file

        :param str htmlfile: html file name
        """
        self.htmlfile=htmlfile
        ret=True
        if lib.GetPlatform() == 'MACOSX' and lib.IsWxVersion2():
            ret = self.htmlpan.LoadFile(self.htmlfile)
            mess='This function does not work on MacOSX and wxpython2.8'
            mess+='Please browse "users-guide-all.html" in the FUDATASET/users-guide/html directory'
            #wx.MessageBox(mess)
            #self.OnClose(1)
        else:
            ret=self.htmlpan.LoadFile(self.htmlfile)
        if not ret:
            wx.MessageBox('Failed to load htmlfile='+htmlfile)

    def SetTitle(self,title):
        self.title=title
        self.SetTitle(self.title)

    def GetTitle(self):
        return self.title

    def GetTextDic(self):
        return self.textdic

    def GetTreeItemList(self):
        return self.treeitemlst

    def TreeCollapse(self):
        self.treepan.CollapseAll()

    def TreeExpand(self):
        self.treepan.ExpandAll()

    def XXOnRightClick(self,event):
        (xx,yy)=wx.GetMousePosition()
        (x, y)=self.ScreenToClientXY(xx,yy)
        (selitem, flags) = self.HitTest((x, y))
        name=self.treepan.GetItemText(selitem)
        if name in self.textdic:
            mess=self.textdic[name]
            lib.MessageBoxOK(mess,'ToolsTipString')
        event.Skip()

    def OnTreeSelChanged(self,event):
        if not self.ready: return
        selitem=self.treepan.GetSelection()
        name=self.treepan.GetItemText(selitem)
        self.TreeSelChanged(selitem)
        self.curname=name

    def TreeSelChanged(self,selitem):
        name=self.treepan.GetItemText(selitem)
        if name == self.rootname: name='root'
        #if not self.toolsdic.has_key(name): return
        if self.prvname: self.treepan.SetItemBold(self.prvname,False)
        try: self.treepan.SetItemBold(self.prvname,False)
        except: pass
        self.treepan.SetItemBold(selitem,True)
        self.prvname=selitem
        #
        if name in self.htmldic:
            fudocdir=self.model.setctrl.GetDir('FUdocs')
            htmlfile=self.htmldic[name]
            htmlfile=lib.PathJoin(fudocdir,htmlfile)
            if lib.GetPlatform() == 'WINDOWS':
                htmlfile=htmlfile.replace('//','\\')
            self.SetHtmlFile(htmlfile)
        elif name in self.textdic:
            text=self.textdic[name]
            self.htmlpan.SetHtmlText(text)

    def OnPaint(self,event):
        event.Skip()

    def TreeSelCancel(self,event):
        print(' seltree Cancel')

    def TreeSelApply(self,event):
        selitm=self.treepan.GetSelections()
        text=self.treepan.GetItemText(selitm)

    def OnClose(self,event):
        #self.winctrl.Close(self.winlabel) #Win('TreeSelWin')
        try: self.parent.CloseHelpWin()
        except: pass
        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        self.Destroy()

    def CatHtmlText(self):
        """

        :return str text: concatinates text
        """
        name=self.curname
        #if self.curname == self.rootname: name="root"
        prtlst=[]
        case,sectionlst=self.GetTreeRankOfName(name)
        if case == '': return
        if case == 'Page': prtlst.append(name)
        elif case == 'Section':
            prtlst.append(name)
            for item in sectionlst: prtlst.append(item)
        elif case == 'Root':
            prtlst.append('root')
            for i in range(len(self.treeitemlst)):
                prtlst.append(self.treeitemlst[i][0])
                nitem=self.treeitemlst[i][1]
                if nitem > 0:
                    for item in self.treeitemlst[i][1]:
                        prtlst.append(item)
        filelst=[]
        for name in prtlst:
            if name in self.htmldic:
                fudocdir=self.model.setctrl.GetDir('FUdocs')
                htmlfile=self.htmldic[name]
                htmlfile=lib.PathJoin(fudocdir,htmlfile)
                if lib.GetPlatform() == 'WINDOWS':
                    htmlfile=htmlfile.replace('//','\\')
                if not os.path.exists(htmlfile): continue
                filelst.append(htmlfile)
        text=lib.CatTextInFiles(filelst)
        return text,filelst

    def Print(self,prt):
        """ Print html file

        :param bool prt: True for print, False for preview
        """
        text,filelst=self.CatHtmlText()
        if len(filelst) <= 0: return
        tmpdir,tail=os.path.split(filelst[0])
        tmphtmlfile=lib.PathJoin(tmpdir,'temp-for-print.html')
        f=open(tmphtmlfile,'w')
        f.write(text)
        f.close()
        if lib.GetPlatform() == 'WINDOWS':
            tmphtmlfile=tmphtmlfile.replace('//','\\')
        #
        htmlprt=wx.html.HtmlEasyPrinting(name='Printing users guide',
                                         parentWindow=self)
        if prt: htmlprt.PrintFile(tmphtmlfile)
        else: htmlprt.PreviewFile(tmphtmlfile)
        # remove temp html file
        try: os.remove(tmphtmlfile)
        except: pass

    def GetTreeRankOfName(self,name):
        case=''; sectionlst=[]
        if name == self.rootname: return 'Root',[]
        # section
        for i in range(len(self.treeitemlst)):
            if name == self.treeitemlst[i][0]:
                return 'Section',self.treeitemlst[i][1]
        for i in range(len(self.treeitemlst)):
            for name in self.treeitemlst[i][1]:
                return 'Page',[]

    def SaveHtmlFile(self):
        """ concatinate html file

        :param str onefile: True for one html file, False for hierarchical html
        """
        filename=lib.GetFileName(self,"html(*.html)|*.html",rw="w")
        if len(filename) <= 0: return
        text,filelst=self.CatHtmlText()
        f=open(filename,'w')
        f.write(text)
        f.close()
        mess='Saved html filename='+filename
        self.statusbar.SetStatusText(mess)

    def SetPrintOptions(self):
        pass

    def Usage(self):
        blk=3*' '
        text='Usage:\n\n'
        text=text+blk+'*Tree panel - Right click collapses all items\n\n'

        text=text+blk+'*HTML panel - Back to the previous page in history '
        text=text+'by right click on the panel\n'
        text=text+blk+'*HTML panel - Move to next page in history '
        text=text+'by left click on the panel\n'
        viewer=TextViewer_Frm(self,title="User's guide",text=text)

    def OnMenu(self,event):
        """ Menu handler
        """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        # File menu
        if item == "Print": self.Print(True)
        elif item == "Preview": self.Print(False)
        elif item == "Set options": self.SetPrintOptions()
        elif item == "Save htmls as one file": self.SaveHtmlFile()
        elif item == 'Expand all items': self.ExpandAllItems()
        elif item == 'Collapse all items': self.CollapseAllItems()
        # Help
        elif item == "Usage": self.Usage()


    def MenuItems(self):
        menubar=wx.MenuBar()
        submenu=wx.Menu()
        # File menu
        submenu.Append(-1,'Print','Print current page/Section')
        submenu.Append(-1,'Preview','Preview current section/page')
        submenu.AppendSeparator()
        #submenu.Append(-1,'Save html as','Save html file')
        submenu.Append(-1,'Save htmls as one file','one html file')
        #submenu.Append(-1,'Set options','Set header/footer')
        submenu.AppendSeparator()
        submenu.Append(-1,'Expand all items','expand all items')
        submenu.Append(-1,'Collapse all items','collapse all items')

        menubar.Append(submenu,'File')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Usage','Usage of the panel')
        menubar.Append(submenu,'Help')
        return menubar

class TextViewerWithTreeIndex_Frm(wx.MiniFrame):
    """ 'html' document is not suported yet 29Jun2015 """
    def __init__(self,parent,id,winpos,winsize,winlabel='HelpTree',
         treewidth=140,title='Help',docfile='',doctype='text',expandall=True,
         rootname='root',search=True):
        self.title=title
        winpos  = lib.SetWinPos(winpos)
        #winsize=lib.WinSize(winsize)
        wx.MiniFrame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
                          style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|\
                          wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent # futool
        self.model=self.parent.model
        self.winctrl=self.model.winctrl
        self.winlabel=winlabel
        #self.winctrl=model.winctrl
        #self.mdlwin=model.mdlwin
        #xxself.ctrlflag=model.ctrlflag
        #self.model=model #parent.model
        [w,h]=self.GetClientSize()
        self.treewidth=treewidth
        if treewidth <= 0: self.treewidth=120
        if self.treewidth > w: self.treewidth=w-20
        self.expandall=expandall
        self.search=search
        self.lenstr=0
        self.bgcolor='white'
        self.searchall=False
        #
        self.rootname=rootname
        self.treeitemlst=[]
        self.toolsdic={}
        self.tipdic={}
        self.expanditemid=None
        #self.saveitems=None
        font=self.GetFont()
        self.SetFont(font)
        self.prvname=None
        self.curpos=0
        self.searchstr=''
        self.searhcall=False
        #self.MakeItemLst()
        # Bind the OnSelChanged method to the tree
        self.doctype=doctype
        self.docfile=docfile
        self.textpan=None
        self.htmlpan=None
        self.CreatePanel()
        self.Show()
        # read docfile
        if self.docfile != '':
            self.treeitemlst,self.tipdic=self.ReadDocFile(self.docfile)
        if len(self.treeitemlst) > 0:
            self.SetTreeItemList(self.rootname,self.treeitemlst)
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)
    @staticmethod
    def ReadDocFile(docfile):
        contentslst=[]; itemlst=[]; tipdic={}; grplst=[]; text=''
        if not os.path.exists(docfile):
            mess='docfile='+docfile+' not found.'
            lib.MessageBoxOK(mess,'HelpPanel_Frm(ReadDocFile')
            return contentslst,tipdic
        #
        foundr=False; foundg=False; foundi=False; text=''
        f=open(docfile,'r')
        for s in f.readlines():
            if s[:1] == '#': continue
            #print 's',s
            if s[:8] == 'ROOT END':
                foundr=False
                tipdic['root']=text
                continue
            if s[:9] == 'GROUP END':
                foundg=False; grplst.append(itemlst)
                contentslst.append(grplst); grplst=[]
                text=''
                continue
            if s[:8] == 'ITEM END':
                tipdic[itemnam]=text
                foundi=False; text=''
                continue
            if s[:4] == 'ROOT':
                foundr=True
                text=''
                continue
            if s[:5] == 'GROUP':
                foundg=True; itemlst=[]
                grpnam=s[5:].strip()
                grplst.append(grpnam)
                continue
            if s[:4] == 'ITEM':
                foundi=True
                itemnam=s[4:].strip()
                text=''
                itemlst.append(itemnam)
                continue
            if foundi:
                text=text+s #+'\n'
                continue
            if foundr:
                text=text+s #+'\n'
                continue
        f.close()
        #
        return contentslst,tipdic

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        # tree panel
        yloc=8
        if self.search:
            ypos=2; xloc=w-300
            self.panel=wx.Panel(self,-1,pos=[0,0],size=[w,25])
            self.panel.SetBackgroundColour('white')
            sttxt=wx.StaticText(self.panel,-1,"Search:",pos=(xloc,ypos+2),
                                size=(60,18))
            sttxt.SetBackgroundColour('white')
            self.tclinp=wx.TextCtrl(self.panel,-1,pos=[xloc+60,ypos],
                                    size=[150,20],style=wx.TE_PROCESS_ENTER)
            self.tclinp.Bind(wx.EVT_TEXT,self.OnSearchText)
            #self.alltext=wx.CheckBox(self.panel,-1,"all",pos=[220,ypos],size=[30,20])
            #self.alltext.Bind(wx.EVT_CHECKBOX,self.OnSearchAll)
            #self.alltext.Disable()
            btnprev=wx.Button(self.panel,-1,"<",pos=(xloc+225,ypos),
                              size=(20,20))
            btnprev.Bind(wx.EVT_BUTTON,self.OnPrevSearch)
            btnnext=wx.Button(self.panel,-1,">",pos=(xloc+260,ypos),
                              size=(20,20))
            btnnext.Bind(wx.EVT_BUTTON,self.OnNextSearch)
            yloc += 20
        treepos=[0,yloc]
        tw=self.treewidth
        treesize=[tw,h-yloc]
        self.treepan=wx.TreeCtrl(self,-1,pos=treepos,size=treesize) #,
                                 #style=wx.TR_HIDE_ROOT)
        self.treepan.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelChanged)
        #self.treepan.Bind(wx.EVT_RIGHT_DOWN,self.OnRightClick)
        # descripton panel
        textpos=[tw+5,yloc]
        textsize=[w-tw-5,h-yloc]
        if self.doctype == 'text':
            self.textpan=wx.TextCtrl(self,-1,pos=textpos,size=textsize,
               style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2|wx.TE_NOHIDESEL)
            self.textpan.SetBackgroundColour(self.bgcolor)
        # this option is not tested
        elif self.doctype == 'html':
            self.htmlpan=wx.html.HtmlWindow(self,-1,pos=textpos,size=textsize,
                                            style=wx.NO_BORDER)
            #self.htmlpan.LoadPage('help.html') #http://zetcode.com/wxpython/advanced/
    def SetBGColor(self,color):
        self.bgcolor=color
        self.textpan.SetBackgroundColour(self.bgcolor)

    def OnPrevSearch(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchstr=self.tclinp.GetValue().strip()
        start=0
        end=self.textpan.GetInsertionPoint()-self.lenstr
        text=self.textpan.GetString(start,end)
        self.lenstr=len(self.searchstr)
        found=text.rfind(self.searchstr)
        if found >= 0:
            self.textpan.SetSelection(found,found+self.lenstr)
        else: pass

    def OnNextSearch(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchstr=self.tclinp.GetValue().strip()
        start=self.textpan.GetInsertionPoint()+self.lenstr
        end=self.textpan.GetLastPosition()
        text=self.textpan.GetString(start,end)
        self.lenstr=len(self.searchstr)
        found=text.find(self.searchstr)
        if found >= 0:
            self.textpan.SetSelection(start+found,start+found+self.lenstr)
        else: pass

    def OnSearchText(self,event):
        self.searchstr=self.tclinp.GetValue().strip()
        self.lenstr=0

    def OnSearchAll(self,event):
        #self.searchall=self.alltext.GetValue()
        self.searchall=False

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):
        self.panel.Destroy()
        self.treepan.Destroy()
        self.textpan.Destroy()
        self.CreatePanel()
        self.SetItemsToTree()
        self.DispTips()
        self.tclinp.SetValue(self.searchstr)
        #self.alltext.SetValue(self.searchall)

    def DispTips(self):
        pass


    def SetTreeItemList(self,rootname,treeitemlst):
        self.rootname=rootname
        self.treeitemlst=treeitemlst
        self.SetItemsToTree()

    def SetItemsToTree(self):
        """

        :param lst treelst: [[chainnam,[resnam1,...],[chainam2,[resnam1,]],...]
        treeitemlst=[
                     ['PDB tools',['pdb tool1','pdb tool2']],
                     ['FMO tools',['FMO tool1','FMO tool2']]
                     ]
        """
        self.toolsdic={}
        expanditemid=None
        root=self.treepan.AddRoot(self.rootname)

        for i in range(len(self.treeitemlst)):
            name=self.treeitemlst[i][0]
            if name == '': name=' '
            first=self.treepan.AppendItem(root,name)
            if i == 0: expanditemid=first
            for j in range(len(self.treeitemlst[i][1])):
                second=self.treeitemlst[i][1][j]
                self.treepan.AppendItem(first,second)
                self.toolsdic[self.treeitemlst[i][1][j]]=True
        rootid=self.treepan.GetRootItem()
        self.treepan.SetItemBold(rootid,True)
        if self.expandall: self.treepan.ExpandAll()
        else: self.treepan.Expand(rootid)
        text=self.tipdic['root']
        if self.doctype == 'text': self.textpan.SetValue(text)
        elif self.doctype == 'html': self.htmlpan.SetPage(text)
        # change cursor 0: arrow
        lib.ChangeCursor(self,0)

    def SetToolsTipDic(self,tipdic):
        self.tipdic=tipdic

    def SetTitle(self,title):
        self.title=title
        self.SetTitle(self.title)

    def GetTitle(self):
        return self.title

    def GetTipDic(self):
        return self.tipdic

    def GetTreeItemList(self):
        return self.treeitemlst

    def TreeCollapse(self):
        self.treepan.CollapseAll()

    def TreeExpand(self):
        self.treepan.ExpandAll()

    def XXOnRightClick(self,event):
        (xx,yy)=wx.GetMousePosition()
        (x, y)=self.ScreenToClientXY(xx,yy)
        (selitem, flags) = self.HitTest((x, y))
        name=self.treepan.GetItemText(selitem)
        if name in self.tipdic:
            mess=self.tipdic[name]
            lib.MessageBoxOK(mess,'ToolsTipString')
        event.Skip()

    def OnTreeSelChanged(self,event):
        selitem=self.treepan.GetSelection()
        name=self.treepan.GetItemText(selitem)
        if name == self.rootname: name='root'
        #if not self.toolsdic.has_key(name): return
        if self.prvname: self.treepan.SetItemBold(self.prvname,False)
        try: self.treepan.SetItemBold(self.prvname,False)
        except: pass
        self.treepan.SetItemBold(selitem,True)
        self.prvname=selitem
        if name in self.tipdic: text=self.tipdic[name]
        else: text='' #'no document available\n'
        if self.doctype == 'text': self.textpan.SetValue(text)
        elif self.doctype == 'html': self.htmlpan.SetPage(text)
    def XXOnFocus(self,event):
        return
        if self.saveitems:
            for item in self.saveitems:
                self.UnselectItem(item)
                self.SetItemBold(item,False)

    def XXOnResize(self, event):
        self.pantree.Destroy()
        self.SetMinSize([160,100])
        self.SetMaxSize([160,2000])
        self.size=self.GetClientSize()
        self.CreateTreeSelPanel()

    def OnPaint(self,event):
        event.Skip()

    def XXTreeSelOK(self,event):
        self.treepan.TreeSelApply(event)
        self.OnClose(1)
        #
        #self.ctrlflag.Set('TreeSelWin',False)
        #self.Destroy()

    def TreeSelCancel(self,event):
        print(' seltree Cancel')

    def TreeSelApply(self,event):
        selitm=self.treepan.GetSelections()
        text=self.treepan.GetItemText(selitm)

    def OnClose(self,event):
        #self.winctrl.Close(self.winlabel) #Win('TreeSelWin')
        try: self.parent.CloseHelpWin()
        except: pass
        self.Destroy()

class Tutorial_Frm(wx.Frame):
    def __init__(self,parent,id,winpos,winsize,winlabel='',
                 title='FU Tutorial',expandall=False,rootname='',
                 navimode=False,viewer='html'):
        """

        :param bool namimode: True for use navigation, False for use
        "ScriptEditor".
        """
        self.title=title
        if len(winpos) == 0: winpos=[0,20]
        if len(winsize) == 0: winsize=[240,300]
        winsize=lib.WinSize(winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,size=winsize,
                          style=wx.RESIZE_BORDER|wx.SYSTEM_MENU|wx.CAPTION|\
                          wx.CLOSE_BOX) #|wx.FRAME_FLOAT_ON_PARENT)
        self.parent=parent # futool
        self.model=self.parent.model
        self.mdlwin=self.model.mdlwin
        self.winctrl=self.model.winctrl
        self.winlabel=winlabel
        #
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        #self.stepmenuid=wx.NewId()
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[Tutorial]')
        #
        self.curdir=os.getcwd()
        self.docdir=self.model.setctrl.GetDir('FUdocs')
        self.tutorialdir=lib.PathJoin(self.docdir,'tutorial')
        self.treefile='' #tutorialdoc.contents'
        self.treefile=lib.PathJoin(self.tutorialdir,self.treefile)
        #self.treefile=lib.ReplaceBackslash(self.treefile)
        self.tutorialdatadir=lib.PathJoin(self.tutorialdir,'data')
        if not os.path.isdir(self.tutorialdatadir):
            self.OnClose(1)
            return

        os.chdir(self.tutorialdatadir)
        #
        self.navimode=navimode
        self.editorwin=None
        self.docwin=None
        self.inittree=False
        self.expandall=expandall
        self.rootname=rootname
        self.treeitemlst=[]
        self.scriptdic={}
        self.textdic={}
        self.htmldic={}
        self.expanditemid=None
        self.demodic={}
        self.demo=True
        self.navitext=''
        self.viewer=viewer # 'html' or 'text'
        #
        self.sleep=True
        self.sleeptime=1 # in sec
        #self.saveitems=None
        font=self.GetFont()
        self.SetFont(font)

        self.prvname=None
        #e
        self.CreatePanel()
        self.Hide()
        # copy data form FUdocs/data for tutorial
        self.SetData()

        self.Show()
        #
        self.Bind(wx.EVT_MENU,self.OnMenu)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_MOVE,self.OnMove)

    def CreatePanel(self):
        [w,h]=self.GetClientSize(); htree=h-30
        self.treepan=wx.TreeCtrl(self,-1,pos=[0,0],size=[w,htree]) #,
                                 #style=wx.TR_HIDE_ROOT)
        self.treepan.Bind(wx.EVT_TREE_SEL_CHANGED,self.OnTreeSelChanged)
        self.treepan.Bind(wx.EVT_RIGHT_DOWN,self.OnRightClick)
        ypan=h-30
        self.panel=wx.Panel(self,-1,pos=[0,ypan],size=[w,30])
        yloc=5; xloc=w-190
        self.btndemo=wx.Button(self.panel,-1,"Demo",pos=[xloc,yloc],
                               size=(50,20))
        self.btndemo.Bind(wx.EVT_BUTTON,self.OnDemo)
        #self.btndemo.SetToolTipString('Execute script at one step')
        lib.SetTipString(self.btndemo,'Execute script at one step')
        self.btnstart=wx.Button(self.panel,-1,"Start",pos=[xloc+60,yloc],
                                size=(50,20))
        self.btnstart.Bind(wx.EVT_BUTTON,self.OnStart)
        #self.btnstart.SetToolTipString('Start tutorial')
        lib.SetTipString(self.btnstart,'Start tutorial')
        btnclose=wx.Button(self.panel,-1,"Close",pos=[xloc+120,yloc],
                           size=(50,20))
        btnclose.Bind(wx.EVT_BUTTON,self.OnClose)
        #btnclose.SetToolTipString('Close this panel')
        lib.SetTipString(btnclose,'Close this panel')

    def SetContentsData(self,rootname,treeitemlst,textdic,htmldic,
                        scriptdic,demodic):
        self.rootname=rootname
        self.treeitemlst=treeitemlst
        self.textdic=textdic
        self.htmldic=htmldic
        self.scriptdic=scriptdic
        self.demodic=demodic
        if len(self.treeitemlst) > 0:
            self.SetTreeItemList(self.rootname,self.treeitemlst)
        #
        self.Show()

    def GetScriptForSelectedItem(self):
        """

        :param str dicname: 'script' or 'demo'
        """
        selitem=self.treepan.GetSelection()
        itemname=self.treepan.GetItemText(selitem)
        if self.demo: dic=self.demodic
        else: dic=self.scriptdic
        if itemname not in dic:
            mess='No script/demo file for itemname='+itemname
            lib.MessageBoxOK(mess,'Tutorial_Frm(OnStart)')
            return ''
        file=dic[itemname]
        filename=lib.PathJoin(self.tutorialdir,file)
        return filename

    def MakeScriptBlocks(self,scriptfile):
        scriptblocklst=[]; nblocks=0
        if not os.path.exists(scriptfile):
            mess='Not found script file='+scriptfile
            lib.MessageBoxOK(mess,'Tutorial_Frm(MakeScriptBlocks)')
            return nblocks,scriptblocklst
        f=open(scriptfile,'r')
        textlst=f.readlines()
        f.close()
        found=False; text=''
        for s in textlst:
            if s[:3] == '#-#':
                nblocks += 1
                if found and len(text) > 0: scriptblocklst.append(text)
                found=True; text=''
            else: text=text+s+'\n'
        if len(text) > 0:
            scriptblocklst.append(text)
            if nblocks == 0: nblocks=1
        return nblocks,scriptblocklst

    def OnStart(self,event):
        self.stepnmb=0; self.demo=False
        self.curscript=self.GetScriptForSelectedItem()
        if self.curscript == '': return
        """
        self.RunTutorial(True)
        """
        try: self.docwin.Destroy()
        except: pass
        try: self.navictrl.Destroy()
        except: pass
        # is shell active
        self.pyshell=self.model.winctrl.GetWin('Open PyShell')
        if not self.pyshell:
            mess='PyShell is not active.'
            lib.MessageBoxOK(mess,'Tutorial(RunScript)')
        mess='Starts Tutorial: script='+self.curscript+'\n'
        self.model.ConsoleMessage(mess)
        #
        if self.navimode:
            self.nblocks,self.scriptblocklst= \
                                     self.MakeScriptBlocks(self.curscript)
            # open navictrl
            if self.nblocks > 0:
                self.stepno=0
                pos=self.model.mdlwin.GetPosition()
                size=self.model.mdlwin.GetSize()
                winpos=[pos[0]+size[0]+20,pos[1]+20]
                self.navictrl=TextBox_Frm(self,winpos=winpos,
                                          title='Navigation',
                                          retmethod=self.RetFromNavi)
                self.navitext=mess+'\n> Press "OK" button to proceed'
                self.Navigation(self.nblocks,self.stepno)
        else:
            if not self.editorwin:
                # open ScriptEditor
                [x,y]=self.GetPosition(); [w,h]=self.GetSize()
                winpos=[x+w,y]; winsize=[500,300]
                title='ScriptEditor'
                self.editorwin=TextEditor_Frm(self,-1,winpos,winsize,title,'',
                                              scriptmode=True)
            # set script text to ScriptEditor
            self.editorwin.LoadTextFromFile(self.curscript)

    def RetFromNavi(self,retvalue):
        """ Return from navigation panel

        :param str retvalue: return value, 'ok' or 'cancel'
        (from subwin.TextBox_Frm instance)
        """
        if retvalue == 'ok':
            if self.stepno >= self.nblocks:
                mess='End of script block encountered. step='+str(self.stepno)
                self.model.ConsoleMessage(mess)
                try: self.navictrl.Destroy()
                except: pass
                self.stepno=-1
                return
            self.model.mdlwin.SetFocus()
            mess='# Step page='+str(self.stepno)
            self.model.ConsoleMessage(mess)
            ###ExecProg_Frm.EVT_THREADNOTIFY(self.model.mdlwin,self.EndThread)
            try: text=self.scriptblocklst[self.stepno]
            except:
                self.stepno=self.nblocks
                return
            tempfile=self.MakeTempFile(text)
            tempfile=tempfile.replace('\\','//')
            # pyshell.shell.runfile(tempfile) # do not work as expected!
            #py3#method='execfile('+"'"+tempfile+"'"+')'
            method = 'exec(open(' + "'" + tempfile + "'" + ').read())'
            self.pyshell.shell.run(method)
            self.stepno += 1
            if self.stepno >= self.nblocks:
                try: self.navictrl.Destroy()
                except: pass
            else: self.Navigation(self.nblocks,self.stepno)

        elif retvalue == 'cancel':
            mess='Cancelled by user at step='+str(self.stepno-1)
            self.model.ConsoleMessage(mess)
            try: self.navictrl.Destroy()
            except: pass
            self.stepno=-1
            return

    def OnDemo(self,event):
        self.stepnmb=0; self.demo=True
        self.curscript=self.GetScriptForSelectedItem()
        if self.curscript == '': return
        self.RunDemo(False)

    def EndThread(self):
        pass

    def Navigation(self,nblocks,step):
        text=self.navitext
        selitem=self.treepan.GetSelection()
        itemname=self.treepan.GetItemText(selitem)
        mess='Tutorial title='+itemname+'\n'
        mess=mess+'Step page='+str(step)+'/'+str(nblocks)+'\n'
        mess=mess+50*'-'+'\n'
        mess=mess+text
        #[x,y]=self.GetPosition()
        #winpos=[x+20,y+20] # ignored in MS WINDOWS
        #title='Navigation'
        self.navictrl.SetText(mess)
        #dlg=wx.MessageDialog(self,mess,caption='Navigation',pos=winpos,
        #                     style=wx.OK|wx.CANCEL)
        #if dlg.ShowModal() == wx.ID_OK: return True
        #else: return False
        #return lib.MessageBoxOKCancel(mess,title)
        """
        subwin.TextBox_Frm(self,title='Navigation',retmethod=self.RetFromNavi)
        """

    def SetNavigation(self,text):
        self.navitext=text

    def RunTutorial(self,withguide):
        """ Execute tutorial script step-by-step

        :param bool withguide: True for execute script step-by-step
        with navigation
                               False for without
        """
        try: self.docwin.Destroy()
        except: pass
        #
        pyshell=self.model.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='PyShell is not active.'
            lib.MessageBoxOK(mess,'Tutorial(RunScript)')
        mess='Starts Tutorial: script='+self.curscript+'\n'
        self.model.ConsoleMessage(mess)
        #
        nblocks,scriptblocklst=self.MakeScriptBlocks(self.curscript)
        if len(scriptblocklst) > 0:
            for step in range(len(scriptblocklst)):
                self.model.mdlwin.SetFocus()
                self.stepno=step+1
                mess='# Step number='+str(step+1)
                self.model.ConsoleMessage(mess)
                ExecProg_Frm.EVT_THREADNOTIFY(self.model.mdlwin,self.EndThread)
                if not self.demo:
                    retcode=self.Navigation(nblocks,step+1)
                    if not retcode:
                        mess='Cancelled by user at step='+str(step+1)
                        self.model.ConsoleMessage(mess)
                        break
                if self.demo and self.sleep: wx.Sleep(self.sleeptime)
                text=scriptblocklst[step]
                tempfile=self.MakeTempFile(text)
                tempfile=tempfile.replace('\\','//')
                # pyshell.shell.runfile(tempfile) # do not work as expected!
                #py3#method='execfile('+"'"+tempfile+"'"+')'
                method = 'exec(open(' + "'" + tempfile + "'" + ').read())'
                pyshell.shell.run(method)
                #pyshell.shell.prompt()

    def RunDemo(self,withguide):
        """ Execute tutorial script step-by-step

        :param bool withguide: True for execute script step-by-step
        with navigation
                               False for without
        """
        try: self.docwin.Destroy()
        except: pass
        #
        pyshell=self.model.winctrl.GetWin('Open PyShell')
        if not pyshell:
            mess='PyShell is not active.'
            lib.MessageBoxOK(mess,'Tutorial(RunScript)')
        mess='Starts Tutorial: script='+self.curscript+'\n'
        self.model.ConsoleMessage(mess)
        #
        nblocks,scriptblocklst=self.MakeScriptBlocks(self.curscript)
        if len(scriptblocklst) > 0:
            for step in range(len(scriptblocklst)):
                self.model.mdlwin.SetFocus()
                self.stepno=step+1
                mess='# Step number='+str(step+1)
                self.model.ConsoleMessage(mess)
                ExecProg_Frm.EVT_THREADNOTIFY(self.model.mdlwin,self.EndThread)
                """
                if not self.demo:
                    retcode=self.Navigation(nblocks,step+1)
                    if not retcode:
                        mess='Cancelled by user at step='+str(step+1)
                        self.model.ConsoleMessage(mess)
                        break

                if self.demo and self.sleep: wx.Sleep(self.sleeptime)
                """
                if self.sleep: wx.Sleep(self.sleeptime)
                #
                text=scriptblocklst[step]
                tempfile=self.MakeTempFile(text)
                tempfile=tempfile.replace('\\','//')
                # pyshell.shell.runfile(tempfile) # do not work as expected!
                #py#method='execfile('+"'"+tempfile+"'"+')'
                method = 'exec(open(' + "'" + tempfile + "'" + ').read())'
                pyshell.shell.run(method)
                #pyshell.shell.prompt()

    def MakeTempFile(self,text):
        scrdir=self.model.setctrl.GetDir('Scratch')
        if not os.path.isdir(scrdir):
            mess='Not found "Scratchs" directory.'
            lib.MessageBoxOK(mess,'TextEditor(MakeTempFile)')
            return
        tempfile='tutorial-temp.py'
        tempfile=os.path.join(scrdir,tempfile)
        f=open(tempfile,'w')
        f.write(text)
        f.close()
        return tempfile

    def OnRightClick(self,event):
        if self.docwin is None:
            selitem=self.treepan.GetSelection()
            name=self.treepan.GetItemText(selitem)
            if name == self.rootname: name='root'

            if self.viewer == 'html':
                if name in self.htmldic:
                    htmlfile=self.htmldic[name]
                    docdir=self.model.setctrl.GetDir('FUdocs')
                    htmldir=os.path.join(docdir,'tutorial//html')
                    htmldir=os.path.join(docdir,htmldir)
                    htmlfile=os.path.join(htmldir,htmlfile)
                    if lib.GetPlatform() == 'WINDOWS':
                        htmlfile=htmlfile.replace('//','\\')
                    ###htmlfile=htmlfile.replace('//','\\')
                    self.OpenHtmlViewer(htmlfile)
            else: # text
                if name in self.textdic: text=self.textdic[name]
                else: text=''
                self.OpenTextViewer(text)
        else:
            try: self.docwin.Destroy()
            except: pass
            self.docwin=None

        event.Skip()

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):
        try: selitem=self.treepan.GetSelection()
        except: pass
        self.treepan.Destroy()
        self.panel.Destroy()
        self.CreatePanel()
        self.SetItemsToTree()
        try: self.treepan.SelectItem(selitem,True)
        except: pass

    def SetTreeItemList(self,rootname,treeitemlst):
        self.rootname=rootname
        self.treeitemlst=treeitemlst
        self.SetItemsToTree()

    def SetItemsToTree(self):
        """

        eaxmple: treeitemlst=[
                     ['PDB tools',['pdb tool1','pdb tool2']],
                     ['FMO tools',['FMO tool1','FMO tool2']]
                     ]
        """
        self.toolsdic={}
        expanditemid=None
        root=self.treepan.AddRoot(self.rootname)

        for i in range(len(self.treeitemlst)):
            name=self.treeitemlst[i][0]
            if name == '': name=' '
            first=self.treepan.AppendItem(root,name)
            if i == 0: expanditemid=first
            for j in range(len(self.treeitemlst[i][1])):
                second=self.treeitemlst[i][1][j]
                self.treepan.AppendItem(first,second)
                self.toolsdic[self.treeitemlst[i][1][j]]=True
        rootid=self.treepan.GetRootItem()
        self.treepan.SetItemBold(rootid,True)
        if self.expandall: self.treepan.ExpandAll()
        else: self.treepan.Expand(rootid)
        if not self.inittree:
            self.treepan.SelectItem(rootid,True)
            self.inittree=True
        #
        lib.ChangeCursor(self,0)

    def SetTextDic(self,textdic):
        self.textdic=textdic

    def SetTitle(self,title):
        self.title=title
        self.SetTitle(self.title)

    def GetTitle(self):
        return self.title

    def GetTextDic(self):
        return self.textpdic

    def GetTreeItemList(self):
        return self.treeitemlst

    def OnTreeSelChanged(self,event):
        selitem=self.treepan.GetSelection()
        name=self.treepan.GetItemText(selitem)
        if name == self.rootname: name='root'
        if self.prvname: self.treepan.SetItemBold(self.prvname,False)
        try: self.treepan.SetItemBold(self.prvname,False)
        except: pass
        self.treepan.SetItemBold(selitem,True)
        self.prvname=selitem

        if name in self.scriptdic: self.btnstart.Enable()
        else: self.btnstart.Disable()
        if name in self.demodic: self.btndemo.Enable()
        else: self.btndemo.Disable()
        #
        """
        if self.viewer == 'html':
            if self.htmldic.has_key(name):
                htmlfile=self.htmldic[name]
                docdir=self.model.setctrl.GetDir('FUdocs')
                htmldir=os.path.join(docdir,'tutorial//html')
                htmldir=os.path.join(docdir,htmldir)
                htmlfile=os.path.join(htmldir,htmlfile)
                if lib.GetPlatform() == 'WINDOWS': htmlfile=htmlfile.replace('//','\\')
                ###htmlfile=htmlfile.replace('//','\\')
                self.OpenHtmlViewer(htmlfile)
        else: # text
            if self.textdic.has_key(name): text=self.textdic[name]
            else: text=''
            self.OpenTextViewer(text)
        """

    def OpenHtmlViewer(self,htmlfile):
        if self.docwin:
            [wd,hd]=self.docwin.GetSize()
            self.docwin.Destroy()
        if not os.path.exists(htmlfile): return
        wd=400
        ysize=200
        [x,y]=self.GetPosition()
        [w,h]=self.GetSize()
        winpos=[x,y+h]; winsize=[wd,ysize]
        selname=self.treepan.GetItemText(self.treepan.GetSelection())
        title='Tutorial: item='+selname
        self.docwin=HtmlViewer_Frm(self,winpos=winpos,winsize=winsize,
                                      htmlfile=htmlfile,fumodel=self.model)

    def OpenTextViewer(self,text):
        if self.docwin:
            [wd,hd]=self.docwin.GetSize()
            self.docwin.Destroy()
        if len(text) <= 0: text='No description is availabel'
        wd=400
        ysize=(len(text.split('\n'))+1)*18
        if ysize < 20: ysize=20
        if ysize > 200: ysize=200
        ysize=200
        [x,y]=self.GetPosition()
        [w,h]=self.GetSize()
        winpos=[x,y+h+10]; winsize=[wd,ysize]
        selname=self.treepan.GetItemText(self.treepan.GetSelection())
        title='Tutorial: item='+selname
        self.docwin=TextViewer_Frm(self,winpos=winpos,winsize=winsize,
                                   title=title,text=text,model=self.model)

    def SetSleep(self,on):
        if on:
            self.sleep=True
            if self.sleeptime == 0: self.sleeptime=1
        else: self.sleep=False

    def GetSleepTime(self):
        text=wx.GetTextFromUser('Please enter sleep time in sec.',
                                caption='Sleep')
        if len(text) > 0: self.sleeptime=int(text)
        print(('sleeptime',self.sleeptime))

    def SetSleepTime(self,time):
        """ time in sec """
        self.sleeptime=time

    def TreeCollapse(self):
        self.treepan.CollapseAll()

    def TreeExpand(self):
        self.treepan.ExpandAll()

    def OnPaint(self,event):
        event.Skip()

    def SetData(self):
        """ copy data file in FUDATASET/FUdocs/data to tutorial/data

        """
        extlst=['all'] # exts to be copied
        #
        docdatadir=lib.PathJoin(self.docdir,'data')
        tutorialdatadir=lib.PathJoin(self.tutorialdir,'data')
        # Delete tutorial data
        lib.DeleteFilesInDirectory(tutorialdatadir,'all')
        # copy files with extentions in extlst from docdatadir
        filelst=lib.GetFilesInDirectory(docdatadir,extlst)
        for file in filelst:
            if os.path.isdir(file): continue
            shutil.copy(file,tutorialdatadir)
        # delete all files in scratch in tutorial
        tutorialscratchdir=lib.PathJoin(self.tutorialdir,'scratch')
        lib.DeleteFilesInDirectory(tutorialscratchdir,'all')

    def OnClose(self,event):
        #self.winctrl.Close(self.winlabel) #Win('TreeSelWin')
        os.chdir(self.curdir)
        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        try: self.editorwin.Destroy()
        except: pass
        try: self.model.ShowWin()
        except: pass
        self.Destroy()

    def ExpandAllItems(self):
        try: self.treepan.ExpandAll()
        except: pass

    def CollapseAllItems(self):
        try: self.treepan.CollapseAll()
        except: pass

    def Usage(self):
        blk=3*' '
        text='Usage:\n\n'
        text=text+blk+'*Click an item in the tree menu items.\n'
        text=text+blk+'(Right click to view the description)\n'
        text=text+blk+'*Push "Demo" button to execute the demo.\n'
        text=text+blk+'*Push "Start" button to open the instruction panel\n'
        text=text+blk+'   and follow the instructions\n'
        winsize=[550,180]
        viewer=TextViewer_Frm(self,title='Tutorial',text=text,winsize=winsize)

    def OnMenu(self,event):
        """ Menu handler
        """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        bChecked=self.menubar.IsChecked(menuid)
        # Option
        if item == 'Set sleep in "Demo"': self.SetSleep(bChecked)
        if item == 'Set sleep time': self.GetSleepTime()
        if item == 'Reset data': self.SetData()
        if item == 'Expand all items': self.ExpandAllItems()
        if item == 'Collapse all items': self.CollapseAllItems()
        # Help
        if item == 'Usage': self.Usage()

    def MenuItems(self):
        menubar=wx.MenuBar()
        submenu=wx.Menu()
        # option
        id=wx.NewId()
        submenu.Append(id,'Set sleep in "Demo"','Set sleep on/off',
                       kind=wx.ITEM_CHECK )
        submenu.Append(-1,'Set sleep time','Set sleep time')
        submenu.AppendSeparator()
        submenu.Append(-1,'Reset data','Reset data for tutorial')
        submenu.AppendSeparator()
        submenu.Append(-1,'Expand all items','Expand all items')
        submenu.Append(-1,'Collapse all items','Collapse all items')
        menubar.Append(submenu,'Options')
        submenu.Check(id,True)
        # help
        submenu=wx.Menu()
        submenu.Append(-1,'Usage','Open usage document panel')
        menubar.Append(submenu,'Help')

        return menubar


class RelatedFunctions(object):
    def __init__(self,parent,id,model,menulst=[],tiplst=[],curitem=''):
        """ execute related functions

        :param obj parent: window class object
        """
        self.parent=parent # window object
        self.model=model
        #
        self.defaulttipdic=self.DefaultTipDic()
        self.menulst=menulst
        self.tiplst=tiplst
        if len(self.tiplst) <= 0: self.tiplst=self.SetTipList()
        self.curitem=curitem
        # create ListBoxMenu
        retmethod=self.OnItemSelected
        menulabel='RelatedFunctions'
        #self.listboxmenu=lib.ListBoxMenu_Frm(self,-1,winpos,winsize,menulabel,menulst,tiplst)
        self.listmenu=ListBoxMenu_Frm(parent,-1,[],[],retmethod, # winpos=[],winsize=[]
                                        self.menulst,tiplst=self.tiplst,   # submenudic={},subtipdic={}
                                        menulabel=menulabel)

    def OnItemSelected(self,item,menulabel):
        if item == '' or item == '---': return # separator
        if item == 'Close': self.OnClose(1)
        if item == 'CloseMe': self.OnClose(1)
        elif item == "ZmtViewer": self.OpenZmtViewer()
        elif item == "RotCnfEditor": self.OpenRotCnfEditor()
        elif item == "ZmtCnfEditor": self.OpenZmtCnfEditor()
        elif item == "TINKER": self.ExecTinker()
        elif item == 'GAMESS': self.ExecGAMESS()
        elif item == 'OneByOneViewer': self.OpenOneByOneViewer()
        else:
            mess='Not defined item='+item
            mess=mess+'. Please modify the source of this class.'
            lib.MessageBoxOK(mess,'subwin.RelatedFunctions')
        self.OnClose(1)

    def DefaultTipDic(self):
        defaulttipdic={}
        defaulttipdic['Close']='Close this panel'
        defaulttipdic['CloseMe']='Close this panel'
        defaulttipdic['---']='This is separator'
        defaulttipdic['']='This is separator'
        defaulttipdic['ZmtViewer']='Display Z-matrix'
        defaulttipdic['RotCnfEditor']='Edits conformation by bond-rotations'
        defaulttipdic['ZmtCnfEditor']= \
                                'Edits conformation by Z-matrix type paramters'
        defaulttipdic['TINKER']='Molecular mechanics program'
        defaulttipdic['GAMESS']='Molecular orbital program'
        defaulttipdic['OneByOneViewer']='View resdiue/fragment one-by-one'
        return defaulttipdic

    def SetTipList(self):
        tiplst=[]
        for name in self.menulst:
            if name in self.defaulttipdic:
                tiplst.append(self.defaulttipdic[name])
            else: tiplst.append('Not availabel')
        return tiplst

    def OpenZmtViewer(self):
        build.ZMatrixEditor_Frm(self.model.mdlwin,-1)

    def ExecTinker(self):
        self.model.ExecuteAddOnScript('tinker-optimize.py',False)

    def ExecGAMESS(self):
        self.model.ExecuteAddOnScript('gamess-user.py',False)

    def OpenRotCnfEditor(self):
        build.RotateBond_Frm(self.model.mdlwin,-1,winpos=[50,150])

    def OpenZmtCnfEditor(self):
        pos=self.model.mdlwin.GetPosition()
        size=self.model.mdlwin.GetSize()
        winpos=[pos[0]+size[0],pos[1]+50]
        build.ZMCnfEditor_Frm(self.model.mdlwin,-1,self.model,winpos=winpos)

    def OpenOneByOneViewer(self):
        self.model.menuctrl.OnShow('One-by-One',True)

    def OnClose(self,event):
        try: self.Destroy()
        except: pass

class BitmapButtonWithDispWin(object):
    def __init__(self,parent,id,iconfile,winpos,menulst,tiplst=[],displst=[],
                 dispwidth=25,retmethod=None,curitem=''):
        """ Note: bitmap button size=[40,25] (fixed)


        """
        if len(winpos) <=0: winpos=[0,0]
        self.parent=parent # window object
        self.menulst=menulst
        self.tiplst=tiplst
        self.displst=displst
        self.retmethod=retmethod
        self.winpos=winpos
        self.dispwidth=dispwidth
        self.winlabel='BitmapButtonWithDispWin'
        self.curitem=curitem
        # constants
        self.btnwidth=40; self.btnheight=25
        self.btnsize=[self.btnwidth,self.btnheight]
        self.disppos=[self.winpos[0]+self.btnwidth,self.winpos[1]]
        # load bitmap
        if os.path.exists(iconfile):
            self.iconbmp=iconbmp=wx.Bitmap(iconfile,wx.BITMAP_TYPE_ANY)
        else: self.iconbmp=None
        self.btn=None
        self.CreateButton()

        self.btn.Bind(wx.EVT_MOVE,self.OnMove)

    def CreateButton(self):
        if self.iconbmp == None: self.btn=wx.Button(self.parent,-1,"BTN",
                                              pos=self.winpos,size=self.btnsize)
        else: self.btn=wx.BitmapButton(self.parent,-1,bitmap=self.iconbmp,
                                       pos=self.winpos,size=self.btnsize)

        self.btn.Bind(wx.EVT_BUTTON,self.OnButton)
        self.dispwin=wx.TextCtrl(self.parent,-1,'',pos=self.disppos,
                                 size=(self.dispwidth+2,self.btnheight-4),
                                 style=wx.TE_READONLY)
        self.dispwin.SetValue(self.DispText())

    def DispText(self):
        try: idx=self.menulst.index(self.curitem)
        except: idx=-1
        if idx >=0: text=self.displst[idx]
        else: text=self.curitem[:2]
        return text

    def OnButton(self,event):
        lbmenu=subwin.ListBoxMenu_Frm(self.btn,-1,[],[],self.OnMenu,
                                      self.menulst,self.tiplst)
        event.Skip()

    def OnMenu(self,menuitem,label):
        try: idx=self.menulst.index(menuitem)
        except: idx=-1
        if idx >=0: text=self.displst[idx]
        else: text=menuitem[:2]
        self.dispwin.SetValue(text)
        try: self.retmethod(menuitem,self.winlabel)
        except: pass
        self.curitem=menuitem

    def OnMove(self,event):
        self.btn.Destroy()
        self.dispwin.Destroy()
        self.CreateButton()
        event.Skip()


class Reset_Button(wx.BitmapButton):
    def __init__(self,parent,id,retmethod=None,winpos=[],tips=None):
        """ Reset bitmap button

        :param obj parent: parent panel object
        :paream obj retmethod: return method
        :param str tips: tips string
        """
        hbtn=22;
        winsize=(hbtn,hbtn)
        if len(winpos) <= 0:
            pos=parent.GetPosition()
            size=parent.GetSize()
            winpos=(size[0]-hbtn,0)
        resetbmp=const.SETCTRL.GetIconBmp('reset')
        #
        wx.BitmapButton.__init__(self,parent,id,bitmap=resetbmp,pos=winpos,
                                 size=winsize)
        # Reset button
        #try: self.btnreset=wx.BitmapButton(parent,-1,bitmap=self.resetbmp,pos=(w-22,0),size=(hbtn,hbtn))
        #except: self.btnreset=wx.Button(parent,-1,"R",pos=(w-22,0),size=(hbtn,hbtn))
        if tips is None: tipmess = 'Force to restore current molecule in mdlwin'
        else: tipmess = tips
        #self.SetToolTipString(tipmess)
        lib.SetTipString(self,tipmess)
        if retmethod != None: self.Bind(wx.EVT_BUTTON,retmethod)

class GetInputFromUser_Frm(wx.MiniFrame):
    def __init__(self,parent,id,title='',winpos=[],winsize=[],model=None,
                 retmethod=None,labels=[],cellwidth=[],values=[],
                 menu=False,extractbutton=False,extractitems=[],
                 resetmethod=None,selobj=None):
        """ extractbutton is not supported. 11Feb2016

        """
        self.title=title
        if len(self.title) <= 0: self.title='GetInputFromUser'
        self.winlabel='GetInputFromUser' # = helpname
        if len(winpos) <= 0: winpos=lib.WinPos(parent)
        self.winsize=winsize
        self.rowheight=22
        if len(self.winsize) <= 0:
            ndat=len(values); nitem=len(values[0])
            if ndat <= 0: ndat=5
            if nitem <= 0: nitem=2
            self.winsize=self.ComputeWinsize(ndat,nitem,cellwidth)
        self.winsize=lib.MiniWinSize(self.winsize)
        winpos  = lib.SetWinPos(winpos)
        wx.MiniFrame.__init__(self,parent,id,self.title,pos=winpos, \
                 size=self.winsize, \
                 style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)
        #
        self.model=model
        self.retmethod=retmethod
        self.resetmethod=resetmethod
        # extract button
        self.extractbutton=extractbutton
        # title
        try: self.title=self.title+' ['+self.model.mol.name+']'
        except: pass
        self.SetTitle(self.title)
        # Menu
        if menu:
            self.menubar=self.MenuItems()
            self.SetMenuBar(self.menubar)
            lib.InsertTitleMenu(self.menubar,'[GetInput]')
            self.Bind(wx.EVT_MENU,self.OnMenu)
        # vars: variables whose label begin with '!'
        self.labels=labels; self.cellwidth=cellwidth; self.vars=[]
        if len(labels) <= 0:
            self.labels=['!param','value']
        else:
            for i in range(len(self.labels)):
                label=labels[i]
                if self.labels[i][:1] == '!':
                    self.vars.append(True); label=self.labels[i][1:]
                else: self.vars.append(False)
                self.labels[i]=label
        #
        if len(cellwidth) <= 0: self.cellwidth=len(self.labels)*[60]
        if self.extractbutton:
            self.extractitems=extractitems
            if len(self.extractitems) <= 0:
                self.extractitems=['all','selected','item=value']
            self.extract=self.extractitems[0]
        #
        self.changedcolor=(165,40,40)
        self.unchangedcolor=wx.BLACK
        self.errorcolor=wx.RED
        #
        self.selobj=selobj
        self.values=values
        self.savvalues=copy.deepcopy(self.values)
        self.vartype=None
        self.CreatePanel()
        self.CreateGrid()
        if len(self.values) > 0:
            self.SetValuesToCells()
            self.vartype=self.SetVarType(self.values)
        self.changedcol=self.InitChangedCol()
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)

        self.Show()

    def CreatePanel(self):
        [w,h]=self.GetClientSize()
        self.panel=wx.Panel(self,-1,pos=[0,0],size=[w,h])
        self.panel.SetBackgroundColour('light gray')
        hbtn=25; hcb=const.HCBOX
        # Restore button
        if self.resetmethod is not None:
            btnrset=Reset_Button(self.panel,-1,self.OnReset)
            btnrset.SetLabel('Reset')
        yloc=5; xloc=10
        if self.extractbutton:
            txtext=wx.StaticText(self.panel,-1,'Extract:',pos=(xloc,yloc+2),
                                 size=(xloc+40,20))
            #txtext.SetToolTipString('Extract atoms by item and its value')
            lib.SetTipString(txtext,'Extract atoms by item and its value')
            self.cmbsel=wx.ComboBox(self.panel,-1,'',choices=self.extractitems,
                                   pos=(xloc+50,yloc), size=(80,hcb),
                                   style=wx.CB_READONLY) # 28<-22
            self.cmbsel.Bind(wx.EVT_COMBOBOX,self.OnExtract) #ControlPanMdl)
            self.cmbsel.SetValue(self.extract)
            #self.cmbsel.SetToolTipString('Choose extract item')
            lib.SetTipString(self.cmbsel,'Choose extract item')
            xloc += 130
        self.btnundo=wx.Button(self.panel,-1,"Undo",pos=(xloc+20,yloc),
                               size=(50,20))
        self.btnundo.Bind(wx.EVT_BUTTON,self.OnUndo)
        #self.btnundo.SetToolTipString('Undo "Apply"')
        lib.SetTipString(self.btnundo,'Undo "Apply"')
        self.btnaply=wx.Button(self.panel,-1,"Apply",pos=(xloc+90,yloc),
                               size=(50,20))
        self.btnaply.Bind(wx.EVT_BUTTON,self.OnApply)
        #self.btnaply.SetToolTipString('Apply current coordinates')
        lib.SetTipString(self.btnaply,'Apply current coordinates')
        #
        yloc += 25
        wx.StaticLine(self.panel,pos=(0,yloc),size=(w,2),style=wx.LI_HORIZONTAL)
        yloc += 8
        # grid table
        pansize=[w,h-yloc]
        if lib.IsWxVersion2():
            self.grid=wxgrid.Grid(self.panel,-1,pos=[0,yloc],size=pansize)
        else: self.grid=wx.grid.Grid(self.panel,-1,pos=[0,yloc],size=pansize)
        self.grid.EnableGridLines(True)
        self.grid.SetColLabelSize(25)
        self.grid.SetRowLabelSize(0) #50)
        try: self.grid.ShowScrollbars(wx.SHOW_SB_DEFAULT,wx.SHOW_SB_NEVER)
        except: pass

        self.grid.DisableDragCell()
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK,self.OnCellLeftClick)
        #self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.OnCellSelect)
        if lib.IsWxVersion2():
            self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE,self.OnCellChange)
        else:
            self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING,self.OnCellChange)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,self.OnCellRightClick)
        self.grid.Bind(wx.EVT_KEY_DOWN,self.OnKeyDown)

    def CreateGrid(self):
        #
        #self.grid.ClearGrid()
        nrow=len(self.values)
        if nrow == 0: nrow=1
        ncol=len(self.labels)
        self.grid.CreateGrid(nrow,ncol)
        for i in range(ncol): self.grid.SetColSize(i,self.cellwidth[i])
        for i in range(ncol):
            self.grid.SetColLabelValue(i,self.labels[i])
        for i in range(nrow): self.grid.SetRowSize(i,self.rowheight)

    def SetValuesToCells(self):
        if len(self.values) <= 0: return
        self.grid.ClearGrid()
        ncol=len(self.labels); nrow=len(self.values)
        for i in range(nrow):
            self.grid.SetRowLabelValue(i,str(i+1))
            for j in range(ncol):
                val=str(self.values[i][j])
                self.grid.SetCellValue(i,j,val)
                # edit enabled
                self.grid.SetReadOnly(i,j,isReadOnly=self.vars[j])
                try: self.grid.SetCellTextColour(i,j,self.changedcol[i][j])
                except: pass
        self.grid.Refresh()

    def InitChangedCol(self):
        if len(self.values) <= 0: return []
        changedcol=[]
        for i in range(len(self.values)):
            temp=[]
            for j in range(len(self.values[i])): temp.append(self.unchangedcolor)
            changedcol.append(temp)
        return changedcol

    def SetVarType(self,values):
        vartype=[]
        for val in values[0]: vartype.append(lib.ObjectType(val))
        return vartype

    def SetParamsAndValues(self,prmlst,vallst):
        self.params=prmlst
        self.values=vallst

    def OnCellSelect(self,event):
        """ not used """
        self.selectedcell=self.grid.GetSelectedCells()

    def ListSelectedRow(self):
        sellst=[]
        #prmcoldic={0:5,1:7,2:9}
        top=self.grid.GetSelectionBlockTopLeft()
        if len(top) <= 1: return sellst
        bottom=self.grid.GetSelectionBlockBottomRight()
        trow=top[1][0]; tcol=top[1][1]
        brow=bottom[1][0]; bcol=bottom[1][1]
        for i in range(trow,brow+1): sellst.append(i)
        return sellst

    def OnCellLeftClick(self,event):
        row=event.GetRow()
        self.selectedrow=row
        col=self.selectedcol=event.GetCol()
        self.grid.SelectBlock(row,col,row,col)
        self.grid.SetGridCursor(row,col)
         #
        value=self.grid.GetCellValue(row,col)
        if col == 0:
            seqnmb=int(value)-1
            if self.selobj is None: atmlst=[seqnmb]
            else: atmlst=self.selobj[seqnmb]
            if len(atmlst) <= 0: return
            try: self.model.SelectAtomsWithEnv(atmlst,renv=4.0)
            except:
                mess='May be not sequence number of atoms'
                lib.MessageBoxOK(mess,'GetInputFromUser(OnCellLeftClick)')

    def OnCellChange(self,event):
        row=self.selectedrow=event.GetRow()
        col=self.selectedcol=event.GetCol()
        value=self.grid.GetCellValue(row,col)
        value=value.strip()
        value=lib.ConvertStringToValue(value,self.vartype[col])
        if value is None:
            mess='Wrong data. the data type is "'+str(self.vartype[col]+'"')
            lib.MessageBoxOK(mess,'GetDataFromUser(OnCellChange)')
            self.grid.SetCellTextColour(row,col,self.errorcolor)
            return
        self.values[row][col]=value
        #self.grid.SetCellValue(row,col,str(value))
        self.grid.SetCellTextColour(row,col,self.changedcolor)
        self.changedcol[row][col]=self.changedcolor
        self.grid.Refresh()

    def OnCellRightClick(self,event):
        row=event.GetRow(); col=event.GetCol()
        mess=''
        if col == 0: mess='L-Click to select atom with env(4.0A)'
        else:
            if self.vars[col]: mess='Not editable'
            else: mess='Input value and "Enter"'
        tip=TipString(self,mess,bgcolor='yellow')

    def OnKeyDown(self,event):
        # ctrl-c: copy
        row=self.selectedrow; col=self.selectedcol
        if event.ControlDown() and event.GetKeyCode() == 67:
            text=self.grid.GetCellValue(row,col)
            lib.CopyTextToClipboard(text)
        # ctrl-v: paste
        if event.ControlDown() and event.GetKeyCode() == 86:
            text=lib.PasteTextFromClipboard()
            sellst=self.ListSelectedRow()
            if len(sellst) <= 0: sellst=[row]
            for row in sellst:
                if self.grid.IsReadOnly(row,col): continue
                self.grid.SetCellValue(row,col,text)
                self.grid.SetCellTextColour(row,col,self.changedcolor)
        self.grid.Refresh()

        event.Skip()

    def OnExtract(self,event):
        pass

    def OnDeselectAll(self,event):
        self.grid.ClearSelection()
        #nrow=len(self.values)
        #for i in range(nrow): self.grid.DeselectRow(i)

    def OnApply(self,event):
        if self.retmethod is not None:
            self.retmethod('OnApply',self.values)

    def OnCancel(self,event):
        pass

    def OnUndo(self,event):
        self.values=copy.deepcopy(self.savvalues)
        self.changedcol=self.InitChangedCol()
        self.SetValuesToCells()

    def OnReset(self,event):
        self.restmethod()

    def OnResize(self,event):
        self.panel.Destroy()
        self.SetMinSize([self.winsize[0],200])
        self.SetMaxSize([self.winsize[0],2000])
        self.CreatePanel()
        self.CreateGrid()
        self.SetValuesToCells()

    def OnClose(self,event):
        if self.retmethod is not None: self.retmethod('OnClose',self.values)
        self.Destroy()

    def ComputeWinsize(self,ndat,nitem,cellwidth):
        wwin=0
        for w in cellwidth: wwin += w
        wwin += 40
        hwin=self.rowheight*(ndat+1)+25+60
        if hwin > 400: hwin=400
        return [wwin,hwin]

    def MenuItems(self):
        """ not coded yet. 11Feb2016 """
        menubar=wx.MenuBar()

        return menubar

    def OnMenu(self,event):
        """ Menu event handler. not coded yet. 11Feb2016 """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        bChecked=self.menubar.IsChecked(menuid)


class MolChoicePanel(wx.Panel):
    def __init__(self,parent,id,winpos,winsize,mymgr,shape,mode=0):
        # window position

        if len(winpos) <= 0:
            #winpos=parent.canvas.GetScreenPosition()
            winpos=[500,100]
            parwinsize=parent.GetClientSize()
        if shape == 0:
            wbox=mymgr.GetWBox()
            wwin=wbox+115; winsize=(wwin,28) #; winpos[0] -= (wbox-120) # default wwin=230
            winpos[0] += (parwinsize[0]-wwin) #winsize[0]
            wx.MiniFrame.__init__(self,parent,id,pos=winpos,size=winsize,
                                  style=wx.FRAME_FLOAT_ON_PARENT)
        else:
            winpos[0] += parwinsize[0]
            wx.Panel.__init__(self,parent,id,pos=winpos,size=winsize,
                  style=wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.FRAME_FLOAT_ON_PARENT)
            #self.SetTitle('MolChoice')
        self.parent=parent
        self.mdlwin=parent
        self.mymgr=mymgr  # MolChoice
        self.mode=mode
        self.cboxmol=None
        # initialize variables
        self.panelpos=(2,2)
        self.winsize=winsize
        self.shape=shape
        self.panel=None
        self.helpname='MolCoice'
        # set font
        #self.font=self.GetFont()
        #self.font.SetPointSize(8)
        #self.SetFont(self.font)
        # set color
        self.fgcolor='black'
        self.bgcolor='light gray' #'gray'
        self.SetBackgroundColour(self.bgcolor)

        self.hideh=False
        # create panel
        self.CreatePanel()
        self.Show()
        # event handlers
        #??self.Bind(wx.EVT_ENTER_WINDOW,self.OnEnterWindow)
        #??self.Bind(wx.EVT_LEAVE_WINDOW,self.OnLeaveWindow)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

    def CreatePanel(self):
        if self.shape == 0: self.CreatePanel0()
        elif self.shape == 1: self.CreatePanel1()
        self.cboxmol.SetItems(self.mymgr.molnamlst)
        self.cboxmol.SetStringSelection(self.mymgr.selectmol)

    def CreatePanel0(self):
        # pulldown mol choice
        htext=20; hbox=const.HCBOX #18
        btnsize=[8,8]
        if lib.GetPlatform() == 'WINDOWS': btnsize=[10,10]
        xloc=self.panelpos[0]; yloc=self.panelpos[1]
        clsbtn=wx.Button(self,wx.ID_ANY,"",pos=(xloc,yloc),size=btnsize)
        clsbtn.SetBackgroundColour('red')
        clsbtn.Bind(wx.EVT_BUTTON,self.OnClose)
        #clsbtn.SetToolTipString('Close')
        lib.SetTipString(clsbtn,'Close')
        shpbtn=wx.Button(self,wx.ID_ANY,"",pos=(xloc,yloc+10),size=btnsize)
        shpbtn.SetBackgroundColour('white')
        shpbtn.Bind(wx.EVT_BUTTON,self.OnShape)
        #shpbtn.SetToolTipString('Change style')
        lib.SetTipString(shpbtn,'Change style')
        xloc += 14
        st0=wx.StaticText(self,wx.ID_ANY,'Molecule:',pos=(xloc,yloc+2),size=(55,htext))
        st0.SetFont(self.font)
        st0.SetForegroundColour(self.fgcolor)
        st0.Bind(wx.EVT_LEFT_DOWN,self.OnLeftDown)
        st0.Bind(wx.EVT_RIGHT_DOWN,self.OnRightDown)
        wbox=self.mymgr.GetWBox()
        self.cboxmol=wx.ComboBox(self,-1,'',
                           pos=(xloc+56,yloc),size=(wbox,hbox),style=wx.CB_READONLY|wx.WANTS_CHARS)
        self.cboxmol.Bind(wx.EVT_COMBOBOX,self.OnChoiceMol)
        #self.cboxmol.Bind(wx.EVT_COMBOBOX_DROPDOWN,self.OnDropDown)
        #self.cboxmol.Bind(wx.EVT_RIGHT_DOWN,self.RightDown)

        self.cboxsqbt1=wx.Button(self,wx.ID_ANY,"<",pos=(xloc+wbox+60,yloc+2),size=(15,15))
        self.cboxsqbt1.Bind(wx.EVT_BUTTON,self.OnChoicePrevMol)
        self.cboxsqbt2=wx.Button(self,wx.ID_ANY,">",pos=(xloc+wbox+78,yloc+2),size=(15,15))
        self.cboxsqbt2.Bind(wx.EVT_BUTTON,self.OnChoiceNextMol)

    def RightDown(self,event):
        print('right is down')

    def OnDropDown(self,event):
        print('DropDown')

    def CreatePanel1(self):
        # menubar
        #self.menubar=self.MenuItems()
        #self.SetMenuBar(self.menubar)
        #self.Bind(wx.EVT_MENU,self.OnMenu)

        [w,h]=self.GetClientSize()
        ######self.panel=wx.Panel(self,-1,pos=(-1,-1),size=(w,h))

        self.panel=self.parent


        htext=20; hbox=const.HCBOX
        btnsize=[8,8]
        if lib.GetPlatform() == 'WINDOWS': btnsize=[10,10]
        #??xloc=self.panelpos[0]; yloc=self.panelpos[1]
        xloc=5; yloc=5
        clsbtn=wx.Button(self.panel,wx.ID_ANY,"",pos=(xloc,yloc),size=btnsize)
        clsbtn.SetBackgroundColour('red')
        clsbtn.Bind(wx.EVT_BUTTON,self.OnClose)
        #clsbtn.SetToolTipString('Close')
        lib.SetTipString(clsbtn,'Close')
        shpbtn=wx.Button(self.panel,wx.ID_ANY,"",pos=(xloc,yloc+10),size=btnsize)
        shpbtn.SetBackgroundColour('white')
        shpbtn.Bind(wx.EVT_BUTTON,self.OnShape)
        #shpbtn.SetToolTipString('Change style')
        lib.SetTipString(shpbtn,'Change style')
        xloc += 14
        st0=wx.StaticText(self.panel,wx.ID_ANY,'Molecule:',pos=(xloc,yloc+2),size=(55,htext))
        #st0.SetFont(self.font)
        #st0.SetForegroundColour(self.fgcolor)
        self.cboxsqbt1=wx.Button(self.panel,wx.ID_ANY,"<",pos=(xloc+65,yloc),size=(15,htext))
        self.cboxsqbt1.Bind(wx.EVT_BUTTON,self.OnChoicePrevMol)
        self.cboxsqbt2=wx.Button(self.panel,wx.ID_ANY,">",pos=(xloc+90,yloc),size=(15,htext))
        self.cboxsqbt2.Bind(wx.EVT_BUTTON,self.OnChoiceNextMol)
        xloc=5; yloc += 22; wbox=w-10
        self.mymgr.SetWBox(wbox)
        self.cboxmol=wx.ComboBox(self.panel,-1,'',
                           pos=(xloc,yloc),size=(wbox,hbox),style=wx.CB_READONLY|wx.WANTS_CHARS)
        self.cboxmol.Bind(wx.EVT_COMBOBOX,self.OnChoiceMol)

    def OnLeftDown(self,event):
        wbox=self.mymgr.GetWBox()
        wbox += 10
        self.mymgr.SetWBox(wbox)
        self.mymgr.DestroyWin()
        self.mymgr.CreateWin()

    def OnRightDown(self,event):
        wbox=self.mymgr.GetWBox()
        wbox -= 10
        self.mymgr.SetWBox(wbox)
        self.mymgr.DestroyWin()
        self.mymgr.CreateWin()

    def OnResize(self,event):
        if self.shape == 1:
            try:
                self.panel.Destroy()
                self.CreatePanel1()
                self.SetMinSize([50,self.mymgr.winsize1[1]])
                self.SetMaxSize([2000,self.mymgr.winsize1[1]])
                self.cboxmol.SetItems(self.mymgr.molnamlst)
                self.cboxmol.SetStringSelection(self.mymgr.selectmol)
            except: pass
    def OnClose(self,event):
        self.mymgr.DestroyWin()
        self.mymgr.SetOpen(False)

    def OnShape(self,event):
        shape=self.mymgr.GetShape()
        if shape == 0: shape=1
        elif shape == 1: shape=0
        self.mymgr.ChangeShape(shape)

    def OnEnterWindow(self,event):
        #self.CaptureMouse()
        #self.SetFocus()
        return
        #self.SetFocus()
        self.CaptureMouse()
        #self.SetFocus()

    def OnLeaveWindow(self,event):
        #self.ReleaseMouse()
        #self.mdlwin.SetFocus()
        return

        self.ReleaseMouse()
        self.mdlwin.SetFocus()

    def OnChoiceMol(self,event):
        try: name=self.cboxmol.GetStringSelection()
        except: name=''

        self.mdlwin.model.menuctrl.OnShow("Hide hydrogen",self.hideh)

        self.mymgr.ChoiceMol(name,False,True) #True)
        event.Skip()

    def OnChoiceNextMol(self,event):
        if len(self.cboxmol.GetItems()) <= 0: name=''
        else: name=self.cboxmol.GetStringSelection()

        self.mdlwin.model.menuctrl.OnShow("Hide hydrogen",self.hideh)

        self.mymgr.ChoiceNextMol(name,False,True) #True)

    def OnChoicePrevMol(self,event):
        if len(self.cboxmol.GetItems()) <= 0: name=''
        else: name=self.cboxmol.GetStringSelection()

        self.mdlwin.model.menuctrl.OnShow("Hide hydrogen",self.hideh)

        self.mymgr.ChoicePrevMol(name,False,True) #True)

    def HelpDocument(self):
        self.mdlwin.model.helpctrl.Help(self.helpname)

    def Tutorial(self):
        self.mdlwin.model.helpctrl.Trutorial(self.helpname)

    def MenuItems(self):
        """ Menu and menuBar data """
        # Menu items
        menubar=wx.MenuBar()
        # File
        submenu=wx.Menu()
        submenu.Append(-1,"Show BDA points",kind=wx.ITEM_CHECK)
        submenu.Append(-1,"Hide hydrogens",kind=wx.ITEM_CHECK)
        submenu.AppendSeparator()
        #submenu.Append(-1,'Close selected','Close selected molecules')
        menubar.Append(submenu,'Option')
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Tutorial','Tutorial')
        menubar.Append(submenu,'Help')
        #
        return menubar

    def OnMenu(self,event):
        """ Menu event handler """
        menuid=event.GetId()
        item=self.menubar.GetLabel(menuid)
        bChecked=self.menubar.IsChecked(menuid)
        # File menu items
        if item == "Show BDA points":
            self.mdlwin.model.menuctrl.OnFMO("BDA points",bChecked)
        if item == "Hide hydrogens": self.hideh=bChecked
        elif item == 'Close selcted':
            pass
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Tutorial": self.Tutorial()


class ImageViewer_Pan(wx.ScrolledWindow):
    def __init__(self,parent,winpos=(0,20),winsize=(200,400),
                 selmethod=None,popupmenu=None,vscroll=True):
        # note: wx.HSCROLL does not work
        if vscroll: style = wx.VSCROLL
        else:       style = wx.HSCROLL
        winpos  = lib.SetWinPos(winpos)
        wx.ScrolledWindow.__init__(self,parent,-1,pos=winpos,
                                   size=winsize,style=style)
        self.parent   = parent # need to have select method

        self.SetBackgroundColour('white')
        self.selectmethod = selmethod
        self.popupmenu    = popupmenu # [['label',handler],...]

        self.winsize   = winsize
        nrow = self.winsize[1] / 50
        self.SetScrollbars(1,1,0,nrow*self.winsize[1]+10)
        self.ratestepx = 5
        self.ratestepy = 100
        #####self.SetRate(self.ratestepx,self.ratestepy)
        self.SetRate(50,50)

        self.bgcolor   = 'white'
        self.SetBackgroundColour(self.bgcolor)
        self.labelh    = 20
        self.textcolor = 'black'
        self.selcolor  = [0,1,0,1] #'green'

        self.stbmpobjdic = {}

    def SetTextLabelHeight(self,height):
        self.labelh = height

    def SetBGColor(self,color):
        """ bg color of staticbitmap """
        self.bgcolor = color
        self.SetBackgroundColour(self.bgcolor)

    def SetTextColor(self,color):
        self.textcolor = color

    def SetSelectColor(self,color):
        self.selcolor = color

    def SetRate(self,xstep,ystep):
        self.ratestepx = xstep
        self.ratestepy = ystep
        self.SetScrollRate(xstep,ystep)

    def BitmapIcons(self,imglst,labellst,ncol=2):
        """ imgs in imglst are assumed to be PIL image """
        imgsize = imglst[0].size[0]
        imgsz = imgsize #80
        nimg = len(imglst)
        nrow = nimg # a large value
        self.SetScrollbars(1,1,0,nrow*self.winsize[1]+10)
        #
        count = -1
        posy = -imgsize
        posx0 = 10
        for i in range(nrow):
            if count > nimg - 1: break
            posy += imgsize #i * imgsize #self.pansize[1]
            if labellst is not None:
                posy += self.labelh
            for j in range(ncol):
                count += 1
                if count > nimg - 1: break
                img = imglst[count]
                if labellst is not None: name = labellst[count]
                else:                    name = ''
                #if fitsize:
                #    img = lib.ImageThumnail(img,(imgsz,imgsz))
                wximg = lib.PILToWxImage(img)
                if lib.IsWxVersion2():
                    bmp   = wx.BitmapFromImage(wximg)
                else: bmp   = wx.Bitmap(wximg)
                posx = j * imgsize + posx0 #[0] #self.pansize[0]
                bmpposy = posy
                sttext = None
                if labellst is not None:
                    yloc = bmpposy - self.labelh
                    text = str(count+1)+':'+labellst[count]
                    sttext = wx.StaticText(self,-1,'',
                             pos=(posx+5,yloc+4),size=(imgsz,self.labelh)) #imgsize/8,self.labelh-2))
                    sttext.SetLabel(text)
                stbmp = wx.StaticBitmap(self,-1,bitmap=wx.NullBitmap,
                                        pos=(posx,bmpposy),
                                        size=(imgsize,imgsize),
                                        name=str(count),
                                        style=wx.BORDER)
                stbmp.SetBackgroundColour(self.bgcolor)
                stbmp.SetBitmap(bmp)
                stbmp.Bind(wx.EVT_LEFT_DOWN,self.OnSelect)
                if self.popupmenu is not None:
                    stbmp.Bind(wx.EVT_RIGHT_DOWN,self.OnPopupMenu)
                self.stbmpobjdic[count] = [[posx,posy],name,stbmp,sttext]
        self.Refresh()

    def Clear(self):
        self.BitmapIcons(self,[],[])

    def OnPopupMenu(self,event):
        if self.popupmenu is None: return
        print('OnPopupMenu is called')
        obj     = event.GetEventObject()
        objname = obj.GetName()
        iobj = int(objname)
        print(('event obj # = ',iobj))
        print(('event obj name = ',objname))

    def OnSelect(self,event):
        obj     = event.GetEventObject()
        objname = obj.GetName()
        iobj    = int(objname)
        sttext  = self.stbmpobjdic[iobj][3]
        #
        self.selectmethod(iobj,objname)

    def SetLabelColor(self,selectlst):
        nobj = len(self.stbmpobjdic)
        for i in range(nobj):
            sttext = self.stbmpobjdic[i][3]
            if i in selectlst:
                  sttext.SetForegroundColour("green")
            else: sttext.SetForegroundColour("black")
        self.Refresh()

class ImageSheet_Frm(wx.Frame):
    def __init__(self,parent,winpos=[],winsize=[],winlabel=None,
                 vscroll=True):
        self.title = 'Image Sheet'
        self.parent = parent
        if len(winsize) <= 0: self.winsize=(500,300)
        else: self.winsize=winsize
        if len(winpos) <= 0:
            parpos = self.parent.GetPosition()
            self.winpos = [0,20] #self.winpos = [parpos[0]+20,parpos[1]-self.winsize[1]+30]
        else: self.winpos = winpos
        self.winpos  = lib.SetWinPos(self.winpos)
        wx.Frame.__init__(self,parent,-1,self.title,pos=self.winpos,
            size=self.winsize,
            style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)

        self.SetBackgroundColour('light gray')

        self.mdlwin  = self.parent
        self.model   = self.mdlwin.model
        self.winctrl = self.model.winctrl

        if winlabel is None: self.winlabel = 'Open ImageSheet'
        else: self.winlabel = winlabel
        self.vscroll  = vscroll
        # set icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass
        # bitmap icon
        self.getbmp = self.model.setctrl.GetIconBmp('get',imgfrm='.png')
        # Create Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[ImageSheet]')
        try: self.menubar.Check(self.syncid,self.syncmdlwin)
        except: pass

        self.Bind(wx.EVT_MENU,self.OnMenu)
        # Panel layout
        [w,h]=self.GetClientSize()
        # widget height
        self.hcmd    = 35
        self.htext   = 18
        self.hcombo  = 20
        self.hbutton = 25
        # attributes
        self.select_mode = 'single'
        self.checkeddic = {}
        # attributes for view
        #self.nimgcol   = 2
        self.perRow    = 2
        self.imgwidth  = 'auto'
        #
        self.max_nmol   = 200
        self.imgsperRow = 2
        self.imgbgcolor = None
        self.duplicate  = True
        #
        self.imglst     = [] # [[rdmol,name,inpfile],...]
        self.labellst   = []
        self.selectlst  = []
        self.selectmode = 'single' # 'multiple'
        self.ncolumnlst = ['1','2','3','4','5',
                           '6','7','8','9','10']

        self.CreatePanel()
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        #
        self.Show()

    def CreatePanel(self):
        [w,h] = self.GetClientSize()
        hcmd = self.hcmd
        self.cmdpan = wx.Panel(self,-1,pos=(0,0),size=(w,self.hcmd))
        # other widgets
        yloc = 10
        xloc = 10
        #self.selinfotxt = wx.StaticText(self.cmdpan,-1,'Selected: 0 / 0',
        #                         pos=(xloc,yloc),size=(100,self.htext))
        # selection mode
        #xloc += 120
        wx.StaticText(self.cmdpan,-1,'Select:',pos=(xloc,yloc),
                      size=(40,self.htext))
        xloc += 45
        self.singlerbt = wx.RadioButton(self.cmdpan,-1,'single',pos=(xloc,yloc),
                               style=wx.RB_GROUP)
        self.multirbt = wx.RadioButton(self.cmdpan,-1,'multiple',
                                       pos=(xloc+55,yloc))
        if self.select_mode == 'single': self.singlerbt.SetValue(True)
        else: self.multirbt.SetValue(True)
        self.singlerbt.Bind(wx.EVT_RADIOBUTTON,self.OnSingleSelection)
        self.multirbt.Bind(wx.EVT_RADIOBUTTON,self.OnMultipleSelection)

        xloc += 130
        self.htext  = 18
        wx.StaticText(self.cmdpan,-1,'columns:',pos=(xloc,yloc),
                      size=(50,self.htext))
        self.ncolcmb = wx.ComboBox(self.cmdpan,-1,'',choices=self.ncolumnlst, \
              pos=(xloc+55,yloc-3),size=(50,20),
              style=wx.TE_PROCESS_ENTER)
        self.ncolcmb.SetValue(str(self.perRow))
        self.ncolcmb.Bind(wx.EVT_COMBOBOX,self.OnNumberOfColumns)
        self.ncolcmb.Bind(wx.EVT_TEXT_ENTER,self.OnNumberOfColumns)
        #
        self.SetSelectMode(self.selectmode)
        xloc += 120
        self.btnget = wx.BitmapButton(self.cmdpan,-1,bitmap=self.getbmp,
                                     pos=(xloc,yloc-5),size=(25,25))
        #self.btnget.SetBackgroundColour(color)
        self.btnget.Bind(wx.EVT_BUTTON,self.OnGetImage)
        #self.btnget.SetToolTipString('get MDLWIN image and display')
        lib.SetTipString(self.btnget,'get MDLWIN image and display')
        # duplicate
        xloc += 40
        self.ckbdup=wx.CheckBox(self.cmdpan,-1,"Duplicate",pos=(xloc,yloc),
                                size=(80,18))
        self.ckbdup.Bind(wx.EVT_CHECKBOX,self.OnDuplicate)
        self.ckbdup.SetValue(self.duplicate)
        #self.ckbdup.SetToolTipString('allow duplicated molecule')
        lib.SetTipString(self.ckbdup,'allow duplicated molecule')

        hcmd = self.hcmd #35
        self.imgwinpos  = [10,hcmd]
        self.imgwinsize = [w-10,h-hcmd-10]
        self.CreateImagePanel()
        #
        self.Refresh()

    def SetSelectedList(self,selectlst):
        """ return method of Data_Pan.OnSelected  """
        nsel = len(selectlst)
        if nsel <= 0: return
        if self.selectmode == 'multiple':
            for i in selectlst:
                if not i in self.selectlst: self.selectlst.append(i)
                else: self.selectlst.remove(i)
        else:
            i = selectlst[0]
            if i in self.selectlst: self.selectlst.remove(i)
            else:
                self.selectlst = [selectlst[0]]
                if self.syncmdlwin:
                    try: self.model.SwitchMol(isel,True,True,messout=False)
                    except: pass

        self.SetSelectedOnImagePans()

    def ClearAll(self,yes):
        if yes:
            self.imglst = []
            self.labellst = []
        else:
            tmplst = []
            nimg = len(self.imglst)
            for i in range(nimg):
                if not i in self.selectlst: tmplst.append(self.imglst[i])
            self.imglst = tmplst[:]
            self.selectlst = []
        self.OnMove(1)
        self.SetSelectedOnImagePans()

    def SelectAll(self,yes):
        if yes:
            nimg = len(self.imglst)
            self.selectlst = list(range(nimg))
        else: self.selectlst = []
        self.SetSelectedOnImagePans()


    def Select(self,i,name):
        """ return method from subwin.ImageViewer_Pan.OnSelect

        """
        if i in self.selectlst: sel = False
        else:                   sel = True
        if self.selectmode == 'single':
            self.selectlst = []
            if sel:
                self.selectlst.append(i)
        else: # 'multiple'
            if sel: self.selectlst.append(i)
            else:   self.selectlst.remove(i)
        self.SetSelectedOnImagePans()

    def CreateImagePanel(self):
        self.imagepan = ImageViewer_Pan(self,winpos=self.imgwinpos,
                                      winsize=self.imgwinsize,
                                      selmethod=self.Select,
                                      popupmenu=None,
                                      vscroll=self.vscroll)
        #self.imagepan.SetBGColor([255,255,230])
        self.imagepan.SetBGColor([255,255,255])

    def OnSingleSelection(self,event):
        self.select_mode = 'single'
        self.selectmode = 'single'

    def OnMultipleSelection(self,event):
        self.select_mode = 'multiple'
        self.selectmode = 'multiple'

    def OnDuplicate(self,event):
        self.duplicate = self.ckbdup.GetValue()

    def OnIconSize(self,event):
        obj = event.GetEventObject()
        value = obj.GetValue()
        if value == 'auto': width = ComputeIconWidth()
        else:
            try: width = int(obj.GetValue())
            except:
                mess = 'Wrong input'
                wx.MessageBox(mess,View_pan.OnImageSize)
                return
        #
        self.view.iconwidth = width
        self.ChangeIconWidth(width)

    def OnNumberOfColumns(self,event):
        if len(self.imglst) > 0:
            mess = 'Please clear all images("Command"-"Clear all")\n'
            mess += ' before change the number of columns'
            wx.MessageBox(mess,'ImgageSheet_Frm.OnNumberOfColumns')
            return
        self.perRow = int(self.ncolcmb.GetValue()) #GetStringSelection()
        if len(self.imglst) > 0: self.OnMove(1)

    def ChangeBGColorOfImage(self):
        if len(self.selectlst) <= 0:
            mess = 'Please selecte image(s)'
            wx.MessageBox(mess,'ImageSheet.SetImageBGColor')
            return

        bgcolor = lib.ChooseColorOnPalette(self.mdlwin,False,1.0)
        if len(bgcolor) <= 0: return
        self.ChangeColor(rgbto=bgcolor)
        self.imgbgcolor = bgcolor

    def ChangeColor(self,rgbfrom=[0,0,0],rgbto=[1,1,1]):
        if len(self.selectlst) <= 0:
            mess = 'Please selecte image(s)'
            wx.MessageBox(mess,'ImageSheet.SetImageBGColor')
            return
        rf = rgbfrom[0] * 255
        gf = rgbfrom[1] * 255
        bf = rgbfrom[2] * 255
        rt = rgbto[0] * 255
        gt = rgbto[1] * 255
        bt = rgbto[2] * 255
        for i in self.selectlst:
           pilimg = self.imglst[i]
           wximg = lib.PILToWxImage(pilimg)
           wximg.Replace(rf,gf,bf,rt,gt,bt) # <-- not beautiful
           pilimg = lib.WxToPILImage(wximg)
           self.imglst[i] = pilimg
        self.DisplayImage()
        #
    def OpenReorderPanel(self):
        if len(self.imglst) <= 1: return
        #
        winsize = (250,70)
        parpos  = self.GetPosition()
        winpos  = [parpos[0]+20,parpos[1]-winsize[1]+40]
        self.ordpan = wx.Frame(self,-1,pos=winpos,size=winsize,
                               title='ImageSheet: Reorder image',
                               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|\
                               wx.FRAME_FLOAT_ON_PARENT)
        # set icon
        try: lib.AttachIcon(self.ordpan,const.FUMODELICON)
        except: pass
        maximg = len(self.imglst) + 1
        if maximg > 10: maximg = 11
        numlst = list(range(maximg))
        numlst.pop(0)
        numlst = [str(x) for x in numlst]
        yloc = 15
        xloc = 10
        wx.StaticText(self.ordpan,-1,'from:',pos=(xloc,yloc),
                      size=(30,18))
        self.cmbfrm = wx.ComboBox(self.ordpan,-1,'',choices=numlst,
              pos=(xloc+40,yloc-3),size=(40,20),
              style=wx.TE_PROCESS_ENTER)
        xloc += 90
        wx.StaticText(self.ordpan,-1,'to:',pos=(xloc,yloc),
                      size=(20,18))
        self.cmbto = wx.ComboBox(self.ordpan,-1,'',choices=numlst,
              pos=(xloc+30,yloc-3),size=(40,20),
              style=wx.TE_PROCESS_ENTER)
        xloc += 90
        okbt=wx.Button(self.ordpan,-1,"OK",pos=(xloc,yloc-3),size=(30,20))
        okbt.Bind(wx.EVT_BUTTON,self.OnReorderOK)

        self.ordpan.Show()

    def OnReorderOK(self,event):
        frm = int(self.cmbfrm.GetStringSelection()) - 1
        to  = int(self.cmbto.GetStringSelection()) - 1
        self.ReorderImage(frm,to)

    def ReorderImage(self,frm,to):
        if frm == to: return
        imgfrm = self.imglst[frm]
        self.imglst.pop(frm)
        self.imglst.insert(to,imgfrm)
        self.DisplayImage()

    def SetSelectedOnImagePans(self):
        self.imagepan.SetLabelColor(self.selectlst[:])

    def SetSelectMode(self,mode):
        self.selectmode = mode

    def OnGetImage(self,event):
        if self.model.molctrl.GetNumberOfMols() <= 0:
            mess = 'No molecules in MDLWIN'
            wx.MessageBox(mess,'MolIconTable.RestoreMolsInFUModle')
            return

        img,label = self.MakeMDLWINImage()
        if img is None: return

        self.imglst.append(img)
        self.labellst.append(label)

        self.DisplayImage()

    def DisplayImage(self):

        self.imagepan.BitmapIcons(self.imglst,labellst=self.labellst,
                                         ncol=self.perRow)
        self.imagepan.Refresh()

    def CalcSheetWidth(self):
        ncol = int(self.ncolcmb.GetValue())
        [w,h] = self.imagepan.GetClientSize()
        width = int(float(w-25)/float(ncol))
        return width

    def MakeMDLWINImage(self):
        """ not completed 23Sep2017 """

        bgcolor = self.imgbgcolor
        label   = None
        img     = None
        # current molecule in MDLWIN
        molnam = self.model.mol.name
        # check duplication
        if molnam in self.labellst:
            if not self.duplicate:
                mess = 'Duplicate mol images, molname=' + molnam
                wx.MessageBox(mess,'ImageSheet_Frm.MakeMDLWINImage')
                return img,label
            else:  molnam = lib.CheckSameNameAndChangeIt(molnam,self.labellst)        # compute image width, size=[width,width]
        ncol = int(self.ncolcmb.GetValue())
        #width = 'auto'
        #if width == 'auto': sizex = CalcImageWidth(ncol)
        #else:               sizex = int(width)
        #sizex = CalcImageWidth(ncol)
        #
        savebgcolor = self.model.mdlwin.draw.bgcolor
        if bgcolor is not None:
            self.model.ChangeBackgroundColor(bgcolor)

        [w,h] = self.model.mdlwin.GetSize()

        width = self.CalcSheetWidth() #(ncol)
        wximg = self.model.mdlwin.draw.GetGLCanvasImage()
        ###wximg.Replace(0,0,0,255,255,255) # <-- not beatiful
        # need two times Mirror operation: up-side-down, left-side-right
        #wximg = wximg.Mirror(True)
        #wximg = wximg.Mirror(True)  # neeed two times !!
        [wimg,himg] = wximg.GetSize()
        sc = float(width) / float(w)
        wid = int(sc * wimg)
        hei = int(sc * himg)
        self.imgwidth  = wid
        self.imgheight = hei

        wximg.Rescale(wid, hei)

        pilimg = lib.WxToPILImage(wximg)

        img = copy.deepcopy(pilimg)

        label = molnam

        if bgcolor is not None:
            self.model.ChangeBackgroundColor(savebgcolor)

        return img,label

    def ConsoleMessage(self,mess,level=-1):
        if self.parent is None: print(mess)
        else: self.model.ConsoleMessage(mess)

    def OnClose(self,event):
        try:  self.winctrl.Close(self.winlabel)
        except: self.Destroy()
        self.Destroy()

    def OnResize(self,event):
        self.OnMove(1)

    def OnMove(self,event):
        try:
            self.cmdpan.Destroy()
            self.imagepan.Destroy()
            #
            self.CreatePanel()
            self.DisplayImage()
            self.SetSelectedOnImagePans()
        except: pass
        #
        self.Refresh()

    def ReadImageFile(self,filename):
        pass

    def SaveImagesToFile(self,single=True,perRow=None,addname=True):
        """ Save PIL image on file. the save format is determined by the file
         extension. the supported formats are 'bmp','png','gif','jpeg', and
         tiff'
        """

        if single:
            filename = lib.GetFileName(rw='w')
            if len(filename) <= 0: return
            #
            formlst = ['bmp','png','gif','jpeg','tiff']
            base,ext = os.path.splitext(filename)
            form = ext[1:]
            if not form in formlst:
                mess = 'Unknown image format : ' + form
                wx.MessageBox(mess,'ImageSheet_Frm.SaveImageToFile')
                return
        else:
            dirname = lib.GetDirectoryName()
            if len(dirname) <= 0: return
            if not os.path.isdir(dirname):
                mess = 'Directry ' + dirname + 'does not exsist.'
                mess += ' Whould you like to create it?'
                ans = lib.MessageBoxYesNo(mess,'ImageSheet.SaveImagesToFile')
                if not ans: return
                else: os.mkdir(dirnam)
            form = 'png'
        #
        filelst = []
        if not single:
            nimg = len(self.imglst)
            for i in range(nimg):
                molnamform = self.labellst[i] + '.' + form
                molnamform = lib.SuppressBlanks(molnamform)
                file = os.path.join(dirname,molnamform)
                self.imglst[i].save(file,format=form)
                filelst.append(file)
            if len(filelst) > 0:
                mess = 'images were saved to files: '
                mess += str(filelst)
                self.ConsoleMessage(mess)

        else:
            params = {}
            params['wimg']    = self.imgwidth #200
            params['himg']    = self.imgheight #200
            params['perRow'] = self.perRow #2
            params['margin'] = 50 # margin#50

            mess = rwfile.WriteImagesOnFile(filename,self.imglst,params)
            self.ConsoleMessage(mess)


    def CopyImageToClipboard(self):
        """ CopyImageToClipboard """
        if len(self.imglst) == 1: imgidx = 0
        else:
            if len(self.selectlst) <= 0:
                mess = 'Please select a image'
                wx.MessageBox(mess,'ImageSheet.CopyImageToClipBoard')
                return
            imgidx = self.selectlst[0]
        pilimg = self.imglst[imgidx]
        wximg = lib.PILToWxImage(pilimg)
        bmp = wximg.ConvertToBitmap()
        lib.CopyBitmapToClipboard(bmp)

    def PasteImageFromClipboard(self):
        """ PasteImageFromClipboard """
        bmp = lib.PasteBitmapFromClipboard()
        [wimg,himg] = bmp.GetSize()
        if wimg == 0 and himg == 0:
            mess = 'Clipboard is empty'
            wx.MessageBox(mess,'ImageSheet.PasteImageFromClipboard')
            return

        wximg = bmp.ConvertToImage()
        # calc size
        """
        width = self.CalcSheetWidth()
        sc = float(width) / float(wimg)
        wid = int(sc * wimg)
        hei = int(sc * himg)
        """
        wximg.Rescale(self.imgwidth,self.imgheight) #wid, hei)
        pilimg = lib.WxToPILImage(wximg)
        self.imglst.append(pilimg)
        name = 'pasted'
        if len(self.labellst) >= 0:
            count = 0
            for i in range(len(self.labellst)):
                existname = self.labellst[i]
                if existname.find(name) >= 0: count += 1
            if count > 0: name += '(' + str(count) +')'
        self.labellst.append(name)

        self.DisplayImage()

    def HelpDocument(self):
        """
        #helpname = 'MolIconTable'
        helpname = 'users-guide//html//2-6-ImageSheet.html'
        self.model.helpctrl.Help(helpname)
        """

        fudir = self.model.setctrl.GetFUDir()
        fudir += '//FUdocs//'
        helpdata = fudir + 'users-guide//html//2-6-ImageSheet.html'
        HelpMessage(helpdata,datatype='file',viewer='Html',parent=self)

    def HelpWarning(self):
        text  = 'Warning:\n'
        text += '  1. When you change number of columns,\n'
        text += '    Clear all images before it.\n'
        text += '    Otherwise a fatal error will occur.\n'
        text += '  2. Background color of a image can be changed \n'
        text += '    from black to white by "Command"-"Image bg B to W".\n'
        text += '    Better qualty is obtained by changing the background\n'
        text += '    color of MDLWIN before import the image.\n'
        HelpMessage(text,datatype='text',viewer='Text',parent=self,
                           winsize=(450,200))

    def Tutorial(self):
        helpname = 'MolIconTable'
        helpname = 'users-guide//html//2-4-MolIconTable.html'
        self.model.helpctrl.Tutorial(helpname)

    def OnMenu(self,event):
        # Menu event handler
        menuid   = event.GetId()
        menuitem = self.menubar.FindItemById(menuid)
        item     = menuitem.GetItemLabel()
        #
        wildcardimg = 'png(*.png)|*.png|bmp(*.bmp)|*.bmp|All(*.*)|*.*'
        wildcardsav = 'sdf(*.sdf)|*.sdf|All(*.*)|*.*'
        # File
        if item == "Read image file":
            wildcard = wildcardimg
            filename=lib.GetFileName(self,wildcard,"r",True,"")
            if len(filename) > 0: self.ReadImageFile(filename)

        elif item == "Get MDLWIN image": self.OnGetImage(1)
        # Save image
        elif item == "to a single file": self.SaveImagesToFile(single=True)

        elif item == "to separate files": self.SaveImagesToFile(single=False)

        elif item == "Redraw": self.OnResize(1)
        # quit
        elif item == "Quit": self.OnClose(1)
        # Edit
        elif item == "Copy selected images": self.CopyImageToClipboard()
        elif item == "Paste image": self.PasteImageFromClipboard()
        # Commands
        elif item == "Clear all": self.ClearAll(True)
        elif item == "Clear selected": self.ClearAll(False)

        elif item == "Select all": self.SelectAll(True)
        elif item == "Deselect all": self.SelectAll(False)

        elif item == "Image bg B to W":
            self.ChangeColor()
            #self.ChangeBGColorOfImage()
        elif item == "Reorder Image": self.OpenReorderPanel()
        # Params
        elif item == "Set params": self.OpenParamWin()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Warning": self.HelpWarning()

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        #submenu.Append(-1,"Read image file","Open file")
        submenu.Append(-1,"Get MDLWIN image","Make MDLWIN image")
        submenu.AppendSeparator()
        # save image
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"to a single file","single file")
        subsubmenu.Append(-1,"to separate files","All molecules")
        #submenu.AppendMenu(-1,"Save selected images",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Save selected images",subsubmenu)
        #
        submenu.AppendSeparator()
        submenu.Append(-1,"Redraw", "Redraw")

        submenu.AppendSeparator()
        submenu.Append(-1,"Quit", "Quit")
        menubar.Append(submenu,"File")
        # Edit
        submenu=wx.Menu()
        submenu.Append(-1,"Copy selected images","")
        submenu.Append(-1,"Paste image","")
        menubar.Append(submenu,"Edit")
        # Commands
        submenu=wx.Menu()
        submenu.Append(-1,"Clear selected","Clear selected")
        submenu.Append(-1,"Clear all","Clear all")
        submenu.AppendSeparator()
        submenu.Append(-1,"Select all","Select all")
        submenu.Append(-1,"Deselect all","Deselect all")
        submenu.AppendSeparator()
        submenu.Append(-1,"Image bg B to W","set bg color")
        submenu.AppendSeparator()
        submenu.Append(-1,"Reorder Image","reorder image")

        menubar.Append(submenu,"Command")
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Warning','Help Warning')
        menubar.Append(submenu,'Help')

        return menubar


class MolIconData_Pan(wx.Panel):
    """ Used in MolIconTable_Frm """
    def __init__(self,parent,ctrler,panpos,pansize):
        panpos  = lib.SetWinPos(panpos)
        wx.Panel.__init__(self,parent,-1,pos=panpos,size=pansize)
        self.SetBackgroundColour('light gray')
        #
        self.ctrler       = ctrler # Data instance
        self.selectmethod = self.ctrler.SetSelectedList
        # widget height
        self.htext   = 18
        self.hcombo  = 20
        self.hbutton = 20
        #
        self.listobj = None # list data object
        #
        self.CreateWidgets()

    def CreateWidgets(self):
        [w,h] = self.GetClientSize()
        yloc = 0
        xloc = 10
        wlst = w - 12
        hlst = h -yloc

        winpos = (10,0)
        winsize = (w-12,h)
        self.listobj=wx.ListCtrl(self,-1,pos=winpos,size=winsize,
                                 style=wx.LC_REPORT)
        self.listobj.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnSelected)
        #self.listobj.SetToolTipString('Select item(s)')
        lib.SetTipString(self.listobj,'Select item(s)')
        # table items
        self.listobj.InsertColumn(0,'data#',width=30,
                                  format=wx.LIST_FORMAT_RIGHT)
        self.listobj.InsertColumn(1,'sel',width=20)
        self.listobj.InsertColumn(2,'name',width=100)
        self.listobj.InsertColumn(3,'file',width=200)

    def CountSelected(self):
        nsel = len(self.GetSelectedItems())
        ndat = self.listobj.GetItemCount()
        for i in range(ndat):
            if self.listobj.IsChecked(i): nsel += 1
        return nsel,ndat

    def DeleteAll(self):
        self.listobj.DeleteAllItems()

    def SetItemValue(self,vallst):
        """
        vallst [['s',name,filename],...]
        """
        ndat = len(vallst)

        for i in range(ndat):
            [sel,name,file] = vallst[i]
            idx = self.listobj.InsertStringItem(i,str(i+1))
            self.listobj.SetStringItem(idx,1,sel)
            self.listobj.SetStringItem(idx,2,name)
            self.listobj.SetStringItem(idx,3,file)

        self.listobj.Refresh()

    def GetSelectedItems(self):
      """ Get selected items in listobj

      :return: selectlst(lst) - list of selected item numbers
      """
      selectlst = []
      item = self.listobj.GetFirstSelected()
      if item < 0: return selectlst
      selectlst.append(item)
      while len(selectlst) != self.listobj.GetSelectedItemCount():
        item = self.listobj.GetNextSelected(item)
        if not item in selectlst: selectlst.append(item)
      return selectlst

    def OnSelected(self,event):
        item = self.listobj.GetFirstSelected()
        if item < 0: return
        selectlst = self.GetSelectedItems()
        self.selectmethod(selectlst)

    def SetSelectFlag(self,selectlst):
        nitm = self.listobj.GetItemCount()
        for i in range(nitm):
            if i in selectlst: sel = 's'
            else:              sel = ' '
            self.listobj.SetStringItem(i,1,sel)

class MolIconParams_Frm(wx.Frame):
    """ Used in MolIconTable_Frm """
    def __init__(self,parent,id,winpos=[],winsize=[],winlabel='MolIconTable'):
        self.title = 'MolIconParams'
        self.parent = parent
        [x,y] = parent.GetPosition()
        if len(winpos) <= 0:  winpos  = [x+50,y+50]
        winpos  = lib.SetWinPos(winpos)
        if len(winsize) <= 0: winsize = (170,200)
        wx.Frame.__init__(self,parent,id,self.title,pos=winpos,
            size=winsize,style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)

        self.SetBackgroundColour('light gray')

        self.winlabel = winlabel
        #
        self.max_nmol   = self.parent.max_nmol
        self.molsperRow = self.parent.molsperRow
        #self.max_heavy_atoms = 100
        self.sanitize   = self.parent.sanitize
        self.removeHs   = self.parent.removeHs
        self.kekulize   = self.parent.kekulize
        self.draw3d     = self.parent.draw3d
        #
        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.Show()

    def CreatePanel(self):
        [w,h] = self.GetClientSize()
        self.panel = wx.Panel(self,-1,pos=(0,0),size=(w,h))
        self.SetBackgroundColour('light gray')
        yloc = 10
        xloc = 20
        ckbsan = wx.CheckBox(self.panel,-1,"sanitize",pos=(xloc,yloc),
                                size=(100,18))
        ckbsan.SetValue(self.sanitize)
        ckbsan.Bind(wx.EVT_CHECKBOX,self.OnInput)
        yloc += 25
        ckbrmv = wx.CheckBox(self.panel,-1,"removeHs",pos=(xloc,yloc),
                                size=(100,18))
        ckbrmv.SetValue(self.removeHs)
        ckbrmv.Bind(wx.EVT_CHECKBOX,self.OnInput)
        yloc += 25
        ckbkek = wx.CheckBox(self.panel,-1,"kekulize",pos=(xloc,yloc),
                                size=(100,18))
        ckbkek.SetValue(self.kekulize)
        ckbkek.Bind(wx.EVT_CHECKBOX,self.OnInput)
        yloc += 25
        ckb3d = wx.CheckBox(self.panel,-1,"draw3d",pos=(xloc,yloc),
                                size=(100,18))
        ckb3d.SetValue(self.draw3d)
        ckb3d.Bind(wx.EVT_CHECKBOX,self.OnInput)
        yloc += 25
        wx.StaticText(self,-1,'max. nmols:',pos=(xloc,yloc),
                      size=(80,18))
        tclmxmol = wx.TextCtrl(self.panel,-1,"",pos=(100,yloc),size=(40,20),
                                style=wx.TE_PROCESS_ENTER)
        tclmxmol.SetValue(str(self.max_nmol))
        tclmxmol.Bind(wx.EVT_TEXT_ENTER,self.OnMaxMols)
        yloc += 30
        canbt=wx.Button(self.panel,-1,"Cancel",pos=(20,yloc),size=(50,20))
        canbt.Bind(wx.EVT_BUTTON,self.OnCancel)
        aplbt=wx.Button(self.panel,-1,"Apply",pos=(90,yloc),size=(50,20))
        aplbt.Bind(wx.EVT_BUTTON,self.OnApply)

    def OnMolsPerRow(self,event):
        obj = event.GetEventObject()
        value = int(obj.GetValue())
        self.molsperRow = value

    def OnMaxMols(self,event):
        obj = evetn.GetEventObject()
        maxnmol = int(obj.GetValue())
        self.max_nmol = maxnmol

    def OnInput(self,event):
        obj = event.GetEventObject()
        label = obj.GetLabel()
        value = obj.GetValue()
        if   label == 'sanitize': self.sanitize = value
        elif label == 'removeHs': self.removeHs = value
        elif label == 'kekulize': self.kekulize = value
        elif label == 'draw3d':   self.draw3d   = value

    def SetParams(self):
        self.parent.sanitize   = self.sanitize
        self.parent.removeHs   = self.removeHs
        self.parent.kekulize   = self.kekulize
        self.parent.draw3d     = self.draw3d
        self.parent.max_nmol   = self.max_nmol
        self.parent.molsperRow = self.molsperRow

        self.parent.PrintParams()

    def OnApply(self,event):
        self.SetParams()
        self.OnClose(1)

    def OnClose(self,event):
        try:  self.winctrl.Close(self.winlabel)
        except: self.Destroy()

    def OnCancel(self,event):
        self.OnClose(1)

class MolIconTable_Frm(wx.Frame):
    """ Needs MolIconData_Pan and MolIconParams_Frm classes """
    def __init__(self,parent,winpos=[],winsize=[],winlabel=None,
                 drug_drop=True,datawin=True,vscroll=True):
        self.title = 'MolIconTable'
        self.parent = parent
        if len(winsize) <= 0: self.winsize=lib.WinSize([500,300])
        else: self.winsize=winsize
        if len(winpos) <= 0:
            parpos = self.parent.GetPosition()
            self.winpos = [0,20] #[parpos[0],parpos[1]-self.winsize[1]+10]
        else: self.winpos = winpos
        self.winpos  = lib.SetWinPos(self.winpos)
        wx.Frame.__init__(self,parent,-1,self.title,pos=self.winpos,
            size=self.winsize,
            style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER)

        self.SetBackgroundColour('light gray')

        if not rdkit_ready:
            mess = 'Failed to import RDKit. Unable to continue.'
            wx.MessageBox(mess,'MolIconTable_Frm.__init__')
            self.Onclose(1)

        if winlabel is None: self.winlabel = 'Open MolIconTable'
        else: self.winlabel = winlabel

        self.datawin  = datawin
        self.vscroll  = vscroll
        #self.helpname = ???
        if parent is not None:
            self.mdlwin  = self.parent
            self.model   = self.mdlwin.model
            self.winctrl = self.model.winctrl
        # set icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass

        self.syncmdlwin = True
        # Create Menu
        self.menubar=self.MenuItems()
        self.SetMenuBar(self.menubar)
        lib.InsertTitleMenu(self.menubar,'[MolIcon]')
        try: self.menubar.Check(self.syncid,self.syncmdlwin)
        except: pass

        self.Bind(wx.EVT_MENU,self.OnMenu)
        # drag-and-drop operation
        if drug_drop:
            self.OpenDropFiles = self.OpenDropFiles #dropfilemethod
            droptarget = lib.DropFileTarget(self) #.scrollwin)
            self.SetDropTarget(droptarget)
        # Panel layout
        [w,h]=self.GetClientSize()
        self.spliterwin_pos  = None
        self.spliterwin_size = None
        self.sashposition    = 140
        self.minsashpos      = 140
        self.hcmd            = 35
        # widget height
        self.htext   = 18
        self.hcombo  = 20
        self.hbutton = 25
        # attributes
        self.select_mode = 'single'
        self.checkeddic = {}
        # attributes for view
        self.niconcol   = 5
        self.iconwidth  = 'auto'
        #
        self.max_nmol   = 200
        self.max_heavy_atoms = 100
        self.molsperRow = 4
        self.sanitize   = False
        self.removeHs   = True # False
        self.kekulize   = True
        self.autoload   = False # load mol object from fu
        #self.draw2d     = True
        self.draw3d     = False
        #
        self.mollst     = [] # [[rdmol,name,inpfile],...]
        self.sdftextlst = None
        self.selectlst  = []
        self.selectmode = 'single' # 'multiple'
        self.ncolumnlst = ['1','2','3','4','5',
                           '6','7','8','9','10']

        self.CreatePanel()

        if self.autoload: self.RestoreMolsInMDLWIN()
        #
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_SIZE,self.OnResize)
        #
        self.Show()

    def CreatePanel(self):
        [w,h] = self.GetClientSize()
        hcmd = self.hcmd
        self.cmdpan = wx.Panel(self,-1,pos=(0,0),size=(w,self.hcmd))
        # Reset button
        if self.parent is not None:
            Reset_Button(self.cmdpan,-1,retmethod=self.OnRestoreMols,
                                winpos=(w-20,0))
        # other widgets
        yloc = 10
        xloc = 10
        self.selinfotxt = wx.StaticText(self.cmdpan,-1,'Selected: 0 / 0',
                                 pos=(xloc,yloc),size=(100,self.htext))
        # selection mode
        xloc += 120
        wx.StaticText(self.cmdpan,-1,'Select:',pos=(xloc,yloc),
                      size=(40,self.htext))
        xloc += 45
        self.singlerbt = wx.RadioButton(self.cmdpan,-1,'single',pos=(xloc,yloc),
                               style=wx.RB_GROUP)
        self.multirbt = wx.RadioButton(self.cmdpan,-1,'multiple',
                                       pos=(xloc+60,yloc))
        if self.select_mode == 'single': self.singlerbt.SetValue(True)
        else: self.multirbt.SetValue(True)
        self.singlerbt.Bind(wx.EVT_RADIOBUTTON,self.OnSingleSelection)
        self.multirbt.Bind(wx.EVT_RADIOBUTTON,self.OnMultipleSelection)

        xloc += 145
        self.htext  = 18
        wx.StaticText(self.cmdpan,-1,'columns:',pos=(xloc,yloc),
                      size=(50,self.htext))
        self.ncolcmb = wx.ComboBox(self.cmdpan,-1,'',choices=self.ncolumnlst, \
              pos=(xloc+55,yloc-2),size=(50,25),
              style=wx.TE_PROCESS_ENTER)
        self.ncolcmb.SetValue(str(self.niconcol))
        self.ncolcmb.Bind(wx.EVT_COMBOBOX,self.OnNumberOfColumns)
        self.ncolcmb.Bind(wx.EVT_TEXT_ENTER,self.OnNumberOfColumns)
        #
        self.SetSelectMode(self.selectmode)

        hcmd = self.hcmd #35

        if self.datawin:
            self.spliterwin_pos  = [0,hcmd]
            self.spliterwin_size = [w,h-hcmd-10]
            self.CreateSpliterPanel()
        else:
            self.imgwinpos  = [10,hcmd]
            self.imgwinsize = [w-10,h-hcmd-10]
            self.CreateImagePanel()
        #
        self.Refresh()

    def CreateSpliterPanel(self):
        # create spliterwindow
        [w,h]   = self.GetClientSize()
        panpos  = [0,self.hcmd]
        pansize = [w,h-self.hcmd-10]
        self.splwin = wx.SplitterWindow(self,-1,pos=panpos,size=pansize,
                                      style=wx.SP_3D)
        # panel on left window
        [w,h] = self.splwin.GetSize()
        xsize = self.sashposition
        ysize = h
        dpos = (10,0)
        dsize = (xsize,ysize)
        # panel on right window
        xpos = self.sashposition + 2
        ypos = 0
        xsize = w - xpos - 5
        ysize = h
        vpos  = (xpos,0)
        vsize = (xsize,h)
        self.datapan = MolIconData_Pan(self.splwin,self,panpos=dpos,
                                           pansize=dsize)
        #self.viewpan = View_Pan(self.splwin,self,panpos=vpos,pansize=vsize)
        self.imagepan = ImageViewer_Pan(self.splwin,winpos=vpos,winsize=vsize,
                                     selmethod=self.Select,
                                     popupmenu=self.PopupMenu,
                                     vscroll=self.vscroll)
        #
        self.splwin.SplitVertically(self.datapan,self.imagepan,
                                    sashPosition=self.sashposition) #w-150)
        self.splwin.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED,
                         self.OnSplitWinChanged)

        self.UpdateDataList()

    def CreateImagePanel(self):
        self.imagepan = ImageViewer_Pan(self,winpos=self.imgwinpos,
                                      winsize=self.imgwinsize,
                                      selmethod=self.Select,
                                      popupmenu=self.PopupMenu,
                                      vscroll=self.vscroll)
        self.imagepan.SetBGColor([240,255,255])

    def CreateDataPanel(self,parpan,panpos,pansize):
        ypan = 0
        panpos = [0,0]
        pansize = parpan.GetClientSize()
        pansize[0] -= 10
        pansize[1] -= 10
        datapan = MolIconData_Pan(parpan,self,panpos=panpos,
                           pansize=pansize,retmethod=self.SetSelectedList)

        self.SetSelectMode(self.selectmode)

        self.UpdateDataList()

        return datapan

    def OnRestoreMols(self,event):
        self.RestoreMolsInMDLWIN()

    def OnSingleSelection(self,event):
        self.select_mode = 'single'
        self.selectmode = 'single'

    def OnMultipleSelection(self,event):
        self.select_mode = 'multiple'
        self.selectmode = 'multiple'

    def SelectedInfo(self):
        ndat = len(self.mollst)
        nsel = len(self.selectlst)
        label = 'Selected: ' + str(nsel) + ' / ' + str(ndat)
        self.selinfotxt.SetLabel(label)

    def OnIconSize(self,event):
        obj = event.GetEventObject()
        value = obj.GetValue()
        if value == 'auto': width = ComputeIconWidth()
        else:
            try: width = int(obj.GetValue())
            except:
                mess = 'Wrong input'
                wx.MessageBox(mess,View_pan.OnImageSize)
                return
        #
        self.view.iconwidth = width
        self.ChangeIconWidth(width)

    def OnNumberOfColumns(self,event):
        if len(self.mollst) > 0:
            mess = 'Please clear all images("Command"-"Clear"-"Clear all")\n'
            mess += ' before change the number of columns'
            wx.MessageBox(mess,'ImgageSheet_Frm.OnNumberOfColumns')
            return

        self.niconcol = int(self.ncolcmb.GetValue()) #GetStringSelection()
        if len(self.mollst) > 0: self.OnMove(1)

    def PopupMenu(self):
        pass

    def OnPopupMenu(self,event):
        print('OnPopupMenu is called')

    def SetDraw3D(self,on):
        self.draw3d = on

    def DisplayIconTable(self):
        if len(self.mollst) <= 0: return
        #
        if not self.draw3d:
            imglst,labellst = self.MakeImageList(self.mollst,
                                                 kekulize=self.kekulize,
                                                 removeHs=self.removeHs)
        else:
            imglst,labellst = self.Make3DImageList(self.mollst)

        self.imagepan.BitmapIcons(imglst,labellst=labellst,
                                         ncol=self.niconcol)
        self.imagepan.Refresh()

    def UpdateDataList(self):
        lstmol = []
        self.namlst = []
        nmol = len(self.mollst)
        if nmol <= 0: return
        #
        self.datapan.DeleteAll()
        vallst = []
        nmol = len(self.mollst)
        for i in range(nmol):
            [molobj,name,inpfile] = self.mollst[i]
            sel = ' '
            if i in self.selectlst: sel = 's'
            vallst.append([sel,name,inpfile])

        self.datapan.SetItemValue(vallst)

    def OpenDropFiles(self,filenames):
        """ Event handler for drag-and-drop files
            The number of files is limitted to one in this application
        """
        if len(filenames) <= 0: return
        if len(filenames[0]) <= 0: return
        self.ReadFile(filenames[0])
        #
        #nfil = len(filenames)
        #for file in filenames: self.ReadFile(file)

    def RestoreMolsInMDLWIN(self):
        mollst = self.GetMolsFromFUModel()
        if len(mollst) <= 0:
            mess = 'No molecules in MDLWIN'
            wx.MessageBox(mess,'MolIconTable.RestoreMolsInFUModle')
            return

        self.mollst = mollst[:]
        self.DisplayIconTable()

        if self.datawin: self.UpdateDataList()

    def GetMolsFromFUModel(self):
        mollst = []
        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return mollst
        mess = 'MolIconTable '
        mess += 'imported molecules from FU. nmol = ' + str(nmol)
        self.ConsoleMessage(mess)
        nget = nmol
        if nmol > self.max_nmol:
            nget = self.max_nmol
            mess = 'Number of molecules ' + str(nmol)
            mess += ' exceeds max_nmol ' + str(self.max_nmol)
            self.ConsoleMessage(mess)
        #
        failedlst = []
        self.sdftextlst = []
        for i in range(nget):
            fumol     = self.model.molctrl.GetMol(i)
            name      = fumol.name
            inpfile   = fumol.inpfile
            sdfstring = fumol.WriteSDFMol(None)
            self.sdftextlst.append(sdfstring)
            rdmol = self.RDMolFromSDFString(sdfstring)
            if self.removeHs:
                try: rdmol = Chem.RemoveHs(rdmol)
                except: pass
            if rdmol is None:
                failedlst.append([i,name])
                continue
            try: rdmol.SetProp("_Name",name)
            except: rdmol.SetProp("_Name",'nomame-'+str(i))
            mollst.append([rdmol,name,inpfile])

        if len(failedlst) > 0:
            mess = 'Failed to convert FUMol to RDmol object: \n'
            mess += '    ' + str(failedlst)
            self.ConsoleMessage(mess)
            wx.MessageBox(mess,'mol-icontable.GetMolsFromFUModel')
        return mollst

    def RDMolFromSDFString(self,sdfstring):
        """
        MolFromMolBlock( (AtomPairsParameters)molBlock [, (bool)sanitize=True
        [, (bool)removeHs=True [, (bool)strictParsing=True]]]) -> Mol :
        :return obj rdmol: rdmol(obj) - RDKit Molecule object
        """
        rdmol = Chem.MolFromMolBlock(sdfstring,sanitize=self.sanitize,
                                     removeHs=self.removeHs)
        return rdmol

    def SetSelectedList(self,selectlst):
        """ return method of MolIconData_Pan.OnSelected  """
        nsel = len(selectlst)
        if nsel <= 0: return
        if self.selectmode == 'multiple':
            for i in selectlst:
                if not i in self.selectlst: self.selectlst.append(i)
                else: self.selectlst.remove(i)
        else:
            i = selectlst[0]
            if i in self.selectlst: self.selectlst.remove(i)
            else:
                self.selectlst = [selectlst[0]]
                if self.syncmdlwin:
                    try: self.model.SwitchMol(isel,True,True,messout=False)
                    except: pass

        self.SetSelectedOnDataAndImagePans()

    def Select(self,i,name):
        """ return method from subwin.ImageViewer_Pan.OnSelect

        """
        if i in self.selectlst: sel = False
        else:                   sel = True
        if self.selectmode == 'single':
            self.selectlst = []
            if sel:
                self.selectlst.append(i)
                if self.syncmdlwin:
                    try: self.model.SwitchMol(i,True,True,messout=False)
                    except: pass
        else: # 'multiple'
            if sel: self.selectlst.append(i)
            else:   self.selectlst.remove(i)
        self.SetSelectedOnDataAndImagePans()

    def SetSelectedOnDataAndImagePans(self):
        self.imagepan.SetLabelColor(self.selectlst[:])
        if self.datawin: self.datapan.SetSelectFlag(self.selectlst)
        self.SelectedInfo()

    def SetSelectMode(self,mode):
        self.selectmode = mode

    def SetSyncMDLWIN(self,on):
        self.syncmdlwin = on
        mess = 'Synchronize with MDLWIN was turned ' + on
        wx.MessageBox(mess,'MolIconTable_win.SetSyncMDLWIN')

    def Test_MakeMolList(self):
        """ not used in normal run """
        dirnam = 'e://ATEST//mol_table'
        namlst = ['mol-1','mol-2','mol-3','mol-4']
        molsmi = ['c1nccc2n1ccc2','C1=CC=CN=C1','c1cc1','OC1C2C1CC2']
        inisdf = "e://ATEST//mono_results//opv_mols_4.sdf"
        sdflst = [dirnam+'//'+nam+'.sdf' for nam in namlst]

        molpul = Chem.SDMolSupplier(inisdf)

        for mol in molpul:
            print(('natm',mol.GetNumAtoms()))
            print((mol.GetProp('_Name')))
            #self.mollst.append(mol)
        lst = [mol for mol in molpul]
        mollst = []
        nmol = len(lst)
        for i in range(nmol):
            name = lst[i].GetProp('_Name')
            mollst.append([lst[i],name,'smiles'])
        print(('nmol',len(mollst)))
        return mollst

    def MakeImageList(self,mollst,kekulize=True,removeHs=False):
        def CalcImageWidth(ncol):
            [w,h] = self.imagepan.GetClientSize()
            width = int(float(w-25)/float(ncol))
            return width
        labellst = []
        imglst   = []
        nmol     = len(mollst)
        # compute image width, size=[width,width]
        ncol = int(self.ncolcmb.GetValue())
        width = 'auto'
        if width == 'auto': sizex = CalcImageWidth(ncol)
        else:               sizex = int(width)
        #
        for i in range(nmol):
            mol = mollst[i][0]
            if mol is None:
                print('mol is None')
                continue
            #try: legend = mol.GetProp("_Name")
            #except: legend = 'noname'+'-'+str(i)
            legend = mollst[i][1]
            labellst.append(legend)
            # Draw: RDKit module
            try:
                img = Draw.MolToImage(mol,(sizex,sizex),kekulize=kekulize)
                imglst.append(img)
            except:
                mess = legend + ': Failed to create 2D image by '
                mess += 'RDKit.Draw.MolToImage. skipped'
                self.ConsoleMessage(mess)
                wx.MessageBox(mess,'mol-icontable.MakeImageList')

        return imglst,labellst

    def Make3DImageList(self,mollst):
        """ not completed 23Sep2017 """
        def CalcImageWidth(ncol):
            [w,h] = self.imagepan.GetClientSize()
            width = int(float(w-25)/float(ncol))
            return width

        labellst = []
        imglst   = []
        nmol     = len(mollst)
        # compute image width, size=[width,width]
        ncol = int(self.ncolcmb.GetValue())
        width = 'auto'
        if width == 'auto': sizex = CalcImageWidth(ncol)
        else:               sizex = int(width)
        #
        savecurmol = self.model.curmol
        savebgcolor = self.model.mdlwin.draw.bgcolor

        #self.model.ChangeBackgroundColor([1,1,1,1])
        [w,h] = self.model.mdlwin.GetSize()

        width = CalcImageWidth(ncol)
        for i in range(nmol):
            molnam = mollst[i][1]
            print(('i,molnam',i,molnam))
            #img = Draw.MolToImage(mol,(sizex,sizex),kekulize=kekulize)
            """self.model.SwitchMol(curmol"""
            curmol = self.model.molctrl.GetMolIndex(molnam)

            print(('i,curmol',i,curmol))

            self.model.SwitchMol(curmol,False,True,notify=False)
            #mol=self.model.molctrl.GetMol(curmol)

            ###self.model.DrawMol(False)
            ###bigimg = wx.EmptyImage(w,h)
            ###bigimg.SetRGBRect((0,0,w,h),255,255,255)

            wximg = self.model.mdlwin.draw.GetGLCanvasImage()
            # need two times Mirror operation: up-side-down, left-side-right
            wximg = wximg.Mirror(True)
            wximg = wximg.Mirror(True)  # neeed two times !!
            [wimg,himg] = wximg.GetSize()
            sc = float(width) / float(w)
            wid = int(sc * wimg)
            hei = int(sc * himg)
            wximg.Rescale(wid, hei)
            ###bigimg.Paste(wximg,0,0)
            pilimg = lib.WxToPILImage(wximg)

            imglst.append(copy.deepcopy(pilimg))

            labellst.append(molnam)

        #self.model.ChangeBackgroundColor(savebgcolor)
        self.model.SwitchMol(savecurmol,False,True,notify=False)
        return imglst,labellst


    def MessageBoxOK(self,mess,title='',parent=None):
        wx.MessageBox(mess, title, wx.OK | wx.ICON_INFORMATION)

    def OnClose(self,event):
        #winlabel = 'Open MolIconTable'
        try:  self.winctrl.Close(self.winlabel)
        except: self.Destroy()
        self.Destroy()

    def OnResize(self,event):
        self.OnMove(1)
        event.Skip()

    def OnMove(self,event):
        try:
            self.cmdpan.Destroy()
            if self.datawin: self.splwin.Destroy()
            else: self.imagepan.Destroy()
            #
            self.CreatePanel()
            if self.datawin: self.UpdateDataList()
            self.DisplayIconTable()
            self.SetSelectedOnDataAndImagePans()
        except: pass
        #
        self.Refresh()

    def OnSplitWinChanged(self,event):
        self.sashposition = self.splwin.GetSashPosition()
        self.OnMove(1)

    def ConsoleMessage(self,mess,level=-1):
        if self.parent is None: print(mess)
        else: self.model.ConsoleMessage(mess)

    def Message(self,mess):
        self.mdlwin.statusbar.SetStatusText(mess)

    def Message2(self,mess):
        self.model.Message2(mess)

    def GetFileNameExt(self,filename):
        head,tail = os.path.split(filename)
        base,ext  = os.path.splitext(tail)
        form = ext[1:]
        return form

    def CloseSelectedMolsInModel(self):
        mess = 'Sorry, not implemented'
        wx.MessageBox(mess,'MolIconTable.CloseMols')
        return

        if len(self.selectlst) <= 0:
            mess = 'No selected molecules'
            wx.MessageBox(mess,'MolIconTable.CloseSelectedMolsInModel')
            return

        for i in self.selectlst:
            self.model.RemoveMol(self.selectlst)


    def SaveFile(self,filename,selected=False):
        form = self.GetFileNameExt(filename)
        if form != 'sdf':
            mess = 'Only SDF format is supported'
            wx.MessageBox(mess,'MolIconTable.SaveFile')
            return
        nmol   = len(self.mollst)
        sellst = self.selectlst[:]
        if not selected: sellst = list(range(nmol))
        sdfstring = ''
        nsel = len(sellst)
        for i in sellst:
            mol = self.mollst[i][0]
            sdfstring += Chem.MolToMolBlock(mol,kekulize=False)
            sdfstring += '$$$$\n'
        #
        f = open(filename,'w')
        f.write(sdfstring)
        f.close()

        mess = 'Saved '
        if selected: mess += 'selected '
        mess += str(nsel) + ' molecules on file = ' + filename
        self.ConsoleMessage(mess)

    def SaveImage(self,filename,selected=False,perRow=None,imgSize=(200,200),
                  addname=True):
        """ Save PIL image on file. the save format is determined by the file
         extension. the supported formats are 'bmp','png','gif','jpeg', and
         tiff'
        """
        formlst = ['bmp','png','gif','jpeg','tiff']
        form = self.GetFileNameExt(filename)
        if not form in formlst:
            mess = 'Unknown image format : ' + form
            wx.MessageBox(mess,'MolIconTable.SaveImage')
            return
        #
        if perRow == None: perRow = self.niconcol
        nmol   = len(self.mollst)
        sellst = self.selectlst[:]
        if not selected: sellst = list(range(nmol))
        nsel = len(sellst)
        #
        legendlst = None
        if addname: legendlst = []
        mols      = []
        for i in sellst:
            mol = self.mollst[i][0]
            mols.append(mol)
            if addname: legendlst.append(mol.GetProp('_Name'))
        # make PIL image data
        img = Draw.MolsToGridImage(mols,molsPerRow=perRow,
                                   subImgSize=imgSize,legends=legendlst)
        img.save(filename,form)
        #
        nmol = len(self.mollst)
        mess = 'Saved image data of '
        if selected: mess += 'selected '
        mess += str(nsel) +' molecules on file = '
        mess += filename
        self.ConsoleMessage(mess)

    def ReadFile(self,filename,append=False):
        #form = self.GetFileNameExt(filename)
        head,tail = os.path.split(filename)
        base,ext  = os.path.splitext(tail)
        form = ext[1:]
        formlst = ['sdf','smi']
        if not form in formlst:
            mess = 'Only SDF or SMILES file is accepted'
            wx.MessageBox(mess,'MolIconTable.ReadFile')
            return

        filename = str(filename)
        if form == 'sdf':   suppl = Chem.SDMolSupplier(filename)
        elif form == 'smi': suppl = Chem.SmilesMolSupplier(filename)
        #
        mols = [x for x in suppl]
        mollst = [] # mollst: [[rdmol,name,inpfile],..]
        i = 1
        for mol in mols:
            i += 1
            try: name = mol.GetProp('_Name')
            except:
                name = base + '-' + str(i)
                mol.SetProp('_Name',str(name))
            mollst.append([mol,name,filename])
        #
        nmol = len(mollst)
        mess = 'MolIconTable: '
        if append: mess += 'appended '
        else:     mess += 'read '
        mess += ' molecules from file.' + '\n'
        mess += '    number of molecules = ' + str(nmol) +'\n'
        mess += '    inputfile = ' + filename
        self.ConsoleMessage(mess)
        #
        if not append: self.mollst  = mollst
        else:          self.mollst += mollst

        self.DisplayIconTable()

        if self.datawin: self.UpdateDataList()

    def ClearAll(self,yes):
        if yes: self.mollst = []
        else:
            tmplst = []
            nmol = len(self.mollst)
            for i in range(nmol):
                if not i in self.selectlst: tmplst.append(self.mollst[i])
            self.mollst = tmplst[:]
            self.selectlst = []
        self.OnMove(1)
        self.SetSelectedOnDataAndImagePans()

    def SelectAll(self,yes):
        if yes:
            nmol = len(self.mollst)
            self.selectlst = list(range(nmol))
        else: self.selectlst = []
        self.SetSelectedOnDataAndImagePans()

    def CopySDFTextToClipboard(self,selected=True):
        text = ''
        if selected:
            for i in self.selectlst:
                text += Chem.MolToMolBlock(self.mollst[i][0])
                text += '$$$$\n'
        else:
            for i in range(len(self.mollst)):
                text += Chem.MolToMolBlock(self.mollst[i][0])
                text += '$$$$\n'
        lib.CopyTextToClipboard(text)

    def PasteFromClipboard(self,form='smi'):
        """ paste append """
        string = lib.PasteTextFromClipboard()
        if len(string) <= 0:
            mess = 'Empty in clipboard.'
            wx.MessageBox(mess,'MolIconTable.PasteFromClipboard')
            return
        string = str(string)
        mollst = []
        nmol0 = 0
        if form == 'smi': # 'smi name\n',...
            textlst = string.split('\n')
            print(('smi',textlst))
            for i in range(len(textlst)):
                text = textlst[i].strip()
                items = lib.SplitStringAtSpaces(text)
                if len(items) <= 0: continue
                if len(items[0]) <= 0: contine
                if len(items) <= 1: name = 'smi-' + str(i)
                else:               name = items[1]
                nmol0 += 1
                mol = Chem.MolFromSmiles(items[0].strip())
                if mol is None: continue
                mol.SetProp('_Name',name)
                mollst.append([mol,name,'paste-smi'])
        elif form == 'sdf':
            textlst = string.split('$$$$\n')
            print(('sdf',textlst))
            for i in range(len(textlst)):
                if len(textlst[i]) <= 0: continue
                nmol0 += 1
                mol = Chem.MolFromMolBlock(textlst[i].strip())
                if mol is None: continue
                try: name = mol.GetProp('_Name')
                except: mol.SetProp('_Name','sdf-' + str(i))
                mollst.append([mol,name,'paste-sdf'])
        else:
            mess = 'The format is not supported. form = ' + form
            wx.MessageBox(mess,'MolIconTable.PasteFomClipboard')
            return
        # message
        nmol = len(mollst)
        mess  = 'Paste ' + form + ' string including ' + str(nmol0)
        mess += 'molecules\n'
        mess += '    ' + str(nmol) + ' moleucles were created and appended\n'
        self.ConsoleMessage(mess)
        #
        self.mollst = mollst
        #
        self.DisplayIconTable()
        if self.datawin: self.UpdateDataList()

    def OpenParamWin(self):
        self.paramwin = MolIconParams_Frm(self,-1)

    def HelpDocument(self):
        """
        #helpname = 'MolIconTable'
        helpname = 'users-guide//html//2-4-MolIconTable.html'
        helpname = 'MolIconTable//html//MolIconTable.html'
        self.model.helpctrl.Help(helpname)
        """
        fudir = self.model.setctrl.GetFUDir()
        fudir += '//FUdocs//'
        helpdata = fudir + 'users-guide//html//2-4-MolIconTable.html'
        HelpMessage(helpdata,datatype='file',viewer='Html',parent=self)

    def HelpWarning(self):
        text  = 'Warning:\n'
        text += '   When you change number of columns,\n'
        text += '   Clear all images before it.\n'
        text += '   Otherwise a fatal error will occur.'
        HelpMessage(text,datatype='text',viewer='Text',parent=self,
                           winsize=(400,120))

    def Tutorial(self):
        helpname = 'MolIconTable'
        helpname = 'users-guide//html//2-4-MolIconTable.html'
        self.model.helpctrl.Tutorial(helpname)

    def PrintParams(self):
        nl = '\n'
        mess  = 'MolIconTabel: Current parameters:' + nl
        mess += '    sanitize   = ' + str(self.sanitize) + nl
        mess += '    removeHs   = ' + str(self.removeHs) + nl
        mess += '    kekulize   = ' + str(self.kekulize) + nl
        mess += '    draw3d     = ' + str(self.draw3d) + nl
        mess += '    max_nmol   = ' + str(self.max_nmol) + nl
        mess += '    molsperRow = ' + str(self.molsperRow)
        self.ConsoleMessage(mess)

    def MenuItems(self):
        # Menu items
        menubar=wx.MenuBar()
        # File menu
        submenu=wx.Menu()
        if self.parent is not None:
            self.syncid = wx.NewId()
            submenu.Append(self.syncid,"Sync with MDLWIN",
                           "Synchronize data with Model",True)
            submenu.Append(-1,"Get Mols in MDLWIN",
                           "Get molecules in MDLWIN")
            submenu.AppendSeparator()
        # File
        submenu.Append(-1,"Open","Open file")
        submenu.Append(-1,"Append","Append mols in file")
        submenu.AppendSeparator()
        # Save
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Selected","Selected")
        subsubmenu.Append(-1,"All","All molecules")
        #submenu.AppendMenu(-1,"Save sdf in sigle file",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Save sdf in sigle file",subsubmenu)
        # save image
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Selected mols","Selected")
        subsubmenu.Append(-1,"All mols","All molecules")
        #submenu.AppendMenu(-1,"Save image",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Save image",subsubmenu)
        #
        submenu.AppendSeparator()
        submenu.Append(-1,"Quit", "Quit")
        menubar.Append(submenu,"File")
        # Edit
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"copy selected","copy selected in a SDF string")
        subsubmenu.Append(-1,"copy all","copy all molecules in a SDF string")
        #submenu.AppendMenu(-1,"Copy SDF",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Copy SDF",subsubmenu)
        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"paste sdf","paste sdf string")
        subsubmenu.Append(-1,"paste smiles","paste smiles string")
        #submenu.AppendMenu(-1,"Paste",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Paste",subsubmenu)
        menubar.Append(submenu,"Edit")
        # Commands
        submenu=wx.Menu()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Clear all","Clear all")
        subsubmenu.Append(-1,"Clear selected","Clear selected")
        #submenu.AppendMenu(-1,"Clear",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Clear",subsubmenu)
        submenu.AppendSeparator()
        subsubmenu=wx.Menu()
        subsubmenu.Append(-1,"Select all","select all")
        subsubmenu.Append(-1,"Deselect all","Deselect all")
        #submenu.AppendMenu(-1,"Select",subsubmenu)
        lib.AppendMenuWx23(submenu,-1,"Select",subsubmenu)
        menubar.Append(submenu,"Command")
        # Params
        submenu=wx.Menu()
        submenu.Append(-1,"Set params","set parameters")
        menubar.Append(submenu,"Params")
        # Help
        submenu=wx.Menu()
        submenu.Append(-1,'Document','Help document')
        submenu.Append(-1,'Warning','Help Warning')
        menubar.Append(submenu,'Help')

        return menubar

    def OnMenu(self,event):
        # Menu event handler
        menuid   = event.GetId()
        menuitem = self.menubar.FindItemById(menuid)
        item     = menuitem.GetItemLabel()
        #
        wildcardimg = 'png(*.png)|*.png|bmp(*.bmp)|*.bmp|All(*.*)|*.*'
        wildcardsav = 'sdf(*.sdf)|*.sdf|All(*.*)|*.*'
        # File
        if item == "Open":
            wildcard = 'sdf(*.sdf,*.smi)|*.sdf;*.smi|All(*.*)|*.*'
            filename=lib.GetFileName(self,wildcard,"r",True,"")
            if len(filename) > 0: self.ReadFile(filename,append=False)
        elif item == "Append":
            wildcard = 'sdf(*.sdf,*.smi)|*.sdf;*.smi|All(*.*)|*.*'
            filename=lib.GetFileName(self,wildcard,"r",True,"")
            if len(filename) > 0: self.ReadFile(filename,append=True)
        elif item == "Get Mols in MDLWIN":
            self.RestoreMolsInModel()
        elif item == "Sync with MDLWIN":
            if self.menubar.IsChecked(self.syncid):
                  self.syncmdlwin = True
            else: self.syncmdlwin = False
        elif item == "Close selected in MDLWIN":
            self.CloseSelectedMolsInModel()
        elif item == "Close all mols":
            self.CloseMols(selected=FRalse)
        elif item == "Selected":
            filename=lib.GetFileName(self,wildcardsav,"r",True,"")
            if len(filename) > 0:
                self.SaveFile(filename,selected=True)
        elif item == "All":
            filename=lib.GetFileName(self,wildcardsav,"r",True,"")
            if len(filename) > 0:
                self.SaveFile(filename,selected=False)
        elif item == "Selected mols":
            filename=lib.GetFileName(self,wildcardimg,"r",True,"")
            if len(filename) > 0:
                self.SaveImage(filename,selected=True)
        elif item == "All mols":
            filename=lib.GetFileName(self,wildcardimg,"r",True,"")
            if len(filename) > 0:
                self.SaveImage(filename,selected=False)
        # Edit
        elif item == "copy selected": self.CopySDFTextToClipboard(True)
        elif item == "copy all": self.CopySDFTextToClipboard(False)
        elif item == "paste sdf": self.PasteFromClipboard('sdf')
        elif item == "paste smiles": self.PasteFromClipboard('smi')


        # Commands
        elif item == "Clear all": self.ClearAll(True)
        elif item == "Clear selected": self.ClearAll(False)
        elif item == "Select all": self.SelectAll(True)
        elif item == "Deselect all": self.SelectAll(False)
        # Params
        elif item == "Set params": self.OpenParamWin()
        # Help
        elif item == "Document": self.HelpDocument()
        elif item == "Warning": self.HelpWarning()
        elif item == "Quit":
            self.OnClose(0)

class Preference_Frm(wx.Frame):
    def __init__(self,parent,winpos=[]):
        self.title = 'Preference'
        self.parent = parent
        winsize = (220,340) # (220,300)
        [x,y] = parent.GetPosition()
        if len(winpos) <= 0:  winpos  = [x-winsize[0]+100,y+50]
        winpos  = lib.SetWinPos(winpos)
        winsize = lib.WinSize(winsize,False)
        wx.Frame.__init__(self,parent,-1,self.title,pos=winpos,
            size=winsize,style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|\
            wx.FRAME_FLOAT_ON_PARENT)

        self.mdlwin = parent
        self.model  = self.mdlwin.parent
        self.winlabel='Preference'
        #
        self.SetBackgroundColour('light gray')
        # set icon
        try: lib.AttachIcon(self,const.FUMODELICON)
        except: pass

        self.savecurmol = None
        self.savemodel    = None
        self.savethick    = None
        self.saveradius   = None
        self.savebgcolor  = None

        self.saveelmcolor = None
        self.saveopacity  = None

        self.modellst    = ['','line','stick','ball-and-stick','CPK']
        self.thicklst    = ['','0.5','1','2','3','4','5','10']
        self.radiuslst   = ['','0.1','0.2','0.3','0.4','0.5']
        self.bgcolorlst  = ['','black','white','gray','blue',
                            'yellow','orange','brown',
                            'cyan','green','purple',
                            'magenta','red',
                            '---','on color palette']
        self.elmcolorlst = ['','default','---','red','magenta',
                 'yellow','orange','brown','blue','cyan','green','purple',
                 'white','gray','black','---','on color palette']
        self.elmnamelst  = ['','H','C','N','O','S','P']
        self.opacitylst  = ['','0.2','0.3','0.4','0.5','0.6','0.8','1.0']
        self.bgcolor     = None
        self.elmcolor    = None
        #
        self.cmbobjlst = []
        #
        self.saveatoms = self.SaveAtoms()

        self.CreatePanel()

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.Show()

    def CreatePanel(self):
        [w,h] = self.GetClientSize()
        self.panel = wx.Panel(self,-1,pos=(0,0),size=(w,h))
        self.SetBackgroundColour('light gray')
        hcb=25 # const.HCBOX
        hbt=25
        self.cmbobjlst = []
        yloc = 10
        xloc = 20
        wx.StaticText(self.panel,-1,"Model:",pos=(xloc,yloc),size=(40,18))
        cmbmdl=wx.ComboBox(self.panel,-1,'',choices=self.modellst,
                            pos=(xloc+50,yloc), size=(130,hcb),
                            style=wx.CB_READONLY)
        cmbmdl.SetStringSelection('---')
        self.cmbobjlst.append([cmbmdl,'model'])
        #self.cmbmdl.Bind(wx.EVT_COMBOBOX,self.OnModel)
        yloc += 30
        wx.StaticText(self.panel,-1,"Line/stick thick:",pos=(xloc,yloc),
                          size=(95,18),style=wx.TE_PROCESS_ENTER)
        cmbtic=wx.ComboBox(self.panel,-1,'',choices=self.thicklst,
                            pos=(140,yloc), size=(60,hcb))
        cmbtic.SetStringSelection('')
        self.cmbobjlst.append([cmbtic,'thick'])
        yloc += 30
        wx.StaticText(self.panel,-1,"Circle/ball radius:",pos=(xloc,yloc),
                          size=(95,18))
        cmbrad=wx.ComboBox(self.panel,-1,'',choices=self.radiuslst,
                            pos=(140,yloc), size=(60,hcb))
        cmbrad.SetStringSelection('')
        self.cmbobjlst.append([cmbrad,'radius'])

        yloc += 30
        wx.StaticText(self.panel,-1,"Background color:",pos=(xloc,yloc),
                          size=(120,18))
        yloc += 20
        bgcol=wx.ComboBox(self.panel,-1,'',choices=self.bgcolorlst,
                           pos=(xloc+50,yloc), size=(130,hcb),
                           style=wx.CB_READONLY)
        bgcol.Bind(wx.EVT_COMBOBOX,self.OnColor)
        bgcol.SetStringSelection('')
        self.cmbobjlst.append([bgcol,'bgcolor'])

        yloc += 30
        wx.StaticText(self.panel,-1,"Element color:",pos=(xloc,yloc),
                          size=(120,18))
        yloc += 20
        self.elmnam=wx.ComboBox(self.panel,-1,'',choices=self.elmnamelst,
                           pos=(xloc+10,yloc-3), size=(60,hcb),
                           style=wx.TE_PROCESS_ENTER)
        self.elmnam.SetStringSelection('')
        elmcol=wx.ComboBox(self.panel,-1,'',choices=self.elmcolorlst,
                           pos=(xloc+80,yloc-3), size=(100,hcb),
                           style=wx.CB_READONLY)
        elmcol.Bind(wx.EVT_COMBOBOX,self.OnColor)
        elmcol.SetStringSelection('')
        self.cmbobjlst.append([elmcol,'elmcolor'])
        yloc += 25
        wx.StaticText(self.panel,-1,"Opacity:",pos=(xloc,yloc),size=(50,18))
        cmbopa=wx.ComboBox(self.panel,-1,'',choices=self.opacitylst,
                           pos=(xloc+60,yloc-2), size=(80,hcb),
                           style=wx.TE_PROCESS_ENTER)
        cmbopa.SetStringSelection('')
        self.cmbobjlst.append([cmbopa,'opacity'])
        yloc+=30
        # advanced setting
        advbt=wx.Button(self.panel,-1,"Other settings",pos=(xloc,yloc),size=(150,hbt))
        advbt.Bind(wx.EVT_BUTTON,self.OnOtherSetting)

        yloc += 30
        lin1=wx.StaticLine(self.panel,pos=(-1,yloc),size=(w,2),
                           style=wx.LI_HORIZONTAL)
        yloc += 10

        self.rbtcur=wx.RadioButton(self.panel,-1,'current',pos=(25,yloc),
                               style=wx.RB_GROUP)
        lib.SetTipString(self.rbtcur,'current molecule only')
        self.rbtall=wx.RadioButton(self.panel,-1,'all',pos=(100,yloc))
        lib.SetTipString(self.rbtall,'all opened molecules')
        self.rbttsk=wx.RadioButton(self.panel,-1,'task',pos=(150,yloc))
        lib.SetTipString(self.rbttsk,'during the task')

        self.rbtcur.SetValue(True)
        yloc+=25
        x0 = 10
        canbt=wx.Button(self.panel,-1,"Cancel",pos=(x0+10,yloc),size=(55,hbt))
        canbt.Bind(wx.EVT_BUTTON,self.OnCancel)
        aplbt=wx.Button(self.panel,-1,"Apply",pos=(x0+75,yloc),size=(50,hbt))
        aplbt.Bind(wx.EVT_BUTTON,self.OnApply)
        #canbt.SetToolTipString('Recover all atomic params and bgcolor')
        lib.SetTipString(canbt,'Recover all atomic params and bgcolor')
        aplbt=wx.Button(self.panel,-1,"Close",pos=(x0+135,yloc),size=(50,hbt))
        aplbt.Bind(wx.EVT_BUTTON,self.OnClose)

    def SaveAtoms(self):
        saveatoms = []
        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        for i in range(nmol):
            saveatm = []
            mol = self.model.molctrl.GetMol(i)
            natm = len(mol.atm)
            for ia in range(natm):
                atom = mol.atm[ia]
                attr = [atom.model,atom.color,atom.thick,atom.thickbs,
                        atom.atmrad]
                saveatm.append(attr)
            saveatoms.append(saveatm)
        return saveatoms

    def OnOtherSetting(self,event):
        # open other setting panel
        mess='Under construction.\n'
        mess+='Execute a command "fum.setctrl.SetParam(param_name)=value"\n'
        mess+=' in the pyshell console to change a parameter value.\n'
        mess+='You can check the parameter name by executing \n'
        mess+='the [Help]-[Document]-[Vew setting Params] menu.'
        wx.MessageBox(mess,'subwin.OnOtherSetting')

    def OnApply(self,event):
        # check no molecule
        setparam=None
        if self.rbtcur.GetValue():
            curmol=self.model.curmol
        elif self.rbtall.GetValue():
            curmol=None
        elif self.rbttsk.GetValue():
            curmol=None
            setparam=True

        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        self.savecurmol = self.model.curmol
        molmodel=None
        for cmbobj,objname in self.cmbobjlst:
            value = cmbobj.GetStringSelection()
            if value == '---' or value == '': continue
            if objname == 'bgcolor':
                if value == 'on color palette':
                    if self.bgcolor is not None:
                        bgcolor = self.bgcolor
                        self.bgcolor = None
                        cmbobj.SetStringSelection('')
                    else: bgcolor = []
                else: bgcolor = const.RGBColor[value]
                if len(bgcolor) <= 0: continue
                self.ChangeBGColor(True,bgcolor,curmol)
                if setparam:
                    self.model.setctrl.SetParam('win-color',bgcolor)
            elif objname == 'model':
                modelnum = {'line':0, 'stick':1,'ball-and-stick':2,'CPK':3}
                mdlnum = modelnum[value]
                molmodel=mdlnum
                self.ChangeModel(True,mdlnum,curmol)
                if setparam:
                    self.model.setctrl.SetParam('mol-model',mdlnum)

            elif objname == 'thick':
                value = cmbobj.GetValue()
                try: value = float(value)
                except:
                    mess = 'Error thick input = ' + str(value)
                    wx.MessageBox(mess,'Preference.OnApply')
                    return
                self.ChangeThick(True,value,curmol)
                if setparam:
                    if molmodel == 0 or molmodel == 1:
                        self.model.setctrl.SetParam('bond-thick',value)
                    elif molmodel == 2:
                        self.model.setctrl.SetParam('bond-thick-bs', value)
            elif objname == 'radius':
                value = cmbobj.GetValue()
                try: value = float(value)
                except:
                    mess = 'Error radius input = ' + str(value)
                    wx.MessageBox(mess,'Preference.OnApply')
                    return
                self.ChangeRadius(True,value,curmol)
                if setparam:
                    if molmodel == 2:
                        self.model.setctr.SetParam('atom-sphere-radius',value)

            elif objname == 'opacity':
                value = cmbobj.GetValue()
                try: value = float(value)
                except:
                    mess = 'Error opacity input = ' + str(value)
                    wx.MessageBox(mess,'Preference.OnApply')
                    return
                self.ChangeOpacity(True,value,curmol)
                if setparam:
                    wx.MessageBox('Opacity can not be set during a task')
            elif objname == 'elmcolor':
                elmname = self.elmnam.GetStringSelection()
                elm = lib.ElementNameFromString(elmname)
                self.saveelmcolor = []
                elmcolor=[]
                if value == 'on color palette':
                    if self.elmcolor is not None:
                        elmcolor=self.elmcolor
                        cmbobj.SetStringSelection('')
                        self.elmcolor = None
                    else: elmcolor = []
                elif value == 'default':
                    elmcolor=self.model.setctrl.GetElementColor(elm)
                else: elmcolor = const.RGBColor[value]
                if len(elmcolor) <= 0 or elmcolor is None: continue
                #
                self.ChangeElmColor(True,elm,elmcolor,curmol)
                if setparam:
                    self.model.setctrl.SetElementColor(elm,elmcolor)

        self.model.DrawMol(True)

        self.model.SwitchMol(self.savecurmol,False,True,messout=False)

    def OnColor(self,event):
        obj = event.GetEventObject()
        name = None
        for cmbobj,objname in self.cmbobjlst:
            if obj == cmbobj: name = objname
        value = obj.GetStringSelection()
        if value != 'on color palette': return
        color = lib.ChooseColorOnPalette(self.mdlwin,False,1.0)
        if len(color) <= 0: obj.SetStringSelection('')
        else:
            if   name == 'elmcolor':
                self.elmcolor = color
                del self.elmcolor[3]
            elif name == 'bgcolor':  self.bgcolor  = color

    def ChangeElmColor(self,change,elm=None,elmcolor=None,curmol=None):
        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        if curmol is not None:
            mollst=[curmol]
        else: mollst=list(range(nmol))
        if change: # apply
            self.saveelmcolor = []
            for i in mollst: #range(nmol):
                saveatm = []
                self.model.SwitchMol(i,False,True,messout=False)
                mol = self.model.mol
                saveatm = self.SaveAtomAttrib(mol,'color')
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    if self.model.mol.atm[ia].elm == elm:
                        self.model.mol.atm[ia].color = elmcolor
                self.saveelmcolor.append(saveatm)
                #self.model.DrawMol(True)
        else: # Undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                saveatm = self.saveelmcolor[i]
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    self.model.mol.atm[ia].color = saveatm[ia]
                self.model.DrawMol(True)
            self.saveelmcolor = None

    def ChangeOpacity(self,change,opacity=None,curmol=None):
        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        if curmol is not None:
            mollst=[curmol]
        else: mollst=list(range(nmol))
        if change: # apply
            self.saveopacity = []
            for i in mollst: #range(nmol):
                saveatm = []
                self.model.SwitchMol(i,False,True,messout=False)
                mol = self.model.mol
                saveatm = self.SaveAtomAttrib(mol,'opacity')
                self.saveopacity.append(saveatm)
                natm = len(self.model.mol.atm)
                for ia in range(natm): self.model.mol.atm[ia].color[3] = opacity
                #self.model.DrawMol(True)
        else: # Undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                saveatm = self.saveopacity[i]
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    self.model.mol.atm[ia].color[3] = saveatm[ia]
                #self.model.DrawMol(True)
            self.saveopacity = None

    def ChangeRadius(self,change,radius=None,curmol=None):
        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        if curmol is not None:
            mollst=[curmol]
        else: mollst=list(range(nmol))
        if change: # apply
            self.saveradius = []
            for i in mollst: #range(nmol):
                saveatm = []
                self.model.SwitchMol(i,False,True,messout=False)
                mol = self.model.mol
                saveatm = self.SaveAtomAttrib(mol,'radius')
                self.saveradius.append(saveatm)
                natm = len(self.model.mol.atm)
                for ia in range(natm): self.model.mol.atm[ia].atmrad = radius
                #self.model.DrawMol(True)
        else: # Undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                saveatm = self.saveradius[i]
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    self.model.mol.atm[ia].radius = saveatm[ia]
                #self.model.DrawMol(True)
            self.saveradius = None

    def ChangeThick(self,change,thick=None,curmol=None):
        nmol = self.model.molctrl.GetNumberOfMols()
        if curmol is not None:
            mollst=[curmol]
        else: mollst=list(range(nmol))
        if nmol <= 0: return
        if change: # apply
            self.savethick = []
            for i in mollst: #range(nmol):
                saveatm = []
                self.model.SwitchMol(i,False,True,messout=False)
                mol = self.model.mol
                saveatm = self.SaveAtomAttrib(mol,'thick')
                self.savethick.append(saveatm)
                natm = len(self.model.mol.atm)
                for ia in range(natm): self.model.mol.atm[ia].thick = thick
                #self.model.DrawMol(True)
        else: # Undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                saveatm = self.savethick[i]
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    self.model.mol.atm[ia].thick = saveatm[ia]
                #self.model.DrawMol(True)
            self.savethick = None

    def ChangeBGColor(self,change,bgcolor=None,curmol=None):
        """ change=True or False (undo) """
        nmol = self.model.molctrl.GetNumberOfMols()
        if curmol is not None: mollst=[curmol]
        else: mollst=list(range(nmol))
        if nmol <= 0: return
        if change: # change
            self.savebgcolor = []
            for i in mollst: # range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                oldbgcolor = self.model.mdlwin.draw.bgcolor
                self.savebgcolor.append(oldbgcolor)
                self.model.ChangeBackgroundColor(bgcolor)
        else: # undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                bgcolor = self.savebgcolor[i]
                self.model.ChangeBackgroundColor(bgcolor)
            self.savebgcolor = None

    def ChangeModel(self,change,mdlnum=None,curmol=None):
        nmol = self.model.molctrl.GetNumberOfMols()
        if curmol is not None:
            mollst=[curmol]
        else: mollst=list(range(nmol))
        if nmol <= 0: return
        if change: # change
            self.savemodel = []
            for i in mollst: #range(nmol):
                saveatm = []
                self.model.SwitchMol(i,False,True,messout=False)
                mol = self.model.mol
                saveatm = self.SaveAtomAttrib(mol,'model')
                self.savemodel.append(saveatm)
                natm = len(self.model.mol.atm)
                for ia in range(natm): self.model.mol.atm[ia].model = mdlnum
                #self.model.DrawMol(True)
        else: # undo
            for i in mollst: #range(nmol):
                self.model.SwitchMol(i,False,True,messout=False)
                saveatm = self.savemodel[i]
                natm = len(self.model.mol.atm)
                for ia in range(natm):
                    self.model.mol.atm[ia].model = saveatm[ia]
                #self.model.DrawMol(True)
            self.savemodel = None

    def SaveAtomAttrib(self,mol,attr):
        atmattr = []
        for atom in mol.atm:
             if   attr == 'model': atmattr.append(atom.model)
             elif attr == 'color': atmattr.append(atom.color[:3])
             elif attr == 'thick': atmattr.append(atom.thick)
             elif attr == 'thickbs': atmattr.append(atom.thickbs)
             elif attr == 'radius': atmattr.append(atom.atmrad)
             elif attr == 'opacity': atmattr.append(atom.color[3])
        return atmattr

    def CanNotUndoMessage(self,item):
        """ item=bgcolor,elmcolor,... """
        mess = 'Unable to undo. No ' + item + ' data is save'
        wx.MessageBox(mess,'Preference.Undo')

    def OnCancel(self,event):
        if self.saveatoms is None:
            mess = 'No saved atom params. Unable to recover'
            wx.MessageBox(mess,'Preference.OnCancel')
            return

        nmol = self.model.molctrl.GetNumberOfMols()
        if nmol <= 0: return
        for i in range(nmol):
            try: saveatm = self.saveatoms[i]
            except:
                mess  = 'Molecule data in MDLWIN have changed.\n'
                mess += '    Recovery may not complete'
                wx.MessageBox(mess,'ImageSheet.OnCancel')
                break
            mol = self.model.molctrl.GetMol(i)
            natm = len(mol.atm)
            for ia in range(natm):
                mol.atm[ia].model   = saveatm[ia][0]
                mol.atm[ia].color   = saveatm[ia][1]
                mol.atm[ia].thick   = saveatm[ia][2]
                mol.atm[ia].thickbs = saveatm[ia][3]
                mol.atm[ia].atmrad  = saveatm[ia][4]
            self.model.molctrl.SetMol(i,mol)

        if self.savebgcolor: self.ChangeBGColor(False)
        else: self.model.DrawMol(True)

        mess = 'All atomic paramters were recovered'
        self.ConsoleMessage(mess)

    def OnClose(self,event):
        try: self.model.winctrl.Close(self.winlabel)
        except: pass
        self.Destroy()

    def ConsoleMessage(self,mess):
        self.model.ConsoleMessage(mess)

class ProgressBar_Frm(wx.Frame):
    def __init__(self,parent,winpos=[],winsize=[],title='',mess='',
                 interval=10,bgcolor=[]):
        self.title=title
        if len(title) <= 0: self.title = 'Progress Bar'
        if len(winsize) <= 0: winsize = lib.WinSize((300,100),False)
        if len(winpos) <= 0:
            [x,y] = parent.GetPosition()
            if len(winpos) <= 0:  winpos  = [x+100,y+100]
        if len(bgcolor) <= 0: bgcolor=[255,255,0] #[200,200,200]
        self.interval=interval
        wx.Frame.__init__(self, parent,-1, self.title,size=winsize,pos=winpos,
               style=wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX|wx.FRAME_FLOAT_ON_PARENT)
        # set icon
        try: lib.AttachIcon(self,const.FUPLOTICON)
        except: pass
        #
        self.SetBackgroundColour(bgcolor)
        self.SetTitle(self.title)
        self.Show()
        
        wx.StaticText(self,-1,mess,pos=(20,10),size=(winsize[0]-40,22))
        # timer
        self.timer=wx.Timer(self) #,-1)
        self.Bind(wx.EVT_TIMER,self.OnTimer) #,self.timer)
        
        self.maxrange=winsize[0]-50
        self.prgbar=wx.Gauge(self,-1,range=self.maxrange,pos=(20,40),
                             size=(winsize[0]-50,10),
                             style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        self.prgbar.SetValue(0) #self.maxrange)
        #        
        self.Bind(wx.EVT_CLOSE,self.OnClose)
    
    def StartProgressBar(self,interval=-1):
        if interval <= 0: self.interval=10
        else: self.interval=interval
        self.timer.Start(self.interval)
        
    def OnTimer(self,event):
        count=self.prgbar.GetValue()+1
        if count > self.maxrange: count=0
        self.prgbar.SetValue(count) #self.prgbar.Pulse()
        self.prgbar.Refresh()
        wx.Sleep(self.interval/1000.0) # arg in sec
        
    def OnClose(self,event):
        self.Close()
        
    def Close(self):
        try:
            self.timer.Stop()
        except: pass
        try:
            self.prgbar.Destroy()
        except: pass
        try:
            self.Destroy()
        except: pass


class ListParameter_Pan(wx.Panel):
    """ A panel to entering/changeing parameter values in "param = value" list format

    Constructor:
        parent=wx.Frame(None,-1,title='ListParamters',pos=[0,0],size=[400,500])
        lstpan=ListParameterPanel(parent, winpos=[0,0], winsize=size,
                     paramlst=None, jsonparamfile=None,
                     applycancelbutton=False,retmethod=None,
                     helpfile=None,,winlabel='ListParameter_Pan')

    :param obj parent: parent object
    :param lst winpos: window position, default: [0,0]
    :param lst winsize: window size, default [400,250]
    :param lst paramlst: list of grouplst,grouptiplst,defaultdic,tipsdic,
                [grouplst,grouptiplst,defaultdic,tipsdic]
                grouplst: list of paramter groups, ['group1','group2',...]
                grouptiplst: list of tips for groups, ['tip string for group1',...]
                defaultdic: dictionary of default parameter values,
                    {'grp1':{'grp1-param1':[val1,val2...],...}...}
                tipsdic: dictionary of tip striungs, {'grp1':{'grp1-param1':tip_str1,...},...}
    :param str jsonparamfile: parameter definition file name, a json file(xxx.json).
                alternative or addition to "paramlst"
    :param str curgroup: current group name, default:grouplst[0]
    :param bool applycancelbutton: True to make "apply" and "close" buttons, Fasle otherwise
    :param obj retmethod: a method of the parent object "def retmethod(changeddic)"
               executed when the 'Apply' button is pressed.
               The argument is changed parameter values(dic) and info(str),
               retmethod({'grp1':{'grp1-param1:val2,....},...},'apply')
    :param obj messmethod: a print method of the parent, default:None
    :param str helpfile: html help document file. If this is not None,
                a help button will be attached to the list_param_panel.
    :param str winlabel: the label of this window
    """
    def __init__(self, parent, winpos=[], winsize=[],
                 paramlst=None, jsonparamfile=None,curgroup=None,
                 applycancelbutton=True,addremovebutton=True,
                 retmethod=None,messmethod=None,helpfile=None,
                 winlabel='ListParameter'):
        self.title='ListParameter_Pan'
        if len(winpos) <= 0:  winpos=[0,0]
        if len(winsize) <= 0: winsize=lib.WinSize([400,300])
        winpos  = lib.SetWinPos(winpos)
        wx.Panel.__init__(self, parent, -1, pos=winpos,size=winsize)

        self.parent=parent
        self.retmethod=retmethod
        self.messmethod=messmethod # the argument is "mess"(str)
        self.helpfile=helpfile
        self.winlabel=winlabel
        # window color
        self.winsize = winsize
        self.panelbgcolor = "light gray"
        self.maxlistboxmenuheight = 400
        self.applycancelbutton=applycancelbutton
        self.addremovebutton=addremovebutton
        # font size and color
        self.fontheight=20 # 15
        self.setcolor=wx.RED #wx.BLUE #wx.CYAN
        self.unsetcolor=wx.BLACK
        self.needcolor=(165, 42, 42) # brown
        #
        if paramlst is None:
            grouplst=grouptiplst=[]
            defaultdic=tipsdic={}
        else:
            grouplst,grouptiplst,defaultdic,tipsdic=paramlst

        self.grouplst=grouplst
        self.grouptiplst=grouptiplst
        self.defaultdic=defaultdic
        self.tipsdic=tipsdic
        self.changeddic={}
        if len(self.defaultdic) > 0:
            self.changeddic=self.SetChangedDic(self.defaultdic)

        if jsonparamfile is not None:
            self.AddParameterGroups(jsonparamfile, checkdup=False,
                                    updateselbox=False)

        self.curgroup=curgroup
        if len(self.grouplst) > 0:
            self.curgroup=self.grouplst[0]
        #
        self.openlistboxmenu = False
        self.selectedrow = 0
        self.selectedcol = 0
        #
        self.grouppanel = None
        self.listpanel = None

        self.CreatePanel()

        self.OnSelectGroup(1)
        self.selectbox=None
        self.tipview = None
        #
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_MOVE, self.OnMove)

        self.Show()

    def SetChangedDic(self,defaultdic):
        changeddic={}
        for grp in defaultdic:
            changeddic[grp]={}
        return changeddic

    def CreatePanel(self):
        winsize = self.GetClientSize()
        width = winsize[0];
        height = winsize[1]
        panpos = (-1, -1)
        panheight = winsize[1]  # -35
        if self.applycancelbutton:
            panheight = winsize[1] - 40
        # panel
        self.panel = wx.Panel(self, -1, pos=panpos, size=winsize)
        self.panel.SetBackgroundColour(self.panelbgcolor)
        yloc = 0
        #
        self.grppanpos = [0, yloc]
        grppanwidth = 100  # 80
        self.grppansize = [grppanwidth, panheight - yloc]
        self.CreateGroupPanel(self.grppanpos, self.grppansize)
        #
        wx.StaticLine(self.panel, pos=[grppanwidth + 7, yloc], size=[2, self.grppansize[1]-40],
                      style=wx.LI_VERTICAL)
        #
        lstxloc = grppanwidth + 20
        lstpanwidth = width - lstxloc
        lstpanpos = [lstxloc, yloc]  # [inpxloc,0]
        lstpansize = [lstpanwidth, panheight - yloc]
        self.CreateListPanel(lstpanpos, lstpansize)
        # apply/cancel button
        if self.applycancelbutton:
            yloc = panheight
            wx.StaticLine(self.panel, pos=[0, yloc], size=[width, 2], style=wx.LI_HORIZONTAL)
            yloc += 8
            xloc=int(width/2) - 80
            self.btnapl = wx.Button(self.panel, -1, "Apply", pos=[xloc, yloc], size=(70, 22))
            lib.SetTipString(self.btnapl, 'Apply')
            self.btnapl.Bind(wx.EVT_BUTTON, self.OnApply)
            xloc+=90
            self.btncls = wx.Button(self.panel, -1, "Cancel", pos=[xloc, yloc], size=(70, 22))
            lib.SetTipString(self.btncls, 'Cancel the changes')
            self.btncls.Bind(wx.EVT_BUTTON, self.OnCancel)

    def CreateGroupPanel(self, panpos, pansize):

        self.grouppanel = wx.Panel(self.panel, -1, pos=panpos, size=pansize)
        self.grouppanel.SetBackgroundColour(self.panelbgcolor)
        #
        height = pansize[1]
        width = pansize[0]
        btnyloc=pansize[1] - 70
        xloc = 10
        yloc = 5  # panpos[1]+5
        btnheight = 70;
        lbheight = btnyloc - btnheight
        lbsize = [pansize[0] - 10, lbheight]
        #
        wx.StaticText(self.grouppanel, -1, "Select a group:", pos=(xloc, yloc), size=(110, 20))
        yloc += 20
        if self.grouplst is not None:
            glst=self.grouplst
        else:
            glst=[]
        self.selectbox = wx.ListBox(self.grouppanel, -1, choices=glst,
                                    pos=[xloc, yloc], size=lbsize,
                                    style=wx.LB_SINGLE | wx.LB_HSCROLL)  # wx.LB_NEEDED_SB (vertical scroll bar)
        if len(glst) > 0:
            self.selectbox.SetStringSelection(self.curgroup)
        ###self.selectbox.Bind(wx.EVT_RIGHT_DOWN, self.OnSelectRightClick)

        #if self.curparam in self.donenamedic:
        #    try:
        #        idx = self.grouplst.index(self.curparam)
        #    except:
        #        idx = -1
        #    # is not suppoted in WINDOWS ?
        #    #""if idx >= 0: self.selectbox.SetItemForegroundColour(idx,self.setcolor)"""

        yloc += lbsize[1] + 10
        # buttons
        if self.addremovebutton:
            self.btnrmv = wx.Button(self.grouppanel, -1, "Remove", pos=[15, yloc], size=(70, 22))
            # self.btnrmv.SetToolTip('Remove selected group')
            lib.SetTipString(self.btnrmv, 'Remove selected group')
            self.btnrmv.Bind(wx.EVT_BUTTON, self.OnRemoveGroup)
            yloc += 30
            self.btnadd = wx.Button(self.grouppanel, -1, "Add", pos=[15, yloc], size=(70, 22))
            self.btnadd.Bind(wx.EVT_BUTTON, self.OnAddGroup)
            lib.SetTipString(self.btnadd, 'Read parameter definition files and add to groups')
        yloc=height -30
        wx.StaticLine(self.grouppanel, pos=[10, yloc-10], size=[width, 2], style=wx.LI_HORIZONTAL)
        self.btngsav = wx.Button(self.grouppanel, -1, "Save all", pos=[25, yloc], size=(70, 22))
        self.btngsav.Bind(wx.EVT_BUTTON, self.OnSaveParameters)
        lib.SetTipString(self.btngsav, 'Save parameters in all groups')
        # event handlers
        self.selectbox.Bind(wx.EVT_LISTBOX, self.OnSelectGroup)
        self.selectbox.Bind(wx.EVT_RIGHT_DOWN, self.OnGroupPanelRightClick)

    def CreateListPanel(self, panpos, pansize):
        self.listpanel = wx.Panel(self.panel, -1, pos=panpos, size=pansize)
        self.listpanel.SetBackgroundColour(self.panelbgcolor)
        #
        height = pansize[1]
        btnheight = 25;
        gridwidth = pansize[0] - 10
        self.gridwidth=gridwidth
        gridheight = pansize[1] - btnheight - 40
        btnyloc = pansize[1] - btnheight - 5
        #btnxloc=int(gridwidth/2) - 80
        xloc = 0;
        yloc = 5
        # title = 'Params of "' + self.curgroup+'"'
        self.SetGroupNameOnListPanel(xloc, yloc, self.curgroup,self.gridwidth)
        yloc += 20
        # created Variable Table
        gridpos = [xloc, yloc]
        gridsize = [gridwidth, gridheight]
        if self.curgroup is not None:
            nrow= len(self.defaultdic[self.curgroup].keys())
        else:
            nrow=0
        # help button
        yloc=2
        xloc=gridwidth-20
        # help button
        if self.helpfile is not None:
            btnhlp=Help_Button(self.listpanel,winpos=[xloc,yloc],helpfile=self.helpfile)
        #
        self.CreateGridPanel(self.listpanel, gridpos, gridsize, nrow)
        self.SetDataToGridTable(self.curgroup)
        # buttons
        yloc = btnyloc
        xloc=0
        btnopn = wx.Button(self.listpanel, -1, "Read", pos=(xloc, yloc), size=(50, 22))
        btnopn.Bind(wx.EVT_BUTTON, self.OnReadParameterFile)
        lib.SetTipString(btnopn, 'Read parameter values')
        xloc+=60
        btnsav = wx.Button(self.listpanel, -1, "Save", pos=(xloc, yloc), size=(50, 22))
        btnsav.Bind(wx.EVT_BUTTON, self.OnSaveParameters)
        lib.SetTipString(btnsav, 'Save parameters in this group')
        xloc+=60
        btnrsetall = wx.Button(self.listpanel, -1, "ResetAll", pos=(xloc, yloc), size=(70, 22))
        btnrsetall.Bind(wx.EVT_BUTTON, self.OnResetAllParams)
        lib.SetTipString(btnrsetall, 'Reset all parameter values to initial ones')
        xloc+=80
        btnrset = wx.Button(self.listpanel, -1, "Reset", pos=(xloc, yloc), size=(50, 22))
        btnrset.Bind(wx.EVT_BUTTON, self.OnResetGroupParams)
        lib.SetTipString(btnrset, 'Reset selected value to initial one')

    def SetGroupNameOnListPanel(self,xloc,yloc,group,gridwidth):
        if group is None:
            return
        title = 'Params of "' + group+'"'
        stinp = wx.StaticText(self.listpanel, -1, title, pos=(xloc, yloc), size=(gridwidth-30, 20))
        # stinp.SetToolTip('Select a cell and input value directly or R-click to pop up select items/tip')
        lib.SetTipString(stinp, 'Select a cell and input value directly or R-click to pop up select items/tip')

    def CreateGridPanel(self, panel, panpos, pansize, nrow):
        self.gridpanel = wx.Panel(self.listpanel, -1, pos=panpos, size=pansize)
        self.gridpanel.SetBackgroundColour('white')
        self.grid = wx.grid.Grid(self.gridpanel, -1, pos=[0, 0], size=pansize)
        self.grid.EnableGridLines(False)
        self.grid.SetColLabelSize(0)
        self.grid.SetRowLabelSize(0)

        self.grid.SetScrollbars(0, 20, 0, 5)
        try:
            #self.grid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)
            #self.grid.ShowScrollbars(wx.SHOW_SB_ALWAYS, wx.SHOW_SB_ALWAYS)
            self.grid.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_DEFAULT)
        except:
            pass
        ###self.grid.DisableDragCell()
        # self.grid.EnableCellEditControl(False)
        # self.grid.DisableDragColMove()
        # self.grid.SetSelectionBackground('white')
        eqwidth=20
        varwidth=int((pansize[0]-eqwidth)/2)
        valwidth=varwidth
        self.grid.CreateGrid(nrow + 1, 3)
        self.grid.SetColSize(0, varwidth)
        self.grid.SetColSize(1, eqwidth)
        self.grid.SetColSize(2, valwidth)
        for i in range(nrow): self.grid.SetRowSize(i, 22)
        # make the first col read-only
        self.grid.SetReadOnly(0, 1, isReadOnly=True)
        for i in range(nrow + 1):
            self.grid.SetReadOnly(i, 0, isReadOnly=True)
            self.grid.SetReadOnly(i, 1, isReadOnly=True)

        #self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.OnGridCellSelect)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnGridCellSelect)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnGridRightClick)
        if wx.version()[0:2] == '2.':
            self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.OnGridCellChange)
        else:
            self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self.OnGridCellChange)

    def OnResetGroupParams(self, event):
        """ Reset the selected parameter value to the default value

        """
        curvarnam = self.grid.GetCellValue(self.selectedrow, 0)
        print('curvarnam=',curvarnam)
        if curvarnam is None or curvarnam == '':
            wx.MessageBox('Select a parameter and try again.','OnResetGroupParams')
            return
        if self.curgroup in self.changeddic:
            if curvarnam in self.changeddic[self.curgroup]:
                self.changeddic[self.curgroup].pop(curvarnam)
        if lib.ObjectType(self.defaultdic[self.curgroup][curvarnam]) == 'tuple':
            value=self.defaultdic[self.curgroup][curvarnam][0]
        else:
            value = self.defaultdic[self.curgroup][curvarnam]
        self.SetValueToGridCell(value, self.unsetcolor)

        mess='The parameter "'+curvarnam+'" was reset.'
        self.MessMethod(mess)

    def OnResetAllParams(self, event):
        """ Reset all parameters in this group to default values

        """
        self.changeddic[self.curgroup]={}
        self.SetDataToGridTable(self.curgroup)

        mess='All parameter values were reset.'
        self.MessMethod(mess)

    def OnSaveParameters(self,event):
        """ Event handler of the 'Save' and 'Save all' buttons

        """
        # check button label, 'Save' or 'Save all'
        obj=event.GetEventObject()
        label=obj.GetLabel()
        if label.lower() == 'save':
            grouplst=[self.curgroup]
        elif label.lower() == 'save all':
            grouplst=self.grouplst
        #
        title='OnSaveParameters'
        mess='Do you want to save the unchanged parameters\n'
        mess+=' as well as the modified ones?'
        dlg = wx.MessageDialog(None, mess, title,
                               style=wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP)
        if dlg.ShowModal() == wx.ID_YES:
            allparams=True
        else:
            allparams=False

        wcard='params (*.prm)|*.prm'
        filename = lib.GetFileName(None,wcard,rw='w',check=True)

        paramvaldic=self.ParamAndValueDic(grouplst,allparams=allparams)
        self.WriteParameterFile(filename,paramvaldic,messout=True)

    def ParamAndValueDic(self,grouplst,allparams=True):
        """ Return dictionary of parameters and their values

        :param lst grouplst: list of parameter groups
        :return: paramvaldic(dic) - dictionary of parameters and values,
                                    {'group_name':{'pram_name' : value,...},...}
        """
        paramvaldic={}
        for grp in grouplst:
            if not grp in paramvaldic:
                paramvaldic[grp]={}
            for param in list(self.defaultdic[grp].keys()):
                if grp in self.changeddic and param in self.changeddic[grp]:
                    val=self.changeddic[grp][param]
                    paramvaldic[grp][param] = val
                else:
                    if lib.ObjectType(self.defaultdic[grp][param]) == 'tuple':
                        val=self.defaultdic[grp][param][0]
                    else:
                        val = self.defaultdic[grp][param]
                    if allparams:
                        paramvaldic[grp][param]=val
        return paramvaldic

    def OnReadParameterFile(self,event):
        """ read a xxx.prm file, see the 'OnSaveParamValues' method
        # set values in the file to parameters in the listctrl
        # open file
        # set values to params
        """
        paramfile=lib.GetFileName(None,'param(*.prm)|*.prm',rw='r',check=True)
        if paramfile == '':
            return
        grouplst,changeddic=self.ReadParameterFile(paramfile)
        others=[]
        iscurgroup=False
        only=True
        for grp in grouplst:
            if grp != self.curgroup:
                others.append(grp)
            else:
                iscurgroup=True
        if not iscurgroup or len(others) > 0:
            mess='Contains parameters for groups other than the current group.\n'
            mess+='Do you want to apply these(yes) or just the current group(no)?'
            dlg = wx.MessageDialog(None, mess, 'OnReadParameterFile',
                                   style=wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            if dlg.ShowModal() == wx.ID_YES:
                only=False
            else:
                only=True

        self.changeddic=self.CheckGroupParams(changeddic,curgrouponly=only)

        self.SetDataToGridTable(self.curgroup)

    def CheckGroupParams(self, changeddic,curgrouponly=False,messout=True):
        newchangeddic={}
        skipgrps=[]
        skipprms=[]
        for grp in list(changeddic.keys()):
            if not grp in self.defaultdic:
                if not grp in skipgrps: skipgrps.append(grp)
                continue
            if curgrouponly:
                if grp != self.curgroup:
                    if not grp in skipgrps: skipgrps.append(grp)
                    continue
            if not grp in newchangeddic:
                newchangeddic[grp]={}

            for prm in list(changeddic[grp].keys()):
                if not prm in list(self.defaultdic[grp].keys()):
                    if not [grp,prm] in skipprms:
                        skipprms.append([grp,prm])
                    continue
                newchangeddic[grp][prm]=changeddic[grp][prm]

        if messout:
            mess=''
            mess1=''
            if len(skipgrps) > 0:
                mess += 'Ignored groups:\n'
                for grp in skipgrps:
                    mess+='   '+grp+', '
            if len(mess) > 0:
                mess=mess[:-2]+'\n'
            if len(skipprms) > 0:
                mess1 += 'Ignored [group,param]:\n'
                for [grp,prm] in skipprms:
                    mess1 += '   ['+grp+','+prm+'], '
            if len(mess1) > 0:
                mess1 = mess1[:-2] + '\n'
            mess=mess+mess1
            if len(mess) > 0:
                wx.MessageBox(mess,'.ListParameter_Frm.CheckGroupParams')

        return newchangeddic

    def OnApply(self,event):
        try:
            self.retmethod(self.changeddic,'apply')
        except:
            mess='Error occured in return method='+str(self.retmethod)
            wx.MessagebBox(mess,'ListParamter_Pan.OnApply')

    def OnCancel(self,event):
        self.changeddic={}
        try:
            self.retmethod(self.changeddic,'cancel')
        except:
            mess='Error occured in return method='+str(self.retmethod)
            wx.MessagebBox(mess,'ListParamter_Pan.OnCancel')

    def OnSelectValue(self, value, menulabel):
        self.returnvalue = value
        self.openlistboxmenu = False
        if value == '<close>': return  # or value == '': return
        if value.upper() == 'NONE':
            self.SetDataToGridTable(self.curgroup)
            return
        curvarnam = self.grid.GetCellValue(self.selectedrow, 0)
        if len(curvarnam.strip()) <= 0: return
        #
        valuecolor = self.setcolor
        setvalue = True

        if self.returnvalue == 'color picker':
            color = lib.ChooseColorOnPalette(self.parent, True, -1)
            if color == '':
                value=self.defaultdic[self.curgroup][curvarnam]
                setvalue=False
            else:
                try:
                    value = [color[0] / 255, color[1] / 255, color[2] / 255]
                except:
                    pass
                if len(self.defaultdic[self.curgroup][curvarnam]) == 4:
                    value.append(1.0) # [r,g,b,a]

        if value == '': setvalue = False
        if not setvalue:
            if lib.ObjectType(self.defaultdic[self.curgroup][curvarnam]) == 'tuple':
                value = self.defaultdic[self.curgroup][curvarnam][0]
            else:
                value = self.defaultdic[self.curgroup][curvarnam]
            valuecolor = self.unsetcolor

        self.SetValueToGridCell(str(value), valuecolor)
        self.changeddic[self.curgroup][curvarnam]=value
        self.changed=True

    def OnGridCellChange(self, event):
        self.selectedrow = event.GetRow()
        self.selectedcol = event.GetCol()
        if self.selectedcol != 2: return

        curparam = self.grid.GetCellValue(self.selectedrow, 0)
        print('curparam=',curparam)

        value = self.grid.GetCellValue(self.selectedrow, self.selectedcol)
        print('0:value=', value)
        value = value.strip()

        #valobj=value
        ###valobj=lib.StringToVariableType(str(value))
        ###if valobj is None:
        ###    mess='Warning: Failed to judge the variable type'
        ###    wx.MessageBox(mess,'OnGridCellChange')
        vallst=self.defaultdic[self.curgroup][curparam]
        color = self.setcolor
        if lib.ObjectType(vallst) == 'list':
            ###strvallst=[str(x) for x in vallst]
            ###if not str(valobj) in strvallst:
            self.defaultdic[self.curgroup][curparam].append(value)
        self.changeddic[self.curgroup][curparam]=value

        self.grid.SetCellTextColour(self.selectedrow, self.selectedcol, color)
        self.changed = True

    def OpenListBoxMenu(self, menulst, retmethod):
        [x,y]=wx.GetMousePosition()
        winpos=[x+20,y]
        winheight=len(menulst)*self.fontheight+10
        if winheight > self.maxlistboxmenuheight:
            winheight=self.maxlistboxmenuheight
        winsize=[100,winheight]
        listboxmenu=ListBoxMenu_Frm(self,-1,winpos,winsize,retmethod,menulst)
        self.openlistboxmenu = True
        return listboxmenu

    def OnGridRightClick(self, event):
        if self.openlistboxmenu: return

        self.grid.SetGridCursor(self.selectedrow, self.selectedcol)
        self.grid.SetCellBackgroundColour(self.selectedrow, self.selectedcol, 'light blue')
        self.grid.SetReadOnly(self.selectedrow, self.selectedcol, isReadOnly=False)

        curvarnam = self.grid.GetCellValue(self.selectedrow, 0)
        curvarnam = curvarnam.strip()
        if len(curvarnam) <= 0: return

        if self.selectedcol == 2: # popup choose value menu
            curvallst = self.defaultdic[self.curgroup][curvarnam]
            if lib.ObjectType(curvallst) == 'tuple':
                vallst=[str(x) for x in curvallst]
                # open listbox menu items
                menulst = ['<close>']
                menulst = menulst + vallst
                menulabel = 'SelectValue'
                self.listboxmenu = self.OpenListBoxMenu(menulst,self.OnSelectValue)
            elif lib.ObjectType(curvallst) == 'list' and curvarnam.find('-color') >= 0:
                menulst = ['<close>','color picker']
                menulabel = 'SelectValue'
                self.listboxmenu = self.OpenListBoxMenu(menulst,self.OnSelectValue)

        elif self.selectedcol == 0: # show tip string
            if self.tipview:
                self.tipview.Destroy()
            try:
                string=self.tipsdic[self.curgroup][curvarnam]
            except:
                string='No description.'
            winpos=wx.GetMousePosition()
            winsize=[300,100]
            title='"'+curvarnam+'" tip string'
            self.tipview=TextViewer_Frm(self,winpos,winsize,title=title,text=string)

    def OnGridCellSelect(self, event):
        self.grid.SetCellBackgroundColour(self.selectedrow, self.selectedcol, 'white')
        self.selectedrow = event.GetRow()
        self.selectedcol = event.GetCol()
        self.grid.ClearSelection()

        self.grid.SetGridCursor(self.selectedrow, self.selectedcol)

        if self.openlistboxmenu:
            try:
                self.listboxmenu.Destroy()
                self.openlistboxmenu = False
            except:
                pass

    def SetValueToGridCell(self, value, color):
        self.grid.SetCellValue(self.selectedrow, 2, str(value))
        self.grid.SetCellTextColour(self.selectedrow, self.selectedcol, color)


    def SetDataToGridTable(self, curgroup):
        """

        :param str param: parameter name in the 'self.curgroup' group
        """
        if curgroup is None:
            return

        varlst = [] # self.gmsuser.varlstdic[name]

        try:
            self.curgrouptipdic = self.tipsdic[curgroup] #[param]
        except:
            self.curgrouptipdic={}
        #
        vardic=self.defaultdic[curgroup] # {param1:[val1,val2,..],...}
        varlst=list(vardic.keys()) # [param1,param2,...]
        varlst.sort()
        nrow = len(varlst)
        vallst=[]
        textcolorlst=[]
        for param in varlst:
            if curgroup in self.changeddic and param in self.changeddic[curgroup]:
                vallst.append(self.changeddic[curgroup][param])
                textcolorlst.append(self.setcolor)
            else:
                if lib.ObjectType(vardic[param]) == 'tuple':
                    vallst.append(vardic[param][0])
                else:
                    vallst.append(vardic[param])
                textcolorlst.append(self.unsetcolor)

        self.grid.ClearGrid()
        irow = -1
        for i in range(nrow):
            items = []
            var = varlst[i].strip()
            irow += 1
            items.append(var)
            items.append('=')
            items.append(vallst[i])

            for j in range(3):
                self.grid.SetCellValue(irow, j, str(items[j]))
            self.grid.SetCellTextColour(irow, 2, textcolorlst[i])
            self.grid.Refresh()

    def OnRemoveGroup(self, event):
        if len(self.grouplst) <= 1:
            mess = 'Can not remove the last name group!'
            lib.MessageBoxOK(mess, 'ListParamterPanel:RemoveGroup')
            return

        delgroup=self.curgroup
        del self.defaultdic[self.curgroup]
        self.grouplst.remove(self.curgroup)
        self.curgroup=self.grouplst[0]
        self.OnResize(1)

        mess='The group"'+delgroup+'" has been deleted.'
        self.MessMethod(mess)

    def GetChangedDic(self):
        return self.changeddic

    def GetDefaultDic(self):
        return self.defaultdic

    def OnAddGroup(self, event):
        """ Add parameter group button

        :param event:
        :return:
        """
        # get filename, xxx.json
        fileext='.json'
        wcard="parameter file("+fileext+")|*"+fileext
        filename=lib.GetFileName(None,wcard,'r',True)
        if filename == '':
            return

        self.AddParameterGroups(filename)

    def AddParameterGroups(self,filename,checkdup=True,updateselbox=True):

        print('self.selectbox in AddParamterGroups=',self.selectbox)

        if not os.path.exists(filename):
            mess='The file does not exist.'
            wx.MessageBox(mess,'AddParameterGroups')
            return

        jsondic=rwfile.ReadJSON(filename)
        #
        grouplst,grouptiplst,defaultdic,tipsdic=self.MakeDefaultDicFromJsonDic(jsondic)
        if checkdup and self.grouplst is not None:
            grouplst,defaultdic,tipsdic=self.CheckDuplicateGroups(grouplst,defaultdic,tipsdic)
        changeddic=self.SetChangedDic(defaultdic)

        if len(self.grouplst) > 0:
            self.grouplst=self.grouplst+grouplst
            self.grouptiplst=self.grouptiplst+grouptiplst
            self.defaultdic.update(defaultdic)
            self.tipsdic.update(tipsdic)
            self.changeddic.update(changeddic)
        else:
            self.grouplst=grouplst
            self.grouptiplst = grouptiplst
            self.defaultdic=defaultdic
            self.tipsdic=tipsdic
            self.changeddic=changeddic
        # update ListBox
        self.OnResize(1)
        if updateselbox:
            self.selectbox.SetItems([])
            self.selectbox.SetItems(self.grouplst)
            if self.curgroup is not None:
                self.selectbox.SetStringSelection(self.curgroup)
        mess='Json file "'+filename+'" has applied to add groups.'
        self.MessMethod(mess)

    def CheckDuplicateGroups(self,grouplst,defaultdic,tipsdic):
        duplst=[]
        for grpname in grouplst:
            if grpname in self.grouplst:
                if not grpname in duplst:
                    duplst.append(grpname)
        if len(duplst) > 0:
            mess='There are duplicated group names,\n'
            mess+='   '+str(duplst)+'\n\n'
            mess+='Do you want to remove(yes) or accept(no) them?'
            dlg = wx.MessageDialog(None, mess, 'CheckDuplicateGroups',
                                   style=wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            rename=True
            if dlg.ShowModal() == wx.ID_YES:
                rename=False

            for grp in duplst:
                grouplst.remove(grp)
                newnam=grp+'.x'
                if rename:
                    grouplst.append(newnam)
                try:
                    defaultdic[newnam]=defaultdic[grp]
                    tipsdic[newnam]=tipsdic[grp]
                    del defaultdic[grp]
                    del tipsdic[grp]
                except:
                    pass

        return grouplst,defaultdic,tipsdic

    def MakeDefaultDicFromJsonDic(self,jsondic,sortgroup=True):
        grouplst= list(jsondic.keys())
        if sortgroup:
            grouplst.sort()
        mess=''
        defaultdic={}
        tipsdic={}
        grouptiplst=[]
        for grp in jsondic:
            defaultdic[grp]={}
            tipsdic[grp]={}
            if 'description' in jsondic[grp]:
                grouptiplst.append(jsondic[grp]['description'])
            else:
                grouptiplst.append('No description.')

            for param in jsondic[grp]:
                if param == 'description': continue
                defval=None
                vallst=None
                for kwd in jsondic[grp][param]:
                    val=jsondic[grp][param][kwd]
                    if kwd.lower() == 'default':
                        defval=val
                    elif kwd.lower() == 'description':
                        tipsdic[grp][param]=val
                    elif kwd.lower() == 'range':
                        # change list to tuple
                        vallst=tuple(val)
                if vallst is not None:
                    if defval is not None and defval in vallst:
                        vallst=list(vallst)
                        vallst.remove(defval)
                        vallst=[defval]+vallst
                        vallst=tuple(vallst)
                    defaultdic[grp][param] = vallst
                else:
                    if defval is not None:
                        defaultdic[grp][param]= defval
                    else:
                        if not gtip:
                            mess+='   Missing "default" or "range" for group:param "'
                            mess+= grp+':'+param+'"\n'

        if len(mess) > 0:
            mess='Error in json dictionary:\n'+mess
            wx.MessageBox(mess,'MakeDefaultDicFromJsonDic')

        return grouplst,grouptiplst,defaultdic,tipsdic

    def ReadParameterFile(self,filename,textdat=None):
        """ Read parameter file

        :param str filename: file name
        :param str textdat: Text data that takes precedence over files
        :return: grouplst(lst) - list of groups, ['group1','group2',...]
                 changeddic(dic) - dictonary of read paramter values,
                                   {'group1':{'param1':'value1',..},...}

        #the file format:
        #    # Parameter file # comment
        #    [paramset1]      # group name
        #    param1=value2    # param name=param value
        #    param2 = 0.9
        #    [paramset2]
        #    param3=5
        #    ...
        """
        if not os.path.exists(filename):
            mess='The file does not exist.'
            wx.MessageBox(mess,'rwfile.ReadParameterFile')
            return

        if textdat is None:
            with open(filename,'r') as f:
                textdat=f.read()
        textlst=textdat.split('\n')

        grouplst=[]
        changeddic={}
        gname=''
        for s in textlst:
            s=s.strip()
            if len(s) <= 0: continue
            if s[0] == '#': continue
            if s[0] != '[' and gname != '':
                var,val=lib.GetKeyAndValue(s, conv=True)
                changeddic[gname][var]=val
                continue
            if s[0] == '[': # group name
                nc=s.find(']')
                if nc < 0:
                    nc=20
                gname=s[1:nc].strip()
                if len(gname) > 0:
                    grouplst.append(gname)
                    changeddic[gname]={}
        mess='The paramter file "'+filename+'" has been read.'
        self.MessMethod(mess)

        return grouplst,changeddic

    def MessMethod(self,mess):
        if self.messmethod is not None:
            try:
                self.messmethod(mess)
            except:
                mess='Errors occured in the messmethod "'+str(self.messmethod)+'".'
                wx.MessageBox(mess,'ListParamter_Pan.MessMethod')
        else:
            try:
                print(mess)
            except:
                pass

    def WriteParameterFile(self,filename,paramvaldic=None,sortparams=True,messout=True):
        """ Write parameters to file

        :param str filename: file name
        :param dic paramvaldic: dictionary of parameters and their values,
                                {'group name':{'param_name':value,...},...}
        :param bool sortparams: True to sort paramters, False otherwise
        :param bool messout: True to show a message box, False otherwise

        the file format:
            # title comment
            [group name]
            param_name=value
            ...
        """
        if paramvaldic is None:
            mess='No parameters/values​ are given to write.'
            wx.MessageBox(mess,'rwfile.WriteParameterFile')
            return

        maxnam=0
        for grp in list(paramvaldic.keys()):
            paramlst=list(paramvaldic[grp].keys())
            for param in paramlst:
                if len(param) > maxnam:
                    maxnam=len(param)

        text ='# Parameter file created at '+lib.DateTimeText()+'\n'
        text+='\n'
        for grp in list(paramvaldic.keys()):
            paramlst=list(paramvaldic[grp].keys())
            if sortparams:
                paramlst.sort()
            text+='['+grp+']\n'
            for param in paramlst:
                value=paramvaldic[grp][param]
                text+=param + (maxnam-len(param)) * ' '+ ' = '+str(value)+'\n'
            text+='\n'

        with open(filename,'w') as f:
            f.write(text)

        if messout and self.messmethod is None:
                mess = 'The parameter file "' + filename + ' is created'
                wx.MessageBox(mess,'SaveParameters')
        if len(paramvaldic.keys()) == 1:
            mess='The "'+list(paramvaldic.keys())[0]+'" group was '
        else:
            mess='All groups were '
        mess+='save to "'+filename+'".'
        self.MessMethod(mess)

    def OnSelectGroup(self, event):
        if len(self.grouplst) <= 0:
            return

        curgroup = self.selectbox.GetStringSelection()
        if curgroup == "":
            curgroup=self.curgroup
        self.curgroup=curgroup
        self.SetDataToGridTable(curgroup)
        try:
            self.SetGroupNameOnListPanel(0, 5, curgroup,self.gridwidth)
            self.listpanel.Refresh()
        except:
            pass

    def OnGroupPanelRightClick(self, event):
        if self.tipview:
            self.tipview.Destroy()
        try:
            idx=self.grouplst.index(self.curgroup)
            string = self.grouptiplst[idx]
        except:
            string = 'No description.'
        winpos = wx.GetMousePosition()
        winsize = [300, 100]
        title = '"' + self.curgroup + '" tip string'
        self.tipview = TextViewer_Frm(self, winpos, winsize, title=title, text=string)
        # view=TipString(self,string,winpos=winpos,bgcolor='yellow')

    def OnClose(self, event):
        try:
            self.retmethod(self.changeddic)
        except:
            pass
        self.Destroy()

    def OnMove(self, event):
        pass

    def OnResize(self, event):
        savopenlistwin = self.openlistboxmenu
        self.panel.Destroy()
        if self.openlistboxmenu:
            self.listboxmenu.Destroy()
            self.openlistboxmenu = False
        self.SetMinSize(self.winsize)
        self.SetMaxSize([self.winsize[0], 2000])
        self.CreatePanel()

        if savopenlistwin:
            self.OnGridRightClick(1)


class Help_Button():
    """ Help button class

    Constructor;
        helpbtn=Help_Button(parent, winpos=[0,0], winsize=[20,22],
                     helpfile=None, tips='Help', bgcolor=[255,255,128],
                     viewerpos=[10,10],viewersize=[600,400])

    :param obj parent: a parent panel object
    :param lst winpos: position on the parent panel, defautl:[0,0]
    :param lst winsize: the size of the button. default:[20,22]
    :param str helpfile: a html- or a text-document file, default:None (open filer)
    :param str tips: a tips string
    :param lst bgcolor: the background color of the button, default:yellow
    :param lst viewerpos: the position of html viewer on the parent panel, default:[10,10]
    :param lst viewersize: the size of html viewer, defautl:[600,400]
    """
    def __init__(self, parent, winpos=[0,0], winsize=[20,22],
                 helpfile=None, tips='Help',bgcolor=[255,255,128],
                 viewerpos=[10,10],viewersize=[600,400],title='Help'):
        self.btnhlp = wx.Button(parent, -1, "?", pos=winpos, size=winsize)

        self.parent=parent
        self.htmlfile=None
        self.textfile=None
        if helpfile is not None:
            fileext=os.path.splitext(helpfile)[1]
            if fileext == '.html':
                self.htmlfile = helpfile
            elif fileext == '.txt':
                self.textfile=helpfile
        self.title=title
        self.viewerpos=viewerpos
        self.viewersize=viewersize

        self.btnhlp.Bind(wx.EVT_BUTTON, self.OnHelpButton)
        self.btnhlp.SetBackgroundColour(bgcolor)
        lib.SetTipString(self.btnhlp,tips)

    def OnHelpButton(self,event):
        title='Help_Button.OnHelpButton'
        if self.htmlfile is None and self.textfile is None:
            mess='help document file(a html or a text file) is not set.\n'
            mess+='do you want to open a help file?'
            dlg = wx.MessageDialog(None, mess, title,
                                   style=wx.YES_NO | wx.ICON_QUESTION | wx.STAY_ON_TOP)
            if dlg.ShowModal() == wx.ID_NO:
                return
            else:
                wcard='html, text(*.html,*.txt)|*.html;*.txt'
                helpfile=lib.GetFileName(None,wcard,rw='r',check=True)
                if helpfile == '': return

                ext=os.path.splitext(helpfile)[1]
                if   ext == '.html':
                    self.htmlfile=helpfile
                elif ext== '.txt':
                    self.textfile=helpfile

        if self.htmlfile is not None:
            if not os.path.exists(self.htmlfile):
                mess='the html file "'+self.htmlfile+'" does not exist.'
                wx.MessageBox(mess,title)
                return
            #
            helpwin = HtmlViewer_Frm(self.parent, winpos=self.viewerpos,
                                     winsize=self.viewersize,
                                     htmlfile=self.htmlfile,title=self.title)
        elif self.textfile is not None:
            if not os.path.exists(self.htmlfile):
                mess='the html file "'+self.htmlfile+'" does not exist.'
                wx.MessageBox(mess,title)
                return
            #
            helpwin = TextViewer_Frm(self.parent, winpos=self.viewerpos,
                                     winsize=self.viewersize,
                                     textfile=self.textfile,title=self.title)

    def SetHTMLFile(self,htmlfile):
        """ Set help document file, xxx.html.

        :param str htmlfile: html document file, xxx.html
        """
        self.htmlfile=htmlfile

    def SetTextFile(self,textfile):
        """ Set help document file, xxx.txt.

        :param str textfile: text document file, xxx.txt
        """
        self.textfile=textfile

    def SetButtonColor(self,bgcolor):
        self.btnhlp.SetBackgroundColour(bgcolor)

    def SetTipString(self,tips):
        lib.SetTipString(self.btnhlp, tips)

    def Close(self):
        self.btnhlp.Destroy()


#!/bin/sh
# -*- coding: utf-8

# Test ListParamter_Pan(wx.Panel) class in "subwin" module

import os
import wx
import sys
sys.path.insert(0,'..//src')

import fumodel
import subwin


def start():
    # parent 'Frame'
    winsize=[400,400]
    frm = wx.Frame(None, -1, title='Parent frame for "ColorButton_Pan"',
                   pos=[0, 0], size=winsize)
    statusbar=frm.CreateStatusBar()
    messmethod=statusbar.SetStatusText # messmethod(mess)
    frm.SetBackgroundColour('white')
    panel=wx.Panel(frm,-1)
    #
    itemlst=['H','C','N','O']
    colordic={}
    colordic['H']=[255,255,255]
    colordic['C']=[0.0,0.0,0.0]
    colordic['N']=[0.0,0.0,255]
    colordic['O']=[255,0.0,0.0]
    btnpan = subwin.ColorButton_Pan(panel,winpos=(20,20),
                winsize=(80,120),
                itemlst=itemlst,colordic=colordic,
                itemtitle='Element',adddelbutton=False,
                bgcolor='yellow',torgb255=False,vscroll=True,
                messmethod=messmethod)
    #
    colordic={}
    colordic['ALA']=[1.0,1.0,1.0]
    colordic['GLY']=[0.0,0.0,0.0]
    colordic['PHE']=[0.0,0.0,1.0]
    colordic['LYS']=[1.0,0.0,0.0]
    itemlst=list(colordic.keys())
    btnpan = subwin.ColorButton_Pan(panel,winpos=(150,20),
                winsize=(100,120),
                itemlst=itemlst,colordic=colordic,
                itemtitle=None, adddelbutton=True,
                closebtn=False,
                bgcolor='green',torgb255=True,vscroll=True)

    frm.Show()

#----------------------------------------
if __name__ == '__main__':
    app=wx.App(False)
    start()
    app.MainLoop()

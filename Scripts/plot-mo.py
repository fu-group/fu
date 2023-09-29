#!/bin/sh
# -*- coding: utf-8
#
#--------------------
# scripyt: plot-mo.py
# -------------------
# function: plot orbitals
# usage: This script is executed in PyShell.
#        >>> fum.ExecuteAddOnScript('plot-mo.py',False)
# note: plot orbitals in GAMESS output file
#
import cube
#import rwfile
global plotmo

mode = 2 # no menu mode
pos0 = 0
count=0
winlabel='PlotMO-1'
if count is not None: pos0 = 155 * count

mdlwinpos  = fum.mdlwin.GetPosition()
mdlwinsize = fum.mdlwin.GetClientSize()
winpos = [mdlwinpos[0]+mdlwinsize[0]+10,mdlwinpos[1]+20]
winpos = [winpos[0]+pos0,winpos[1]]
#if mode == 1: winsize[1] -= 25 # no menu in the case of mode=1
winsize=[180,450]
pltmo = cube.DrawCubeData_Frm(fum.mdlwin,winpos,winsize,fum,
                            fum,mode,winlabel=winlabel,
                            wincount=count) # mode=1
pltmo.Show()

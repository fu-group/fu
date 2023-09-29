#!/bin/sh
# -*- coding: utf-8 -*- 
#
#-----------
# Script: mutate-residue.py
# ----------
# function: mutate residues
# usage: This script is executed in fu-PyShell shell.
#        >>> fum.ExecuteAddOnScript('mutate-residue.py',False)
# change history
# Sep2015 - the first version
import build
# main program
#norun=False
mdlwinpos=fum.mdlwin.GetPosition()
mdlwinsize=fum.mdlwin.GetSize()
winpos=[mdlwinpos[0]+mdlwinsize[0],mdlwinpos[1]+50]
addhyd=build.AddHydrogen_Frm(fum.mdlwin,-1,fum,winpos=winpos)
#if norun: addhyd.Destroy()
#else: addhyd.Show()

#!/bin/sh
# -*- coding: utf-8
#
#-----------
# scripyt: plot-energy.py
# ----------
# function: plot orbital energy
# usage: This script is executed in PyCrust shell.
#        >>> fum.ExecuteAddOnScript('plot-energy.py',False)
# note: plot orbital energies in GAMESS output file
#
# ----------
# change history
# the first version for fu ver.0.5.2 22Apr2019
# -----------

import cube
#
global plote
plte = cube.PlotEnergy_Frm(fum.mdlwin,fum,mode=0,
         norbdat=1,orbtitle=None,erange=None)
plte.Show()

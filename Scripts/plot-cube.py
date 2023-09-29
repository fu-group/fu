#-----------
# scripyt: plot-mo.py
# ----------
# function: plot orbitals
# usage: This script is executed in PyShell.
#        >>> fum.ExecuteAddOnScript('plot-mo.py',False)
# note: plot orbitals in GAMESS output file
#
# ----------
# change history
# the first version for fu ver.0.5.2 22Apr2019
# -----------
import cube
#import rwfile
global plotcube

mode=0 # no menu mode
winlabel='PlotCube'
mdlwinpos=fum.mdlwin.GetPosition()
mdlwinsize=fum.mdlwin.GetClientSize()
winpos=[mdlwinpos[0]+mdlwinsize[0]+30,mdlwinpos[1]+50]
#if const.SYSTEM == const.MACOSX: winsize=[85,315]
if mode == 1: winsize[1] -= 25 # no menu in the case of mode=1
winsize=[180,360]
pltcube = cube.DrawCubeData_Frm(fum.mdlwin,winpos,winsize,fum,
                            fum.mdlwin,mode,winlabel=winlabel) # mode=1
pltcube.Show()

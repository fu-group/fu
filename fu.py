#!/bin/sh
# -*- coding: utf-8

Version="FU ver.0.5.2"
Copyright="Copyright (c) 2013-17, FU User Group. All rights reserved."
License="The BSD 2-Clause License" # http://opensource.org/licenses/BSD-2-Clause).
Contributors="FU User Group"
Acknowledgement="The development of this software is partially supported by CMSI (2013-14)"

import os
import wx
import sys

def start():
    app=wx.App(False)
    global fum # Create Model instance

    progdir=os.path.split(sys.argv[0])[0].strip()
    progdir=os.path.abspath(progdir)
    progsrc=os.path.join(progdir,'src')
    sys.path.insert(0,progsrc)
    import fumodel
    #
    parent=None; mode=0
    fum=fumodel.Model_Frm(parent,progdir,mode)
    parent=fum
    fum.OpenMdlWin(parent)
    #
    app.MainLoop()

#----------------------------------------
if __name__ == '__main__':
    start()

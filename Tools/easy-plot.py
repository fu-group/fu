#!/bin/sh
# -*- coding: utf-8

def EasyPlot():
    winpos=[-1,-1]; winsiz=[680,400]
    title='Easy Plot for Output'
    ctrlflag=fuctrl.CtrlFlag()
    eplwin=fupanel.ExecProg_Frm(fut,-1,None,winpos,winsiz,title)
    # remove several menu items
    eplwin.exmenu.Remove(3)
    eplwin.exmenu.Remove(4)
    menu=eplwin.exmenu.GetMenu(0)
    itemtxt=["Save log as","Output on display","Load output file","View output file"]
    for txt in itemtxt:
        item=eplwin.menuitemdic[txt]
        menu.DeleteItem(item)     
    items=menu.GetMenuItems()
    nsep=4; isep=0
    for item in items:
        if item.IsSeparator():
            menu.RemoveItem(item); isep += 1
            if isep == nsep: break
    #
    eplwin.Show()
#
epl=EasyPlot()


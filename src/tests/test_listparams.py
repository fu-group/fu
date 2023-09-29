#!/bin/sh
# -*- coding: utf-8

# Test ListParamter_Pan(wx.Panel) class in "subwin" module

import os
import wx
import sys
sys.path.insert(0,'..//src')

import fumodel
import subwin

def RetMethod(changeddic,info=''):
    """ take-away value from subwin.ListParameter_Pan()

    :param dic changeddic: changed value dictionary,
                 changeddic['paramset1']={}, no changed params in 'paramset1'
                 changeddic['paramset2']['param3']=value,
                                 the changed value of 'param3' in 'paramset2'
    :param str info: 'apply' or 'cancel'
    """
    print('info=',info)
    print('changeddic=',str(changeddic))


def start():
    grouplst=['paramset1','paramset2']
    grouptiplst=['parameter set1','parameter set2']
    defaultdic={}
    defaultdic['paramset1']={}
    defaultdic['paramset2']={}
    # the default value is assumed to be the first value in the possible value list
    defaultdic['paramset1']['param1']=('value1','value2','value3')
    defaultdic['paramset1']['param2']=(True,False)
    defaultdic['paramset1']['param3']=(0.1,0.2,0.3)
    defaultdic['paramset1']['param4']=(0,1,2,3)

    defaultdic['paramset2']['param5-color'] = [0, 0, 1] # color [rgb]
    defaultdic['paramset2']['param6-color']=[0,0,1,1]   # color [rgba]
    defaultdic['paramset2']['param7'] = ('red', 'green', 'blue')
    defaultdic['paramset2']['param8'] = ([1, 0, 0],[0,1,0],[0,0,1])

    tipsdic={}
    tipsdic['paramset1']={}
    tipsdic['paramset2']={}
    tipsdic['paramset1']['param1']='this is a string variable'
    tipsdic['paramset1']['param2']='this is a bool variable'
    tipsdic['paramset1']['param3']='this is a floating number variable'
    tipsdic['paramset1']['param4'] = 'this is an integer variable'
    tipsdic['paramset2']['param5-color']='this is a color list variable'
    tipsdic['paramset2']['param6'] = 'this is a string or color name vafriable'
    tipsdic['paramset2']['param7'] = 'this is a list or color variable'
    retmethod=RetMethod
    winsize=[400, 300]
    # Example of jsonfile contents(remove the "#" at the beginning of each line)
    # a "range" list is programmatically converted to a tuple after loading
    #{
    #    "group1": {
    #        "param1": {
    #            "description": "param1 integer value",
    #            "default": 1
    #         },
    #        "param2": {
    #            "description": "param2 integter variable",
    #            "range": [1, 2, 3, 4, 5],
    #            "default": 5
    #         }
    #    },
    #    "group2": {
    #        "param3": {
    #           "description": "param3 string variable",
    #            "range": ["opt1", "opt2", "opt3"],
    #            "default": "opt2"
    #         },
    #        "param4-color": {
    #           "description": "param4-color color variable",
    #           "default": [1.0,1.0,1.0,1.0]
    #         },
    #        "param5": {
    #           "description": "param5 list variable",
    #         "range" : [[1.0,1.0,1.0], [0.0,0.0,0.0]],
    #         "default": [1.0,1.0,1.0]
    #         }
    #    }
    #}
    helpfile = 'C://FUDATASET-0.5.3//FUdocs//SubWinTools//html//SubWinTools.html'
    jsonfile='c://ATEST//defparam.json'
    #paramlst=[grouplst,grouptiplst,defaultdic,tipsdic]
    paramlst = [grouplst, [], defaultdic, tipsdic]
    # parent 'Frame'
    frm = wx.Frame(None, -1, title='Parent frame for "ListParameters_Pan"',
                   pos=[0, 0], size=winsize)
    statusbar=frm.CreateStatusBar()
    messmethod=statusbar.SetStatusText # messmethod(mess)
    #
    lstpan = subwin.ListParameter_Pan(frm, winpos=[0, 0], winsize=winsize,
                        paramlst=paramlst,jsonparamfile=None,
                        curgroup=None,applycancelbutton=True,
                        addremovebutton=True,
                        retmethod=retmethod,messmethod=messmethod,
                        helpfile=helpfile)

    frm.Show()

#----------------------------------------
if __name__ == '__main__':
    app=wx.App(False)
    start()
    app.MainLoop()

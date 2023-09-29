#!/bin/sh
# -*- coding: utf-8
#
#-----------
# scripyt: out2orbfile.py
# ----------
# function: convert and merge GAMESS output files into an .orb file
# usage: This script is executed in PyShell.
#        > python out2orbfile.py [--inp outfile_list] [--out orbfile]
# note: GAMESS output files should include 'basis set' and 'MO' data
#
# ----------
# change history
# the first version for fu ver.0.5.2, 22Apr2019
# -----------

import sys
import os
import argparse
import wx
import numpy

sys.path.insert(0,'../')
import fumodel
import lib
import cube
import rwfile
import const


def ArgParse():
    parser = argparse.ArgumentParser()
    mess ='[filename1,filename2,...], GAMESS output files(.out or .log)'
    mess+=' in parentheses'
    parser.add_argument('-i', '--inp',help=mess)
    parser.add_argument('-o', '--out', help='filename, output "orb" file name(.orb)') #,action='store_true')
    args = parser.parse_args()
    return args.inp,args.out

def GetGMSOutFiles():
    mess='Input GMS output files, like "[gmsout1,gmsout2,..]"(without ").\n'
    mess+='Null input open filer'
    gmsfiles=lib.GetStringsFromUser(mess) 
    if len(gmsfiles) <= 0:  
        wcard="GAMESS output(*.out,*.log)|*.out;*.log|all(*.*)|*.*"
        filelst=lib.GetFileNames(None,wcard=wcard,rw='r')
        if len(filelst) > 0:
            gmsfiles='['
            for file in filelst: gmsfiles+=file+','
            gmsfiles=gmsfiles[:-1]+']'   
        else: gmsfiles=None
    return gmsfiles

def GetOrbFileName():
        mess='Input file name of orbfile(.orb)\n'
        mess+='Null input open filer'
        orbfile=lib.GetStringsFromUser(mess)
        if len(orbfile) <= 0:  
            wcard="orbfile(*.orb)|*.orb"
            orbfile=lib.GetFileName(wcard=wcard,rw='r',check=True)
            if len(orbfile) <= 0: orbfile=None
        return orbfile

def WriteORBFile(filename,ngrp,imollst,titlelst,atomcclst,noccalst,noccblst,
                 nbaslst,basdiclst,eiglstlst,symlstlst,moslstlst,
                 perRow=5,eigau=True):
    """ write orbital data in the 'orb' format. this file(.orb) is used to draw
        MOs in the 'DrawCubeData_Frm' class
    :param str filename: file name
    :param str datnam: data name
    :param lst grplst: list og group names
    :param dic grpobjdic: dictionary of group data, {datgrp:grpobj,...
                          datgrp=datnam + ':' + grplst[i]
                          grpobj={'name':group name, 'atomcc':atom ccordinates,
                                  'basdic':basdic,'eiglst':eigenvalues,
                                  'symlst':orbital symmetry list,
                                  'molst':MO coefficient 2D list, [bas][orb]}
                          basdic={'nshell':nshell,
                                  'noccs':[nocca,noccb],
                                  'shltyp':list of shell type,1(S),3(P),4(L),6(D)
                                  'shlcntr':list of shell center,
                                  'shlgau':list of gaussians belonging to the shell,
                                  'ex':list of gaussian exponents,
                                  'cs':list of s contraction coefficients,
                                  'cp':list of p contraction coefficients,
                                  'cd':list of d contraction coefficients,
                                  'cf':list of f contraction coefficients(not used)}
    For the file format, see the 'ch3oh-dimer.orb' file in
        the 'FUDATASET/FUdocs/file-format/ directry
    """
    nl = '\n'; blk6 = 6 * ' '
    ff18='%18.10f'; ff4='%4.1f'; ff11 = '%11.4f'; ff10 = '%10.6f'
    fi4 = '%4d'; fi3='%03d'
    def WriteValues(vallst,form,efc=1.0,strdat=False,space=0):
        nval = len(vallst)
        count = 0
        mess = ''
        text = ''
        line = 0
        for i in range(nval):
            count += 1
            if strdat: text += form[0] * ' ' + vallst[i] + form[1] * ' '
            else: text += form % (efc * vallst[i])
            if count == perRow:
                line += 1
                if line > 1 and space != 0:  mess += space * ' '
                mess += text + nl
                text = ''
                count = 0
        if count > 0:
            line += 1
            if line > 1 and space != 0:  mess += space * ' '
            mess += text + nl
        return mess

    def AppendNumbers(intlst):
        text = ''
        ndat = len(intlst)
        for i in range(ndat):
            text += str(intlst[i]) +', '
        return text[:-2]

    def ShellDataString(atmlab,shlcntr,shltyp,shlgau,
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

    mess  = '# Orbital file(.orb) created by FU. ' + lib.DateTimeText() + nl
    mess += '# $ should be at the first column' + nl
    mess += '# All keywords are case sensitive!' + nl + nl

    efc = 1.0
    if eigau: efc = 1.0 / 27.2113845
    #ngrp = len(grplst)
    for ig in range(ngrp):
        #datgrp = datnam + ':' + grplst[ig]
        #grpobj = grpobjdic[datgrp]
        
        mess += '$MOLECULES ' +str(imollst[ig]+1) + nl
        mess += nl
        #
        #nc = grpnamlst[ig].find(':')
        #title = grpnamlst[ig][:nc]
        title = titlelst[ig]
        mess += 'TITLE         = ' + title + nl + nl
        atomcc = atomcclst[ig]
        natm = len(atomcc)
        mess += 'NATOMS        = ' + str(natm) + nl
        #nshell = len(grpobj.basdic['shltyp'])
        nshell = len(basdiclst[ig]['shltyp'])
        mess += 'NSHELLS       = '
        mess += str(nshell) + nl
        mess += 'NBASIS        = '
        #mess += str(grpobj.nbasis) + nl
        mess += str(nbaslst[ig]) + nl
        mess += 'NOCCA         = '
        mess +=  str(noccalst[ig]) + nl
        mess += 'NOCCB         = '
        mess +=  str(noccblst[ig]) + nl + nl
        # atomic coordinates
        mess += '$COORDINATES BOHR' + nl
        atmlab = []
        for i in range(natm):
            an = atomcc[i][0]
            elm = const.ElmSbl[an]
            label = elm + (fi3 % (i+1))
            atmlab.append(label)
            mess += label + blk6
            mess += ff4 % float(an)
            mess += ff18 % atomcc[i][1]
            mess += ff18 % atomcc[i][2]
            mess += ff18 % atomcc[i][3] + nl
        mess += '$END' + nl + nl
        # Shell
        basdic = basdiclst[ig]
        shltyp  = basdic['shltyp']
        shlcntr = basdic['shlcntr']
        shlgau  = basdic['shlgau']
        ex = basdic['ex']
        cs = basdic['cs']
        cp = basdic['cp']
        cd = basdic['cd']
        cf = basdic['cf']
        mess += '$SHELLS' + nl
        mess += ShellDataString(atmlab,shlcntr,shltyp,shlgau,
                    ex,cs,cp,cd,cf)
        mess += '$END' + nl + nl
        # orbital energy
        mess += '$ENERGY (EV)' + nl
        mess += WriteValues(eiglstlst[ig],ff11,efc=efc)
        mess += '$END' + nl + nl
        # symmetry
        mess += '$SYMMETRY' + nl
        mess += WriteValues(symlstlst[ig],[4,5],strdat=True)
        mess += '$END' + nl + nl
        # MO coefficients
        norb = len(moslstlst[ig])
        mess += '$ORBITALS' + nl
        moslst = numpy.transpose(moslstlst)
        for j in range(norb):
            text = WriteValues(moslst[j],ff10,space=4)
            mess += fi4 % (j+1) + text
        mess += '$END' + nl + nl
    # write to file
    if filename is None: return mess
    else:    
        f = open(filename,'w')
        f.write(mess)
        f.close()

def MakeOrbObj(nocc,atomcc,eiglst,symlst,moslst,basdic):
    """  useing cube.GridMO object """
    toev = 27.2113845
    orbobj = cube.GridMO(None)
    orbobj.noccs    = nocc[:] # [nocca,noccb]
    orbobj.homo     = nocc[0] - 1
    orbobj.lumo     = nocc[0]
    orbobj.natoms   = len(atomcc) # natoms
    orbobj.nbasis   = len(eiglst) # nbasis
    orbobj.atomcc   = atomcc[:]
    #####orbobj.basoptlst= basoptlst
    #orbobj.coorddic = retcoord
    eiglst = [x * toev for x in eiglst]
    orbobj.eiglst   = eiglst[:]
    orbobj.symlst   = symlst[:]
    orbobj.moslst   = moslst[:]
    orbobj.basdic   = basdic
    #size0 = self.model.setctrl.GetParam('cube-mo-grid-size')
    #orbobj.SetSize0(size0)
    #morange = self.model.setctrl.GetParam('cube-mo-range') # #occ-#vac
    #gridmargin = self.model.setctrl.GetParam('cube-mo-grid-margin')
    #orbobj.gridmargin = gridmargin
    #minmo = orbobj.homo - morange[0] + 1
    #if minmo < 0: minmo = 0
    #maxmo = orbobj.lumo + morange[1] - 1
    #nmos = len(orbobj.eiglst)
    #if maxmo > nmos: maxmo = nmos - 1
    #orbobj.morange  = [minmo,maxmo] # homo -10, lumo + 8
    #morange1 = [minmo+1,maxmo+1]

    return orbobj


def ReadGamessOutput(gmsfile):
    grpdic={}
    base,ext  = os.path.splitext(os.path.split(gmsfile)[1])    
    natoms,nbasis,atomcc,noccs,eiglst,symlst,moslst,basdic,basoptlst = \
              rwfile.ReadMOsInGMSOutput(gmsfile)
    if natoms < 0: return
    #if not self.CheckBasis(nbasis,basdic['shltyp']):
    #    return
    #ngrps = 1
    #grpname = base
    """
    natomslst = [natoms]; nbasislst = [nbasis]; noccslst  = [noccs]
    atomcclst = [atomcc]; symlstlst = [symlst]; eiglstlst = [eiglst]
    moslstlst = [moslst]; basdiclst = [basdic]
    """
    #orbobj=MakeOrbObj(noccs,atomcc,eiglst,symlst,moslst,basdic)

    
    return natoms,nbasis,atomcc,noccs,eiglst,symlst,moslst,basdic,basoptlst

def start():
    """
    usage: > python out2orbfile.py [--inp outfile_list] [--out orbfile]
    
    """
    gmsfiles,orbfile=ArgParse()
    if gmsfiles is None:
        gmsfiles=GetGMSOutFiles()
        if gmsfiles is None: sys.exit()
    if out is None:
        orbfile=GetOrbFileName()
        if orbfile is None: sys.exit()
    # convert string data to list object
    gmsfiles=lib.StringToList(gmsfiles)
    gmsfiles=[lib.RemoveQuots(x) for x in gmsfiles]        
    #
    gmslst=[]
    orbtext=''
    count=-1
    toev = 27.2113845
    for file in gmsfiles:
        outtext=''
        count+=1
        title,ext  = os.path.splitext(os.path.split(file)[1])    
        natoms,nbasis,atomcc,noccs,eiglst,symlst,moslst,basdic,basoptlst=\
                                               ReadGamessOutput(file)
        # convert unit to eV
        eiglst=[x*toev for x in eiglst]
        if natoms <= 0:
            pass
            #outtext+='\n# ReadGamessOutput: natoms is 0 in gmsfile='+file+'\n\n'
        else:
            ngrp=1
            outtext+=WriteORBFile(None,ngrp,[count],[title],[atomcc],[noccs[0]],
                                         [noccs[1]],[nbasis],[basdic],[eiglst],
                                         [symlst],[moslst],
                                         perRow=5,eigau=True)
        if len(outtext) > 0:
            orbtext+=outtext
            gmslst.append(file)
    #
    if len(orbtext) >= 0:
        f = open(orbfile,'w')
        f.write(orbtext)
        f.close()
    else:
        wx.MessageBox('orbtext is empty.')
        sys.exit()
    #
    print(('input GAMESS output files=',gmsfiles))
    if len(gmslst) > 0: 
        print(('converted GAMESS output files=',gmslst))
        print(('created orbfile=',orbfile))
    else: 
        print('Failed to convert to "orb" file')
        
if __name__ == "__main__":
    # usage: > python out2orbfile.py[--inp outfile_list] [--out orbfile]
    inp,out=ArgParse()
    if not inp or not out: app=wx.App(False)
    start()
    if not inp or not out: app.MainLoop()
    
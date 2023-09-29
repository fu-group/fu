#!/bin/sh
# -*- coding: utf-8 -*- 
#
#-----------
# Script: ob-minimize.py
# ----------
# function: minimize using openbabel tools
# usage: This script is executed in PyCrust shell.
#        >>> fum.fum.ExecuteAddOnScript('ob_minimize.py',False)
# ----------

import openbabel, pybel
import sys
sys.path.insert(0,'..//')
import const
import rwfile
import lib

""" execute 'obabel' in command shell
cmd='obabel e://TEST//fk506.mol -O e://TEST//obabel-opt.mol --minimize --steps 500 --sd'
retcod=subprocess.call(cmd,shell=True)


--log        output a log of the minimization process (default= no log)
--crit <converge>     set convergence criteria (default=1e-6)
--sd         use steepest descent algorithm (default = conjugate gradient)
--newton     use Newton2Num linesearch (default = Simple)
--ff <forcefield-id>       select a forcefield (default = Ghemical)
--steps <number>    specify the maximum number of steps (default = 2500)
--cut        use cut-off (default = don't use cut-off)
--rvdw <cutoff>     specify the VDW cut-off distance (default = 6.0)
--rele <cutoff>     specify the Electrostatic cut-off distance (default = 10.0)
--freq <steps>     specify the frequency to update the non-bonded pairs (default 

def run(cmd, logfile):
    p = subprocess.Popen(cmd, shell=True, universal_newlines=True, stdout=logfile)
    ret_code = p.wait()
    logfile.flush()
    return ret_code

"""
def XXRunOBabel():
    cmd='obabel e://TEST//fk506.mol -O e://TEST//obabel-opt.mol --minimize --steps 500 --sd --log'
    info = subprocess.STARTUPINFO()
    info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = subprocess.SW_HIDE
    #    proc = subprocess.Popen(..., startupinfo=info)
    process=subprocess.Popen(cmd,bufsize=-1,
               stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
               stdin=subprocess.PIPE,startupinfo=info)
    return process

def XXOutput(process,logfile):    
    # dispaly output text
    text=''
    #process.wait()
    
    while True:
        line=process.stdout.readline()
        if not line: break
        text=text+line
    f=open(logfile,"w")
    f.write(text)
        ###wx.Yield()
    f.close()
"""
import subprocess
logfile='e://TEST//obabel-opt.log'
process=RunOBabel()
Output(process,logfile)


"""

def UpdateFUMolCoords(fumol,atomcc,conect=None):
    natm = len(atomcc)
    if len(fumol.atm) != natm:
        print(('The number of atoms in fumol object ', len(fumol.atm)))
        print(('   is not equal to that of AtomCC',natm))
        print('   Unable to update coordinates!')
        return
    for i in range(natm):
        fumol.atm[i].cc  = atomcc[i][1:]
        fumol.atm[i].elm = atomcc[i][0]
        if conect is not None: fumol.conect = conect           
    return fumol
    
def GetOBAtomCC(obmol):
    natm = obmol.OBMol.NumAtoms()
    atomcc = []
    for i in range(natm):
        Atom = obmol.OBMol.GetAtom(i+1)
        an = Atom.GetAtomicNum()
        elm = const.ElmSbl[an]
        x = Atom.GetX()
        y = Atom.GetY()
        z = Atom.GetZ()
        atomcc.append([elm,x,y,z])
    return atomcc

def GetFUAtomCC(fumol):
    natm = len(fumol.atm)
    atomcc = []
    for atom in fumol.atm:
        atomcc.append([atom.elm,atom.cc[0],atom.cc[1],atom.cc[2]])
    return atomcc

def FUToOBMol(fumol):
    natm = len(fumol.atm)
    print(('fumodel. natm=',natm))
    #for atom in fumol.atm:
    #    print atom.seqnmb,atom.cc
    """    
    obmol = openbabel.OBMol()
    print 'Should print 0 (atoms)'
    print obmol.NumAtoms()
    obconv = OBConversion()
    obconv.SetInFromat('sdf')
    obconv.ReadFile(obmol)
    """ 
    name = fumol.name
    atomcc = GetFUAtomCC(fumol)
    conlst = []
    typlst = []
    for atom in fumol.atm:
        conlst.append(atom.conect)
        typlst.append(atom.bndmulti)

    sdstring = lib.AtomCCToSDFText(atomcc,conlst,typlst,name=name)
    obmol = pybel.readstring("sdf",sdstring)
    return obmol

""" pybel function """
def make3D(obmol,forcefield='UFF',steps=500,crit=0.0001):
    forcefield = forcefield.lower()
    openbabel.OBBuilderBuild(obmol)
    obmol.AddHydrogens()
    ff = openbabel.OBForceField.FindForceField(forcefield)
    
    success = ff.Setup(obmol)
    if not success:
        print(('Failed to assign forcefield = ',forcefield))
        return
    print(('retcod from ',forcefield))
    ff.SteepestDescent(steps,crit)
    ff.GetCoordinates(molobj)
    print((ff.Energy()))
    return molobj

""" pybel function """
def localopt(molobj=None,forcefield='UFF',steps=500,crit=0.0001):
    forcefield = forcefield.lower()
    
    print(('forcefield',forcefield))
    
    ff = openbabel.OBForceField.FindForceField(forcefield)
    success = ff.Setup(molobj.OBMol)
    
    print(('success',success))
    
    if not success:
        return
    #print 'localopt: retcod from ',forcefield,success
    ff.SteepestDescent(steps,crit)
    ff.GetCoordinates(molobj.OBMol)
    ffenergy = ff.Energy()
    #print ff.Energy()
    return molobj
    
fumol = fum.mol
print(('mol.name',fumol.name))

obmol = FUToOBMol(fumol)
#print 'obmol after FUToOBMol',obmol
obmol = localopt(molobj=obmol,forcefield='uff',steps=500,crit=0.1)
#print 'obmol after localopt',obmol
atomcc = GetOBAtomCC(obmol)

fum.mol = UpdateFUMolCoords(fumol,atomcc,conect=None)



fum.DrawMol(True)



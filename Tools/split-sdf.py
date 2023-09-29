#!/bin/sh
# -*- coding: utf-8
#
import re
import sys
import os
#from view import MolChoice

"""
if (len(sys.argv) != 2):
    print 'Usage: # python %s chemblsdf' % sys.argv[0]
    quit()

sdffile = sys.argv[1]
"""
sdffile='f://ChEMBL//chembl_19.sdf'
fi = open(sdffile, 'r')
savedir='f://ChEMBL//sdf-files'
mol = []; i=0; maxdat=10
while i <= maxdat:
    line = fi.readline()
    if not line:
        break
    if line[:4] == "$$$$":
        i += 1
        mol.append(line)
        title = mol[0][:-1]+'.sdf'
        filename=os.path.join(savedir,title)
        fo = open(filename, 'w')
        for m in mol:
            fo.write(m)
        fo.close()
        mol = []
    else:
        mol.append(line)
fi.close()

#print mol


#!/bin/sh
# -*- coding: utf-8

"""
Should run in FU Pyshell !
"""

import rwfile


# Open file = E://Dawson//Kitaura//G2-complex//AFG2-his88-2ss-optimized-complex//
# mol2file//AFG2_beta-abiopt-best_pose.mol2
# resnamdat
resatmdat=fum.ListResidueAtoms()
resnamlst=resatmdat[0]
resatmlst=resatmdat[1]


fmoout='e:/Dawson/Kitaura/B1-complex/AFB1-his66-2ss-optimized-complex/fmo-calc/AFB1_beta-abiopt-main_pose-fmo.out'
err,version,mulchg=rwfile.ReadFMOMulliken(fmoout)

#mulchg[7314]=[7315, 97, 29.0, 0.012792, 0.073466]
tchg=0.0
nres=len(resnamlst)
reschglst=nres*[0]
for i in range(len(resnamlst)):
    resnam=resnamlst[i]
    for j in resatmlst[i]:
        reschglst[i]+=mulchg[j][4]
        tchg+=mulchg[j][4]
    if len(resatmlst[i]) == 1: resnamlst[i]+='-atom:'+str(resatmlst[i][0]+1)
print ('Residue charge: rennum,resnam,chg')
for i in range(len(resnamlst)):
    resnam=resnamlst[i]
    try: print((i, resnam, reschglst[i]))
    except:
        print(('Error resnam',resnam))

print(('Total charge=',tchg))


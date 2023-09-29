#!/bin/sh
# -*- coding: utf-8
import const

inpfile='e://ATEST//tmp.xyz'
outfile='e://ATEST//tmpconv.xyz'

blk = '   '
fi4 = '%4d'
ff4='%4.0f'
ff12 = '%12.8f'
conv=1.0 # 0.529917724

f=open(inpfile,'r')
textlst=f.readlines()
f.close()

natm=0
text='coord from gamess\n'
for s in textlst:
    s=s.strip()
    if len(s) <= 0: continue
    items=s.split()
    print(('items=',items))
    an = int(float(items[1]) + 0.1)
    elm=const.ElmSbl[an]

    #elm=fi4 % an
    x = float(items[2]) * conv
    y = float(items[3]) * conv
    z = float(items[4]) * conv
    natm+=1
    # Gamess input format
    #text+=blk+items[0]+blk+(fi4 % an)+blk+(ff12 % x)+blk+(ff12 % y)+blk+(ff12 % z) +'\n'
    # xyz format
    text+=blk+elm+blk+(ff12 % x)+blk+(ff12 % y)+blk+(ff12 % z) +'\n'

text=(fi4 % natm)+'\n'+text

f=open(outfile,'w')
f.write(text)
f.close()

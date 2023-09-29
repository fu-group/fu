# test-readparamterfile
# usage: exce python27 in this directory.
# $ python
# >>> execfile(test-readparameterfile.py)
#
# the result will be,  
# ('paramdic=', "{'mol-model': 0, 'element-color': {'C': [0.498039215686,
# 0.498039215686, 0.498039215686, 1.0], 'CL': [0.0, 1.0, 1.0, 1.0]}, 'aa-
# residue-color': {'GLY': [1.0, 0.0, 0.0, 1.0], 'ILE': [0.0, 0.0, 1.0, 1.0],
# 'GLN': [1.0, 0.658823529412, 1.0, 1.0]}, 'aa-tube-radius': 0.2, 'hydrogen-
# bond-color': [0.0, 1.0, 1.0, 1.0]}")

import sys
sys.path.insert(0,'../')

import fumodel
import rwfile

paramfile='./data/readparameterfile.prm'
paramdic=rwfile.ReadParameterFile(paramfile)
print('paramdic=',str(paramdic))

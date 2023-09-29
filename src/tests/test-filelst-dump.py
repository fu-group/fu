# fu logging
# Created by kitaura at 2015/07/01 15:59:38
# result file=H://FUDATASET//Logs\fu-150701155938.result
#
#-#
# files used in this session
filename4="H://ps2//3arca//extract-res//3arca-UNL743L.pdb"
filename0="H://ps2//3arca//extract-res//3arca-UNL722D.pdb"
filename1="H://ps2//3arca//extract-res//3arca-UNL723D.pdb"
filename2="H://ps2//3arca//extract-res//3arca-UNL732I.pdb"
filename3="H://ps2//3arca//extract-res//3arca-UNL733I.pdb"
filenamelst=[filename0,filename1,filename2,filename3,filename4]
#
fum.HideToolsWin()
for filename in filenamelst:
    fum.ReadFiles(filename,True)
    fum.ChangeDrawModel(2)
    fum.DumpDrawItems(drwfile='')

#-#
# remove all moledcules
fum.RemoveMol(True)

# fu logging
# Created by kitaura at 2015/07/01 15:59:38
# result file=H://FUDATASET//Logs\fu-150701155938.result
#
# files used in this session
filename4="H://ps2//3arca//extract-res//3arca-UNL743L.pdb"
filename0="H://ps2//3arca//extract-res//3arca-UNL722D.pdb"
filename1="H://ps2//3arca//extract-res//3arca-UNL723D.pdb"
filename2="H://ps2//3arca//extract-res//3arca-UNL732I.pdb"
filename3="H://ps2//3arca//extract-res//3arca-UNL733I.pdb"
filenamelst=[filename0,filename1,filename2,filename3,filename4]
#
fum.HideToolsWin()

for filename in filenamelst:
    fum.ReadFiles(filename,True)
    #drwfile=filename.replace('.pdb','.dwrpic')
    fum.RestoreDrawItems(drwfile='') #drwfile)

fum.SaveLog(False)
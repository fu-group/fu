#----- tools tests ---- by kk, 26Jun2015
# This script is created based-on logging files (.logging)

def AddH():
    nmol=fum.molctrl.GetNumberOfMols()
    for i in range(nmol):
        mol=fum.molctrl.GetMol(i)
        fum.SwitchMol(i,True,True)
        fum.AddHydrogenUseBondLength()
        if fum.mol.name=='3arca-UNL763A.pdb':
            fum.SelectAtmNam(' C5 ',True)
            fum.AddGroup1H()
        if fum.mol.name=='3arca-UNL745C.pdb':
            fum.SelectAtmNam(' C5 ',True)
            fum.AddGroup1H()
        if fum.mol.name=='3arca-UNL723D.pdb':
            fum.SelectAtmNam(' C5 ',True)
            fum.AddGroup1H()

#2 'resnam"='UNL'
fut.extractRes(inp='h://ps2//3arca//3arca.pdb',outdir='h://ps2//3arca//extract-res',resnames='UNL',onefile=False,rres='0.0',renv='0.0',verbose=False)
fut.viewClose()
fut.view(-1,addbonds=True)
# method
AddH()
# save all data as pdb file
fum.WriteAllAsPDBFiles()


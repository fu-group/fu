# -*- coding: utf-8

def convert_atmnam():
    # arguments: jobopt=1(old to new), 2:(new to old)
    # ipdb='file name'
    # program name
    prgnam='convert_atmnam'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        jobopt=futoolslib.GetSysArgs('jobopt')
        if not jobopt:
            # job option
            prmpt='convert  1:old to new, 2:new to old.'
            jobopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        #
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read PDB file name
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file(.pdb)',True)
        futoolslib.INPUTPDBFILE=pdbfile            
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        # read pdb file
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(pdbfile)
        #
        if jobopt == 1: tonew=True
        else: tonew=False
        ncnv,pdbatm=futoolslib.ConvertPDBAtmNam(pdbatm,tonew)
        text=['old to new','new to old']
        mess1='converted pdb atom name from '+text[jobopt-1]
        mess2='number of converted atoms='+str(ncnv)
        print(mess1); print(mess2)
        print((pdbfile+' was saved.'))
        if ncnv > 0:
            # save file
            text=['old to new','new to old']
            mess1='converted pdb atom name from '+text[jobopt-1]
            mess2='number of converted atoms='+str(ncnv)
            comment='REMARK '+mess1+' by "convert_atom" tool.\n' 
            comment=comment+'REMARK '+mess2
            fumole.fuMole.WritePDBAtom(pdbfile,pdbatm,pdbcon,comment)
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)
convert_atmnam()

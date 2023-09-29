#!/bin/sh
# -*- coding: utf-8

def change_atom_order_in_wat():
    # arguments:  ipdb,opdb, ter=1 or 2(del),cmd='quit'
    # program name
    prgnam='change_atom_order_in_wat' 
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        cmd=''
        inpfile=futoolslib.GetSysArgs('ipdb')
        if not inpfile:
            # input file names
            inpfile=futoolslib.ConsoleInputOfFileName('input PDB file',True)
            if inpfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=inpfile
        outfile=futoolslib.GetSysArgs('opdb')
        if not outfile:
            outfile=futoolslib.ConsoleInputOfOutputFileName('output PDB file',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        ter=futoolslib.GetSysArgs('ter')
        if not ter:
            prmpt='Do you want to delete TER? 1:no, 2:yes'
            ter=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        # read PDB atoms
        time1=time.clock()
        futoolslib.MessJobStart('change-atom-order-in-wat')
        pdbatm,pdbcon=fumole.fuMole.ReadPDBAtom(inpfile)
        # pdbatm:[[label,natm,atmnam,alt,resnam,chain,resnmb,[fx,fy,fz],focc,fbfc,elm,chg],...]
        natm=len(pdbatm); i=0; nchange=0
        tmp=[]
        while i <= natm-3:
            res=pdbatm[i][4]
            if res == 'HOH' or res == 'WAT' or res == 'H2O':
                o=-1; h1=-1; h2=-1
                for j in range(i,i+3): 
                    if pdbatm[j][10] == ' O' and o < 0: o=j
                    elif pdbatm[j][10] == ' H' and h1 < 0: h1=j
                    elif pdbatm[j][10] == ' H' and h2 < 0: h2=j
                if o > 0 and o != i:
                    nchange += 1
                    tmp.append(pdbatm[o]); tmp.append(pdbatm[h1]); tmp.append(pdbatm[h2])
                i += 3
            else:
                if pdbatm[i][0][:3] == 'TER' and ter == 2:
                    i += 1; continue
                tmp.append(pdbatm[i]); i += 1
        #
        pdbatm=tmp
        print(('nchange',nchange))
        # write pdbatm on output file
        if nchange > 0:
            pdbatm=futoolslib.RenumberAtmNmbInPdbAtm(pdbatm)
            comment='REMARK created by '+prgnam+' at '+lib.DateTimeText()+'\n'
            comment=comment+'REMARK parent pdb file='+inpfile
            fumole.fuMole.WritePDBAtom(outfile,pdbatm,[],comment)
        else:
            print(('no hydrogen atoms in input pdb file: '+inpfile))
            print(('so, output pdb file: '+outfile+' is not created.'))
        #
        time2=time.clock(); etime=time1-time2
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

change_atom_order_in_wat()



#!/bin/sh
# -*- coding: utf-8

def delete_wat():
    # arguments: ipdb,opdb,solnam3chars,oxynam=four chars in ""
    # rcut=float, cmd='quit'
    # program name
    prgnam='delete_wat'
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            # read input PDB file
            pdbfile=futoolslib.ConsoleInputOfFileName('PDB file',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        outfile=futoolslib.GetSysArgs('opdb')
        if not outfile:
            # read output file name    
            outfile=futoolslib.ConsoleInputOfOutputFileName('output PDB file',True)
            if outfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.OUTPUTPDBFILE=outfile
        solnam=futoolslib.GetSysArgs('solnam')
        if not solnam:
            # residue name of solvent molecules
            print('+++ Input residue name of solvent molecules, three characters, like SOL')
            solnam=sys.stdin.readline()
            solnam=futoolslib.RemoveNull(solnam)
            solnam=solnam[0:3]
        if len(solnam) <= 0: solnam=futoolslib.SOLNAM
        oxynam=futoolslib.GetSysArgs('oxynam')
        if not oxynam:
            print('+++ Input atom name of oxygen atom, four characters with double quotations; " O  "')
            oxynam=sys.stdin.readline()
            oxynam=futoolslib.RemoveNull(oxynam)
            oxynam=lib.GetStringBetweenQuotation(oxynam)[0]
        if len(oxynam) <= 0: oxynam=futoolslib.OXYNAM
        print(('oxynam',len(oxynam),oxynam))
        if len(oxynam) != 4: 
            print('Error in format of atom name')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        print(('residue name and atom name of solvent molecule', solnam,oxynam))
        # cut-off distance
        rcut=futoolslib.GetSysArgs('rcut')
        if not rcut:
            print('+++ enter cut-off distance in Angstrom')
            rcut=sys.stdin.readline()
            rcut=futoolslib.RemoveNull(rcut)
            rcut=float(rcut)
        print(('rcut',rcut))
        # compute distance
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        cc2=[]; cc1=[]
        index=[]; dellst=[]
        # read PDB data
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        # pdbatm:[[label,natm,atmnam,alt,resnam,chain,resnmb,[fx,fy,fz],focc,fbfc,elm,chg],...]
        natm=len(pdbatm)
        for i in range(len(pdbatm)):
            resnam=pdbatm[i][4]; atmnam=pdbatm[i][2]; cc=pdbatm[i][7]
            if resnam == solnam:   #'HOH': #'SOL':
                if atmnam != oxynam: continue
                cc2.append(cc)
                index.append(i) 
            else: cc1.append(cc)
        #
        print(('number of atoms in input PDB file',len(pdbatm)))
        print(("number of waters",len(cc2))) #len(sol.mol)
        print(('number of solute atoms',len(cc1))) #len(pro.mol) 
        if len(cc1) <= 0 or len(cc2) <= 0:
            print('Warning: no water oxygens or solutes')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        rmax=100000.0 #threshold;
        ndel,itemp=fuflib.find_contact_atoms(cc1,cc2,rcut,rmax)    
        print(('number of deleted oxygens',ndel))
        for i in range(ndel):
            if itemp[i] < 0:
                print("Error in 'find_contact_atoms' medule.")
                break
            ii=itemp[i]; ii=index[ii]
            dellst.append(ii) # OW (atom name in GROMACS)
            try:
                if pdbatm[ii+1][10] == ' H': dellst.append(ii+1) # HW1
                if pdbatm[ii+2][10] == ' H': dellst.append(ii+2) # HW2
            except: pass
        # delete "SOL"
        print(('number of deleted atoms',len(dellst)))
        #wrk.DelAtoms(dellst)
        ndel=0
        for i in dellst:
            ii=i-ndel; del pdbatm[ii]; ndel += 1
        
        print(('number of atoms after delete '+solnam,len(pdbatm)))
        # make PDB file
        pdbatm=futoolslib.RenumberAtmNmbInPdbAtm(pdbatm)
        comment='REMARK created by '+prgnam+' at '+lib.DateTimeText()
        comment=comment+'REMARK parent pdb file='+pdbfile
        rwfile.WritePDBAtom(outfile,pdbatm,[],comment)
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)

delete_wat()

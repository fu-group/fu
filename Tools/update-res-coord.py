#!/bin/sh
#!/bin/sh

def update_res_coord():
    # relace residues in traget mol with those in resfile.
    # arguments: ipdb,opdb,resfile=['resfile1,resfile2,...}
    # program name
    prgnam='update_res_coord'
    done=False; futoolslib.ClearFileNameVar()
    # define priority character
    #if args.has_key('pchar'): pchar=args['pchar']
    args=[]
    while not done:            
        pdbfilelst=futoolslib.GetSysArgs('ipdb')
        if not pdbfilelst:
            # read PDB file name
            pdbfilelst=futoolslib.ConsoleInputOfStringData('input target pdb file(s)')
            if len(pdbfilelst) <= 0:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        if pdbfilelst[0][:1] == '<':
            if len(pdbfilelst) == 1: filesfile=pdbfilelst[0][1:]
            else: filesfile=pdbfilelst[1]
            filesfile=filesfile.strip()
            if not os.path.isfile(filesfile):
                print((filesfile+' file not found. job quit.'))
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            else: pdbfilelst=futoolslib.ReadFileNamesInFile(filesfile)
        try: print(filesfile)
        except: filesfile=pdbfilelst[0]
        #futoolslib.INPUTPDBFILE=pdbfiles
        filelst=futoolslib.GetSysArgs('rescoord')
        if not filelst:
            # read PDB file name
            filelst=futoolslib.ConsoleInputOfStringData('input residue coordinate file(s)')
            if len(filelst) <= 0:
                print('input null. quit the job.')
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
            resfile='console'  
            if filelst[0][:1] == '<':
                if len(filelst) == 1: file=filelst[0][1:]
                else: file=filelst[1]
                file=file.strip()
                if not os.path.isfile(file):
                    print((file+' file not found. job quit.'))
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
                else: filelst=futoolslib.ReadFileNamesInFile(file)
                resfile=file
            if len(filelst) <= 0:
                    print('no coordinate files to be replaced. quit the job.')
                    done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        
        print(('pdbfiles',pdbfilelst))
        print(('filelst',filelst))
        # check number of files
        if len(pdbfilelst) != len(filelst):
            print('number of pdb and coordinates files is not the same. quit the job.')
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        # check exist files
        nopdbfile=[]; nocoordfile=[]
        for fil in pdbfilelst:
            if not os.path.isfile(fil): nopdbfile.append(fil)
        for fil in filelst:
            if not os.path.isfile(fil): nocoordfile.append(fil)
        if len(nopdbfile) > 0:
            for fil in nopdbfile:
                print(('pdb file not exists. file=',fil))        
        if len(nocoordfile) > 0:
            for fil in nocoordfile:
                print(('coordinate file not exists. file=',fil))        
        if len(nopdbfile) > 0 or len(nocoordfile) > 0:
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break 
        #outfile=futoolslib.GetSysArgs('opdb')
        #if not outfile:
            # read output file name    
            #outfile=futoolslib.ConsoleInputOfOutputFileName('output pdb files',True)
            #if outfile == '':
                #done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #futoolslib.OUTPUTPDBFILE=outfile
        #
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        """ UpdateCoord has changed """
        nupd,outlst,outmess,devdic=futoolslib.UpdateCoord(prgnam,pdbfilelst,filelst)
        if len(outmess) > 0:
            for mess in outmess: print(mess)
        print('rms heavy atom deviantion (A), max dev, and max dev atom')
        for name, value in list(devdic.items()):
            print(('   ',name+': ','%6.3f' % value[0]+', '+'%6.3f' % value[1]+', '+value[2]))
        nc=filesfile.rfind('.')
        lstfile=filesfile[:nc]+'-coord.spl'
        #
        #if len(outlst) > 2:
        comment='# created by '+prgnam+' at '+lib.DateTimeText()+'\n'
        #comment=comment+'# target pdb file'+pdbfile
        futoolslib.WriteFileNames(lstfile,outlst,[],comment)
        print(('output pdb filelist file is created. file=',lstfile))
        print(('number of updated residues=',nupd))
        #
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        cmd,done=futoolslib.JobCmd(prgnam,[])
        #while fut.IsQuit():
        #    cmd,done=futoolslib.JobCmd(prgnam,args)
    #self.ToolsCmd(cmd,prgnam)

update_res_coord()


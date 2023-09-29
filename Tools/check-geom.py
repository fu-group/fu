#!/bin/sh
# -*- coding: utf-8

def check_geom():
    """
    # args:
    # jobopt=(1:bond length, 2:angle, 3:vdW contact)
    # fmin=0.8 (in case of jobopt=1)
    # fmax=1.2 (in case jobopt=1)
    # amin=90.0 (in case of jobopt=2)
    # fc=0.9 (in case of jobopt=3)
    # ipdb='filename of input'
    # logopt=(1: save log, 2:do not)
    # conopt=(1:create con data, 2:no quit)
    # mkbnd=(1:create,2:quit job) (in case of conopt=1)
    # cmd='quit'
    """
    # program name
    prgnam='check_geom'
    #cmddic=futoolslib.GetToolsCmd(prgnam)
    done=False; futoolslib.ClearFileNameVar()
    args=[]
    while not done:
        jobopt=-1; pdbfile=''; outfile=''; logopt=-1; logfile=''
        conopt=-1
        print('! this program requres pdb file with connect data.')
        #
        jobopt=futoolslib.GetSysArgs('jobopt')
        if not jobopt:
            # job option
            jobtxt=['bond length','angle','short contact']
            prmpt='select check option. 1:bond length, 2:angle, 3:vdW contact, 4:quit.'
            jobopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,4,1)
        if jobopt == 4:
            done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        # default fmin=0.8; fmax=1.2; amin=90.0; fc=0.7
        if jobopt == 1:
            fmin=futoolslib.GetSysArgs('fmin')
            fmax=futoolslib.GetSysArgs('fmax')
            if not fmin or not fmax:
                print('threshold length should be give by factors:fmin and fmax for')
                print('r < fmin*r0, r> fmax*r0 (r0:standard single bond length).')
                prmpt='input fmin and fmax, like "0.8 1.2" (do not type quotes)'
                item=futoolslib.ConsoleInputOfStringData(prmpt)
                if len(item) >= 2:
                    fmin=float(item[0]); fmax=float(item[1])
                else:
                    fmin=0.8; fmax=1.2
            mess='find bond whose distance is shorter than '+str(fmin)+' or longer than '
            mess=mess+str(fmax)+' times of standard value'
            print(mess)
        elif jobopt == 2:
            amin=futoolslib.GetSysArgs('amin')
            if not amin:
                prmpt='input minimum angle in degrees, like "90.0" (do not type quotes)'
                item=futoolslib.ConsoleInputOfStringData(prmpt)
                try:
                    if len(item) >= 1: amin=float(item[0])
                except: pass
                if not amin: amin=90.0  
            print(('find bond angel being smaller than '+str(amin)+' degrees.'))
        else:
            fc=futoolslib.GetSysArgs('fc')
            if not fc:
                prmpt='input fmin for r < fmin*(sum of van der Waals radii), like "0.8" (do not type quotes)'
                item=futoolslib.ConsoleInputOfStringData(prmpt)
                if len(item) >= 1: 
                    if len(item[0]) > 0: fc=float(item[0])
                    else: fc=0.8
                else: fc=0.8
            print(('find atom pair whose distance is shorter than factor '+str(fc)+'.'))
        # read PDB file name
        pdbfile=futoolslib.GetSysArgs('ipdb')
        if not pdbfile:
            pdbfile=futoolslib.ConsoleInputOfFileName('pdb file(.pdb)',True)
            if pdbfile == '':
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        futoolslib.INPUTPDBFILE=pdbfile
        logopt=futoolslib.GetSysArgs('logopt')
        if not logopt:
            # read mht file
            logopt=1
            prmpt="do you want to output in log file? 1:yes, 2:no"
            logopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
        logfile=pdbfile.replace('.pdb','.log')
        # read base name of created PDB file
        pdbatm,pdbcon=rwfile.ReadPDBAtom(pdbfile)
        mkbnd=False
        if len(pdbcon) <= 0:
            print('no connect data in the pdb file.')
            conopt=futoolslib.GetSysArgs('conopt')
            if not conopt:
                prmpt='do you want to create? 1:yes, 2:no, quit the job.'
                conopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)
            if conopt == 2:
                done=True; cmd=futoolslib.JobInterrupt(prgnam); break
        #
        if len(pdbatm) > 10000:
            print('job may take several minutes for 10,000 atoms.')
        #
        time1=time.clock()
        futoolslib.MessJobStart(prgnam)
        #
        if len(pdbcon) <= 0 and conopt == 1:
            # make connect data
            pdbcon=futoolslib.MakePdbCon(pdbatm)
            mkbnd=True
        #        
        text=''
        if jobopt == 1:
            nbnd,iatm,jatm,rij,iskip,jskip=futoolslib.CheckBondLengths(pdbatm,pdbcon,fmin,fmax)
            """ important function. check short dist but no-bond """
            """ add bond if needed new program? 'FindMissingBonds' """
            print(('total number of bond length parameters=',nbnd))
            if len(iatm) > 0:
                print(('number of wrong length bonds=',len(iatm)))
                text=futoolslib.OutputTextOfDistance(pdbatm,rij,iatm,jatm)
                print(text)
                if len(iatm) > 100:
                    print('if you have long list, connect data may be missing in pdb file.')
                for i in range(len(iatm)):
                    futoolslib.SELECTATM.append(iatm[i])
                    futoolslib.SELECTATM.append(jatm[i])
                #print 'SELECTATM in check_geom',futoolslib.SELECTATM
            else:
                print(('number of skipped bonds to check=',len(iskip)))
                print('there is no short or long bond for checked bonds.')
        elif jobopt == 2:
            nang,chkang=futoolslib.CheckBondAngle(pdbatm,pdbcon,amin)
            print(('total number of angle parameters=',nang))
            if len(chkang) > 0:
                print(('number of wrong value angles=',len(chkang)))
                text=futoolslib.OutputTextOfAngle(chkang)
                print(text)
                if len(chkang) > 100:
                    print('if you have long list, connect data may be missing in pdb file.')
                else:
                    for i in range(len(chkang)):
                        futoolslib.SELECTATM.append(chkang[i][0])
                        futoolslib.SELECTATM.append(chkang[i][1])
                        futoolslib.SELECTATM.append(chkang[i][2])
            else:
                print('there is no small bond angle.')
        elif jobopt == 3:
            npair,iatm,jatm=futoolslib.CheckShortContact(pdbatm,pdbcon,fc)
            text=futoolslib.OutputTextOfShortContact(pdbatm,iatm,jatm)
            if npair <= 0:
                print('there is no short contact atom pairs.')
            else:
                print(('number of short contact atom pairs: ',npair))
                if npair <= 1000:
                    print(text)
                    #print ' number,atom i,atom j'
                    #for i in range(npair): print i+1,iatm[i]+1,jatm[i]+1
                    for i in range(len(iatm)):
                        futoolslib.SELECTATM.append(iatm[i])
                        futoolslib.SELECTATM.append(jatm[i])
                else:
                    print('too many pairs. print skipped (see log file).')
                    print('connect data may be missing in pdb file.')
            #text=futoolslib.OutputTextOfShortContact(pdbatm,iatm,jatm)
        # write log in file
        if logopt == 1:
            comment='[input pdb file]  '+pdbfile+'\n'
            comment=comment+'[job option] '+jobtxt[jobopt-1]
            futoolslib.WriteCheckGeomLog(logfile,comment,text)
        #-----
        time2=time.clock(); etime=time2-time1
        futoolslib.MessJobEnd(prgnam,etime)
        #
        # save pdb
        if mkbnd and len(pdbcon) > 0:
            print('pdb connect data were created.')
            prmpt='do you want to rewrite pdb file with connect data? 1:yes, 2:no.'
            savopt=futoolslib.ConsoleInputOfIntegerOption(prmpt,1,2,1)    
            if savopt:
                comment=prgnam+' is used to create connect data.'
                fumole.fuMole.WritePDBAtom(pdbfile,pdbatm,pdbcon,comment)
                print((pdbfile+' was saved with connect data.'))
                futoolslib.OUTPUTPDBFILE=pdbfile
        # session log
        battxt=futoolslib.BatchText(prgnam,jobopt,pdbfile,outfile,logopt,logfile,'quit')
        addtext=''
        if jobopt == 1:
            addtext=addtext+",fmin="+str(fmin)+",logopt="+str(logopt)+",fmax="+str(fmax)
        elif jobopt == 2: addtext=addtext+",amin="+str(amin)
        else: addtext=addtext+",fc="+str(fc)
        if conopt == 1: addtext=addtext+",conopt="+str(conopt)
        if len(addtext) > 0: battxt=futoolslib.BatchTextAppend(battxt,addtext)            
        futoolslib.WriteSessionLog(battxt)
        if mkbnd and len(pdbcon) > 0:
            logtxt=pdbfile+"was rewitten with conect data "
            logtxt=logtxt+" which are created based-on bond length."
            futoolslib.WriteSessionLog(logtxt)
        #
        cmd,done=futoolslib.JobCmd(prgnam,args)
        while fut.IsQuit():
            cmd,done=futoolslib.JobCmd(prgnam,args)

    #self.ToolsCmd(cmd,prgnam)
check_geom()

#!/bin/sh
# -*- coding: utf-8

import lib

def RunlistRes():
    """ Input args for "lstRes" tool and execute the tool
        lstRes(self,inp='',resknd='non-aa',opt='uniq',verbose=False)
        inp: input file name
        resknd: ['aa','non-aa','all']
        opt: ['uniq','defect']
    """
    toolname='RunlstRes'
    done=False; run=False; inpfile=True
    #
    filename=lib.ConsoleInputOfFileNames('input PDB file',True)
    if len(filename) <= 0: #filename == '':
        files=fut.getINP()
        if len(files) <= 0:
            #done=True; cmd=fut.JobInterrupt(toolname); break
            print('No input PDB file. Unable to contine.')
            inpfile=False
        print(('input PDB file is taken from OPTS. filename=',files))
        filename=files
        #    done=True; cmd=fut.JobInterrupt(toolname); break
    if inpfile:
        print(('filename=',filename))
        
        done=True
        #
        prmpt='enter residue kind 1:"aa", 2:"non-aa", 3:"all", or "quit"'
        kndopt=lib.ConsoleInputOfIntegerOption(prmpt,1,3,1)
        txt=['aa','non-aa','all']
        print(('resknd=',txt[kndopt-1]))            
        fut.ARGS['resknd']=txt[kndopt-1]
        #
        prmpt='enter option 1:"uniq", 2:"defect", 3:"resnam", 4:"all" or 3:"quit"'
        kndopt=lib.ConsoleInputOfIntegerOption(prmpt,1,4,1)
        txt=['uniq','defect','resnam','all']
        print(('opt=',txt[kndopt-1]))            
        fut.ARGS['opt']=txt[kndopt-1]
        #
        resnamlst=[]
        if kndopt == 4:
            prmpt='Input resdue name, e.g. "ALA,..." (do not enter ")'
            resnamlst=lib.ConsoleInputOfStringData(prmpt)
            if len(resnamlst) <= 0: 
                print('Tools(lstRes): "resnamlst" is empty.')
                return
            else: 
                resnam=''
                for res in resnamlst: resnam=resnam+','+res.strip()
                resnam=resnam[:-1]
                fut.ARGS['resnam']=resnam
                print(('resnamlst=',resnamlst))
        #
        run=True
        
        # end message
        """
        cmd,done=fut.JobCmd(toolname,args)
        while fut.IsQuit():
            cmd,done=fut.JobCmd(toolsname,args)
            run=False
        """
        ARGS=fut.ARGS
        if run: 
            for file in filename:
                fut.ARGS=ARGS
                fut.ARGS['inp']=file
                #print 'run lstRes, ARGS',fut.ARGS
                fut.listRes()
            done=True
        # view results
        doneview=False
        while not doneview:
            viwopt,viwnmb=fut.InputOfViewOption()
            if viwopt < 0: break
            fut.view(viwnmb-1)
            
RunlistRes()



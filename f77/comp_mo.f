      double precision function mo_value_at(x,y,z,mo,
     +                                      shltyp,shlxyz,shlgau,
     +                                      ex,cs,cp,cd,cf,
     +                                      nshl,ngau,nbas)
      implicit none
      integer nshl,ngau,nbas
      integer shlgau(nshl,2)
      real(8) x,y,z,mo(nbas),shlxyz(nshl,3)
      real(8) ex(ngau),cs(ngau),cp(ngau),cd(ngau),cf(ngau)
      integer shltyp(nshl)

      real(8) x0,y0,z0,val,pi,thre,px,py,pz
      integer ibas,ish,ig,ng,ist,ied
      real(8) rr,exig,exrr,exval,norms,normp,nmdx2,nmdxy
      real(8) sums,sumpx,sumpy,sumpz
      real(8) sumdxx,sumdyy,sumdzz,sumdxy,sumdyz,sumdzx
      real(8) gnormconst
      
      pi=3.141592654
      thre=-12.0
      val=0.0
      ibas=1
      do ish = 1,nshl
          x0=shlxyz(ish,1)
          y0=shlxyz(ish,2)
          z0=shlxyz(ish,3)
          px=x-x0
          py=y-y0
          pz=z-z0
          rr=px*px+py*py+pz*pz
          if (shltyp(ish).eq.1) then
c             write(*,*) 'ish,shltyp',ish,shltyp(ish)
              sums=0.0
              ist=shlgau(ish,1)+1
              ied=shlgau(ish,2)+1
c             write(*,*) 'ist,ied',ist,ied
              do ig=ist,ied
                  exig=ex(ig)
                  exrr=-exig*rr
c                 write(*,*) 'thre,exrr',thre,exrr
                  if (exrr.gt.thre) then
                       norms=gnormconst(exig,0,0,0)
                       exval=norms*exp(exrr)
c                      write(*,*) 'norms,exval',norms,exval
                       sums=sums+cs(ig)*exval
                  end if
              end do
              val=val+mo(ibas+0)*sums
              ibas=ibas+1
          else if (shltyp(ish).eq.3) then
              sumpx=0.0
              sumpy=0.0
              sumpz=0.0
              ist=shlgau(ish,1)+1
              ied=shlgau(ish,2)+1
              do ig=ist,ied
                  exig=ex(ig)
                  exrr=-exig*rr
                  if (exrr.gt.thre) then
                       normp=gnormconst(exig,1,0,0)
                       exval=normp*exp(exrr)
                       sumpx=sumpx+cp(ig)*px*exval
                       sumpy=sumpy+cp(ig)*py*exval
                       sumpz=sumpz+cp(ig)*pz*exval
                  end if
              end do
              val=val+mo(ibas+0)*sumpx
              val=val+mo(ibas+1)*sumpy
              val=val+mo(ibas+2)*sumpz
              ibas=ibas+3
          else if (shltyp(ish).eq.4) then
              sums=0.0
              sumpx=0.0
              sumpy=0.0
              sumpz=0.0
              ist=shlgau(ish,1)+1
              ied=shlgau(ish,2)+1
              do ig=ist,ied
                  exig=ex(ig)
                  exrr=-exig*rr
                  if (exrr.gt.thre) then
                       norms=gnormconst(exig,0,0,0)
                       normp=gnormconst(exig,1,0,0)
                       exval=exp(exrr)
                       sums=sums+cs(ig)*exval*norms
                       sumpx=sumpx+cp(ig)*px*exval*normp
                       sumpy=sumpy+cp(ig)*py*exval*normp
                       sumpz=sumpz+cp(ig)*pz*exval*normp
                  end if
              end do
              val=val+mo(ibas+0)*sums
              val=val+mo(ibas+1)*sumpx
              val=val+mo(ibas+2)*sumpy
              val=val+mo(ibas+3)*sumpz
              ibas=ibas+4
          else if (shltyp(ish).eq.6) then
              sumdxx=0.0
              sumdyy=0.0
              sumdzz=0.0
              sumdxy=0.0
              sumdyz=0.0
              sumdzx=0.0
              ist=shlgau(ish,1)+1
              ied=shlgau(ish,2)+1
              do ig=ist,ied
                  exig=ex(ig)
                  exrr=-exig*rr
                  if (exrr.gt.thre) then
                     exval=exp(exrr)
                     nmdx2=gnormconst(exig,2,0,0)
                     nmdxy=gnormconst(exig,1,1,0)
                     sumdxx=sumdxx+cd(ig)*px*px*exval*nmdx2
                     sumdyy=sumdyy+cd(ig)*py*py*exval*nmdx2
                     sumdzz=sumdzz+cd(ig)*pz*pz*exval*nmdx2
                     sumdxy=sumdxy+cd(ig)*px*py*exval*nmdxy
                     sumdyz=sumdyz+cd(ig)*py*pz*exval*nmdxy
                     sumdzx=sumdzx+cd(ig)*pz*px*exval*nmdxy
                  end if
              end do
              val=val+mo(ibas+0)*sumdxx
              val=val+mo(ibas+1)*sumdyy
              val=val+mo(ibas+2)*sumdzz
              val=val+mo(ibas+3)*sumdxy
              val=val+mo(ibas+4)*sumdyz
              val=val+mo(ibas+5)*sumdzx
              ibas=ibas+6
c         else if (shltyp(ish).eq.10) then
          else
              write(*,*) 'Shell type is not supported.',shltyp(ish)
              exit
          end if

c         write(*,*) 'ish,val',ish,val

      end do    
     
c     write(*,*) 'val after ish loop',val
 
      mo_value_at = val

      return

      end function mo_value_at
      


      integer function factri(n)
      implicit none
      integer,intent(in) :: n
      integer i,fn

      fn=1
      do i=1,n
          fn=fn*i
      enddo
      factri = fn
      end function factri

      double precision function gnormconst(a,l,m,n)
      implicit none
      real(8),intent(in) :: a
      integer,intent(in) :: l,m,n
      integer factri
      real(8) nc1,nc2,pi,fl,fm,fn,f2l,f2m,f2n
      
      pi=3.141592654
      nc1=(2.0*a/pi)**0.75
      if ((l.eq.0) .and. (m.eq.0) .and. (n.eq.0)) then
          gnormconst=nc1
      else
          fl=float(factri(l))
          fm=float(factri(m))
          fn=float(factri(n))
          f2l=float(factri(2*l))
          f2m=float(factri(2*m))
          f2n=float(factri(2*n))
          nc2=((8.0*a)**(l+m+n)*fl*fm*fn)/(f2l*f2m*f2n)
          gnormconst=nc1*sqrt(nc2)
      end if

      return

      end function gnormconst





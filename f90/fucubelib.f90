
Subroutine make_polygons(moval, ex, ey, ez, boxmin, thres, ndiv, maxpoly, &
     nx, ny, nz, polygons, npoly )
  implicit none
  integer,intent(in) :: nx, ny, nz, ndiv
  real(8),intent(in) :: moval(0:nx-1,0:ny-1,0:nz-1)
  real(8),intent(in) :: ex(0:2), ey(0:2), ez(0:2), boxmin(0:2), thres
  integer,intent(in) :: maxpoly
  real(8),intent(out) :: polygons(0:maxpoly-1,0:3,0:2)
  integer,intent(out) :: npoly
  integer,allocatable :: bvtx(:,:,:)
  real(8),allocatable :: weight(:,:,:,:,:,:), movaldiv(:,:,:)
  integer :: nxdiv, nydiv, nzdiv, ixdiv, iydiv, izdiv, jx, jy, jz, ixx, iyy, izz
  integer :: icube, ibit, i, j, k, ix, iy, iz
  integer :: polys(0:2,0:4), itri, imid, triangle(0:2), pos0(0:2), pos1(0:2)
  real(8) :: moval0, moval1, dif0, dif1, dif01, posxyz(0:2)
  real(8) :: pos(0:2), midpos(0:2,0:2), vec01(0:2), vec02(0:2), vnorm(0:2), v
  real(8) :: x(0:1), y(0:1), z(0:1), exdiv(0:2), eydiv(0:2), ezdiv(0:2)
  integer :: midvtx(0:2, 0:1, 0:11)
  integer :: cubepoly(0:2, 0:4, 0:255)

! mid point number -> 2 vertices (ix,iy,iz = 0 or 1) of the edge
  midvtx(0:2, 0:1, 0:11) = reshape( (/ &
       0,0,0, 1,0,0, &
       0,1,0, 1,1,0, &
       0,0,0, 0,1,0, &
       1,0,0, 1,1,0, &
       0,0,1, 1,0,1, &
       0,1,1, 1,1,1, &
       0,0,1, 0,1,1, &
       1,0,1, 1,1,1, &
       0,0,0, 0,0,1, &
       1,0,0, 1,0,1, &
       0,1,0, 0,1,1, &
       1,1,0, 1,1,1  &
       /), shape(midvtx) )

! cube's 8 verticies in/out pattern (2**8=256) -> 0-5 surface triangles * 3 midpoints
  cubepoly(0:2, 0:4, 0:255) = reshape( (/ &
       -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 8, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        3, 9, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 3, 8,  3, 9, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 1, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8,10, 0, 10, 1, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 3, 9,  1,10, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        1, 3, 9,  1, 9,10,  8,10, 9, -1,-1,-1, -1,-1,-1, &
        1,11, 3, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        3, 1,11,  2, 8, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 1, 9,  1,11, 9, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 1,11,  2,11, 8,  9, 8,11, -1,-1,-1, -1,-1,-1, &
        3, 2,11,  2,10,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        3, 0, 8,  3, 8,11, 10,11, 8, -1,-1,-1, -1,-1,-1, &
        0, 2,10,  0,10, 9, 11, 9,10, -1,-1,-1, -1,-1,-1, &
        8,10, 9,  9,10,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 6, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 4, 2,  4, 6, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 4, 6,  9, 3, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        9, 4, 6,  9, 6, 3,  2, 3, 6, -1,-1,-1, -1,-1,-1, &
        2,10, 1,  6, 4, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        6,10, 1,  6, 1, 4,  0, 4, 1, -1,-1,-1, -1,-1,-1, &
        0, 3, 9,  1, 2,10,  4, 6, 8, -1,-1,-1, -1,-1,-1, &
        1, 3, 9,  1, 9,10,  9, 4,10,  4, 6,10, -1,-1,-1, &
        1,11, 3,  4, 6, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 2, 4,  2, 4, 6,  1,11, 3, -1,-1,-1, -1,-1,-1, &
        0, 9, 1,  9, 1,11,  4, 6, 8, -1,-1,-1, -1,-1,-1, &
        1,11, 9,  1, 9, 2,  2, 9, 6,  4, 6, 9, -1,-1,-1, &
       10, 2,11,  2,11, 3,  8, 4, 6, -1,-1,-1, -1,-1,-1, &
        6,10,11,  6,11, 4,  4,11, 0,  3, 0,11, -1,-1,-1, &
        0, 2, 1,  2,10, 9,  9,10,11,  4, 6, 8, -1,-1,-1, &
        9, 4, 6, 10, 9, 6,  9,10,11, -1,-1,-1, -1,-1,-1, &
        9, 7, 4, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 9, 7,  0, 2, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 0, 7,  0, 3, 7, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 8, 2,  4, 2, 7,  3, 7, 2, -1,-1,-1, -1,-1,-1, &
        9, 7, 4, 10, 1, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 0,10,  0,10, 1,  9, 7, 4, -1,-1,-1, -1,-1,-1, &
        3, 0, 7,  0, 7, 4,  2,10, 1, -1,-1,-1, -1,-1,-1, &
        1, 3, 7,  1, 7,10, 10, 7, 8,  4, 8, 7, -1,-1,-1, &
       11, 3, 1,  9, 4, 7, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        3, 1,11,  2, 0, 8,  7, 4, 9, -1,-1,-1, -1,-1,-1, &
        1,11, 7,  4, 1, 7,  1, 4, 0, -1,-1,-1, -1,-1,-1, &
        2, 1,11,  2,11, 8, 11, 7, 8,  7, 4, 8, -1,-1,-1, &
       10, 3,11,  2,10, 3,  7, 4, 9, -1,-1,-1, -1,-1,-1, &
        3, 0, 2,  0, 8,11, 11, 8,10,  7, 4, 9, -1,-1,-1, &
        2,10,11,  2,11, 0,  0,11, 4,  7, 4,11, -1,-1,-1, &
        7, 4, 8,  7, 8,11, 10,11, 8, -1,-1,-1, -1,-1,-1, &
        8, 9, 6,  9, 7, 6, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 9, 7,  0, 7, 2,  6, 2, 7, -1,-1,-1, -1,-1,-1, &
        8, 0, 3,  8, 3, 6,  7, 6, 3, -1,-1,-1, -1,-1,-1, &
        2, 3, 6,  6, 3, 7, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 6, 9,  6, 9, 7, 10, 1, 2, -1,-1,-1, -1,-1,-1, &
        9, 7, 6,  9, 6, 0,  0, 6, 1, 10, 1, 6, -1,-1,-1, &
        8, 0, 9,  0, 3, 6,  6, 3, 7, 10, 1, 2, -1,-1,-1, &
        6,10, 1,  3, 6, 1,  6, 3, 7, -1,-1,-1, -1,-1,-1, &
        8, 7, 9,  6, 8, 7,  3, 1,11, -1,-1,-1, -1,-1,-1, &
        0, 9, 4,  9, 7, 2,  2, 7, 6,  1,11, 3, -1,-1,-1, &
        0, 1,11,  7, 0,11,  6, 0, 7,  0, 6, 8, -1,-1,-1, &
        1,11, 7,  1, 7, 2,  6, 2, 7, -1,-1,-1, -1,-1,-1, &
        2,10, 3,  3,10,11,  6, 8, 7,  7, 8, 9, -1,-1,-1, &
        3, 0,11,  0,10,11,  7, 0, 9,  6, 0, 7,  0, 6,10, &
        8, 0, 6,  0, 7, 6, 10, 0, 2, 11, 0,10,  0,11, 7, &
        7,10,11,  7, 6,10, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        6, 5,10, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 6, 5,  8, 0, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        6, 5,10,  3, 9, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 8, 3,  8, 3, 9,  6, 5,10, -1,-1,-1, -1,-1,-1, &
        2, 6, 1,  6, 5, 1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 6, 5,  8, 5, 0,  1, 0, 5, -1,-1,-1, -1,-1,-1, &
        2, 1, 6,  1, 6, 5,  3, 9, 0, -1,-1,-1, -1,-1,-1, &
        6, 5, 1,  6, 1, 8,  8, 1, 9,  3, 9, 1, -1,-1,-1, &
        5,10, 6,  1, 3,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 6, 5,  8, 2, 0, 11, 3, 1, -1,-1,-1, -1,-1,-1, &
        0,11, 1,  9, 0,11, 10, 6, 5, -1,-1,-1, -1,-1,-1, &
        2, 1, 3,  1,11, 8,  8,11, 9,  6, 5,10, -1,-1,-1, &
        6, 5,11,  3, 6,11,  6, 3, 2, -1,-1,-1, -1,-1,-1, &
        8, 6, 5,  8, 5, 0,  5,11, 0, 11, 3, 0, -1,-1,-1, &
        2, 6, 5, 11, 2, 5,  9, 2,11,  2, 9, 0, -1,-1,-1, &
        6, 5,11,  6,11, 8,  9, 8,11, -1,-1,-1, -1,-1,-1, &
       10, 8, 5,  8, 4, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 2, 0, 10, 0, 5,  4, 5, 0, -1,-1,-1, -1,-1,-1, &
        4, 8, 5,  8, 5,10,  0, 3, 9, -1,-1,-1, -1,-1,-1, &
        9, 4, 5,  9, 5, 3,  3, 5, 2, 10, 2, 5, -1,-1,-1, &
        2, 8, 4,  2, 4, 1,  5, 1, 4, -1,-1,-1, -1,-1,-1, &
        0, 4, 1,  1, 4, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 8, 6,  8, 4, 1,  1, 4, 5,  3, 9, 0, -1,-1,-1, &
        1, 3, 9,  4, 1, 9,  1, 4, 5, -1,-1,-1, -1,-1,-1, &
        4,10, 5,  8, 4,10, 11, 3, 1, -1,-1,-1, -1,-1,-1, &
       10, 2, 8,  2, 0, 5,  5, 0, 4, 11, 3, 1, -1,-1,-1, &
        8, 4,10, 10, 4, 5,  9, 0,11, 11, 0, 1, -1,-1,-1, &
       10, 2, 5,  2, 4, 5, 11, 2, 1,  9, 2,11,  2, 9, 4, &
        8, 4, 5,  8, 5, 2,  2, 5, 3, 11, 3, 5, -1,-1,-1, &
       11, 3, 0, 11, 0, 5,  4, 5, 0, -1,-1,-1, -1,-1,-1, &
        0, 2, 9,  2,11, 9,  4, 2, 8,  5, 2, 4,  2, 5,11, &
       11, 4, 5, 11, 9, 4, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        7, 4, 9,  6,10, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 9, 7,  0, 8, 2,  5,10, 6, -1,-1,-1, -1,-1,-1, &
        3, 4, 7,  0, 3, 4,  5,10, 6, -1,-1,-1, -1,-1,-1, &
        4, 8, 0,  8, 2, 7,  7, 2, 3,  5,10, 6, -1,-1,-1, &
        2, 5, 6,  1, 2, 5,  4, 9, 7, -1,-1,-1, -1,-1,-1, &
        8, 6,10,  6, 5, 0,  0, 5, 1,  9, 7, 4, -1,-1,-1, &
        0, 3, 4,  4, 3, 7,  1, 2, 5,  5, 2, 6, -1,-1,-1, &
        4, 8, 7,  8, 3, 7,  5, 8, 6,  1, 8, 5,  8, 1, 3, &
        5,10, 6,  1,11, 3,  4, 9, 7, -1,-1,-1, -1,-1,-1, &
        0, 8, 2,  1,11, 3,  4, 9, 7,  5,10, 6, -1,-1,-1, &
       11, 7, 9,  7, 4, 1,  1, 4, 0, 10, 6, 5, -1,-1,-1, &
        4,10, 6,  4, 8, 2,  1, 4, 2,  1, 4,10,  5,11, 7, &
        5,11, 1, 11, 3, 6,  6, 3, 2,  4, 9, 7, -1,-1,-1, &
        3, 4, 9,  3, 0, 8,  6, 3, 8,  6, 3, 4,  7, 5,11, &
        4,11, 7,  4, 0,11,  5,11, 6,  6,11, 2,  0, 2,11, &
        7, 4,11,  6, 5,11,  6,11, 8,  4,11, 8, -1,-1,-1, &
        9, 7, 5, 10, 9, 5,  9,10, 8, -1,-1,-1, -1,-1,-1, &
        0, 9, 7,  0, 7, 2,  7, 5, 2,  5,10, 2, -1,-1,-1, &
        0, 3, 7,  0, 7, 8,  8, 7,10,  5,10, 7, -1,-1,-1, &
        5,10, 2,  5, 2, 7,  3, 7, 2, -1,-1,-1, -1,-1,-1, &
        8, 9, 7,  5, 8, 7,  1, 8, 5,  8, 1, 2, -1,-1,-1, &
        9, 7, 5,  9, 5, 0,  1, 0, 5, -1,-1,-1, -1,-1,-1, &
        2, 8, 1,  8, 5, 1,  3, 8, 0,  7, 8, 3,  8, 7, 5, &
        5, 3, 7,  5, 1, 3, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        7, 5, 6,  5,10, 9,  9,10, 8,  3, 1,11, -1,-1,-1, &
       10, 3, 1, 10, 2, 0,  9,10, 0,  9,10, 3, 11, 7, 5, &
       10, 7, 5, 10, 8, 7, 11, 7, 1,  1, 7, 0,  8, 0, 7, &
        5,10, 7,  1,11, 7,  1, 7, 2, 10, 7, 2, -1,-1,-1, &
        3, 5,11,  3, 2, 5,  7, 5, 9,  9, 5, 8,  2, 8, 5, &
       11, 3, 5,  9, 7, 5,  9, 5, 0,  3, 5, 0, -1,-1,-1, &
        2, 8, 0, 11, 7, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11, 7, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        5, 7,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 8, 2,  5, 7,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        5, 7,11,  3, 0, 9, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 9, 3,  8, 2, 9, 11, 5, 7, -1,-1,-1, -1,-1,-1, &
        7,11, 5, 10, 2, 1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 1,10,  0, 8, 1,  5, 7,11, -1,-1,-1, -1,-1,-1, &
        1, 2,10,  0, 3, 9,  5, 7,11, -1,-1,-1, -1,-1,-1, &
        1, 3, 0,  3, 9,10, 10, 9, 8,  5, 7,11, -1,-1,-1, &
        7, 3, 5,  3, 1, 5, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        1, 3, 5,  3, 5, 7,  0, 8, 2, -1,-1,-1, -1,-1,-1, &
        5, 7, 9,  0, 5, 9,  5, 0, 1, -1,-1,-1, -1,-1,-1, &
        1, 5, 7,  9, 1, 7,  8, 1, 9,  1, 8, 2, -1,-1,-1, &
        2,10, 5,  7, 2, 5,  2, 7, 3, -1,-1,-1, -1,-1,-1, &
        0, 8,10,  0,10, 3,  3,10, 7,  5, 7,10, -1,-1,-1, &
        0, 2,10,  0,10, 9, 10, 5, 9,  5, 7, 9, -1,-1,-1, &
        5, 7, 9,  5, 9,10,  8,10, 9, -1,-1,-1, -1,-1,-1, &
       11, 5, 7,  4, 8, 6, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 6, 4,  2, 0, 6,  7,11, 5, -1,-1,-1, -1,-1,-1, &
        9, 0, 3,  8, 4, 6, 11, 5, 7, -1,-1,-1, -1,-1,-1, &
        9, 4, 8,  4, 6, 3,  3, 6, 2, 11, 5, 7, -1,-1,-1, &
        6, 8, 4,  2,10, 1,  7,11, 5, -1,-1,-1, -1,-1,-1, &
        6,10, 2, 10, 1, 4,  4, 1, 0,  7,11, 5, -1,-1,-1, &
        3, 9, 0,  2,10, 1,  7,11, 5,  6, 8, 4, -1,-1,-1, &
        6,11, 5,  6,10, 1,  3, 6, 1,  3, 6,11,  7, 9, 4, &
        7, 5, 3,  5, 3, 1,  6, 8, 4, -1,-1,-1, -1,-1,-1, &
        2, 0, 6,  6, 0, 4,  3, 1, 7,  7, 1, 5, -1,-1,-1, &
       11, 7, 9,  0, 5, 7,  1, 5, 0,  4, 6, 8, -1,-1,-1, &
        6, 9, 4,  6, 2, 9,  7, 9, 5,  5, 9, 1,  2, 1, 9, &
        1,10, 5,  7, 2,10,  3, 2, 7,  6, 8, 4, -1,-1,-1, &
        7,10, 5,  7, 3,10,  6,10, 4,  4,10, 0,  3, 0,10, &
        7, 8, 4,  7, 9, 0,  2, 7, 0,  2, 7, 8,  6,10, 5, &
        9, 5, 7,  9, 4, 6, 10, 9, 6, 10, 9, 5, -1,-1,-1, &
        5, 4,11,  4, 9,11, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        9, 4,11,  4,11, 5,  8, 2, 0, -1,-1,-1, -1,-1,-1, &
        0, 3,11,  5, 0,11,  0, 5, 4, -1,-1,-1, -1,-1,-1, &
        8, 2, 3,  8, 3, 4,  4, 3, 5, 11, 5, 3, -1,-1,-1, &
        5,11, 4, 11, 4, 9,  1, 2,10, -1,-1,-1, -1,-1,-1, &
        0, 8, 1,  1, 8,10,  4, 9, 5,  5, 9,11, -1,-1,-1, &
        9, 3,11,  5, 0, 3,  4, 0, 5,  1, 2,10, -1,-1,-1, &
        5, 3,11,  5, 4, 3,  1, 3,10, 10, 3, 8,  4, 8, 3, &
        9, 3, 1,  9, 1, 4,  5, 4, 1, -1,-1,-1, -1,-1,-1, &
        7, 9, 3,  1, 4, 9,  5, 4, 1,  0, 8, 2, -1,-1,-1, &
        5, 4, 1,  1, 4, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        4, 8, 2,  1, 4, 2,  4, 1, 5, -1,-1,-1, -1,-1,-1, &
        5, 4, 9,  3, 5, 9,  2, 5, 3,  5, 2,10, -1,-1,-1, &
        9, 3, 4,  3, 5, 4,  8, 3, 0, 10, 3, 8,  3,10, 5, &
        0, 2,10,  5, 0,10,  0, 5, 4, -1,-1,-1, -1,-1,-1, &
        5, 8,10,  5, 4, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11, 5, 6,  8,11, 6, 11, 8, 9, -1,-1,-1, -1,-1,-1, &
        9,11, 5,  6, 9, 5,  2, 9, 6,  9, 2, 0, -1,-1,-1, &
        8, 0, 3,  8, 3, 6,  3,11, 6, 11, 5, 6, -1,-1,-1, &
       11, 5, 6, 11, 6, 3,  2, 3, 6, -1,-1,-1, -1,-1,-1, &
        7, 5, 6,  8,11, 5,  9,11, 8, 10, 1, 2, -1,-1,-1, &
        1, 6,10,  1, 0, 6,  5, 6,11, 11, 6, 9,  0, 9, 6, &
        5, 2,10,  5, 6, 8,  0, 5, 8,  0, 5, 2,  1, 3,11, &
        6,11, 5,  6,10, 1,  3, 6, 1,  3, 6,11, -1,-1,-1, &
        6, 8, 9,  6, 9, 5,  5, 9, 1,  3, 1, 9, -1,-1,-1, &
        0, 9, 2,  9, 6, 2,  1, 9, 3,  5, 9, 1,  9, 5, 6, &
        5, 6, 8,  0, 5, 8,  5, 0, 1, -1,-1,-1, -1,-1,-1, &
        1, 6, 2,  1, 5, 6, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 5, 2,  5, 3, 2,  8, 5, 6,  9, 5, 8,  5, 9, 3, &
       10, 5, 6,  0, 9, 3, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        5, 2,10,  5, 6, 8,  0, 5, 8,  0, 5, 2, -1,-1,-1, &
       10, 5, 6, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11,10, 7, 10, 6, 7, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        6,10, 7, 10, 7,11,  2, 0, 8, -1,-1,-1, -1,-1,-1, &
       11, 7,10,  7,10, 6,  9, 0, 3, -1,-1,-1, -1,-1,-1, &
        8, 2, 9,  9, 2, 3, 10, 6,11, 11, 6, 7, -1,-1,-1, &
        7,11, 1,  2, 7, 1,  7, 2, 6, -1,-1,-1, -1,-1,-1, &
        6, 7,11,  1, 6,11,  0, 6, 1,  6, 0, 8, -1,-1,-1, &
        5,11, 1,  2, 7,11,  6, 7, 2,  3, 9, 0, -1,-1,-1, &
        9, 1, 3,  9, 8, 1, 11, 1, 7,  7, 1, 6,  8, 6, 1, &
        1,10, 6,  1, 6, 3,  7, 3, 6, -1,-1,-1, -1,-1,-1, &
       11, 1,10,  6, 3, 1,  7, 3, 6,  2, 0, 8, -1,-1,-1, &
        9, 0, 1,  9, 1, 7,  7, 1, 6, 10, 6, 1, -1,-1,-1, &
        2, 1, 8,  1, 9, 8,  6, 1,10,  7, 1, 6,  1, 7, 9, &
        7, 3, 6,  6, 3, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        3, 0, 8,  6, 3, 8,  3, 6, 7, -1,-1,-1, -1,-1,-1, &
        7, 9, 0,  2, 7, 0,  7, 2, 6, -1,-1,-1, -1,-1,-1, &
        6, 9, 8,  6, 7, 9, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 4, 7, 11, 8, 7,  8,11,10, -1,-1,-1, -1,-1,-1, &
        2, 0, 4,  2, 4,10, 10, 4,11,  7,11, 4, -1,-1,-1, &
        6, 4, 7, 11, 8, 4, 10, 8,11,  9, 0, 3, -1,-1,-1, &
       11, 4, 7, 11,10, 4,  9, 4, 3,  3, 4, 2, 10, 2, 4, &
        2, 8, 4,  2, 4, 1,  4, 7, 1,  7,11, 1, -1,-1,-1, &
        7,11, 1,  7, 1, 4,  0, 4, 1, -1,-1,-1, -1,-1,-1, &
       11, 0, 3, 11, 1, 2,  8,11, 2,  8,11, 0,  9, 4, 7, &
        1, 7,11,  1, 3, 9,  4, 1, 9,  4, 1, 7, -1,-1,-1, &
        7, 3, 1, 10, 7, 1,  8, 7,10,  7, 8, 4, -1,-1,-1, &
        1,10, 3, 10, 7, 3,  0,10, 2,  4,10, 0, 10, 4, 7, &
        4, 7, 8,  7,10, 8,  0, 7, 9,  1, 7, 0,  7, 1,10, &
        4, 7, 9,  2, 1,10, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 8, 4,  7, 2, 4,  2, 7, 3, -1,-1,-1, -1,-1,-1, &
        7, 0, 4,  7, 3, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        7, 8, 4,  7, 9, 0,  2, 7, 0,  2, 7, 8, -1,-1,-1, &
        4, 7, 9, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        6, 4, 9,  6, 9,10, 11,10, 9, -1,-1,-1, -1,-1,-1, &
        5, 6, 4,  9,10, 6, 11,10, 9,  8, 2, 0, -1,-1,-1, &
       11,10, 6,  4,11, 6,  0,11, 4, 11, 0, 3, -1,-1,-1, &
        6, 4,10,  4,11,10,  2, 4, 8,  3, 4, 2,  4, 3,11, &
        1, 2, 6,  1, 6,11, 11, 6, 9,  4, 9, 6, -1,-1,-1, &
        8, 6, 0,  6, 1, 0,  9, 6, 4, 11, 6, 9,  6,11, 1, &
        3,11, 0, 11, 4, 0,  2,11, 1,  6,11, 2, 11, 6, 4, &
        3,11, 1,  8, 6, 4, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        1,10, 6,  1, 6, 3,  6, 4, 3,  4, 9, 3, -1,-1,-1, &
        9, 2, 0,  9, 3, 1, 10, 9, 1, 10, 9, 2,  8, 6, 4, &
        1,10, 6,  4, 1, 6,  1, 4, 0, -1,-1,-1, -1,-1,-1, &
        1, 8, 2,  1,10, 6,  4, 1, 6,  4, 1, 8, -1,-1,-1, &
        6, 4, 9,  3, 6, 9,  6, 3, 2, -1,-1,-1, -1,-1,-1, &
        6, 0, 8,  6, 4, 9,  3, 6, 9,  3, 6, 0, -1,-1,-1, &
        2, 4, 0,  2, 6, 4, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 6, 4, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11,10, 9,  9,10, 8, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       10, 2, 0,  9,10, 0, 10, 9,11, -1,-1,-1, -1,-1,-1, &
        8, 0, 3, 11, 8, 3,  8,11,10, -1,-1,-1, -1,-1,-1, &
       11, 2, 3, 11,10, 2, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11, 1, 2,  8,11, 2, 11, 8, 9, -1,-1,-1, -1,-1,-1, &
        9, 1, 0,  9,11, 1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       11, 0, 3, 11, 1, 2,  8,11, 2,  8,11, 0, -1,-1,-1, &
        3,11, 1, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        9, 3, 1, 10, 9, 1,  9,10, 8, -1,-1,-1, -1,-1,-1, &
        9, 2, 0,  9, 3, 1, 10, 9, 1, 10, 9, 2, -1,-1,-1, &
        0,10, 8,  0, 1,10, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 1,10, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        8, 3, 2,  8, 9, 3, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        0, 9, 3, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
        2, 8, 0, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, &
       -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1, -1,-1,-1  &
       /), shape(cubepoly) )


  ! interpolation
  nxdiv = (nx-1) * ndiv + 1
  nydiv = (ny-1) * ndiv + 1
  nzdiv = (nz-1) * ndiv + 1
  allocate( movaldiv(0:nxdiv-1,0:nydiv-1,0:nzdiv-1) )
  movaldiv = 0d0

  allocate( weight(0:1,0:1,0:1,0:ndiv,0:ndiv,0:ndiv) )
  do izdiv = 0, ndiv
  do iydiv = 0, ndiv
  do ixdiv = 0, ndiv
     x(0) = real(ixdiv) / ndiv
     y(0) = real(iydiv) / ndiv
     z(0) = real(izdiv) / ndiv
     x(1) = 1d0 - x(0)
     y(1) = 1d0 - y(0)
     z(1) = 1d0 - z(0)
     do jz = 0, 1
     do jy = 0, 1
     do jx = 0, 1
        weight(jx,jy,jz,ixdiv,iydiv,izdiv) = x(1-jx) * y(1-jy) * z(1-jz)
     end do
     end do
     end do
  end do
  end do
  end do

  do iz = 0, nz-2
  do iy = 0, ny-2
  do ix = 0, nx-2
     do izdiv = 0, ndiv
     do iydiv = 0, ndiv
     do ixdiv = 0, ndiv
        v = 0d0
        do jz = 0, 1
        do jy = 0, 1
        do jx = 0, 1
           v = v + moval(ix+jx,iy+jy,iz+jz) * weight(jx,jy,jz,ixdiv,iydiv,izdiv)
        end do
        end do
        end do
        ixx = ix * ndiv + ixdiv
        iyy = iy * ndiv + iydiv
        izz = iz * ndiv + izdiv
        movaldiv(ixx,iyy,izz) = v
     end do
     end do
     end do
  end do
  end do
  end do
  deallocate( weight )

  exdiv(:) = ex(:) / ndiv
  eydiv(:) = ey(:) / ndiv
  ezdiv(:) = ez(:) / ndiv

  ! determine each vertices wherther in/out of the threshold surface
  allocate( bvtx(0:nxdiv-1,0:nydiv-1,0:nzdiv-1) )
  bvtx(:,:,:) = 0
  do iz = 0, nzdiv-1
  do iy = 0, nydiv-1
  do ix = 0, nxdiv-1
     if( movaldiv(ix,iy,iz) > thres ) then
        bvtx(ix,iy,iz) = 1
     endif
  end do
  end do
  end do

  npoly = 0
  do iz = 0, nzdiv-2
  do iy = 0, nydiv-2
  do ix = 0, nxdiv-2
     
     posxyz(:) = (/ix, iy, iz/)

     icube = 0
     ibit = 1
     do k = 0, 1
     do j = 0, 1
     do i = 0, 1
        icube = icube + bvtx(ix+i,iy+j,iz+k) * ibit
        ibit = ibit * 2
     end do
     end do
     end do

     polys(:,:) = cubepoly(:,:,icube)

     do itri = 0, 4
        if( polys(1,itri) < 0 ) then
           exit
        end if

        triangle(:) = polys(:,itri)

        do imid = 0, 2
           pos0(:) = midvtx(:,0,triangle(imid))
           pos1(:) = midvtx(:,1,triangle(imid))
           moval0 = movaldiv( ix+pos0(0), iy+pos0(1), iz+pos0(2) )
           moval1 = movaldiv( ix+pos1(0), iy+pos1(1), iz+pos1(2) )
           dif01 = moval0 - moval1
           if( dif01 * dif01 < 1e-20 ) then
              pos(:) = ( pos0(:) + pos1(:) ) * 0.5
           else
              dif0 = moval0 - thres
              dif1 = moval1 - thres
              pos(:) = ( dif0 * pos1(:) - dif1 * pos0(:) ) / dif01
           endif
           pos(:) = pos(:) + posxyz(:)
           pos(:) = pos(0) * exdiv(:) + pos(1) * eydiv(:) + pos(2) * ezdiv(:)
           pos(:) = pos(:) + boxmin(:)

           midpos(:,imid) = pos(:)
        end do

        vec01(:) = midpos(:,1) - midpos(:,0)
        vec02(:) = midpos(:,2) - midpos(:,0)
        vnorm(0) = vec02(1) * vec01(2) - vec02(2) * vec01(1)
        vnorm(1) = vec02(2) * vec01(0) - vec02(0) * vec01(2)
        vnorm(2) = vec02(0) * vec01(1) - vec02(1) * vec01(0)
        v = sqrt( sum( vnorm(:) * vnorm(:) ) )
        if( v < 1d-10 ) cycle
        v = 1d0 / v
        vnorm(:) = vnorm(:) * v
        
        polygons(npoly,0,:) = midpos(:,0)
        polygons(npoly,1,:) = midpos(:,1)
        polygons(npoly,2,:) = midpos(:,2)
        polygons(npoly,3,:) = vnorm(:)
        npoly = npoly + 1

        if( npoly > maxpoly ) then
           deallocate( bvtx, movaldiv )
           return
        endif

     end do
  end do
  end do
  end do

  deallocate( bvtx, movaldiv )

End Subroutine make_polygons


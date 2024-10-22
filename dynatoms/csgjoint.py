from csg.core import CSG
from dynatoms.vtkmath import csgtovtk

def csgTSpin(rad,len,tolerance,scaling,detail):
    """
    Generates a T-spin joint using the constructive solid geometry (csg) library pycsg.
    ---- ----    Top disk
       | |       Top tube (Height is 'topheight')
     --- ---     Mid disk
     |     |     Bottom tube (Height is 'botheight')
     -------     Bottom disk
    Horizontal axes are scaled with the joint width scaling factor (relative to r). Vertical
    axes are not (relative to rad).
    """
    r = rad*scaling
    botheight, topheight = 0.4*rad, 0.3*rad #Need these two quantities to place visualization later.
    height = botheight+topheight
    bottom = -(height/2)

    bottomdisk = CSG.cylinder(radius = 0.8*r+tolerance/2, start = [0,bottom-tolerance/2,0],
                 end = [0,bottom+tolerance/2,0], slices = detail)

    bottomtube = CSG.cylinder(radius = 0.8*r+tolerance/2, start = [0,bottom,0],
                 end = [0,botheight,0], slices = detail) \
                 - CSG.cylinder(radius = 0.8*r-tolerance/2, start = [0,bottom,0],
                 end = [0,botheight,0], slices = detail)

    middisk = CSG.cylinder(radius = 0.8*r+tolerance/2, start = [0,botheight-tolerance/2,0],
              end = [0,botheight+tolerance/2,0], slices = detail) \
              - CSG.cylinder(radius = 0.6*r - tolerance/2, start = [0,botheight-tolerance/2,0],
              end = [0,botheight+tolerance/2,0], slices = detail)

    toptube = CSG.cylinder(radius = 0.6*r+tolerance/2, start = [0,botheight,0],
              end = [0,height,0], slices = detail) \
              - CSG.cylinder(radius = 0.6*r-tolerance/2, start = [0,botheight,0],
              end = [0,height,0], slices = detail)

    topdisk = CSG.cylinder(radius = r+tolerance/2, start = [0,height-tolerance/2,0],
              end = [0,height+tolerance/2,0], slices = detail) \
              - CSG.cylinder(radius = 0.6*r-tolerance/2, start = [0,height-tolerance/2,0],
              end = [0,height+tolerance/2,0], slices = detail)

    bond = CSG.cylinder(radius = r, start = [0,-(len/2),0], end = [0,len/2,0], slices = detail)
    minusjoint = bottomdisk + bottomtube + middisk + toptube + topdisk
    joint = bond-minusjoint

    return(csgtovtk(joint), botheight, topheight)

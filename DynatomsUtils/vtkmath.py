import numpy as np
import math
import itertools
import time

import vtk
import vtkInterface as vtki
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy

from csg.core import CSG
from csg.geom import *

def find_angle(a,b):
	"""
	Finds phi/rho angle between two 3D points.
	"""
	diff = (a-b)
	y = math.degrees(math.acos(diff[2]/np.linalg.norm(diff)))
	z = math.degrees(math.atan2(diff[1],diff[0]))

	return([0,y,z])

def csgtovtk(geom):
	"""
	From a PyCSG solid to vtk polydata object
	"""
	verts, polys, count = geom.toVerticesAndPolygons()

	points = vtk.vtkPoints()
	points.SetData(numpy_to_vtk(verts))

	cellArray = vtk.vtkCellArray()
	s1 = time.clock()
	cells = np.array(tuple(itertools.chain.from_iterable([[len(poly)]+poly for poly in polys])),
	                 dtype = np.int64)

	cellArray.SetCells(count, numpy_to_vtkIdTypeArray(cells))

	polydata = vtk.vtkPolyData()
	polydata.SetPoints(points)
	polydata.SetPolys(cellArray)

	return polydata

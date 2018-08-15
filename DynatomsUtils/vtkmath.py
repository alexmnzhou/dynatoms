import math
import numpy as np

def find_angle(a,b):
	diff = (a-b)
	y = math.degrees(math.acos(diff[2]/np.linalg.norm(diff)))
	z = math.degrees(math.atan2(diff[1],diff[0]))
	return([0,y,z])

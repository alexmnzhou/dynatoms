import numpy as np
import pybel

def open_mol_format(filepath):
	f = open(filepath)
	arr = list(map(str.split, f))
	for i in range(len(arr)):
	    if len(arr[i]) > 0:
	        if list(arr[i][-1])[0] == 'V': #Uses molfile version indicator to locate counts line
	            cts = i
	            break
	head = cts+1 #total number of lines in the header; must be skipped to read data
	atoms = []
	for i in range(len(arr[head:])):
	    aindex = i+head
	    if any(c.isalpha() for c in arr[aindex]):
	        atoms.append(arr[aindex])
	    else:
	        b_start = aindex
	        break
	atoms = np.array(atoms)
	bonds = []
	for i in range(len(arr[b_start:])):
	    bindex = i+b_start
	    if all(c.isdigit() for c in arr[bindex]):
	        bonds.append(arr[bindex])
	    else:
	        break
	bonds = np.array(bonds)
	types = np.array(atoms[:,3],dtype = 'str')
	coords = np.array(atoms[:,:3],dtype = 'float')
	bonded = np.array(bonds[:,:2],dtype = 'int')
	return(types,coords,bonded)

ob_log_handler = pybel.ob.OBMessageHandler()
ob_log_handler.SetOutputLevel(0) #Disable non-critical warnings
mol = next(pybel.readfile("cif","Examples/Molecules/HEBGAX.cif"))

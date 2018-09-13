#!/usr/bin/python3
# Dynatoms is released under the terms of the GPLv3 or higher.

import numpy as np
import pandas as pd
import pybel
import io

ob_log_handler = pybel.ob.OBMessageHandler()
ob_log_handler.SetOutputLevel(0) #Disable non-critical warnings

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
	types = np.array(atoms[:,3], dtype = 'str')
	coords = np.array(atoms[:,:3], dtype = 'float')
	bonded = np.array(bonds[:,:2],dtype = 'int')
	return(types,coords,bonded)

def open_mol_format2(filepath):
	mol = next(pybel.readfile("mol", filepath)).atoms
	types, coords = zip(*[(atom.type, atom.coords) for atom in mol])
	bonded = [bond for atom in mol for bond in bond_find(atom)]
	return(np.array(types,dtype='str'),np.array(coords,dtype='float'),np.array(bonded,dtype='int'))

def bonds_find(atom):
	return [[bond.GetBeginAtom().GetIdx(), bond.GetEndAtom().GetIdx()] for bond in pybel.ob.OBAtomBondIter(atom.OBAtom)]

def open_cif_format(filepath):
	mol = next(pybel.readfile("cif", filepath)).atoms
	types, coords = zip(*[(atom.type, atom.coords) for atom in mol])
	bonded = [bond for atom in mol for bond in bond_find(atom)]
	return(np.array(types),np.array(coords),np.array(bonded))

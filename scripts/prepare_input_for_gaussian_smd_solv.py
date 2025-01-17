#!/usr/bin/env python
# coding: utf-8


from rdkit import Chem
from gen_confs import  gen_confs_set
import numpy as np
import sys, os
import glob


element_dict = {1: "H", 6: "C", 7: "N", 8: "O", 16: "S", 9: "F", 17: "Cl"}


def filter_mol(mol, element_list=[1,6,7,8,9,16,17]):
    elements = all([atom.GetAtomicNum() in element_list for atom in mol.GetAtoms()])
    if elements:
        return True
    else:
        return False


def write_nocharge(fname, xyzblock, mcharge):
    input_file = fname
    name = os.path.basename(fname).replace(".gjf", "") 
    with open(input_file, "w") as f:
        f.write("%chk={}.chk".format(name) + "\n")
        f.write("%nproc=1\n")
        f.write("%mem=8GB\n")
        f.write("#P B3LYP/6-31G* opt\n")
        f.write("\n")
        f.write("Title Card Required\n")
        f.write("\n")
        f.write("{} 1\n".format( mcharge ))
        for line in xyzblock:
            f.write(line + "\n")
        f.write("\n")
        f.write("--Link1--\n")
        f.write("%chk={}.chk".format(name) + "\n")
        f.write("%nproc=1\n")
        f.write("%mem=8GB\n")
        f.write("#p M062X/6-31G* geom=checkpoint guess=read scrf=(smd,solvent=water,externaliteration,1stVac)\n")
        f.write("\n")
        f.write("Title Card Required\n")
        f.write("\n")
        f.write("{} 1\n".format( mcharge ))
        f.write("\n")
    return


def get_xyzblock(species, coords):
    xyzblock = []
    header = str(len(species)) + "\n"
    name = "structure\n"
    xyzblock.append(header)
    xyzblock.append(name)
    for idx in range(len(species)):
        atomic = species[idx]
        crds = coords[idx, :]
        element = element_dict[atomic]
        coordstring = " ".join([str(c) for c in crds])
        line = element + " " + coordstring + "\n"
        xyzblock.append(line)
    xyzblock_string = "".join(xyzblock)
    return xyzblock_string

def gen_gjf(mol, foname):
    if not mol:
        return
    if not filter_mol(mol):
        return
    name = foname
    mcharge = Chem.GetFormalCharge(mol)
    if mcharge < 0:
        foname = foname + "_neg"
    elif mcharge > 0:
        foname = foname + "_pos"
    xyzblock = Chem.MolToXYZBlock(mol).split("\n")[2:]
    if not os.path.exists(os.path.join("DFT_Calc", foname)):
        os.makedirs(os.path.join("DFT_Calc", foname))
    fname = os.path.join("DFT_Calc", foname, name+".gjf")
    Chem.MolToMolFile(mol, os.path.join("DFT_Calc", foname, name+".mol"))
    write_nocharge(fname, xyzblock, mcharge)
    return

if __name__=="__main__":
    smi = "CCCCCC"
    mol_name = "test_mol"
    block = gen_confs_set(smi, num_confs=1)[0]
    mol = Chem.MolFromMolBlock(block)
    gen_gjf( mol, mol_name )



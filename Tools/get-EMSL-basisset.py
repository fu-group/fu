#!/bin/sh
# -*- coding: utf-8

"""
A module that downloads a basis set from the Basis Set Exchange
website and converts it to the NTChem format.
"""

# Names for the different angular momentum values.
_moname = ["S", "P", "D", "F", "H"]

# Base URL for the basis set exchange
_bsse = "https://www.basissetexchange.org/"


def _convert_json_basis(json, atoms):
    """
    Given a json representation of a basis set, this converts it to the
    NTChem format.

    Args:
      json (dict): the json representation of the basis from Basis Set
        Exchange.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms in this basis.

    Returns:
      (str): a basis set string for NTChem.
    """

    # Convert this to the correct NTChem format
    outstr = " Basis\n"
    print(('atoms=',atoms))
    for sym, num in list(atoms.items()):
        outstr += sym + " 0\n"

        for shell in json["elements"][str(num)]["electron_shells"]:
            print(('shell=',shell))
            exponents = shell["exponents"]
            coefficients = shell["coefficients"]
            print(('len(exponents)=',len(exponents)))
            print(('len(coefficients)=', len(coefficients)))
            #try:
            momentums = shell["angular_momentum"]
            print(('mom=',momentums))
            for i in range(0, len(coefficients)):
                print(('i=',i))
                print(('momentums[0]=', momentums[0]))
                am = _moname[int(momentums[0])]
                print(('am=',am))
                outstr += am + " " + str(len(exponents)) + " 1.00\n"
                for j in range(0, len(exponents)):
                    print(('j,exponents[j]=',j,exponents[j]))
                    print(('i,j,coef=',i,j,coefficients[i][j]))
                    outstr += str(exponents[j]) + " "
                    outstr += str(coefficients[i][j]) + "\n"
            #except: pass
        outstr += "****\n"

    outstr += " End\n"

    return outstr

def _convert_json_ecp(json, atoms):
    """
    Given a json representation of a basis set, this converts it to the
    NTChem format.

    Args:
      json (dict): the json representation of the basis from Basis Set
        Exchange.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms in this basis.

    Returns:
      (str): a basis set string for NTChem.
    """

    # Convert this to the correct NTChem format
    outstr = " Basis\n"
    print(('atoms=',atoms))
    for sym, num in list(atoms.items()):
        outstr += sym + " 0\n"

        for shell in json["elements"][str(num)]["electron_shells"]:
            print(('shell=',shell))
            exponents = shell["exponents"]
            coefficients = shell["coefficients"]
            try:
                momentums = shell["angular_momentum"]

                for i in range(0, len(coefficients)):
                    am = _moname[int(momentums[i])]
                    outstr += am + " " + str(len(exponents)) + " 1.00\n"
                    for j in range(0, len(exponents)):
                        outstr += str(exponents[j]) + " "
                        outstr += str(coefficients[i][j]) + "\n"
            except: pass
        outstr += "****\n"

    outstr += " End\n"

    return outstr


def get_gaussian_basis(name, atoms):
    """
    Retrieves the desired gaussian basis from the basis set exchange.
    https://www.basissetexchange.org/

    Args:
      name (str): the name of the basis set you want.
      atoms (dict): a dictionary mapping atomic symbols to atomic numbers for
        the atoms you want.

    Returns:
      (str): the NTChem representation of the basis.
    """
    import requests

    # First check that this basis is available
    r = requests.get(_bsse + '/api/metadata')
    print(('r.keys=',list(r.json().keys())))
    if name.lower() not in list(r.json().keys()):
        raise ValueError("Basis set not available.")

    # Now download the basis set for the desired atoms
    elstr = "/?elements=" + ','.join([str(x) for x in list(atoms.values())])
    basstr = _bsse + '/api/basis/'+name.lower()+'/format/json'
    r = requests.get(basstr+elstr).json()
    print(('r=',r))
    return _convert_json_basis(r, atoms)


if __name__ == "__main__":
    # Be sure to specify the same name as listed on the website.
    basis_name = "def2-SVP"
    #basis_name="LANL2DZ"
    # This dictionary parameter is necessary because we need to know how
    # to convert from atomic number to atomic symbol.
    atoms = {"H": 1, "Cl": 17, "Bi": 81}
    #atoms={"Fe": 26}
    basis = get_gaussian_basis(basis_name, atoms)

    print(basis)

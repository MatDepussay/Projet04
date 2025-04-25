import pytest 
from src.data import *
from src.affichage import afficherCarte
from src.app import menu_terminal

def test_modification_liaison_ameliore_flot():
    original = ListeLiaison[:]
    modifiee = [l if l.depart != "A" or l.arrivee != "E" else liaison("A", "E", 15) for l in ListeLiaison]
    
    flot_avant, _ = ReseauHydraulique(ListeNoeuds, original).calculerFlotMaximal()
    flot_apres, _ = ReseauHydraulique(ListeNoeuds, modifiee).calculerFlotMaximal()
    
    assert flot_apres.flow_value > flot_avant.flow_value


def test_liaison_inexistante():
    assert not liaison_existe("Z", "Q", ListeLiaison)

def test_creation_noeud():
    n = noeud("A", "source", 10)
    assert n.nom == "A"
    assert n.type == "source"
    assert n.capaciteMax == 10
import pytest
from src.data import ReseauHydraulique, ListeLiaison, liaison_existe, noeud, calculerFlotMaximal

def test_liaison_existe():
    assert liaison_existe("A","E", ListeLiaison) == True
    assert liaison_existe("A", "H", ListeLiaison) == False
    assert liaison_existe("E", "A", ListeLiaison) == False
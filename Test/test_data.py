import pytest 
from src.data import *

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

def test_liaison_existe():
    assert liaison_existe("A","E", ListeLiaison) == True
    assert liaison_existe("A", "H", ListeLiaison) == False
    assert liaison_existe("E", "A", ListeLiaison) == False

def test_optimiser_liaisons_priorise_meilleure_liaison():
    
    liste_noeuds = [
        noeud("A", "source", 10),
        noeud("B", "intermediaire"),
        noeud("C", "ville", 10),
    ]

    
    liste_liaisons = [
        liaison("A", "B", 1),  
        liaison("B", "C", 1),  
    ]

    
    liaisons_a_optimiser = [("A", "B"), ("B", "C")]

    
    config_finale, travaux = optimiser_liaisons(liste_liaisons, liaisons_a_optimiser)
    assert len(travaux) == 2
    assert travaux[0][2] <= travaux[1][2]  

 
    for _, cap, _ in travaux:
        assert 1 <= cap <= 20
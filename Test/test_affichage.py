import sys
import os
import pytest
import numpy as np
from unittest.mock import MagicMock
import matplotlib
matplotlib.use('Agg')  # backend non interactif pour tests
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import ReseauHydraulique, Liaison, Noeud
from affichage import afficherCarte, afficherCarteEnoncer

def test_afficherCarte_raises_without_noeuds_ou_liaisons():
    with pytest.raises(ValueError, match="Il faut fournir les noeuds et liaisons"):
        afficherCarte()
        
def test_afficherCarte_affichage_simple():
    noeuds = [
        Noeud(nom="A", type="source", capaciteMax=5),
        Noeud(nom="B", type="ville", capaciteMax=5)
    ]
    liaisons = [Liaison(depart="A", arrivee="B", capacite=5)]
    fig = afficherCarte(noeuds=noeuds, liaisons=liaisons)
    assert fig is not None
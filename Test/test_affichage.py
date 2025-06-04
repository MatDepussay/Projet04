import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # backend non interactif pour tests
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import ReseauHydraulique, Liaison, Noeud
from affichage import afficherCarte, afficherCarteEnoncer


# Tests AfficheCarte


def make_noeuds_liaisons():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "ville", 5),
        # plus de "super_source" ni "super_puits"
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("super_source", "A", 10),  # OK, on utilise les noms, mais pas dans noeuds
        Liaison("B", "super_puits", 5)
    ]
    # Construire index_noeuds juste avec les noeuds de la liste (sans super_*)
    index_noeuds = {n.nom: i for i, n in enumerate(noeuds)}
    # Mais pour le test on ajoute manuellement les super_source et super_puits en index supérieurs
    index_noeuds.update({"super_source": len(noeuds), "super_puits": len(noeuds) + 1})
    return noeuds, liaisons, index_noeuds

def test_afficherCarte_sans_result_erreur_si_args_manquants():
    with pytest.raises(ValueError):
        afficherCarte()

def test_afficherCarte_retourne_figure_basique():
    noeuds, liaisons, index_noeuds = make_noeuds_liaisons()

    fig = afficherCarte(noeuds=noeuds, liaisons=liaisons)
    assert isinstance(fig, plt.Figure)

def test_afficherCarte_avec_result_mock(monkeypatch):
    noeuds, liaisons, index_noeuds = make_noeuds_liaisons()

    result = MagicMock()

    import numpy as np

    # CORRECTION ICI : on prend len(index_noeuds), pas len(noeuds)
    size = len(index_noeuds)
    flow_array = np.zeros((size, size))

    flow_array[index_noeuds["B"], index_noeuds["super_puits"]] = 3
    flow_array[index_noeuds["super_source"], index_noeuds["A"]] = 7
    result.flow = flow_array
    result.flow_value = 10

    # Mock de la méthode liaisons_saturees
    def mock_liaisons_saturees(self, result, index):
        return [("A", "B", 5)]

    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)

    fig = afficherCarte(
        result=result,
        index_noeuds=index_noeuds,
        noeuds=noeuds,
        liaisons=liaisons,
        montrer_saturees=True
    )

def test_afficherCarte_avec_liaisons_saturees(monkeypatch):
    noeuds, liaisons, index_noeuds = make_noeuds_liaisons()

    result = MagicMock()
    import numpy as np
    flow_array = np.zeros((len(index_noeuds), len(index_noeuds)))
    result.flow = flow_array
    result.flow_value = 0

    def mock_liaisons_saturees(self, result, index):
        return []
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)

    fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=noeuds, liaisons=liaisons, montrer_saturees=True)
    assert isinstance(fig, plt.Figure)

## Test afficherCarteEnoncer

def test_afficherCarteEnoncer_genere_figure():
    import numpy as np
    from unittest.mock import MagicMock

    # Données de test simples
    noeuds = [
        Noeud("S", "source", capaciteMax=10),
        Noeud("V", "ville", capaciteMax=8),
        Noeud("X", "intermediaire")
    ]

    liaisons = [
        Liaison("S", "X", 5),
        Liaison("X", "V", 5)
    ]

    # Génère index_noeuds juste pour simuler un environnement complet
    index_noeuds = {n.nom: i for i, n in enumerate(noeuds)}

    # Mock du résultat avec un flow_value
    result = MagicMock()
    result.flow_value = 7  # peut être arbitraire ici

    # Appel de la fonction
    fig = afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, noeuds=noeuds, liaisons=liaisons)

    # Vérifie que la fonction retourne bien une figure matplotlib
    assert isinstance(fig, plt.Figure)


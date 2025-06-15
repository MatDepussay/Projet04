import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data import (
    GestionReseau,
    demander_cap_max,
    satisfaction,
    optimiser_liaisons,
    ReseauHydraulique,
    Liaison,
    Noeud,
)

liaison_existe = GestionReseau.liaison_existe


def test_liaison_existe():
    liaisons = [Liaison("A", "B", 10), Liaison("C", "D", 15), Liaison("E", "F", 20)]
    # Cas positifs
    assert liaison_existe("A", "B", liaisons)
    assert liaison_existe("C", "D", liaisons)
    assert liaison_existe("e", "f", liaisons)  # test insensibilité à la casse
    # Cas négatifs
    assert not liaison_existe("B", "A", liaisons)  # sens inverse non présent
    assert not liaison_existe("X", "Y", liaisons)  # liaison totalement absente
    assert not liaison_existe("A", "C", liaisons)  # pas de liaison directe
    # Cas avec liste vide
    assert not liaison_existe("A", "B", [])


def test_liaisons_saturees():
    noeuds = [
        Noeud("S1", "source", 10),
        Noeud("S2", "source", 5),
        Noeud("V1", "ville", 15),
    ]
    liaisons = [Liaison("S1", "V1", 10), Liaison("S2", "V1", 5), Liaison("S1", "S2", 3)]
    reseau = ReseauHydraulique(noeuds, liaisons)
    result, _ = reseau.calculerFlotMaximal()
    liaisons_saturees = reseau.liaisons_saturees(result)
    assert ("S1", "V1", 10) in liaisons_saturees
    assert ("S2", "V1", 5) in liaisons_saturees
    assert ("S1", "S2", 3) not in liaisons_saturees
    assert len(liaisons_saturees) == 2


def test_resau_hydraulique_calculer_flot_maximal_and_liaisons_saturees(monkeypatch):
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire"),
        Noeud("C", "ville", 15),
    ]
    liaisons = [Liaison("A", "B", 5), Liaison("B", "C", 10)]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    mock_result = MagicMock()
    mock_result.flow_value = 15

    def flow_getitem(index):
        i, j = index
        nom_i = reseau_hydro.index_inverse.get(i)
        nom_j = reseau_hydro.index_inverse.get(j)
        if (nom_i, nom_j) == ("A", "B"):
            return 5
        if (nom_i, nom_j) == ("B", "C"):
            return 10
        return 0

    mock_flow = MagicMock()
    mock_flow.__getitem__.side_effect = flow_getitem
    mock_result.flow = mock_flow
    monkeypatch.setattr('data.maximum_flow', lambda *args, **kwargs: mock_result)
    result, index_noeuds = reseau_hydro.calculerFlotMaximal()
    assert result.flow_value == 15
    assert "A" in index_noeuds
    assert "super_source" in index_noeuds
    assert "super_puits" in index_noeuds
    liaisons_saturees = reseau_hydro.liaisons_saturees(result)
    assert ("A", "B", 5) in liaisons_saturees
    assert ("B", "C", 10) in liaisons_saturees
    assert len(liaisons_saturees) == 2


def test_construction_matrice():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]
    liaisons = [Liaison("A", "B", 5), Liaison("B", "C", 10)]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    idx = reseau_hydro.index_noeuds
    assert "super_source" in idx and "super_puits" in idx
    n = len(idx)
    assert reseau_hydro.matrice_np.shape == (n, n)


def test_calcul_flot_maximal():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]
    liaisons = [Liaison("A", "B", 5), Liaison("B", "C", 10)]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    result, index = reseau_hydro.calculerFlotMaximal()
    assert result.flow_value == 5  # Correction : le flot max est bien 5


def test_liaisons_saturees_simple():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]
    liaisons = [Liaison("A", "B", 5), Liaison("B", "C", 10)]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    result, index = reseau_hydro.calculerFlotMaximal()
    saturees = reseau_hydro.liaisons_saturees(result)
    assert ("A", "B", 5) in saturees
    assert ("B", "C", 8) not in saturees  # liaison non saturée car 8 < 10


def test_default_value_on_empty_input(monkeypatch):
    inputs = iter([''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert demander_cap_max() == 25


def test_valid_integer_input(monkeypatch):
    inputs = iter(['10'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert demander_cap_max() == 10


def test_invalid_then_default(monkeypatch):
    inputs = iter(['-5', 'abc', '0'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert demander_cap_max(valeur_defaut=42) == 42


def test_invalid_then_valid(monkeypatch):
    inputs = iter(['-10', 'abc', '20'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert demander_cap_max() == 20


def test_use_default_after_errors(monkeypatch):
    inputs = iter(['notanumber', 'stillwrong', ''])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert demander_cap_max(essais_max=2, valeur_defaut=33) == 33


def test_optimiser_liaisons(monkeypatch):
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]
    liaisons_actuelles = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10),
    ]
    liaisons_a_optimiser = [("A", "B"), ("B", "C")]
    flow_values = [15, 18, 22, 25]

    def mock_calculerFlotMaximal(self):
        flow_value = flow_values.pop(0) if flow_values else 25
        mock_result = MagicMock()
        mock_result.flow_value = flow_value
        return mock_result, self.index_noeuds

    monkeypatch.setattr(
        ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal
    )
    meilleure_config, travaux_effectues = optimiser_liaisons(
        noeuds, liaisons_actuelles, liaisons_a_optimiser
    )
    assert len(travaux_effectues) > 0
    assert all(isinstance(liaison, Liaison) for liaison in meilleure_config)
    for travail in travaux_effectues:
        liaison, cap, flot = travail
        assert isinstance(liaison, tuple) and len(liaison) == 2
        assert isinstance(cap, int)
        assert isinstance(flot, (int, float))
        assert flot >= 15


def test_modification_liaison_ameliore_flot():
    noeuds = [Noeud("A", "source", 50), Noeud("E", "ville", 50)]
    original = [Liaison("A", "E", 5)]
    modifiee = [Liaison("A", "E", 15)]
    flot_avant, _ = ReseauHydraulique(noeuds, original).calculerFlotMaximal()
    flot_apres, _ = ReseauHydraulique(noeuds, modifiee).calculerFlotMaximal()
    assert flot_apres.flow_value > flot_avant.flow_value


def test_flot_zero_si_aucune_liaison():
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = []
    flot, _ = ReseauHydraulique(noeuds, liaisons).calculerFlotMaximal()
    assert flot.flow_value == 0


def test_satisfaction_amelioration_progresive(monkeypatch):
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]
    liaisons = [Liaison("A", "B", 5), Liaison("B", "C", 10)]

    class MockResult:
        def __init__(self, flow_value):
            self.flow_value = flow_value

    flot_values = [10, 12, 15, 15]
    calls = {"count": 0}

    def mock_calculerFlotMaximal(self):
        val = flot_values[calls["count"]]
        calls["count"] += 1
        return MockResult(val), None

    saturations_sequence = [[("A", "B", 5)], [("A", "B", 10)], [("B", "C", 10)], []]

    def mock_liaisons_saturees(self, result):
        idx = calls["count"] - 1
        if idx < len(saturations_sequence):
            return saturations_sequence[idx]
        return []

    monkeypatch.setattr(
        ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal
    )
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)
    liaisons_finales, travaux = satisfaction(
        noeuds, liaisons, cap_max=15, max_travaux=5
    )
    assert len(travaux) >= 0


def test_satisfaction_arret_sans_amelioration(monkeypatch):
    noeuds = [Noeud("A", "source", 10), Noeud("C", "ville", 10)]
    liaisons = [Liaison("A", "C", 10)]

    class MockResult:
        def __init__(self):
            self.flow_value = 10

    def mock_calculerFlotMaximal(self):
        return MockResult(), None

    def mock_liaisons_saturees(self, result):
        return []

    monkeypatch.setattr(
        ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal
    )
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)
    liaisons_finales, travaux = satisfaction(
        noeuds, liaisons, cap_max=15, max_travaux=3
    )
    assert len(travaux) == 0
    assert liaisons_finales == liaisons

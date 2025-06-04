import sys
import os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import demander_cap_max, satisfaction, optimiser_liaisons, ReseauHydraulique, Liaison, Noeud

def test_liaison_existe():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire",3),
        Noeud("C", "intermediaire"),
        Noeud("E", "intemediaire"),
        Noeud("F","ville", 5)
    ]
    
    liaisons = [
        Liaison("A", "B", 10),
        Liaison("C", "D", 15),
        Liaison("E", "F", 20)
    ]

    # Cas positifs
    assert liaison_existe("A", "B", liaisons) 
    assert liaison_existe("C", "D", liaisons) 
    assert liaison_existe("e", "f", liaisons)   # test insensibilité à la casse

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
        Noeud("V1", "ville", 15)
    ]

    liaisons = [
        Liaison("S1", "V1", 10), 
        Liaison("S2", "V1", 5), 
        Liaison("S1", "S2", 3)
    ]

    reseau = ReseauHydraulique(noeuds, liaisons)

    result, index_noeuds = reseau.calculerFlotMaximal()
    liaisons_saturees = reseau.liaisons_saturees(result, index_noeuds)

    print("\n🔍 Liaisons saturées détectées :")
    for l in liaisons_saturees:
        print(f"  {l[0]} ➝ {l[1]} (capacité : {l[2]})")

    # Assertions de test
    assert ("S1", "V1", 10) in liaisons_saturees
    assert ("S2", "V1", 5) in liaisons_saturees
    assert ("S1", "S2", 3) not in liaisons_saturees
    assert len(liaisons_saturees) == 2


def test_resau_hydraulique_calculer_flot_maximal_and_liaisons_saturees(monkeypatch):
    # Création des noeuds et liaisons
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire"),
        Noeud("C", "ville", 15)
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10)
    ]

    reseau_hydro = ReseauHydraulique(noeuds, liaisons)

    # Création du mock pour le résultat de maximum_flow
    mock_result = MagicMock()
    mock_result.flow_value = 15

    # mock_result.flow doit permettre l'accès flow[i,j]
    def flow_getitem(index):
        i, j = index
        # On mappe les indices selon les liaisons
        nom_i = reseau_hydro.index_inverse.get(i)
        nom_j = reseau_hydro.index_inverse.get(j)

        if (nom_i, nom_j) == ("A", "B"):
            return 5
        if (nom_i, nom_j) == ("B", "C"):
            return 10
        return 0

    # flow est un mock avec __getitem__ redéfini
    mock_flow = MagicMock()
    mock_flow.__getitem__.side_effect = flow_getitem
    mock_result.flow = mock_flow

    # Patch de maximum_flow dans ton module (adapter le chemin)
    monkeypatch.setattr('data.maximum_flow', lambda *args, **kwargs: mock_result)

    # Appel
    result, index_noeuds = reseau_hydro.calculerFlotMaximal()

    assert result.flow_value == 15
    assert "A" in index_noeuds
    assert "super_source" in index_noeuds
    assert "super_puits" in index_noeuds

    liaisons_saturees = reseau_hydro.liaisons_saturees(result, index_noeuds)
    assert ("A", "B", 5) in liaisons_saturees
    assert ("B", "C", 10) in liaisons_saturees
    assert len(liaisons_saturees) == 2

def test_construction_matrice():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15)
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10)
    ]

    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    idx = reseau_hydro.index_noeuds

    # Vérifie que la super source et super puits existent
    assert "super_source" in idx and "super_puits" in idx

    # Vérifie dimensions de la matrice
    n = len(idx)
    assert reseau_hydro.matrice_np.shape == (n, n)

def test_calcul_flot_maximal():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15)
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10)
    ]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    result, index = reseau_hydro.calculerFlotMaximal()
    assert result.flow_value == 8  # S1 peut fournir 10, mais V1 ne peut en recevoir que 8

def test_liaisons_saturees():
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15)
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10)
    ]
    reseau_hydro = ReseauHydraulique(noeuds, liaisons)
    result, index = reseau_hydro.calculerFlotMaximal()
    saturees = reseau_hydro.liaisons_saturees(result, index)

    assert ("A", "B", 5) in saturees
    assert ("B", "C", 8) not in saturees  # liaison non saturée car 8 < 10

## Tests Demander_cap_max

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

## Tests optimiser_liaisons

def test_optimiser_liaisons(monkeypatch):
    # Création de noeuds fictifs
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15),
    ]

    # Liaison actuelle
    liaisons_actuelles = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10),
    ]

    # Liaisons qu'on veut optimiser
    liaisons_a_optimiser = [("A", "B"), ("B", "C")]

    # Fonction pour mocker le flot maximal et simuler un gain progressif
    # On va retourner un flux croissant pour simuler optimisation réussie
    flow_values = [15, 18, 22, 25]  # Valeurs à retourner successivement
    
    def mock_calculerFlotMaximal(self):
        # Prend le flot actuel et renvoie un mock résultat avec flow_value progressif
        flow_value = flow_values.pop(0) if flow_values else 25
        mock_result = MagicMock()
        mock_result.flow_value = flow_value
        return mock_result, self.index_noeuds

    # Patch de la méthode calculerFlotMaximal dans ReseauHydraulique
    monkeypatch.setattr(ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal)

    # Appel de la fonction à tester
    meilleure_config, travaux_effectues = optimiser_liaisons(noeuds, liaisons_actuelles, liaisons_a_optimiser)

    # Vérifications
    # Au moins un travail a été fait (car on simule un gain progressif)
    assert len(travaux_effectues) > 0

    # La meilleure configuration doit être une liste de Liaison
    assert all(isinstance(l, Liaison) for l in meilleure_config)

    # Vérifier que chaque travail a un tuple avec liaison, capacité et flot
    for travail in travaux_effectues:
        liaison, cap, flot = travail
        assert isinstance(liaison, tuple) and len(liaison) == 2
        assert isinstance(cap, int)
        assert isinstance(flot, (int, float))
        assert flot >= 15  # puisque 15 est notre flot initial simulé

    # Optionnel : on peut vérifier que la fonction s'arrête quand aucun gain n’est possible
    # Donc pas plus d’itérations que liaisons_a_optimiser

    # Affichage (facultatif, pour debug)
    print("Travaux effectués :", travaux_effectues)

def test_modification_liaison_ameliore_flot():
    noeuds = [
        Noeud("A", "source", 50),
        Noeud("E", "ville", 50)
    ]
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
    # Préparer noeuds et liaisons
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire", 0),
        Noeud("C", "ville", 15)
    ]
    liaisons = [
        Liaison("A", "B", 5),
        Liaison("B", "C", 10)
    ]

    # Mock de resultats de flot pour simuler augmentation progressive
    class MockResult:
        def __init__(self, flow_value):
            self.flow_value = flow_value

    # Séquence des flots renvoyés par calculerFlotMaximal, simulant augmentation progressive
    flot_values = [10, 12, 15, 15]
    calls = {"count": 0}

    def mock_calculerFlotMaximal():
        val = flot_values[calls["count"]]
        calls["count"] += 1
        return MockResult(val), None

    # Liste des liaisons saturées simulées à chaque étape
    saturations_sequence = [
        [("A", "B", 5)],        # étape 1 : liaison A->B saturée à 5
        [("A", "B", 10)],       # étape 2 : liaison A->B saturée à 10 (après augmentation)
        [("B", "C", 10)],       # étape 3 : liaison B->C saturée à 10
        []                      # étape 4 : plus rien à saturer, fin
    ]

    def mock_liaisons_saturees(result, index):
        idx = calls["count"] - 1
        if idx < len(saturations_sequence):
            return saturations_sequence[idx]
        return []

    # Patch des méthodes
    monkeypatch.setattr(ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal)
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)

    # Appel de la fonction à tester
    liaisons_finales, travaux = satisfaction(noeuds, liaisons, cap_max=15, max_travaux=5)

    # Vérifications
    # - On a fait au moins 2 travaux (car flot augmente 10->12->15)
    assert len(travaux) >= 2

    # - Capacités des liaisons ont augmenté (par exemple, la liaison A->B passe à 10)
    assert any(l.capacite > 5 for l in liaisons_finales if l.depart == "A" and l.arrivee == "B")

    # - Le flot final atteint au moins 15 (dernier flot simulé)
    assert travaux[-1][2] == 15

    # - Travaux correspondent bien aux augmentations effectuées
    for ((depart, arrivee), cap, flot) in travaux:
        assert isinstance(depart, str)
        assert isinstance(arrivee, str)
        assert cap <= 15
        assert flot >= 10

def test_satisfaction_arret_sans_amelioration(monkeypatch):
    # Noeuds et liaisons simples
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("C", "ville", 10)
    ]
    liaisons = [
        Liaison("A", "C", 10)
    ]

    class MockResult:
        def __init__(self):
            self.flow_value = 10

    # Mock calcule toujours le même flot sans amélioration possible
    def mock_calculerFlotMaximal():
        return MockResult(), None

    # Aucune liaison saturée (car flux ne peut augmenter)
    def mock_liaisons_saturees(result, index):
        return []

    monkeypatch.setattr(ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal)
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)

    liaisons_finales, travaux = satisfaction(noeuds, liaisons, cap_max=15, max_travaux=3)

    # Pas de travaux effectués car aucune amélioration
    assert len(travaux) == 0
    # Les liaisons finales sont égales aux initiales
    assert liaisons_finales == liaisons

def test_satisfaction_objectif_utilisateur(monkeypatch):
    # Noeuds et liaisons simples
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("C", "ville", 20)
    ]
    liaisons = [
        Liaison("A", "C", 10)
    ]

    class MockResult:
        def __init__(self, flow_value):
            self.flow_value = flow_value

    flot_values = [5, 10, 20]
    calls = {"count": 0}

    def mock_calculerFlotMaximal():
        val = flot_values[calls["count"]]
        calls["count"] += 1
        return MockResult(val), None

    saturations_sequence = [
        [("A", "C", 10)],
        [("A", "C", 15)],
        []
    ]

    def mock_liaisons_saturees(result, index):
        idx = calls["count"] - 1
        if idx < len(saturations_sequence):
            return saturations_sequence[idx]
        return []

    monkeypatch.setattr(ReseauHydraulique, "calculerFlotMaximal", mock_calculerFlotMaximal)
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", mock_liaisons_saturees)

    objectif = 20
    liaisons_finales, travaux = satisfaction(noeuds, liaisons, objectif=objectif, cap_max=20, max_travaux=5)

    # Le flot final doit être >= objectif
    assert travaux[-1][2] >= objectif
    # La fonction s'arrête quand l'objectif est atteint
    assert len(travaux) <= 5


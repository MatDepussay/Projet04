import sys
import os
from unittest.mock import patch
from pyinstrument import Profiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import optimiser_liaisons, satisfaction, liaison_existe, ReseauHydraulique, Liaison, Noeud
from affichage import afficherCarte, afficherCarteEnoncer
from app import menu_terminal, menu_generalisation, menu_demarrage


def profiler_satisfaction_scenario_simple():
    """Profilage manuel du scénario de satisfaction — à exécuter manuellement pour analyser les performances"""

    noeuds = [
        Noeud("A", "source", 50),
        Noeud("B", "intermediaire"),
        Noeud("C", "ville", 50)
    ]

    liaisons = [
        Liaison("A", "B", 20),
        Liaison("B", "C", 10)
    ]

    liaisons_possibles = [(liaison.depart, liaison.arrivee) for liaison in liaisons]
    objectif_flot = 50

    profiler = Profiler()
    profiler.start()

    satisfaction(
        noeuds=noeuds,
        liaisons_actuelles=liaisons,
        liaisons_possibles=liaisons_possibles,
        objectif_flot=objectif_flot
    )

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

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

def test_noeud_to_dict():
    noeuds = Noeud("A", "source", 100)
    d = noeuds.to_dict()
    assert d == {"nom": "A", "type": "source", "capaciteMax": 100}
    assert not d == {"nom": "A", "type": "source", "capaciteMax": 90}
    assert not d == {"nom": "A", "type": "ville", "capaciteMax": 100}
    assert not d == {"nom": "B", "type": "source", "capaciteMax": 100}

def test_liaison_to_dict():
    liaisons = Liaison("A", "B", 50)
    d = liaisons.to_dict()
    assert d == {"depart": "A", "arrivee": "B", "capacite": 50}
    assert not d == {"depart": "A", "arrivee": "B", "capacite": 100}
    assert not d == {"depart": "B", "arrivee": "A", "capacite": 50}
    assert not d == {"depart": "C", "arrivee": "C", "capacite": 50}

def test_str_reseau_vide():
    reseau = ReseauHydraulique([], [])
    rep = str(reseau)
    assert "--- Noeuds ---" in rep
    assert "--- Liaisons ---" in rep

def test_reseau_hydraulique_str():
    noeuds = [Noeud("A", "source", 100), Noeud("B", "ville", 50)]
    liaisons = [Liaison("A", "B", 70)]
    reseau = ReseauHydraulique(noeuds, liaisons)

    rep = str(reseau)
    assert "--- Noeuds ---" in rep
    assert "Nom : A" in rep
    assert "--- Liaisons ---" in rep
    assert "Départ : A" in rep

def test_creation_noeud():
    n = Noeud("A", "source", 10)
    assert n.nom == "A"
    assert n.type == "source"
    assert n.capaciteMax == 10

def test_liaison_existe():
    liaisons = [Liaison("A", "E", 10), Liaison("B", "C", 15)]
    assert liaison_existe("A", "E", liaisons)
    assert not liaison_existe("A", "H", liaisons)

def test_flot_zero_si_aucune_liaison():
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = []
    flot, _ = ReseauHydraulique(noeuds, liaisons).calculerFlotMaximal()
    assert flot.flow_value == 0

def test_optimiser_liaisons_priorise_meilleure_liaison():
    noeuds = [Noeud("A", "source", 10), Noeud("B", "intermediaire"), Noeud("C", "ville", 10)]
    liaisons = [Liaison("A", "B", 1), Liaison("B", "C", 1)]
    possibles = [("A", "B"), ("B", "C")]

    config_finale, travaux = optimiser_liaisons(noeuds, liaisons, possibles)

    assert len(travaux) == 2
    assert travaux[0][2] <= travaux[1][2]  # Capacité

def test_optimisation_break_quand_aucune_amélioration():
    noeuds = [Noeud("A", "source", 5), Noeud("B", "ville", 5)]
    liaisons = [Liaison("A", "B", 5)]
    possibles = [("A", "B")]

    _, travaux = satisfaction(
        noeuds=noeuds,
        liaisons_actuelles=liaisons,
        liaisons_possibles=possibles,
        objectif_flot=5
    )

    assert len(travaux) <= 1

def test_menu_travaux(monkeypatch, capsys):
    inputs = iter([
        "3",    
        "A", "E",
        "I", "L",
        "n",    
        "5"     
    ])
    
    monkeypatch.setattr("builtins.input", lambda _: next(inputs)) #monkeypatch input pour simuler les entrées utilisateur

    menu_terminal()
    
    out, _ = capsys.readouterr()

    assert "Optimisation de l’ordre des travaux" in out
    assert "Travaux #1" in out
    assert "Au revoir" in out

def simulate_inputs(inputs):
    """ Utilitaire pour simuler les inputs utilisateur """
    return lambda _: next(inputs)

def test_menu_terminal_option_0_ajout_elements(monkeypatch, capsys):
    # Simule la navigation pour ajouter un élément puis retour au menu principal
    inputs = iter([
        "0",  # Ajouter élément
        "5",  # Retour dans menu_ajout_elements
        "5"   # Quitter menu_terminal
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Ajouter un élément" in out or "Choix invalide" not in out

def test_menu_terminal_option_1_affiche_carte_enoncer(monkeypatch, capsys):
    inputs = iter([
        "1",  # Afficher carte de l’énoncé
        "5"   # Quitter
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Carte des Liaisons" in out or "Flot maximal" in out

def test_menu_terminal_option_2_affiche_carte_flot_max(monkeypatch, capsys):
    inputs = iter([
        "2",  # Afficher carte avec flot maximal
        "5"   # Quitter
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Carte" in out or "flot" in out

def test_menu_terminal_option_3_travaux_optimisation(monkeypatch, capsys):
    # On choisit une liaison existante puis arrête la sélection
    inputs = iter([
        "3",     # Choix travaux
        "A", "B",  # liaison valide
        "n",     # ne pas ajouter autre liaison
        "5"      # Quitter
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Optimisation" in out or "Travaux" in out

def test_menu_terminal_option_3_travaux_liaison_invalide(monkeypatch, capsys):
    inputs = iter([
        "3",
        "X", "Y",   # Liaison inexistante
        "A", "B",   # Liaison valide
        "n",        # Fin sélection
        "5"
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "n’existe pas" in out or "Optimisation" in out

def test_menu_terminal_option_4_generalisation(monkeypatch, capsys):
    inputs = iter([
        "4",  # Menu généralisation
        "3",  # Retour menu généralisation
        "5"   # Quitter menu principal
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "MENU GÉNÉRALISATION" in out

def test_menu_terminal_option_5_quitter(monkeypatch, capsys):
    inputs = iter([
        "5"  # Quitter
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Au revoir" in out

def test_menu_option_invalide(monkeypatch, capsys):
    inputs = iter(["xyz", "5"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Choix invalide" in out

### Tests du sous-menu généralisation ###

def test_menu_generalisation_option_1_optimiser(monkeypatch, capsys):
    inputs = iter([
        "1",  # Optimiser liaisons
        "3"   # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "Approvisionner" in out
    assert "Travaux effectués" in out or "Résultat final" in out

def test_menu_generalisation_option_2_assèchement(monkeypatch, capsys):
    # Simule le cas avec au moins une source
    inputs = iter([
        "2",  # Assèchement aléatoire d’une source
        "A", "B",  # Liaison à mettre en travaux (supposons valide)
        "3"   # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    
    # Patch liaison_existe pour que la liaison (A,B) existe
    with patch("data.liaison_existe", return_value=True):
        menu_generalisation()
    
    out, _ = capsys.readouterr()
    assert "Source choisie aléatoirement" in out
    assert "Capacité de la source" in out
    assert "mise en travaux" in out or "Nouvelle capacité" in out

def test_menu_generalisation_option_3_retour(monkeypatch, capsys):
    inputs = iter([
        "3",  # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "MENU" in out or out == ""
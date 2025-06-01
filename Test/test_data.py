import sys
import os
from unittest.mock import patch
from pyinstrument import Profiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import optimiser_liaisons, satisfaction, liaison_existe, ReseauHydraulique, Liaison, Noeud

from app import menu_terminal, menu_generalisation


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

def test_noeud_str():
    noeuds = Noeud("A", "source", 100)
    attendu = "Type : source\n Nom : A\nCapacité Maximale : 100"
    assert str(noeuds) == attendu

def test_liaison_str():
    liaisons = Liaison("A", "B", 50)
    attendu = "Départ : A\n Arrivée : B\nCapacité : 50"
    assert str(liaisons) == attendu

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

def test_menu_option_1(monkeypatch, capsys):
    inputs = iter(["1", "5"])  # Affiche carte Enoncer, puis quitte
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Carte des Liaisons" in out or "Flot maximal" in out

def test_menu_option_2(monkeypatch):
    inputs = iter(["2", "5"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))

    with patch("app.afficherCarte") as mock_afficher:
        menu_terminal()
        mock_afficher.assert_called()  # Vérifie que la fonction a été appelée

def test_menu_option_4_retour(monkeypatch, capsys):
    inputs = iter(["4", "4", "5"])  # entre menu généralisation, puis revient
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "MENU GÉNÉRALISATION" in out

def test_menu_option_invalide(monkeypatch, capsys):
    inputs = iter(["xyz", "5"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Choix invalide" in out

def test_generalisation_optimiser(monkeypatch, capsys):
    inputs = iter(["2", "4"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "Approvisionner" in out
    assert "Résultat final" in out

def test_generalisation_source_out(monkeypatch, capsys):
    inputs = iter([
        "3",     # Choix désactivation d’une source
        "A", "E", # Liaison à modifier
        "5"      # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "Source choisie aléatoirement" in out
    assert "Nouvelle capacité" in out

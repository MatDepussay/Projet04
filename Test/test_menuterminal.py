import sys
import os
from unittest.mock import patch
from pyinstrument import Profiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import menu_terminal, menu_generalisation, menu_demarrage

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
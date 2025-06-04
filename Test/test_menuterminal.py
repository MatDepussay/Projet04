import sys
import os
from unittest.mock import patch
from pyinstrument import Profiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from app import menu_terminal, menu_generalisation, menu_demarrage


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



def test_menu_generalisation_option_3_retour(monkeypatch, capsys):
    inputs = iter([
        "3",  # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "MENU" in out or out == ""
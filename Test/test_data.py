import sys
import os
import builtins
from scipy.sparse import csr_matrix
from unittest.mock import patch
from pyinstrument import Profiler
from io import StringIO
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest 
from data import ListeLiaison, ListeNoeuds, optimiser_liaisons, optimiser_liaisons_pour_approvisionnement, liaison_existe, ReseauHydraulique, liaison, noeud
import builtins

from affichage import afficherCarteEnoncer, afficherCarte
from app import menu_terminal, menu_generalisation


profiler = Profiler()
profiler.start()

# 👉 Ici tu mets la fonction lente
optimiser_liaisons_pour_approvisionnement(
    noeuds=ListeNoeuds,
    liaisons_actuelles=ListeLiaison,
    liaisons_possibles=[(l.depart, l.arrivee) for l in ListeLiaison],
    objectif_flot=50
)

profiler.stop()
print(profiler.output_text(unicode=True, color=True))


def test_modification_liaison_ameliore_flot():
    original = ListeLiaison[:]
    modifiee = [l if l.depart != "A" or l.arrivee != "E" else liaison("A", "E", 15) for l in ListeLiaison]
    
    flot_avant, _ = ReseauHydraulique(ListeNoeuds, original).calculerFlotMaximal()
    flot_apres, _ = ReseauHydraulique(ListeNoeuds, modifiee).calculerFlotMaximal()
    
    assert flot_apres.flow_value > flot_avant.flow_value

def test_noeud_str():
    noeuds = noeud("A", "source", 100)
    attendu = "Type : source\n Nom : A\nCapacité Maximale : 100"
    assert str(noeuds) == attendu

def test_liaison_str():
    liaisons = liaison("A", "B", 50)
    attendu = "Départ : A\n Arrivée : B\nCapacité : 50"
    assert str(liaisons) == attendu

def test_reseau_hydraulique_str():
    noeuds = [
        noeud("A", "source", 100),
        noeud("B", "ville", 50)
    ]
    liaisons = [
        liaison("A", "B", 70)
    ]
    
    reseau = ReseauHydraulique(noeuds, liaisons)
    representation = str(reseau)

    assert "--- Noeuds ---" in representation
    assert "Nom : A" in representation
    assert "Nom : B" in representation
    assert "--- Liaisons ---" in representation
    assert "Départ : A" in representation
    assert "Arrivée : B" in representation
    assert "Capacité : 70" in representation

def test_creation_noeud():
    n = noeud("A", "source", 10)
    assert n.nom == "A"
    assert n.type == "source"
    assert n.capaciteMax == 10

def test_liaison_existe():
    assert liaison_existe("A","E", ListeLiaison) == True
    assert liaison_existe("A", "H", ListeLiaison) == False
    assert liaison_existe("E", "A", ListeLiaison) == False


def test_liaison_inexistante():
    assert not liaison_existe("Z", "Q", ListeLiaison)

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

    config_finale, travaux = optimiser_liaisons(liste_noeuds, liste_liaisons, liaisons_a_optimiser)
    assert len(travaux) == 2
    assert travaux[0][2] <= travaux[1][2]  

    for _, cap, _ in travaux:
        assert 1 <= cap <= 20

def test_optimisation_break_quand_aucune_amélioration():
    # Exemple de réseau très simple
    noeuds = [
        noeud("A", "source", 5),
        noeud("B", "ville", 5)
    ]
    liaisons = [
        liaison("A", "B", 5)  # Capacité déjà suffisante
    ]

    # Liaisons qu’on autorise à "optimiser", mais il n’y a rien à améliorer
    liaisons_possibles = [("A", "B")]

    objectif = 5  # Objectif déjà atteint

    nouvelle_config, travaux = optimiser_liaisons_pour_approvisionnement(
        noeuds=noeuds,
        liaisons_actuelles=liaisons,
        liaisons_possibles=liaisons_possibles,
        objectif_flot=objectif
    )

    # ➤ Puisqu’il n’y a rien à améliorer, on s’attend à ce que `travaux` contienne 0 ou 1 élément max
    assert len(travaux) <= 1

def test_menu_travaux(monkeypatch, capsys):
    inputs = iter([
        "2",    
        "A", "E",
        "I", "L",
        "n",    
        "4"     
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

def test_menu_option_0(monkeypatch, capsys):
    inputs = iter(["0", "4"])  # Affiche carte Enoncer, puis quitte
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Carte des Liaisons" in out or "Flot maximal" in out

def test_menu_option_1(monkeypatch):
    inputs = iter(["1", "4"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))

    with patch("app.afficherCarte") as mock_afficher:
        menu_terminal()
        mock_afficher.assert_called()  # Vérifie que la fonction a été appelée


def test_menu_option_3_retour(monkeypatch, capsys):
    inputs = iter(["3", "3", "4"])  # entre menu généralisation, puis revient
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "MENU GÉNÉRALISATION" in out

def test_menu_option_invalide(monkeypatch, capsys):
    inputs = iter(["xyz", "4"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_terminal()
    out, _ = capsys.readouterr()
    assert "Choix invalide" in out

def test_generalisation_optimiser(monkeypatch, capsys):
    inputs = iter(["1", "3"])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "Approvisionner" in out
    assert "Résultat final" in out

def test_generalisation_source_out(monkeypatch, capsys):
    inputs = iter([
        "2",     # Choix désactivation d’une source
        "A", "E", # Liaison à modifier
        "3"      # Retour
    ])
    monkeypatch.setattr("builtins.input", simulate_inputs(inputs))
    menu_generalisation()
    out, _ = capsys.readouterr()
    assert "Source choisie aléatoirement" in out
    assert "Nouvelle capacité" in out

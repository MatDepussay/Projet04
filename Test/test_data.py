import sys
import os
from unittest.mock import patch
from pyinstrument import Profiler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import ListeLiaisons, ListeNoeuds, optimiser_liaisons, satisfaction, liaison_existe, ReseauHydraulique, Liaison, Noeud

from app import menu_terminal, menu_generalisation


profiler = Profiler()
profiler.start()

# 👉 Ici tu mets la fonction lente
satisfaction(
    noeuds=ListeNoeuds,
    liaisons_actuelles=ListeLiaisons,
    liaisons_possibles=[(liaison.depart, liaison.arrivee) for liaison in ListeLiaisons],
    objectif_flot=50
)

profiler.stop()
print(profiler.output_text(unicode=True, color=True))


def test_modification_liaison_ameliore_flot():
    original = ListeLiaisons[:]
    modifiee = [liaison if liaison.depart != "A" or liaison.arrivee != "E" else Liaison("A", "E", 15) for liaison in ListeLiaisons]
    
    flot_avant, _ = ReseauHydraulique(ListeNoeuds, original).calculerFlotMaximal()
    flot_apres, _ = ReseauHydraulique(ListeNoeuds, modifiee).calculerFlotMaximal()
    
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
    noeuds = [
        Noeud("A", "source", 100),
        Noeud("B", "ville", 50)
    ]
    liaisons = [
        Liaison("A", "B", 70)
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
    n = Noeud("A", "source", 10)
    assert n.nom == "A"
    assert n.type == "source"
    assert n.capaciteMax == 10

def test_liaison_existe():
    assert liaison_existe("A","E", ListeLiaisons)
    assert not liaison_existe("A", "H", ListeLiaisons)
    assert not liaison_existe("E", "A", ListeLiaisons)


def test_liaison_inexistante():
    assert not liaison_existe("Z", "Q", ListeLiaisons)

def test_optimiser_liaisons_priorise_meilleure_liaison():
    
    liste_noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "intermediaire"),
        Noeud("C", "ville", 10),
    ]

    liste_liaisons = [
        Liaison("A", "B", 1),  
        Liaison("B", "C", 1),  
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
        Noeud("A", "source", 5),
        Noeud("B", "ville", 5)
    ]
    liaisons = [
        Liaison("A", "B", 5)  # Capacité déjà suffisante
    ]

    # Liaisons qu’on autorise à "optimiser", mais il n’y a rien à améliorer
    liaisons_possibles = [("A", "B")]

    objectif = 5  # Objectif déjà atteint

    nouvelle_config, travaux = satisfaction(
        noeuds=noeuds,
        liaisons_actuelles=liaisons,
        liaisons_possibles=liaisons_possibles,
        objectif_flot=objectif
    )

    # ➤ Puisqu’il n’y a rien à améliorer, on s’attend à ce que `travaux` contienne 0 ou 1 élément max
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

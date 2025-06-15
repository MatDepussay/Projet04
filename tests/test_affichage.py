import sys
import os
import pytest
import matplotlib.pyplot as plt
from types import SimpleNamespace

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)
from data import Liaison, Noeud, ReseauHydraulique
from affichage import afficherCarte, afficherCarteEnoncer


def test_afficherCarteEnoncer_basic():
    # Création de noeuds et liaisons simples
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "ville", 5),
        Noeud("C", "intermediaire", 0),
    ]
    liaisons = [
        Liaison("A", "B", 10),
        Liaison("B", "C", 5),
    ]

    # Cas 1 : Sans result
    fig = afficherCarteEnoncer(
        result=None, index_noeuds=None, noeuds=noeuds, liaisons=liaisons
    )
    assert isinstance(fig, plt.Figure)
    ax = fig.axes[0]
    assert "Carte des Liaisons" in ax.get_title()

    # Vérifier que les labels des noeuds correspondent aux couleurs/types
    labels = [text.get_text() for text in ax.texts]
    assert any("A\n(10 u.)" in label for label in labels)
    assert any("B\n(5 u.)" in label for label in labels)
    assert any("C" in label for label in labels)

    plt.close(fig)

    # Cas 2 : Avec un résultat simulé
    flow = {
        (0, 1): 8,
        (1, 2): 5,
    }
    result = SimpleNamespace(flow=flow, flow_value=8)
    fig2 = afficherCarteEnoncer(
        result=result, index_noeuds=None, noeuds=noeuds, liaisons=liaisons
    )
    assert any("Flot maximal : 8" in text.get_text() for text in fig2.texts)
    plt.close(fig2)


def test_afficherCarteEnoncer_exceptions():
    # Pas de noeuds ni liaisons : doit lever ValueError
    with pytest.raises(ValueError):
        afficherCarteEnoncer(noeuds=None, liaisons=None)

    with pytest.raises(ValueError):
        afficherCarteEnoncer(noeuds=[], liaisons=None)

    with pytest.raises(ValueError):
        afficherCarteEnoncer(noeuds=None, liaisons=[])


def test_afficherCarte_raises_without_noeuds_ou_liaisons():
    with pytest.raises(ValueError, match="Il faut fournir les noeuds et liaisons"):
        afficherCarte()


def test_afficherCarte_affichage_simple():
    noeuds = [
        Noeud(nom="A", type="source", capaciteMax=5),
        Noeud(nom="B", type="ville", capaciteMax=5),
    ]
    liaisons = [Liaison(depart="A", arrivee="B", capacite=5)]
    fig = afficherCarte(noeuds=noeuds, liaisons=liaisons)
    assert fig is not None


def test_afficherCarte_couleurs_et_labels(monkeypatch):
    noeuds = [
        Noeud("A", "source"),
        Noeud("B", "ville"),
        Noeud("C", "intermediaire"),
        Noeud("D", "intermediaire"),
    ]
    liaisons = [
        Liaison("A", "C", 10),
        Liaison("C", "B", 5),
        Liaison("C", "D", 3),
    ]

    index_noeuds = {"A": 0, "B": 1, "C": 2, "D": 3, "super_source": 4, "super_puits": 5}

    # Création d'un objet result avec des flux simulés
    flow = {
        (4, 0): 10,  # super_source -> A
        (0, 2): 10,  # A -> C
        (2, 1): 5,  # C -> B
        (2, 3): 3,  # C -> D
        (1, 5): 5,  # B -> super_puits
        (3, 5): 3,  # D -> super_puits
    }
    result = SimpleNamespace(flow=flow, flow_value=8)

    # Patch la méthode liaisons_saturees pour éviter erreur
    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", lambda self, result: [])

    fig = afficherCarte(
        result=result, index_noeuds=index_noeuds, noeuds=noeuds, liaisons=liaisons
    )

    # On cherche les labels dans la figure (axe principal)
    ax = fig.axes[0]
    texts = [text.get_text() for text in ax.texts]

    # Labels attendus
    assert "A\n(10 u.)" in texts
    assert "B\n(5 u.)" in texts
    assert "C" in texts
    assert "D" in texts


@pytest.mark.parametrize("montrer_saturees", [True, False])
@pytest.mark.parametrize("with_result", [True, False])
def test_couverture_boucles(monkeypatch, montrer_saturees, with_result):
    noeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "ville", 5),
        Noeud("C", "intermediaire"),
    ]
    liaisons = [
        Liaison("A", "B", 10),
        Liaison("B", "C", 5),
    ]
    index_noeuds = {"A": 0, "B": 1, "C": 2, "super_source": 3, "super_puits": 4}

    if with_result:
        # On inclut uniquement les arêtes présentes dans le graphe pour éviter KeyError
        flow = {
            (3, 0): 10,  # super_source -> A
            (0, 1): 8,  # A -> B
            (1, 2): 5,  # B -> C
            (1, 4): 0,
            (2, 4): 5,  # C -> super_puits
        }
        result = SimpleNamespace(flow=flow, flow_value=8)
    else:
        result = None

    def fake_liaisons_saturees(self, result):
        if montrer_saturees and result:
            return [("A", "B", 10)]  # Saturée A->B
        return []

    monkeypatch.setattr(ReseauHydraulique, "liaisons_saturees", fake_liaisons_saturees)

    # Construire l’index_noeuds comme dans afficherCarte
    reseau_temp = ReseauHydraulique(noeuds, liaisons)
    index_noeuds = reseau_temp.index_noeuds

    fig = afficherCarte(
        result=result,
        index_noeuds=index_noeuds,
        noeuds=noeuds,
        liaisons=liaisons,
        montrer_saturees=montrer_saturees,
    )

    ax = fig.axes[0]

    # Debug print pour voir tous les textes dans ax
    print("Labels dans ax.texts:", [t.get_text() for t in ax.texts])
    print("Labels dans fig.texts:", [t.get_text() for t in fig.texts])

    # Vérifier titre
    if montrer_saturees:
        assert "(liaisons saturées en rouge)" in ax.get_title()
    else:
        assert "(liaisons saturées en rouge)" not in ax.get_title()

    # Vérifier texte flot maximal
    texts = [text.get_text() for text in fig.texts]
    if with_result:
        assert any("Flot maximal" in t for t in texts)
    else:
        assert not any("Flot maximal" in t for t in texts)

    # Vérifier labels d'arêtes
    edge_labels_texts = [t.get_text() for t in ax.texts if "/" in t.get_text()]
    print("Edge labels filtrés:", edge_labels_texts)

    # Vérifier labels d'arêtes
    if with_result:
        edge_labels_texts = [t.get_text() for t in ax.texts if "/" in t.get_text()]
        assert any(label.startswith("8 / 10") for label in edge_labels_texts)
        assert any(label.startswith("5 / 5") for label in edge_labels_texts)
    else:
        # Avec pas de result, les labels sont juste des capacités (ex: "10", "5")
        edge_labels_texts = [t.get_text() for t in ax.texts if t.get_text().isdigit()]
        assert any("10" == label for label in edge_labels_texts)
        assert any("5" == label for label in edge_labels_texts)

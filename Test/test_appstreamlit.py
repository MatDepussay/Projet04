import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data import Noeud, Liaison, GestionReseau, ReseauHydraulique, optimiser_liaisons, satisfaction

def test_ajout_noeud_source():
    """
    Teste l'ajout d'un nœud de type 'source' dans un réseau.
    Vérifie que le nœud est bien ajouté et que son type est correct.
    """
    reseau = GestionReseau()
    noeud = Noeud("A", "source", 10)
    reseau.ListeNoeuds.append(noeud)
    assert len(reseau.ListeNoeuds) == 1
    assert reseau.ListeNoeuds[0].type == "source"

def test_ajout_noeud_ville():
    """
    Teste l'ajout d'un nœud de type 'ville' dans un réseau.
    Vérifie que le nœud est bien ajouté, que son type et sa capacité sont corrects.
    """
    reseau = GestionReseau()
    noeud = Noeud("B", "ville", 15)
    reseau.ListeNoeuds.append(noeud)
    assert reseau.ListeNoeuds[0].type == "ville"
    assert reseau.ListeNoeuds[0].capaciteMax == 15

def test_ajout_liaison():
    """
    Teste l'ajout d'une liaison entre deux nœuds dans un réseau.
    Vérifie que la liaison est bien ajoutée et que ses extrémités sont correctes.
    """
    reseau = GestionReseau()
    n1 = Noeud("A", "source", 10)
    n2 = Noeud("B", "ville", 10)
    reseau.ListeNoeuds.extend([n1, n2])
    liaison = Liaison("A", "B", 5)
    reseau.ListeLiaisons.append(liaison)
    assert len(reseau.ListeLiaisons) == 1
    assert reseau.ListeLiaisons[0].depart == "A"
    assert reseau.ListeLiaisons[0].arrivee == "B"

def test_flot_maximal_simple():
    """
    Teste le calcul du flot maximal sur un réseau simple (une source, une ville, une liaison).
    Vérifie que le flot maximal correspond à la capacité de la liaison.
    """
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = [Liaison("A", "B", 10)]
    reseau = ReseauHydraulique(noeuds, liaisons)
    result, _ = reseau.calculerFlotMaximal()
    assert result.flow_value == 10

def test_optimiser_liaisons_gain():
    """
    Teste l'optimisation automatique des liaisons pour maximiser le flot.
    Vérifie qu'après optimisation, la capacité de la liaison permet d'atteindre la capacité maximale possible.
    """
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = [Liaison("A", "B", 5)]
    liaisons_a_optimiser = [("A", "B")]
    config, travaux = optimiser_liaisons(noeuds, liaisons, liaisons_a_optimiser)
    assert any(travail[1] >= 10 for travail in travaux)  # On doit pouvoir atteindre la capacité max


def test_satisfaction_objectif_inatteignable():
    """
    Teste la fonction satisfaction lorsque l'objectif est inatteignable (source trop faible).
    Vérifie qu'aucun des travaux ne permet d'atteindre l'objectif fixé.
    """
    noeuds = [Noeud("A", "source", 5), Noeud("B", "ville", 10)]
    liaisons = [Liaison("A", "B", 5)]
    nouvelle_config, travaux = satisfaction(
        noeuds=noeuds,
        liaisons=liaisons,
        objectif=10,
        cap_max=5,
        max_travaux=2
    )
    # Impossible d'atteindre 10 car la source est limitée à 5
    assert all(flot <= 5 for _, _, flot in travaux) or travaux == []

def test_reset_reseau():
    """
    Teste la réinitialisation d'un réseau.
    Vérifie que la liste des nœuds et des liaisons est bien vide après réinitialisation.
    """
    reseau = GestionReseau()
    reseau.ListeNoeuds.append(Noeud("A", "source", 10))
    reseau.ListeLiaisons.append(Liaison("A", "B", 5))
    reseau.ListeNoeuds.clear()
    reseau.ListeLiaisons.clear()
    assert len(reseau.ListeNoeuds) == 0
    assert len(reseau.ListeLiaisons) == 0

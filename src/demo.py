from data import *
import scipy as sp
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

noeuds = [
    noeud("A", "source", 15),
    noeud("B", "source", 15),
    noeud("C", "source", 15),
    noeud("D", "source", 10),
    noeud("J", "ville", 15),
    noeud("K", "ville", 20),
    noeud("L", "ville", 15),
    # E, F, G, H, I sont intermédiaires
    noeud("E", "intermediaire"),
    noeud("F", "intermediaire"),
    noeud("G", "intermediaire"),
    noeud("H", "intermediaire"),
    noeud("I", "intermediaire"),
]

liaisons = [
    liaison("A", "E", 7),
    liaison("B", "F", 10),
    liaison("B", "G", 7),
    liaison("C", "A", 5),
    liaison("C", "F", 5),
    liaison("D", "G", 10),
    liaison("E", "F", 5),
    liaison("E", "H", 4),
    liaison("E", "I", 15),
    liaison("F", "G", 5),
    liaison("F", "I", 15),
    liaison("G", "I", 15),
    liaison("H", "J", 7),
    liaison("I", "K", 30),
    liaison("I", "L", 4),
    liaison("K", "J", 10),
]


reseau = ReseauHydraulique(noeuds, liaisons)
flot = reseau.calculerFlotMaximal()
print(f"\n💧 Flot maximum total : {flot}k\n")
#reseau.afficher_flux()



from typing import List, Tuple
import numpy as np
import scipy as sp
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow
import networkx as nx
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class noeud:
    nom: str
    type: str       # "source", "ville", "intermediaire"
    capaciteMax: int = 0

@dataclass
class liaison:
    depart: str
    arrivee: str
    capacite: int

class ReseauHydraulique:
    def __init__(self, noeuds: List[noeud], liaisons: List[liaison]):
        self.noeuds = noeuds
        self.liaisons = liaisons


    def calculerFlotMaximal(self):
        # Liste des noms de noeuds + super-source/puits
        noms_noeuds = [n.nom for n in self.noeuds] + ["super_source", "super_puits"]
        index_noeuds = {nom: i for i, nom in enumerate(noms_noeuds)}
        index_inverse = {i: nom for nom, i in index_noeuds.items()}
        n = len(noms_noeuds)

        # Matrice de capacité
        matrice = [[0] * n for _ in range(n)]

        # Ajout des liaisons
        for l in self.liaisons:
            i, j = index_noeuds[l.depart], index_noeuds[l.arrivee]
            matrice[i][j] = l.capacite

        # Connexions super_source -> sources
        for node in self.noeuds:
            if node.type == "source":
                matrice[index_noeuds["super_source"]][index_noeuds[node.nom]] = node.capaciteMax

        # Connexions villes -> super_puits
        for node in self.noeuds:
            if node.type == "ville":
                matrice[index_noeuds[node.nom]][index_noeuds["super_puits"]] = node.capaciteMax

        # Conversion en matrice creuse
        matrice_np = np.array(matrice)
        matrice_sparse = csr_matrix(matrice_np)

        # Calcul du flot
        result = maximum_flow(matrice_sparse, index_noeuds['super_source'], index_noeuds['super_puits'])

        #print(f"💧 Flot maximal total : {result.flow_value} unités\n")
        #print("➡️ Détail des flux utilisés :\n")

        flow_matrix = result.flow
        for i in range(n):
            for j in range(n):
                flow = flow_matrix[i, j]
                if flow > 0:
                    u = index_inverse[i]
                    v = index_inverse[j]
                #print(f"{u} ➝ {v} : {flow} unités")

        return result, index_noeuds
    
# Définition des noeuds
ListeNoeuds = [
    noeud("A", "source", 15),
    noeud("B", "source", 15),
    noeud("C", "source", 15),
    noeud("D", "source", 10),
    noeud("E", "intermediaire"),
    noeud("F", "intermediaire"),
    noeud("G", "intermediaire"),
    noeud("H", "intermediaire"),
    noeud("I", "intermediaire"),
    noeud("J", "ville", 15),
    noeud("K", "ville", 20),
    noeud("L", "ville", 15),
]

ListeLiaison = [
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

# Création du réseau global
reseau = ReseauHydraulique(ListeNoeuds, ListeLiaison)

# Pour compatibilité avec l’ancien code
def calculerFlotMaximal(liaisons=None):
    if liaisons:
        reseau_temp = ReseauHydraulique(ListeNoeuds, liaisons)
        return reseau_temp.calculerFlotMaximal()
    else:
        return reseau.calculerFlotMaximal()

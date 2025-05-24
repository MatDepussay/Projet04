from typing import List, Tuple, Dict
from numpy import array
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class noeud:
    nom: str
    type: str  # "source", "ville", "intermediaire"
    capaciteMax: int = 0

    def __str__(self):
        return f"Type : {self.type}\n Nom : {self.nom}\nCapacité Maximale : {self.capaciteMax}"

@dataclass
class liaison:
    depart: str
    arrivee: str
    capacite: int

    def __str__(self):
        return f"Départ : {self.depart}\n Arrivée : {self.arrivee}\nCapacité : {self.capacite}"
class ReseauHydraulique:
    def __init__(self, noeuds: List[noeud], liaisons: List[liaison]):
        self.noeuds: Dict[str, noeud] = {n.nom: n for n in noeuds}
        self.liaisons: List[liaison] = liaisons
        
        # Préparer le mapping des noeuds + super-source et super-puits
        self.noms_noeuds = list(self.noeuds.keys()) + ["super_source", "super_puits"]
        self.index_noeuds = {nom: i for i, nom in enumerate(self.noms_noeuds)}
        self.index_inverse = {i: nom for nom, i in self.index_noeuds.items()}
        self.n = len(self.noms_noeuds)

        # Initialiser matrice des capacités (numpy array pour modifier facilement)
        self.matrice_np = array([[0] * self.n for _ in range(self.n)])
        
        # Ajout des liaisons
        for l in self.liaisons:
            i, j = self.index_noeuds[l.depart], self.index_noeuds[l.arrivee]
            self.matrice_np[i][j] = l.capacite

        # Connexions super_source -> sources
        for node in self.noeuds.values():
            if node.type == "source":
                self.matrice_np[self.index_noeuds["super_source"]][self.index_noeuds[node.nom]] = node.capaciteMax

        # Connexions villes -> super_puits
        for node in self.noeuds.values():
            if node.type == "ville":
                self.matrice_np[self.index_noeuds[node.nom]][self.index_noeuds["super_puits"]] = node.capaciteMax

        # Conversion en matrice creuse
        self.matrice_sparse = csr_matrix(self.matrice_np)

    def __str__(self):
        noeuds_str = "\n".join(str(n) for n in self.noeuds.values())
        liaisons_str = "\n".join(str(l) for l in self.liaisons)
        return f"--- Noeuds ---\n{noeuds_str}\n\n--- Liaisons ---\n{liaisons_str}"

    def calculerFlotMaximal(self):

        # Calcul du flot
        result = maximum_flow(self.matrice_sparse,
                              self.index_noeuds['super_source'],
                              self.index_noeuds['super_puits'])

        print(f"💧 Flot maximal total : {result.flow_value} unités\n")
        print("➡️ Détail des flux utilisés :\n")

        flow_matrix = result.flow
        for i in range(self.n):
            for j in range(self.n):
                flow = flow_matrix[i, j]
                if flow > 0:
                    u = self.index_inverse[i]
                    v = self.index_inverse[j]
                    print(f"{u} ➝ {v} : {flow} unités")

        return result, self.index_noeuds
    
def liaison_existe(depart: str, arrivee: str, liaisons: List[liaison]) -> bool:
    for l in liaisons:
        if (l.depart == depart and l.arrivee == arrivee):
            return True
    return False

def optimiser_liaisons(
    noeuds: List[noeud],
    liaisons_actuelles: List[liaison],
    liaisons_a_optimiser: List[Tuple[str, str]]
) -> Tuple[List[liaison], List[Tuple[Tuple[str, str], int, int]]]:
    
    """
    Optimise les capacités des liaisons spécifiées pour maximiser le flot global.
    Retourne la nouvelle config et une liste des travaux effectués :
    [((depart, arrivee), capacité_choisie, flot_max_après_modification)]
    """
    meilleure_config = liaisons_actuelles[:]
    liaisons_restantes = liaisons_a_optimiser[:]
    travaux_effectues = []

    reseau_temp = ReseauHydraulique(noeuds, meilleure_config)
    result_init, _ = reseau_temp.calculerFlotMaximal()
    meilleur_flot = result_init.flow_value

    while liaisons_restantes:
        meilleur_gain = -1
        meilleure_liaison = None
        meilleure_config_temp = None
        meilleur_result_temp = None

        for liaison_cible in liaisons_restantes:
            for cap_test in range(1, 21):
                temp_temp_config = meilleure_config[:]
                for i, l in enumerate(temp_temp_config):
                    if (l.depart, l.arrivee) == liaison_cible:
                        temp_temp_config[i] = liaison(l.depart, l.arrivee, cap_test)

                reseau_temp = ReseauHydraulique(noeuds, temp_temp_config)
                temp_result, _ = reseau_temp.calculerFlotMaximal()

                if temp_result.flow_value > meilleur_gain:
                    meilleur_result_temp = temp_result
                    meilleur_gain = temp_result.flow_value
                    meilleure_liaison = (liaison_cible, cap_test)
                    meilleure_config_temp = temp_temp_config[:]

        if meilleure_liaison:
            meilleure_config = meilleure_config_temp[:]
            travaux_effectues.append((meilleure_liaison[0], meilleure_liaison[1], meilleur_result_temp.flow_value))
            liaisons_restantes.remove(meilleure_liaison[0])
        else:
            break

    return meilleure_config, travaux_effectues

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
def calculerFlotMaximal_temp(noeuds: List[noeud], liaisons: List[liaison]):
    reseau_temp = ReseauHydraulique(noeuds, liaisons)
    return reseau_temp.calculerFlotMaximal()


def optimiser_liaisons_pour_approvisionnement(
    noeuds : List[noeud],
    liaisons_actuelles: List[liaison],
    liaisons_possibles: List[Tuple[str, str]],
    objectif_flot: int = 50
) -> Tuple[List[liaison], List[Tuple[Tuple[str, str], int, int]]]:
    """
    Optimise les liaisons pour atteindre exactement l'objectif de flot ( 50 unités)
    avec le minimum de travaux (liaisons modifiées).

    >>>>>> 
    """
    meilleure_config = liaisons_actuelles[:]
    liaisons_restantes = liaisons_possibles[:]
    travaux_effectues = []

    reseau = ReseauHydraulique(noeuds, liaisons_actuelles)
    result_init, _ = reseau.calculerFlotMaximal()
    flot_actuel = result_init.flow_value

    if flot_actuel >= objectif_flot:
        return meilleure_config, travaux_effectues  # Déjà bon !

    while liaisons_restantes:
        meilleure_liaison = None
        meilleure_config_temp = None
        meilleur_result_temp = None

        for liaison_cible in liaisons_restantes:
            # Cherche si la liaison existe déjà
            index_exist = None
            for i, l in enumerate(meilleure_config):
                if (l.depart, l.arrivee) == liaison_cible:
                    index_exist = i
                    break

            for cap_test in [5, 10, 15, 20]:
                if index_exist is not None:
                    old_liaison = meilleure_config[index_exist]
                    meilleure_config[index_exist] = liaison(old_liaison.depart, old_liaison.arrivee, cap_test)
                else:
                    meilleure_config.append(liaison(liaison_cible[0], liaison_cible[1], cap_test))

                reseau_temp = ReseauHydraulique(noeuds, meilleure_config)
                temp_result, _ = reseau_temp.calculerFlotMaximal()

                if temp_result.flow_value > flot_actuel:
                    meilleure_liaison = (liaison_cible, cap_test)
                    meilleure_config_temp = meilleure_config[:]
                    meilleur_result_temp = temp_result
                    if temp_result.flow_value >= objectif_flot:
                        # restaurer avant break
                        if index_exist is not None:
                            meilleure_config[index_exist] = old_liaison
                        else:
                            meilleure_config.pop()
                        break

                # restaurer
                if index_exist is not None:
                    meilleure_config[index_exist] = old_liaison
                else:
                    meilleure_config.pop()

            if meilleur_result_temp and meilleur_result_temp.flow_value >= objectif_flot:
                break

        if meilleure_liaison:
            meilleure_config = meilleure_config_temp[:]
            travaux_effectues.append((meilleure_liaison[0], meilleure_liaison[1], meilleur_result_temp.flow_value))
            flot_actuel = meilleur_result_temp.flow_value
            liaisons_restantes.remove(meilleure_liaison[0])

            if flot_actuel >= objectif_flot:
                break
        else:
            break  # Aucune amélioration possible

    return meilleure_config, travaux_effectues
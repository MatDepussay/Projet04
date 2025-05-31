from typing import List, Tuple, Dict
from numpy import array
import json
import os
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow

class Noeud:
    def __init__(self, nom: str, type: str, capaciteMax: int = 0)-> None:
        self.nom = nom
        self.type = type # "source", "ville", "intermediaire"
        self.capaciteMax = capaciteMax

    def __str__(self):
        return f"Type : {self.type}\n Nom : {self.nom}\nCapacité Maximale : {self.capaciteMax}"

class Liaison:
    def __init__(self, depart: str, arrivee: str, capacite: int) -> None:
        self.depart = depart
        self.arrivee = arrivee
        self.capacite = capacite

    def __str__(self):
        return f"Départ : {self.depart}\n Arrivée : {self.arrivee}\nCapacité : {self.capacite}"
class ReseauHydraulique:
    def __init__(self, noeuds: List[Noeud], liaisons: List[Liaison]):
        self.noeuds: Dict[str, Noeud] = {n.nom: n for n in noeuds}
        self.liaisons : List[Liaison]= liaisons
        
        # Préparer le mapping des noeuds + super-source et super-puits
        self.noms_noeuds = list(self.noeuds.keys()) + ["super_source", "super_puits"]
        self.index_noeuds = {nom: i for i, nom in enumerate(self.noms_noeuds)}
        self.index_inverse = {i: nom for nom, i in self.index_noeuds.items()}
        self.n = len(self.noms_noeuds)

        # Initialiser matrice des capacités (numpy array pour modifier facilement)
        self.matrice_np = array([[0] * self.n for _ in range(self.n)])
        
        # Ajout des liaisons
        for liaison_obj in self.liaisons:
            i, j = self.index_noeuds[liaison_obj.depart], self.index_noeuds[liaison_obj.arrivee]
            self.matrice_np[i][j] = liaison_obj.capacite

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
        liaisons_str = "\n".join(str(liaison_obj) for liaison_obj in self.liaisons)
        return f"--- Noeuds ---\n{noeuds_str}\n\n--- Liaisons ---\n{liaisons_str}"

    def calculerFlotMaximal(self):
        '''
            Elle calcule le flux qui circulent dans les liaisons ainsi que le flot que les villes reçoivent.
            
            >>> Retourne :
                    Flot maximal total : 37 unités
                    Détail des flux utilisés :
                    A -> E : 7 unités --> Il y a 7k m3 d'eau qui circulent dans la liaison A-E
                    super_source -> A : 7 -->La source a délivre 7K m3 dans le systeme
                    K-> super_puits : 20 --> la ville reçoit 20K m3 du systeme
                    ...
        '''

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
    
def liaison_existe(depart: str, arrivee: str, liaisons: List[Liaison]) -> bool:
    '''
        Vérifie si une liaison existe entre deux nœuds.

    Args:
        depart (str): Le nom du nœud de départ.
        arrivee (str): Le nom du nœud d'arrivée.
        liaisons (List[liaison]): La liste des liaisons disponibles.

    Returns:
        bool: True si une liaison entre `depart` et `arrivee` existe, sinon False.
    '''
    for liaison in liaisons:
        if (liaison.depart == depart and liaison.arrivee == arrivee):
            return True
    return False

def optimiser_liaisons(
    noeuds: List[Noeud],
    liaisons_actuelles: List[Liaison],
    liaisons_a_optimiser: List[Tuple[str, str]]
    ) -> Tuple[List[Noeud], List[Liaison], List[Tuple[Tuple[str, str], int, int]]]:
    
    """
    Optimise l'ordre des travaux à effecter ainsi que les capacités des flots des liaisons choisies pour les travaux afin de maximiser le flot global.
    
    >>> Retourne l'ordre des travaux à effectuer :
        Travaux #1 : Liaison A -> E
        Travaux #2 : Liaison I -> L
        
        Retourne La nouvelle capacité de la liaison ainsi que son impact sur le flot maximal:
        Capacité Choisie : 8 unités
        Nouveau Flot Maxiaml : 38 unités

    """
    meilleure_config = liaisons_actuelles[:]
    liaisons_restantes = liaisons_a_optimiser[:]
    travaux_effectues = []

    reseau_temp = ReseauHydraulique(noeuds, meilleure_config)
    result_init, _ = reseau_temp.calculerFlotMaximal()

    while liaisons_restantes:
        meilleur_gain = -1
        meilleure_liaison = None
        meilleure_config_temp = None
        meilleur_result_temp = None

        for liaison_cible in liaisons_restantes:
            for cap_test in range(1, 21):
                temp_temp_config = meilleure_config[:]
                for i, liaison_obj in enumerate(temp_temp_config):
                    if (liaison_obj.depart, liaison_obj.arrivee) == liaison_cible:
                        temp_temp_config[i] = Liaison(liaison_obj.depart, liaison_obj.arrivee, cap_test)
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
    Noeud("A", "source", 15),
    Noeud("B", "source", 15),
    Noeud("C", "source", 15),
    Noeud("D", "source", 10),
    Noeud("E", "intermediaire"),
    Noeud("F", "intermediaire"),
    Noeud("G", "intermediaire"),
    Noeud("H", "intermediaire"),
    Noeud("I", "intermediaire"),
    Noeud("J", "ville", 15),
    Noeud("K", "ville", 20),
    Noeud("L", "ville", 15),
]

ListeLiaisons = [
    Liaison("A", "E", 7),
    Liaison("B", "F", 10),
    Liaison("B", "G", 7),
    Liaison("C", "A", 5),
    Liaison("C", "F", 5),
    Liaison("D", "G", 10),
    Liaison("E", "F", 5),
    Liaison("E", "H", 4),
    Liaison("E", "I", 15),
    Liaison("F", "G", 5),
    Liaison("F", "I", 15),
    Liaison("G", "I", 15),
    Liaison("H", "J", 7),
    Liaison("I", "K", 30),
    Liaison("I", "L", 4),
    Liaison("K", "J", 10),
]

# Création du réseau global
reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)


def satisfaction(
    noeuds : List[Noeud],
    liaisons_actuelles: List[Liaison],
    liaisons_possibles: List[Tuple[str, str]],
    objectif_flot: int = 50
) -> Tuple[List[Liaison], List[Tuple[Tuple[str, str], int, int]]]:
    """
    Optimise les liaisons à ajouter ou modifier dans un réseau hydraulique afin d'atteindre
    un objectif de flot minimal tout en minimisant les travaux.

    L'algorithme ajoute progressivement des liaisons parmi les options possibles, testant différentes
    capacités, jusqu'à atteindre ou dépasser l'objectif de flot spécifié (satisfaire les besoins en eau de toutes les villes à 100%)

    >>>
    Tuple[List[liaison], List[Tuple[Tuple[str, str], int, int]]]
        - La liste des liaisons après optimisation.
        - La liste des travaux effectués sous la forme ((départ, arrivée), capacité, flot résultant).

    >>> config_finale, travaux = optimiser_liaisons_pour_approvisionnement(noeuds, liaisons_init, options, 50)
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
            for i, liaison_obj in enumerate(meilleure_config):
                if (liaison_obj.depart, liaison_obj.arrivee) == liaison_cible:
                    index_exist = i
                    break

            for cap_test in [5, 10, 15, 20, 25]:
                if index_exist is not None:
                    old_liaison = meilleure_config[index_exist]
                    meilleure_config[index_exist] = Liaison(old_liaison.depart, old_liaison.arrivee, cap_test)
                else:
                    meilleure_config.append(Liaison(liaison_cible[0], liaison_cible[1], cap_test))

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


def sauvegarder_reseau(reseau_nom, noeuds, liaisons, fichier='reseaux.json'):
    """
    Sauvegarde un réseau hydraulique dans un fichier JSON sous le nom spécifié.

    Cette fonction stocke les informations des nœuds et des liaisons dans un fichier 
    pour permettre une réutilisation ou une restauration ultérieure du réseau par l'utilisateur.

    Args:
        reseau_nom (str): Nom attribué au réseau à sauvegarder.
        noeuds (List[Noeud]): Liste des objets Noeud à sauvegarder.
        liaisons (List[Liaison]): Liste des objets Liaison à sauvegarder.
        fichier (str): Nom du fichier JSON dans lequel sauvegarder les données (par défaut 'reseaux.json').

    Exemple:
        >>> sauvegarder_reseau("reseau_1", ListeNoeuds, ListeLiaisons)
    """
    data = {}
    if os.path.exists(fichier):
            with open(fichier, 'r') as f:
                data = json.load(f)

        
    data[reseau_nom] = {
        "noeuds": [n.__dict__ for n in noeuds],
        "liaisons": [l.__dict__ for l in liaisons]
    }

    with open(fichier, 'w') as f:
        json.dump(data, f, indent=4)

def charger_reseaux(fichier='reseaux.json') -> Dict[str, Tuple[List[Noeud], List[Liaison]]]:
    """
    Charge les réseaux hydrauliques sauvegardés depuis un fichier JSON.

    Convertit les données JSON en objets `Noeud` et `Liaison` pour permettre leur réutilisation
    dans l'application. Retourne un dictionnaire contenant les différents réseaux sauvegardés.

    Args:
        fichier (str): Nom du fichier JSON à lire (par défaut 'reseaux.json').

    Returns:
        Dict[str, Tuple[List[Noeud], List[Liaison]]]: 
            Un dictionnaire avec pour clé le nom du réseau, et pour valeur un tuple contenant :
                - la liste des objets `Noeud`
                - la liste des objets `Liaison`

    Exemple:
        >>> reseaux = charger_reseaux()
        >>> noeuds, liaisons = reseaux["reseau_1"]
    """
    if not os.path.exists(fichier):
        return {}

    with open(fichier, 'r') as f:
        data = json.load(f)

    reseaux = {}
    for nom, contenu in data.items():
        noeuds_data = contenu.get("noeuds", [])
        liaisons_data = contenu.get("liaisons", [])

        noeuds = [Noeud(n["nom"], n["type"], n.get("capaciteMax", 0)) for n in noeuds_data]
        liaisons = [Liaison(l["depart"], l["arrivee"], l["capacite"]) for l in liaisons_data]

        reseaux[nom] = (noeuds, liaisons)

    return reseaux

def supprimer_reseaux(fichier='reseaux.json'):
    """
    Supprime définitivement le fichier contenant les réseaux sauvegardés.

    Cette fonction permet à l'utilisateur de réinitialiser complètement
    les données de tous les réseaux enregistrés.

    Args:
        fichier (str): Nom du fichier JSON à supprimer (par défaut 'reseaux.json').

    Exemple:
        >>> supprimer_reseaux()
    """
    if os.path.exists(fichier):
        os.remove(fichier)
from typing import List, Tuple, Dict, Optional
from numpy import array
from itertools import combinations, product
import copy
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
        return f"Nom : {self.nom}, Type : {self.type}, Capacite max : {self.capaciteMax}"


    def to_dict(self):
        return {
            "nom": self.nom,
            "type": self.type,
            "capaciteMax": self.capaciteMax
        }
        
    @staticmethod
    def from_dict(data):
        return Noeud(data["nom"], data["type"], data.get("capaciteMax", 0))

class Liaison:
    def __init__(self, depart: str, arrivee: str, capacite: int) -> None:
        self.depart = depart
        self.arrivee = arrivee
        self.capacite = capacite
    
    def __str__(self):
        return f"Départ : {self.depart}, Arrivée : {self.arrivee}, Capacite : {self.capacite}"

    def to_dict(self):
        return {
            "depart": self.depart,
            "arrivee": self.arrivee,
            "capacite": self.capacite
        }
    
    @staticmethod
    def from_dict(data):
        return Liaison(data["depart"], data["arrivee"], data["capacite"])

# Fonction de création
def creer_noeud(nom : str, type_noeud : str, capacite: int=0, noms_existants: set = None) -> Noeud:
    """
    Crée un noeud après vérification que le nom n'existe pas déjà.

    :param nom: Nom du noeud (str, majuscule recommandée)
    :param type_noeud: Type du noeud ("source", "ville", "intermediaire")
    :param capacite: Capacité maximale (int > 0 pour source/ville)
    :param noms_existants: ensemble des noms déjà utilisés (set)
    :return: instance de Noeud
    :raises ValueError: si nom déjà utilisé ou type invalide ou capacité invalide
    """
    if noms_existants is not None and nom in noms_existants:
        raise ValueError("❌ Ce nom est déjà utilisé. Choisis un autre nom.")

    if type_noeud not in {"source", "ville", "intermediaire"}:
        raise ValueError("❌ Type de noeud invalide. Choisis parmi 'source', 'ville', 'intermediaire'.")

    if type_noeud == "intermediaire":
        # Pas de capacité requise pour intermédiaire
        return Noeud(nom, type_noeud)
    else:
        if capacite <= 0:
            raise ValueError("❌ La capacité doit être un entier positif pour les sources/ville")
        return Noeud(nom, type_noeud, capacite)

def creer_liaison(depart: str, arrivee: str, capacite: int, noms_noeuds: set, liaisons_existantes: list) -> Liaison:
    """
    Crée une liaison après vérification des contraintes.

    :param depart: Nom du noeud de départ (str)
    :param arrivee: Nom du noeud d'arrivée (str)
    :param capacite: Capacité maximale de la liaison (int > 0)
    :param noms_noeuds: ensemble des noms de noeuds existants (set)
    :param liaisons_existantes: liste des liaisons existantes (pour vérifier doublon)
    :return: instance de Liaison
    :raises ValueError: si invalidité (liaison sur même noeud, noeuds inexistants, capacité non positive, doublon)
    """
    if depart == arrivee:
        raise ValueError("❌ Une liaison ne peut pas relier un noeud à lui-même.")

    if depart not in noms_noeuds or arrivee not in noms_noeuds:
        raise ValueError("❌ Noeud de départ ou d’arrivée introuvable.")

    if capacite <= 0:
        raise ValueError("❌ La capacité de la liaison doit être un entier positif.")

    # Vérifie doublon de liaison (même départ et arrivée)
    for l in liaisons_existantes:
        if l.depart == depart and l.arrivee == arrivee:
            raise ValueError("❌ Cette liaison existe déjà.")

    return Liaison(depart, arrivee, capacite)

class GestionReseau:
    def __init__(self, ListeNoeuds: List[Noeud] = None, ListeLiaisons: List[Liaison] = None) -> None:
        self.ListeNoeuds: List[Noeud] = ListeNoeuds if ListeNoeuds is not None else []
        self.ListeLiaisons: List[Liaison] = ListeLiaisons if ListeLiaisons is not None else []
        
    def __str__(self):
        res = "=== Gestion du Réseau ===\n"

        res += "\n-- Noeuds --\n"
        if self.ListeNoeuds:
            for i, noeud in enumerate(self.ListeNoeuds, 1):
                res += f"[Noeud {i}]\n{noeud}\n"
        else:
            res += "Aucun nœud enregistré.\n"

        res += "\n-- Liaisons --\n"
        if self.ListeLiaisons:
            for i, liaison in enumerate(self.ListeLiaisons, 1):
                res += f"[Liaison {i}]\n{liaison}\n"
        else:
            res += "Aucune liaison enregistrée.\n"

        return res
        
    def saisir_noeuds(self, type_noeud: str) -> None:
        """
        Saisie interactive des noeuds (source, ville, intermédiaire).
        Cette fonction demande à l'utilisateur de saisir des noeuds du type spécifié, 
        vérifie les doublons avec la liste globale ListeNoeuds, 
        crée les noeuds et les ajoute à ListeNoeuds.

        :param type_noeud: str - Type du noeud à saisir. Doit être "source", "ville" ou "intermediaire".
        :return: None (modifie directement la liste globale ListeNoeuds)
        """
        demande_capacite = (type_noeud != "intermediaire")
        noms_existants = {n.nom for n in self.ListeNoeuds}

        while True:
            nom = input(f"Nom de la {type_noeud} : ").strip().upper()

            # Pour le cas spécial si tu veux un signal de fin pour les intermédiaires
            if type_noeud == "intermediaire" and nom == "FIN":
                break

            if nom in noms_existants:
                print("❌ Ce nom est déjà utilisé. Choisis un autre nom.")
                continue

            capacite = 0
            if demande_capacite:
                try:
                    capacite = int(input("Capacité maximale : "))
                    if capacite <= 0:
                        print("❌ La capacité doit être un entier positif.")
                        continue
                except ValueError:
                    print("❌ Entrez un entier valide.")
                    continue

            try:
                noeud = creer_noeud(nom, type_noeud, capacite, noms_existants)
                self.ListeNoeuds.append(noeud)
                noms_existants.add(nom)
                print(f"✅ {type_noeud.capitalize()} ajoutée : {nom}")
            except ValueError as e:
                print(e)
                continue

            cont = input(f"Ajouter une autre {type_noeud} ? (o/n) : ").strip().lower()
            if cont != 'o':
                break

    def saisir_liaisons(self) -> None:
        """
        Saisie interactive des liaisons entre noeuds.

        Demande à l'utilisateur de saisir les noeuds de départ et d'arrivée ainsi que la capacité
        pour chaque liaison. La fonction vérifie que :
        - Les noeuds existent dans la liste globale ListeNoeuds,
        - La liaison ne relie pas un noeud à lui-même,
        - La liaison n'existe pas déjà dans la liste globale ListeLiaisons,
        - La capacité est un entier positif.

        Les liaisons valides sont créées via la fonction creer_liaison et ajoutées à ListeLiaisons.

        :return: None (modifie directement la liste globale ListeLiaisons)
        """
        noms_existants = {n.nom for n in self.ListeNoeuds}
        
        while True:
            depart = input("Départ de la liaison : ").strip().upper()
            arrivee = input("Arrivée de la liaison : ").strip().upper()

            if depart == arrivee:
                print("❌ Une liaison ne peut pas relier un noeud à lui-même.")
                continue

            if depart not in noms_existants or arrivee not in noms_existants:
                print("❌ Noeud de départ ou d’arrivée introuvable.")
                continue

            try:
                capacite = int(input("Capacité de la liaison : "))
                if capacite <= 0:
                    print("❌ La capacité doit être un entier positif.")
                    continue
            except ValueError:
                print("❌ Entrez un entier valide.")
                continue

            try:
                liaison = creer_liaison(depart, arrivee, capacite, noms_existants, self.ListeLiaisons)
                self.ListeLiaisons.append(liaison)
                print(f"✅ Liaison ajoutée : {depart} ➝ {arrivee}")
            except ValueError as e:
                print(e)
                continue

            cont = input("Ajouter une autre liaison ? (o/n) : ").strip().lower()
            if cont != 'o':
                break
    
    def sauvegarder_reseau(noeuds : List[Noeud], liaisons : List[Liaison], fichier : str, reseau_nom : str) -> None:
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
            "noeuds": [n.to_dict() for n in noeuds],
            "liaisons": [l.to_dict() for l in liaisons]
        }

        with open(fichier, 'w') as f:
            json.dump(data, f, indent=4)

    def charger_reseaux(fichier : str, reseau_nom: str) -> Tuple[List[Noeud], List[Liaison]]:
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
            raise FileNotFoundError(f"Fichier {fichier} non trouvé.")

        with open(fichier, 'r') as f:
            data = json.load(f)

        if reseau_nom not in data:
            raise ValueError(f"Réseau {reseau_nom} introuvable dans le fichier.")

        noeuds_data = data[reseau_nom]["noeuds"]
        liaisons_data = data[reseau_nom]["liaisons"]

        noeuds = [Noeud.from_dict(nd) for nd in noeuds_data]
        liaisons = [Liaison.from_dict(ld) for ld in liaisons_data]

        return noeuds, liaisons

    def supprimer_reseaux(fichier : str ='reseaux.json') -> None:
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

class ReseauHydraulique:
    def __init__(self, noeuds: List[Noeud], liaisons: List[Liaison]):
        self.noeuds = {n.nom: n for n in noeuds}
        self.liaisons = liaisons
        self.index_noeuds = {nom: i for i, nom in enumerate(self.noeuds.keys())}
        self.index_noeuds.update({"super_source": len(self.index_noeuds), "super_puits": len(self.index_noeuds) + 1})
        self.index_inverse = {v: k for k, v in self.index_noeuds.items()}
        n = len(self.index_noeuds)
        
        self.matrice_np = array([[0] * n for _ in range(n)])

        for l in liaisons:
            i, j = self.index_noeuds[l.depart], self.index_noeuds[l.arrivee]
            self.matrice_np[i][j] = l.capacite

        for node in self.noeuds.values():
            idx = self.index_noeuds[node.nom]
            if node.type == "source":
                self.matrice_np[self.index_noeuds["super_source"]][idx] = node.capaciteMax
            elif node.type == "ville":
                self.matrice_np[idx][self.index_noeuds["super_puits"]] = node.capaciteMax

        self.matrice_sparse = csr_matrix(self.matrice_np)
        print("Construction matrice (np) :")
        print(self.matrice_np)

    def __str__(self):
        noeuds_str = "\n".join(str(n) for n in self.noeuds.values())
        liaisons_str = "\n".join(str(l) for l in self.liaisons)
        return f"--- Noeuds ---\n{noeuds_str}\n\n--- Liaisons ---\n{liaisons_str}"

    def calculerFlotMaximal(self):
        result = maximum_flow(self.matrice_sparse, 
                              self.index_noeuds["super_source"], 
                              self.index_noeuds["super_puits"])
        print(f"💧 Flot maximal total : {result.flow_value} unités\n➡️ Détail des flux utilisés :\n")

        # result.flow est une matrice sparse contenant le flot passant par chaque arc
        flow_matrix = result.flow

        for i in range(flow_matrix.shape[0]):
            for j in range(flow_matrix.shape[1]):
                try:
                    used_flow = flow_matrix[i, j]
                    if used_flow > 0:
                        nom_i = self.index_inverse.get(i, f"[inconnu:{i}]")
                        nom_j = self.index_inverse.get(j, f"[inconnu:{j}]")
                        print(f"{nom_i} ➝ {nom_j} : {used_flow} unités")
                except Exception as e:
                    print(f"(Erreur lors de la lecture du flux de {i} à {j}) : {e}")

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
        
        Retourne :
            - La nouvelle configuration optimisée des liaisons.
            - La liste des travaux effectués sous forme : ((départ, arrivée), capacité choisie, flot atteint)
    """
    meilleure_config = liaisons_actuelles[:]
    liaisons_restantes = liaisons_a_optimiser[:]
    travaux_effectues = []

    reseau_temp = ReseauHydraulique(noeuds, meilleure_config)
    result_init, _ = reseau_temp.calculerFlotMaximal()

    while liaisons_restantes:
        meilleur_gain = result_init.flow_value
        meilleure_liaison = None
        meilleure_config_temp = None
        meilleur_result_temp = None
        meilleure_capacite = 0

        for liaison_cible in liaisons_restantes:
            depart, arrivee = liaison_cible
            
            for cap_test in [5, 10, 15, 20]:
                config_temp = []
                liaison_trouvee = False
                
                for liaison in meilleure_config:
                    if (liaison.depart, liaison.arrivee) == (depart, arrivee):
                        config_temp.append(Liaison(depart, arrivee, cap_test))
                        liaison_trouvee = True
                    else:
                        config_temp.append(liaison)
                
                if not liaison_trouvee:
                    config_temp.append(Liaison(depart, arrivee, cap_test))

                reseau_hydro = ReseauHydraulique(noeuds, config_temp)
                try:
                    result, _ = reseau_hydro.calculerFlotMaximal()
                except Exception as e:
                    print(f"Erreur lors du calcul pour {depart}->{arrivee} cap={cap_test} : {e}")
                    continue

                if result.flow_value > meilleur_gain:
                    meilleur_gain = result.flow_value
                    meilleure_liaison = (depart, arrivee)
                    meilleure_capacite = cap_test
                    meilleure_config_temp = config_temp[:]
                    meilleur_result_temp = result

            if meilleure_liaison:
                meilleure_config = meilleure_config_temp
                travaux_effectues.append((meilleure_liaison, meilleure_capacite, meilleur_result_temp.flow_value))
                liaisons_restantes.remove(meilleure_liaison)
                result_init = meilleur_result_temp  # mise à jour du flot de référence
            else:
                print("🚫 Aucun gain supplémentaire possible. Arrêt de l’optimisation.")
                break

    # Affichage du résumé clair (Qualité UX)
    print("\n📋 Résumé des travaux effectués :")
    for i, (liaison, cap, flot) in enumerate(travaux_effectues, 1):
        print(f"Travaux #{i} : {liaison[0]} -> {liaison[1]}, capacité {cap} ➝ flot atteint : {flot} unités")

    return meilleure_config, travaux_effectues

def demander_cap_max(valeur_defaut=25, essais_max=3) -> int:
    """
    Demande à l'utilisateur la capacité maximale à tester pour chaque liaison.
    Retourne un entier positif ou la valeur par défaut après plusieurs erreurs.
    """
    essais = 0
    while essais < essais_max:
        saisie = input(f"Entrez la capacité maximale à tester pour chaque liaison (défaut {valeur_defaut}) : ").strip()
        if not saisie:
            return valeur_defaut
        try:
            cap = int(saisie)
            if cap > 0:
                return cap
            else:
                print("⚠️ La capacité maximale doit être un entier positif.")
        except ValueError:
            print("⚠️ Entrée invalide, veuillez entrer un entier positif.")
        essais += 1
    print(f"Trop d'erreurs, utilisation de la valeur par défaut {valeur_defaut}.")
    return valeur_defaut



def satisfaction(
    noeuds: List[Noeud],
    liaisons_actuelles: List[Liaison],
    liaisons_possibles: List[Tuple[str, str]],
    objectif_flot: Optional[int] = None,
    cap_max: Optional[int] = None,
    max_travaux: int = 5
) -> Tuple[List[Liaison], List[Tuple[Tuple[str, str], int, int]]]:
    """
    Optimisation gloutonne limitée : à chaque étape, augmente la capacité d'une seule liaison saturée (greedy),
    jusqu'à 5 travaux consécutifs ou jusqu'à atteindre l'objectif.
    """
    if cap_max is None:
        raise ValueError("cap_max doit être défini par l'utilisateur.")

    objectif_calcule = sum(n.capaciteMax for n in noeuds if getattr(n, "type", "").lower() == "ville")
    if objectif_flot is None:
        objectif_flot = objectif_calcule

    config = copy.deepcopy(liaisons_actuelles)
    travaux = []

    reseau = ReseauHydraulique(noeuds, config)
    result, index_noeuds = reseau.calculerFlotMaximal()
    flot_actuel = result.flow_value

    if flot_actuel >= objectif_flot:
        return config, []

    essais = 0
    while flot_actuel < objectif_flot and essais < max_travaux:
        # Cherche les liaisons saturées
        liaisons_sats = liaisons_saturees(result, index_noeuds, config)
        candidates = [l for l in config if (l.depart, l.arrivee) in liaisons_sats and l.capacite < cap_max]
        if not candidates:
            break

        best_gain = 0
        best_liaison = None
        best_cap = None
        best_result = None

        for liaison in candidates:
            old_cap = liaison.capacite
            for new_cap in range(old_cap + 1, cap_max + 1):
                liaison.capacite = new_cap
                reseau_test = ReseauHydraulique(noeuds, config)
                result_test, _ = reseau_test.calculerFlotMaximal()
                gain = result_test.flow_value - flot_actuel
                if gain > best_gain:
                    best_gain = gain
                    best_liaison = (liaison.depart, liaison.arrivee)
                    best_cap = new_cap
                    best_result = result_test
                liaison.capacite = old_cap  # reset

        if best_gain == 0:
            essais += 1  # On compte quand même un essai même si pas d'amélioration
            continue    # On continue jusqu'à max_travaux

        # Applique la meilleure amélioration trouvée
        for liaison in config:
            if (liaison.depart, liaison.arrivee) == best_liaison:
                liaison.capacite = best_cap
                break
        flot_actuel = best_result.flow_value
        travaux.append((best_liaison, best_cap, flot_actuel))
        result = best_result  # update pour la prochaine boucle
        essais += 1

    return config, travaux

def liaisons_saturees(result, index_noeuds, liaisons):
    """Retourne la liste des (depart, arrivee) saturées dans le flot maximal."""
    saturees = []
    flow_matrix = result.flow
    for liaison in liaisons:
        i = index_noeuds[liaison.depart]
        j = index_noeuds[liaison.arrivee]
        if flow_matrix[i, j] >= liaison.capacite and liaison.capacite > 0:
            saturees.append((liaison.depart, liaison.arrivee))
    return saturees
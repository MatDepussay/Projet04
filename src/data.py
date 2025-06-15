from typing import List, Tuple, Dict, Optional
from numpy import array
import json
import os
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow


class Noeud:
    """
    Représente un nœud dans un réseau hydraulique.

    Un nœud peut être de type 'source', 'ville' ou 'intermediaire'.

    Attributs :
        nom (str): Le nom du nœud.
        type (str): Le type de nœud (source, ville ou intermediaire).
        capaciteMax (int): Capacité maximale d'entrée/sortie du nœud.
                            (0 si le nœud est intermédiaire)
    """

    VALID_TYPES = {"source", "ville", "intermediaire"}

    def __init__(self, nom: str, type: str, capaciteMax: int = 0) -> None:
        if type not in self.VALID_TYPES:
            raise ValueError(f"Type de nœud invalide : {type}")
        self.nom = nom
        self.type = type  # "source", "ville", "intermediaire"
        self.capaciteMax = capaciteMax

    def __str__(self):
        return (
            f"Nom : {self.nom}, Type : {self.type}, Capacite max : {self.capaciteMax}"
        )

    def __eq__(self, other):
        if not isinstance(other, Noeud):
            return NotImplemented
        return (self.nom, self.type, self.capaciteMax) == (
            other.nom,
            other.type,
            other.capaciteMax,
        )

    def to_dict(self):
        data = {"nom": self.nom, "type": self.type}
        # Ne stocke la capacité que si ce n'est pas un intermédiaire
        if self.type != "intermediaire":
            data["capaciteMax"] = self.capaciteMax
        return data

    @staticmethod
    def from_dict(data):
        return Noeud(data["nom"], data["type"], data.get("capaciteMax", 0))


class Liaison:
    """
    Représente une liaison entre deux nœuds dans un réseau hydraulique.

    Attributs :
        depart (str): Nom du nœud de départ.
        arrivee (str): Nom du nœud d'arrivée.
        capacite (int): Capacité maximale de la liaison.
    """

    def __init__(self, depart: str, arrivee: str, capacite: int) -> None:
        self.depart = depart
        self.arrivee = arrivee
        self.capacite = capacite

    def __str__(self):
        return f"Départ : {self.depart}, Arrivée : {self.arrivee}, Capacite : {self.capacite}"

    def __eq__(self, other):
        if not isinstance(other, Liaison):
            return NotImplemented
        return (self.depart, self.arrivee, self.capacite) == (
            other.depart,
            other.arrivee,
            other.capacite,
        )

    def to_dict(self):
        return {
            "depart": self.depart,
            "arrivee": self.arrivee,
            "capacite": self.capacite,
        }

    @staticmethod
    def from_dict(data):
        return Liaison(data["depart"], data["arrivee"], data["capacite"])


# Fonction de création
def creer_noeud(
    nom: str,
    type_noeud: str,
    capacite: int = 0,
    noms_existants: Optional[set[str]] = None,
) -> Noeud:
    """
    Crée un noeud après vérification que le nom n'existe pas déjà.

    Args :
        nom: Nom du noeud (str, majuscule recommandée)
        type_noeud: Type du noeud ("source", "ville", "intermediaire")
        capacite: Capacité maximale (int > 0 pour source/ville)
        noms_existants: ensemble des noms déjà utilisés (set)

    >>> return: le noeud créé

    Raises: ValueError: si le nom est déjà utilisé, type invalide ou capacité incorrecte
    """
    if noms_existants is None:
        noms_existants = set()

    if nom in noms_existants:
        raise ValueError("❌ Ce nom est déjà utilisé. Choisis un autre nom.")

    if type_noeud not in {"source", "ville", "intermediaire"}:
        raise ValueError(
            f"❌ Type de noeud invalide : '{type_noeud}'. Doit être 'source', 'ville' ou 'intermediaire'."
        )

    if type_noeud == "intermediaire":
        # Pas de capacité requise pour intermédiaire
        return Noeud(nom, type_noeud)
    else:
        if capacite <= 0:
            raise ValueError(
                "❌ La capacité doit être un entier positif pour les sources/ville"
            )
        return Noeud(nom, type_noeud, capacite)


def creer_liaison(
    depart: str,
    arrivee: str,
    capacite: int,
    noms_noeuds: set[str],
    liaisons_existantes: list[Liaison],
) -> Liaison:
    """
    Crée une liaison après vérification des contraintes.

    Args:
        depart (str): Nom du noeud de départ.
        arrivee (str): Nom du noeud d'arrivée.
        capacite (int): Capacité maximale (> 0) de la liaison.
        noms_noeuds (set[str]): Ensemble des noms de noeuds existants.
        liaisons_existantes (List[Liaison]): Liste des liaisons déjà créées.

    >>> Liaison: La liaison créée.

    Raises: ValueError: Si la liaison est invalide (même noeud, noeuds inexistants, capacité non positive, doublon).
    """
    if depart == arrivee:
        raise ValueError("❌ Une liaison ne peut pas relier un noeud à lui-même.")

    if depart not in noms_noeuds or arrivee not in noms_noeuds:
        raise ValueError("❌ Noeud de départ ou d’arrivée introuvable.")

    if capacite <= 0:
        raise ValueError("❌ La capacité de la liaison doit être un entier positif.")

    if any(
        liaison.depart == depart and liaison.arrivee == arrivee
        for liaison in liaisons_existantes
    ):
        raise ValueError("❌ Cette liaison existe déjà.")

    return Liaison(depart, arrivee, capacite)


class GestionReseau:
    """
    Classe de gestion d'un réseau hydraulique composé de nœuds et de liaisons.

    Cette classe permet :
    - la saisie interactive des nœuds (sources, villes, intermédiaires),
    - la saisie interactive des liaisons entre ces nœuds,
    - la gestion et le stockage des listes de nœuds et de liaisons,
    - la sauvegarde et le chargement des réseaux dans/depuis un fichier JSON,
    - la vérification d'existence des liaisons,
    - la suppression des fichiers de sauvegarde.

    Attributs :
        ListeNoeuds (List[Noeud]) : Liste des objets Noeud représentant les nœuds du réseau.
        ListeLiaisons (List[Liaison]) : Liste des objets Liaison représentant les connexions entre nœuds.

    Méthodes principales :
        - saisir_noeuds(type_noeud) : Saisie interactive des nœuds selon leur type.
        - saisir_liaisons() : Saisie interactive des liaisons entre nœuds.
        - liaison_existe(depart, arrivee, liaisons) : Vérifie si une liaison existe déjà.
        - sauvegarder_reseau(noeuds, liaisons, fichier, reseau_nom) : Sauvegarde un réseau dans un fichier JSON.
        - charger_reseaux(fichier) : Charge tous les réseaux enregistrés dans un fichier JSON.
        - supprimer_reseaux(fichier) : Supprime le fichier de sauvegarde des réseaux.

    Exemple d'utilisation :

        >>> gestion = GestionReseau()
        >>> gestion.saisir_noeuds("source")
        >>> gestion.saisir_noeuds("ville")
        >>> gestion.saisir_noeuds("intermediaire")
        >>> gestion.saisir_liaisons()
        >>> gestion.sauvegarder_reseau(gestion.ListeNoeuds, gestion.ListeLiaisons, "reseaux.json", "reseau_1")
        >>> reseaux = gestion.charger_reseaux("reseaux.json")
    """

    def __init__(
        self, ListeNoeuds: List[Noeud] = None, ListeLiaisons: List[Liaison] = None
    ) -> None:
        self.ListeNoeuds: List[Noeud] = ListeNoeuds if ListeNoeuds is not None else []
        self.ListeLiaisons: List[Liaison] = (
            ListeLiaisons if ListeLiaisons is not None else []
        )

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

        Attributs :
            type_noeud: str - Type du noeud à saisir. Doit être "source", "ville" ou "intermediaire".

        Retourne : None (modifie directement la liste globale ListeNoeuds)
        """
        demande_capacite = type_noeud != "intermediaire"
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

        >>> None (modifie directement la liste globale ListeLiaisons)
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
                liaison = creer_liaison(
                    depart, arrivee, capacite, noms_existants, self.ListeLiaisons
                )
                self.ListeLiaisons.append(liaison)
                print(f"✅ Liaison ajoutée : {depart} ➝ {arrivee}")
            except ValueError as e:
                print(e)
                continue

            cont = input("Ajouter une autre liaison ? (o/n) : ").strip().lower()
            if cont != 'o':
                break

    @staticmethod
    def liaison_existe(depart: str, arrivee: str, liaisons) -> bool:
        """
        Vérifie si une liaison existe entre deux sommets (insensible à la casse).
        """
        depart = depart.upper()
        arrivee = arrivee.upper()
        for liaison in liaisons:
            if liaison.depart.upper() == depart and liaison.arrivee.upper() == arrivee:
                return True
        return False

    @staticmethod
    def sauvegarder_reseaux(
        noeuds: List[Noeud], liaisons: List[Liaison], fichier: str, reseau_nom: str
    ) -> None:
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
            "liaisons": [liaison.to_dict() for liaison in liaisons],
        }

        with open(fichier, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def charger_reseaux(fichier: str) -> Dict[str, Tuple[List[Noeud], List[Liaison]]]:
        """
        Charge tous les réseaux hydrauliques sauvegardés depuis un fichier JSON.

        Args:
        fichier (str): Nom du fichier JSON à lire.

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

        reseaux = {}
        for nom_reseau, contenu in data.items():
            noeuds = [Noeud.from_dict(nd) for nd in contenu.get("noeuds", [])]
            liaisons = [Liaison.from_dict(ld) for ld in contenu.get("liaisons", [])]
            reseaux[nom_reseau] = (noeuds, liaisons)

        return reseaux

    @staticmethod
    def supprimer_reseaux(fichier: str = 'reseaux.json') -> None:
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
    """
    Classe représentant un réseau hydraulique orienté pour le calcul de flot maximal.

    Cette classe permet :
    - de construire la matrice d'adjacence du réseau à partir d'une liste de nœuds et de liaisons,
    - d'ajouter automatiquement une super source et un super puits pour modéliser l'approvisionnement global,
    - de calculer le flot maximal entre la super source et le super puits,
    - d'obtenir le détail des flux utilisés sur chaque liaison,
    - d'identifier les liaisons saturées (utilisées à leur capacité maximale).

    Attributs :
        noeuds (Dict[str, Noeud]) : Dictionnaire des objets Noeud indexés par leur nom.
        liaisons (List[Liaison]) : Liste des objets Liaison représentant les connexions entre nœuds.
        index_noeuds (Dict[str, int]) : Dictionnaire associant chaque nom de nœud à un indice de matrice.
        index_inverse (Dict[int, str]) : Dictionnaire inverse pour retrouver le nom d'un nœud à partir de son indice.
        matrice_np (np.ndarray) : Matrice d'adjacence du réseau (capacités).
        matrice_sparse (csr_matrix) : Version sparse de la matrice pour les algorithmes de flot.

    Méthodes principales :
        - __init__(noeuds, liaisons) : Construit la matrice du réseau avec super source/puits.
        - __str__() : Affiche une représentation textuelle du réseau.
        - calculerFlotMaximal() : Calcule le flot maximal et affiche le détail des flux.
        - liaisons_saturees(result) : Retourne la liste des liaisons saturées pour un résultat de flot donné.

    Exemple d'utilisation :

        >>> reseau = ReseauHydraulique(liste_noeuds, liste_liaisons)
        >>> result, index_noeuds = reseau.calculerFlotMaximal()
        >>> liaisons_sats = reseau.liaisons_saturees(result)
    """

    def __init__(self, noeuds: List[Noeud], liaisons: List[Liaison]):
        self.noeuds = {n.nom: n for n in noeuds}
        self.liaisons = liaisons

        self.index_noeuds = {nom: i for i, nom in enumerate(self.noeuds.keys())}
        self.index_noeuds["super_source"] = len(self.index_noeuds)
        self.index_noeuds["super_puits"] = len(self.index_noeuds)

        self.index_inverse = {v: k for k, v in self.index_noeuds.items()}
        n = len(self.index_noeuds)

        self.matrice_np = array([[0] * n for _ in range(n)])

        for liaison in liaisons:
            i, j = self.index_noeuds[liaison.depart], self.index_noeuds[liaison.arrivee]
            self.matrice_np[i][j] = liaison.capacite

        for node in self.noeuds.values():
            idx = self.index_noeuds[node.nom]
            if node.type == "source":
                self.matrice_np[self.index_noeuds["super_source"]][
                    idx
                ] = node.capaciteMax
            elif node.type == "ville":
                self.matrice_np[idx][
                    self.index_noeuds["super_puits"]
                ] = node.capaciteMax

        self.matrice_sparse = csr_matrix(self.matrice_np)

    def __str__(self):
        noeuds_str = "\n".join(str(n) for n in self.noeuds.values())
        liaisons_str = "\n".join(str(liaison) for liaison in self.liaisons)
        return f"--- Noeuds ---\n{noeuds_str}\n\n--- Liaisons ---\n{liaisons_str}"

    def calculerFlotMaximal(self):
        """
        Calcule le flot maximal entre la super source et le super puits,
        et affiche les flux utilisés sur chaque liaison.

        >>> Returns:
            result: objet de résultat de `maximum_flow`
            index_noeuds: dictionnaire {nom: index} utile pour interpréter les matrices
        """
        result = maximum_flow(
            self.matrice_sparse,
            self.index_noeuds["super_source"],
            self.index_noeuds["super_puits"],
        )
        print(
            f"💧 Flot maximal total : {result.flow_value} unités\n➡️ Détail des flux utilisés :\n"
        )

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

    def liaisons_saturees(self, result):
        """
        Retourne la liste des liaisons saturées (utilisé == capacité).

        Args:
            result: Résultat de maximum_flow (contenant result.flow)

        Returns:
            Liste des liaisons saturées sous forme (nom_depart, nom_arrivee, capacite)
        """
        return [
            (liaison.depart, liaison.arrivee, liaison.capacite)
            for liaison in self.liaisons
            if result.flow[
                self.index_noeuds[liaison.depart], self.index_noeuds[liaison.arrivee]
            ]
            == liaison.capacite
        ]


def optimiser_liaisons(
    noeuds: List[Noeud],
    liaisons_actuelles: List[Liaison],
    liaisons_a_optimiser: List[Tuple[str, str]],
) -> Tuple[List[Liaison], List[Tuple[Tuple[str, str], int, int]]]:
    """
    Optimise l'ordre et la capacités des flots des liaisons choisies afin de maximiser le flot global.

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
                    print(
                        f"Erreur lors du calcul pour {depart}->{arrivee} cap={cap_test} : {e}"
                    )
                    continue

                if result.flow_value > meilleur_gain:
                    meilleur_gain = result.flow_value
                    meilleure_liaison = (depart, arrivee)
                    meilleure_capacite = cap_test
                    meilleure_config_temp = config_temp[:]
                    meilleur_result_temp = result

        if meilleure_liaison:
            meilleure_config = meilleure_config_temp
            travaux_effectues.append(
                (meilleure_liaison, meilleure_capacite, meilleur_result_temp.flow_value)
            )
            if meilleure_liaison in liaisons_restantes:
                liaisons_restantes.remove(meilleure_liaison)
            else:
                print(
                    "⚠️ Liaison déjà supprimée ou non trouvée, arrêt de la boucle pour éviter un blocage."
                )
                break
            result_init = meilleur_result_temp  # mise à jour du flot de référence
        else:
            print("🚫 Aucun gain supplémentaire possible. Arrêt de l’optimisation.")
            break

    print("\n📋 Résumé des travaux effectués :")
    for i, (liaison, cap, flot) in enumerate(travaux_effectues, 1):
        print(
            f"Travaux #{i} : {liaison[0]} -> {liaison[1]}, capacité {cap} ➝ flot atteint : {flot} unités"
        )

    return meilleure_config, travaux_effectues


def demander_cap_max(valeur_defaut=25, essais_max=3) -> int:
    """
    Demande à l'utilisateur la capacité maximale à tester pour chaque liaison.
    Retourne un entier positif ou la valeur par défaut après plusieurs erreurs.
    """
    essais = 0
    while essais < essais_max:
        saisie = input(
            f"Entrez la capacité maximale à tester pour chaque liaison (défaut {valeur_defaut}) : "
        ).strip()
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
    noeuds, liaisons, optimiser_fonction=None, objectif=None, cap_max=25, max_travaux=5
) -> Tuple[List[Liaison], List[Tuple[Tuple[str, str], int, int]]]:
    """
    Optimise les capacités du réseau hydraulique pour satisfaire la demande des villes.

    Cette fonction améliore progressivement les capacités de certaines liaisons du réseau
    (qu'elles soient saturées ou non), afin de maximiser le flot entre les sources et les
    villes, jusqu'à satisfaire entièrement la demande ou atteindre une limite fixée de travaux.

    À chaque itération :
    - on teste une augmentation de capacité pour chaque liaison,
    - on applique la meilleure amélioration détectée (celle qui maximise le flot),
    - on répète jusqu'à `max_travaux` améliorations ou jusqu'à atteindre l'objectif.

    Args:
        noeuds (List[Noeud]): Liste des nœuds du réseau (sources, villes, intermédiaires).
        liaisons (List[Liaison]): Liste des liaisons (arêtes) avec leurs capacités initiales.
        optimiser_fonction (Callable, optional): Fonction personnalisée d’optimisation (non utilisée ici).
        objectif (int, optional): Flot cible à atteindre. Si non spécifié, la somme des demandes des villes est utilisée.
        cap_max (int, optional): Capacité maximale autorisée pour une liaison après amélioration. Par défaut à 25.
        max_travaux (int, optional): Nombre maximal de travaux (améliorations) autorisés. Par défaut à 5.

    Returns:
        Tuple:
            - List[Liaison]: Liste des liaisons après optimisation.
            - List[Tuple[Tuple[str, str], int, int]]: Liste des travaux réalisés, avec pour chacun :
            (liaison modifiée, capacité finale, flot maximal obtenu après modification).
    """
    objectif_utilisateur = objectif or sum(
        n.capaciteMax for n in noeuds if n.type == "ville"
    )
    reseau = ReseauHydraulique(noeuds, liaisons)
    result, index_noeuds = reseau.calculerFlotMaximal()
    travaux_effectues = []
    liaisons_courantes = liaisons[:]
    essais = 0

    while result.flow_value < objectif_utilisateur and essais < max_travaux:
        meilleure_amelioration = None
        meilleur_gain = 0
        meilleur_cap = None
        meilleur_new_flot = None

        # Pour chaque liaison, on essaie d'augmenter d'autant que possible d'un coup
        for liaison in liaisons_courantes:
            depart, arrivee, cap_actuelle = (
                liaison.depart,
                liaison.arrivee,
                liaison.capacite,
            )
            cap_test = cap_actuelle
            flot_ref = result.flow_value
            last_gain = 0
            # On augmente la capacité tant que le flot augmente et qu'on ne dépasse pas cap_max
            for cap_test in range(cap_actuelle + 5, cap_max + 1, 5):
                liaisons_test = [
                    Liaison(
                        liaison_obj.depart,
                        liaison_obj.arrivee,
                        (
                            cap_test
                            if liaison_obj.depart == depart
                            and liaison_obj.arrivee == arrivee
                            else liaison_obj.capacite
                        ),
                    )
                    for liaison_obj in liaisons_courantes
                ]
                reseau_test = ReseauHydraulique(noeuds, liaisons_test)
                result_test, _ = reseau_test.calculerFlotMaximal()
                gain = result_test.flow_value - flot_ref
                if gain > 0:
                    last_gain = gain
                    meilleur_cap_temp = cap_test
                    meilleur_new_flot_temp = result_test.flow_value
                    break  # On s'arrête dès qu'on trouve un gain pour cette liaison

            # Si on a trouvé une amélioration sur cette liaison
            if (
                last_gain > 0
                and (meilleur_new_flot_temp - result.flow_value) > meilleur_gain
            ):
                meilleure_amelioration = (depart, arrivee)
                meilleur_cap = meilleur_cap_temp
                meilleur_gain = meilleur_new_flot_temp - result.flow_value
                meilleur_new_flot = meilleur_new_flot_temp

        if meilleure_amelioration is None:
            print("Aucune amélioration possible, arrêt.")
            break

        # Appliquer la meilleure amélioration trouvée
        depart, arrivee = meilleure_amelioration
        for i, liaison_courante in enumerate(liaisons_courantes):
            if (
                liaison_courante.depart == depart
                and liaison_courante.arrivee == arrivee
            ):
                liaisons_courantes[i] = Liaison(depart, arrivee, meilleur_cap)
                break

        travaux_effectues.append(((depart, arrivee), meilleur_cap, meilleur_new_flot))
        reseau = ReseauHydraulique(noeuds, liaisons_courantes)
        result, _ = reseau.calculerFlotMaximal()
        essais += 1

    print(
        f"✅ Objectif atteint ou optimisation maximale atteinte. Flot final : {result.flow_value} / {objectif_utilisateur}"
    )
    if travaux_effectues:
        # Regroupe les travaux par liaison
        resume_travaux = {}
        for (depart, arrivee), cap, new_flot in travaux_effectues:
            key = (depart, arrivee)
            if key not in resume_travaux:
                resume_travaux[key] = {
                    "cap_depart": None,
                    "cap_fin": cap,
                    "flot": new_flot,
                }
            else:
                resume_travaux[key]["cap_fin"] = cap
                resume_travaux[key]["flot"] = new_flot
        # Cherche la capacité de départ pour chaque liaison
        for depart, arrivee in resume_travaux:
            cap_depart = None
            for liaison_obj in liaisons:
                if liaison_obj.depart == depart and liaison_obj.arrivee == arrivee:
                    cap_depart = liaison_obj.capacite
                    break
            resume_travaux[(depart, arrivee)]["cap_depart"] = cap_depart

        print("📋 Résumé des travaux réalisés :")
        for (depart, arrivee), infos in resume_travaux.items():
            print(
                f"  - Liaison {depart} ➝ {arrivee} : capacité {infos['cap_depart']} ➔ {infos['cap_fin']} unités, flot maximal atteint lors du dernier changement : {infos['flot']} unités"
            )
    else:
        print("Aucune amélioration n'a pu être réalisée.")
    return liaisons_courantes, travaux_effectues

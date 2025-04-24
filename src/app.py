from affichage import afficherCarte
from data import ListeLiaison, ListeSommet, calculerFlotMaximal
import copy

def liaison_existe(u, v, liaisons):
    for a, b, _ in liaisons:
        if (a == u and b == v) or (a == v and b == u):
            return True
    return False


def menu_terminal():
    liaisons_actuelles = copy.deepcopy(ListeLiaison)

    while True:
        print("\n=== MENU ===")
        print("1. Afficher la carte actuelle (Départ)")
        print("2. Travaux")
        print("3. Quitter")

        choix = input("Choix : ")

        if choix == "1":
            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)


        elif choix == "2":
            print("🛠 Sélectionne les liaisons à mettre en travaux (à optimiser automatiquement)")
            liaisons_a_optimiser = []

            while True:
                u = input("Sommet de départ : ").strip().upper()
                v = input("Sommet d’arrivée : ").strip().upper()

                if not liaison_existe(u, v, liaisons_actuelles):
                    print(f"❌ La liaison ({u}, {v}) n’existe pas.")
                    continue

                liaisons_a_optimiser.append((u, v))
                continuer = input("➕ Ajouter une autre liaison ? (o/n) : ").strip().lower()
                if continuer != 'o':
                    break

            print("🔍 Calcul des capacités optimales...")

            # Sauvegarde de la version originale
            original_liaisons = liaisons_actuelles[:]
            meilleure_config = None
            meilleur_flot = -1

            # Pour chaque combinaison de capacités possibles (1 à 20 pour chaque liaison)
            # Ici on teste indépendamment chaque liaison
            for cap_test in range(1, 21):
                test_liaisons = original_liaisons[:]
                for i, (a, b, cap) in enumerate(test_liaisons):
                    for (u, v) in liaisons_a_optimiser:
                        if a == u and b == v:
                            test_liaisons[i] = (a, b, cap_test)

                result, index_noeuds = calculerFlotMaximal(test_liaisons)
                if result.flow_value > meilleur_flot:
                    meilleur_flot = result.flow_value
                    meilleure_config = test_liaisons[:]

            liaisons_actuelles[:] = meilleure_config
            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)

            # Calcul de l’approvisionnement
            appro = {p: result.flow[index_noeuds[p], index_noeuds['super_puits']] for p in ['J', 'K', 'L']}

            print(f"✅ Capacités optimales appliquées. Nouveau flot maximal : {result.flow_value}")
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)


            continuer = input("🔁 Effectuer d'autres travaux ? (o/n) : ").strip().lower()
            if continuer != 'o':
                break


        elif choix == "3":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu_terminal()
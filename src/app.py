from affichage import afficherCarte
from data import ListeLiaison, calculerFlotMaximal, liaison_existe, optimiser_liaisons, optimiser_liaisons_pour_approvisionnement
from data import liaison as Liaison
import copy


def menu_terminal():
    liaisons_actuelles = copy.deepcopy(ListeLiaison)

    while True:
        print("\n=== MENU ===")
        print("1. Afficher la carte actuelle (Départ)")
        print("2. Travaux")
        print("3. Approvisionnement des villes")
        print("4. Quitter")

        choix = input("Choix : ")

        if choix == "1":
            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)

        elif choix == "2":
            print("🛠 Sélectionne les liaisons à mettre en travaux (ordre optimisé automatiquement)")
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

            print("🔍 Optimisation de l’ordre des travaux...")

            # 👉 Appel de la fonction d'optimisation du fichier data
            config_finale, travaux = optimiser_liaisons(liaisons_actuelles, liaisons_a_optimiser)

            for i, (liaison, cap, flot) in enumerate(travaux):
                u, v = liaison
                print(f"🔧 Travaux #{i+1} : Liaison {u} ➝ {v}")
                print(f"   ↪ Capacité choisie : {cap} unités")
                print(f"   🚀 Nouveau flot maximal : {flot} unités\n")

            # 💧 Affichage de la carte finale
            result, index_noeuds = calculerFlotMaximal(config_finale)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
        
        elif choix == "3":
            # Définir les liaisons candidates (ou laisser en dur une liste raisonnable)
            liaisons_possibles = [(l.depart, l.arrivee) for l in ListeLiaison][:20]

            # Appel de la fonction avec objectif 50
            config_finale, travaux = optimiser_liaisons_pour_approvisionnement(ListeLiaison, liaisons_possibles, objectif_flot=50)

            # Affichage du résultat
            print(f"✅ Objectif atteint avec {len(travaux)} travaux :")
            for (u, v), cap, flot in travaux:
                print(f"🔧 {u} → {v} capacité {cap} => flot = {flot} u")

            # Affichage de la carte
            result, index_noeuds = calculerFlotMaximal(config_finale)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
        elif choix == "4":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu_terminal()


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
            u = input("Sommet de départ : ").strip().upper()
            v = input("Sommet d’arrivée : ").strip().upper()

            if not liaison_existe(u, v, liaisons_actuelles):
                print(f"❌ La liaison ({u}, {v}) n’existe pas.")
                continue

            try:
                nouvelle_capacite = int(input("Nouvelle capacité : "))
            except ValueError:
                print("❌ Capacité invalide.")
                continue

            
            for i, (a, b, cap) in enumerate(liaisons_actuelles):
                if (a == u and b == v) or (a == v and b == u):
                    liaisons_actuelles[i] = (a, b, nouvelle_capacite)
                    print(f"✅ Liaison ({a}, {b}) mise à jour à {nouvelle_capacite}")
                    break

            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)

            # Demander à l'utilisateur s'il veut continuer
            continuer = input("🔁 Modifier une autre liaison ? (o/n) : ").strip().lower()
            if continuer != 'o':
                break


        elif choix == "3":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu_terminal()
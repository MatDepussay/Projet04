from affichage import afficherCarte , afficherCarteEnoncer
from data import  ListeNoeuds,ListeLiaison, calculerFlotMaximal, liaison_existe, optimiser_liaisons
from data import liaison as Liaison
import copy
import random

def menu_terminal():
    liaisons_actuelles = copy.deepcopy(ListeLiaison)

    while True:
        print("\n=== MENU ===")
        print("0. Afficher la carte de l'énoncer")
        print("1. Afficher la carte Enoncer avec fluxmax")
        print("2. Travaux")
        print("3. Generalisation")
        print("4. Quitter")

        choix = input("Choix : ")

        if choix == "0":
            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
            afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)
        
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
            sources = [n for n in ListeNoeuds if n.type == "source"]
            
            if not sources:
                print("❌ Aucune source trouvée.")
                continue
            
            # Choisir une source aléatoire
            source_choisie = random.choice(sources)
            print(f"🎲 Source choisie aléatoirement : {source_choisie.nom}")

            # Mise à jour de la capacité de la source à 0
            for n in ListeNoeuds:
                if n.nom == source_choisie.nom:
                    n.capaciteMax = 0
                    break

            # Recalcul du flot maximal
            result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)

        elif choix == "4":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")
        
        
if __name__ == "__main__":
    menu_terminal()
from affichage import afficherCarte, afficherCarteEnoncer
from data import *
from data import liaison as Liaison
import copy
import random
import matplotlib.pyplot as plt 


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
            reseau = ReseauHydraulique(ListeNoeuds, liaisons_actuelles)
            result, index_noeuds = reseau.calculerFlotMaximal()
            afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)


        if choix == "1":
            reseau = ReseauHydraulique(ListeNoeuds, liaisons_actuelles)
            result, index_noeuds = reseau.calculerFlotMaximal()
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)

        elif choix == "2":
            print("🛠 Sélectionne les liaisons à mettre en travaux (ordre optimisé automatiquement)")
            liaisons_a_optimiser = []

            while True:
                u = input("Sommet de départ : ").strip().upper()
                v = input("Sommet d’arrivée : ").strip().upper()
                
                if u == v:
                    print("❌ La liaison ne peut pas être entre un même sommet.")
                    continue

                if not liaison_existe(u, v, liaisons_actuelles):
                    print(f"❌ La liaison ({u}, {v}) n’existe pas.")
                    continue

                liaisons_a_optimiser.append((u, v))
                continuer = input("➕ Ajouter une autre liaison ? (o/n) : ").strip().lower()
                if continuer != 'o':
                    break

            print("🔍 Optimisation de l’ordre des travaux...")

            # 👉 Appel de la fonction d'optimisation du fichier data
            config_finale, travaux = optimiser_liaisons(ListeNoeuds, liaisons_actuelles, liaisons_a_optimiser)

            for i, (liaison, cap, flot) in enumerate(travaux):
                u, v = liaison
                print(f"🔧 Travaux #{i+1} : Liaison {u} ➝ {v}")
                print(f"   ↪ Capacité choisie : {cap} unités")
                print(f"   🚀 Nouveau flot maximal : {flot} unités\n")

            # 💧 Affichage de la carte finale
            result, index_noeuds = calculerFlotMaximal_temp(ListeNoeuds, config_finale)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
        
        elif choix == "3":
            menu_generalisation()

        elif choix == "4":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")
        
def menu_generalisation():
    while True:
        print("\n=== MENU GÉNÉRALISATION ===")
        print("1. Optimiser les liaisons pour approvisionner 100% les villes")
        print("2. Conserver le calcul actuel (flot maximal existant)")
        print("3. Retour")

        choix = input("Choix : ")

        if choix == "1":
            objectif = sum(n.capaciteMax for n in ListeNoeuds if n.type == "ville")
            print(f"\n🎯 Objectif : Approvisionner {objectif} unités (100% des villes)")
            
            # Définir les liaisons modifiables : ici on autorise à modifier toutes les liaisons existantes
            liaisons_modifiables = [(l.depart, l.arrivee) for l in ListeLiaison]

            nouvelle_config, travaux = optimiser_liaisons_pour_approvisionnement(
                liaisons_actuelles=ListeLiaison,
                liaisons_possibles=liaisons_modifiables,
                objectif_flot=objectif
            )

            print("\n🔧 Travaux effectués :")
            for (depart, arrivee), cap, new_flot in travaux:
                print(f"- Liaison {depart} ➝ {arrivee} ajustée à {cap} u. → Flot = {new_flot} u.")

            print("\n📈 Résultat final avec nouvelle configuration :\n")
            reseau_opt = ReseauHydraulique(ListeNoeuds, nouvelle_config)
            result, _ = reseau_opt.calculerFlotMaximal()

        elif choix == "2":
            sources = [n for n in ListeNoeuds if n.type == "source"]
            if not sources:
                print("❌ Aucune source trouvée.")
                return

            source_choisie = random.choice(sources)
            print(f"🎲 Source choisie aléatoirement : {source_choisie.nom}")

            # 💥 Mise à jour de la capacité de la source à 0
            for n in ListeNoeuds:
                if n.nom == source_choisie.nom:
                    print(f"💧 Capacité de la source {n.nom} mise à 0.")
                    n.capaciteMax = 0
                    break

            # Recalcul du flot maximal
            result, index_noeuds = calculerFlotMaximal_temp(ListeNoeuds, ListeLiaison)
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=ListeLiaison)
            plt.pause(0.1)

            # === Sélection d’une liaison à mettre en travaux pendant que la carte est ouverte ===
            print("\n=== Sélectionne une liaison à mettre en travaux ===")
            while True:
                u = input("Sommet de départ : ").strip().upper()
                v = input("Sommet d’arrivée : ").strip().upper()

                if not liaison_existe(u, v, ListeLiaison):
                    print(f"❌ La liaison ({u} ➝ {v}) n’existe pas. Réessaie.")
                    continue
                break

            # Mise en travaux de la liaison
            for liaison in ListeLiaison:
                if liaison.depart == u and liaison.arrivee == v:
                    print(f"🔧 Mise en travaux de la liaison : {u} ➝ {v}")
                    print(f"   Capacité actuelle : {liaison.capacite}")
                    liaison.capacite += 5
                    print(f"   ✅ Nouvelle capacité : {liaison.capacite}")
                    break

            # Recalcul du flot après travaux
            reseau = ReseauHydraulique(ListeNoeuds, ListeLiaison)
            result_modifie, index_noeuds_modifie = reseau.calculerFlotMaximal()

            # Affichage mis à jour
            afficherCarte(result=result_modifie, index_noeuds=index_noeuds_modifie, liaisons=ListeLiaison)
            print(f"🚀 Nouveau flot maximal : {result_modifie.flow_value} u.")
            plt.ioff()

        elif choix == "3":
            break
        else:
            print("⛔ Choix invalide. Réessaie.")


if __name__ == "__main__":
    menu_terminal()


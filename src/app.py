from affichage import afficherCarte, afficherCarteEnoncer
from data import ListeNoeuds, ListeLiaisons, ReseauHydraulique, optimiser_liaisons, optimiser_liaisons_pour_approvisionnement, liaison_existe
import copy
import random
import matplotlib.pyplot as plt 


def menu_terminal():
    """    Affiche un menu interactif dans le terminal pour visualiser et manipuler un réseau hydraulique.

    Ce menu propose plusieurs fonctionnalités :
    0 - Afficher la carte de l'énoncé sans flot maximal.
    1 - Calculer et afficher la carte avec le flot maximal.
    2 - Lancer une optimisation des travaux sur certaines liaisons :
        - L'utilisateur sélectionne manuellement les liaisons à optimiser.
        - Le programme optimise l’ordre des travaux pour maximiser le flot.
        - Affiche les nouvelles capacités et le flot maximal à chaque étape.
    3 - Accéder au sous-menu de généralisation.
    4 - Quitter le programme.

    La fonction exécute une boucle infinie jusqu’à ce que l’utilisateur choisisse de quitter.
    Elle effectue des copies profondes des données pour éviter toute modification accidentelle.

    Aucune valeur n'est retournée. Tous les résultats sont affichés directement dans le terminal."""
    liaisons_actuelles = copy.deepcopy(ListeLiaisons)

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
            reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
            result, index_noeuds = reseau.calculerFlotMaximal()

            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
        
        elif choix == "3":
            menu_generalisation()

        elif choix == "4":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")
        
def menu_generalisation():
    """
    Affiche un menu terminal dédié à des scénarios de généralisation sur le réseau hydraulique.

    Ce menu permet d'explorer et de tester deux cas plus complexes :
    
    1 - Optimiser dynamiquement les liaisons du réseau pour garantir un approvisionnement 
        à 100 % des villes. Cela repose sur un recalcul global des capacités des liaisons existantes 
        pour atteindre un objectif de flot précis (la somme des besoins des villes).
    
    2 - Simuler l'assèchement aléatoire d'une source :
        - Choix aléatoire d'une source dont la capacité est mise à zéro.
        - Affichage du nouveau flot maximal.
        - L'utilisateur choisit ensuite une liaison à renforcer (+5 unités de capacité).
        - Affichage mis à jour avec le nouveau flot après ces travaux.

    3 - Revenir au menu précédent.

    La fonction boucle jusqu'à ce que l'utilisateur choisisse de quitter ce sous-menu.

    Aucune valeur n’est retournée ; les actions sont effectuées et les résultats affichés
    directement dans le terminal et via des cartes graphiques.
    """
    while True:
        print("\n=== MENU GÉNÉRALISATION ===")
        print("1. Optimiser les liaisons pour approvisionner 100% les villes")
        print("2. Assèchement aléatoire d’une source")
        print("3. Retour")

        choix = input("Choix : ")

        if choix == "1":
            objectif = sum(n.capaciteMax for n in ListeNoeuds if n.type == "ville")
            print(f"\n🎯 Objectif : Approvisionner {objectif} unités (100% des villes)")
            
            # Définir les liaisons modifiables : ici on autorise à modifier toutes les liaisons existantes
            liaisons_modifiables = [(liaison.depart, liaison.arrivee) for liaison in ListeLiaisons]

            nouvelle_config, travaux = optimiser_liaisons_pour_approvisionnement(
                noeuds=ListeNoeuds,
                liaisons_actuelles=ListeLiaisons,
                liaisons_possibles=liaisons_modifiables,
                objectif_flot=objectif
            )

            print("\n🔧 Travaux effectués :")
            for (depart, arrivee), cap, new_flot in travaux:
                print(f"- Liaison {depart} ➝ {arrivee} ajustée à {cap} u. → Flot = {new_flot} u.")

            print("\n📈 Résultat final avec nouvelle configuration :\n")
            reseau_opt = ReseauHydraulique(ListeNoeuds, nouvelle_config)
            result, index_noeuds = reseau_opt.calculerFlotMaximal()  # Ce résultat est déjà correct
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=nouvelle_config)

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
            reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
            result, index_noeuds = reseau.calculerFlotMaximal()

            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=ListeLiaisons)
            plt.pause(0.1)

            # === Sélection d’une liaison à mettre en travaux pendant que la carte est ouverte ===
            print("\n=== Sélectionne une liaison à mettre en travaux ===")
            while True:
                u = input("Sommet de départ : ").strip().upper()
                v = input("Sommet d’arrivée : ").strip().upper()

                if not liaison_existe(u, v, ListeLiaisons):
                    print(f"❌ La liaison ({u} ➝ {v}) n’existe pas. Réessaie.")
                    continue
                break

            # Mise en travaux de la liaison
            for liaison in ListeLiaisons:
                if liaison.depart == u and liaison.arrivee == v:
                    print(f"🔧 Mise en travaux de la liaison : {u} ➝ {v}")
                    print(f"   Capacité actuelle : {liaison.capacite}")
                    liaison.capacite += 5
                    print(f"   ✅ Nouvelle capacité : {liaison.capacite}")
                    break

            # Recalcul du flot après travaux
            reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
            result_modifie, index_noeuds_modifie = reseau.calculerFlotMaximal()

            # Affichage mis à jour
            afficherCarte(result=result_modifie, index_noeuds=index_noeuds_modifie, liaisons=ListeLiaisons)
            print(f"🚀 Nouveau flot maximal : {result_modifie.flow_value} u.")
            plt.ioff()

        elif choix == "3":
            break
        else:
            print("⛔ Choix invalide. Réessaie.")


if __name__ == "__main__":
    menu_terminal()


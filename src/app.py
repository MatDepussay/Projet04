from affichage import afficherCarte
from data import ListeLiaison, calculerFlotMaximal
from data import liaison as Liaison


import copy

def liaison_existe(u, v, liaisons):
    for l in liaisons:
        a = l.depart
        b = l.arrivee
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

            meilleure_config = liaisons_actuelles[:]
            liaisons_restantes = liaisons_a_optimiser[:]
            travaux_effectues = []
            flot_actuel, _ = calculerFlotMaximal(meilleure_config)
            meilleur_flot = flot_actuel.flow_value

            while liaisons_restantes:
                meilleur_gain = -1
                meilleure_liaison = None
                meilleure_config_temp = None
                meilleur_result_temp = None

                for liaison_cible in liaisons_restantes:
                    for cap_test in range(1, 21):
                        # Construction d'une nouvelle configuration basée sur la dernière version
                        temp_config = []
                        for l in liaisons_actuelles:
                            if (l.depart, l.arrivee) == liaison_cible or (l.arrivee, l.depart) == liaison_cible:
                                temp_config.append(Liaison(l.depart, l.arrivee, cap_test))
                            else:
                                temp_config.append(Liaison(l.depart, l.arrivee, l.capacite))

                        temp_result, _ = calculerFlotMaximal(temp_config)

                        if temp_result.flow_value > meilleur_gain:
                            meilleur_gain = temp_result.flow_value
                            meilleure_liaison = (liaison_cible, cap_test)
                            meilleure_config_temp = temp_config
                            meilleur_result_temp = temp_result

                if meilleure_liaison:
                    liaisons_actuelles = meilleure_config_temp
                    travaux_effectues.append(meilleure_liaison)
                    liaisons_restantes.remove(meilleure_liaison[0])
                    print(f"🔧 Travaux #{len(travaux_effectues)} : Liaison {meilleure_liaison[0][0]} ➝ {meilleure_liaison[0][1]}")
                    print(f"   ↪ Capacité choisie : {meilleure_liaison[1]} unités")
                    print(f"   🚀 Nouveau flot maximal : {meilleur_result_temp.flow_value} unités\n")

                    result, index_noeuds = calculerFlotMaximal(liaisons_actuelles)
                    afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=liaisons_actuelles)
                else:
                    break  # Plus de gain possible

        elif choix == "3":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu_terminal()
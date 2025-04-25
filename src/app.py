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

                for liaison in liaisons_restantes:
                    for cap_test in range(1, 21):
                        temp_temp_config = meilleure_config[:]
                        for i, (a, b, cap) in enumerate(temp_temp_config):
                            if (a, b) == liaison or (b, a) == liaison:
                                temp_temp_config[i] = (a, b, cap_test)
                        temp_result, _ = calculerFlotMaximal(temp_temp_config)
                        if temp_result.flow_value > meilleur_gain:
                            meilleur_result_temp = temp_result    
                            meilleur_gain = temp_result.flow_value
                            meilleure_liaison = (liaison, cap_test)
                            meilleure_config_temp = temp_temp_config[:]

                if meilleure_liaison:
                    meilleure_config = meilleure_config_temp[:]
                    travaux_effectues.append(meilleure_liaison)
                    liaisons_restantes.remove(meilleure_liaison[0])
                    meilleur_flot = meilleur_result_temp.flow_value

                    print(f"🔧 Travaux #{len(travaux_effectues)} : Liaison {meilleure_liaison[0][0]} ➝ {meilleure_liaison[0][1]}")
                    print(f"   ↪ Capacité choisie : {meilleure_liaison[1]} unités")
                    print(f"   🚀 Nouveau flot maximal : {meilleur_flot} unités\n")
                else:
                    break  # Sécurité




        elif choix == "3":
            print("Au revoir 👋")
            break
        else:
            print("❌ Choix invalide.")

if __name__ == "__main__":
    menu_terminal()
"""
demo.py

Script de démonstration pour la modélisation, l'analyse et l'optimisation d'un réseau hydraulique.

Ce programme effectue plusieurs opérations sur un réseau de distribution d’eau entre des sources et des villes,
en passant par des noeuds intermédiaires, à l’aide d’algorithmes de flot maximal et d’optimisation incrémentale.

Fonctionnalités principales :
----------------------------
1. Définition d’un réseau hydraulique avec des noeuds (sources, villes, intermédiaires) et des liaisons (canalisations).
2. Calcul du flot maximal initial dans le réseau.
3. Optimisation ciblée de certaines liaisons pour augmenter le flot.
4. Comparaison visuelle du réseau avant et après optimisation.
5. Tentative de satisfaction totale des besoins en eau des villes (100 % de la demande).
6. Affichage des liaisons saturées (utilisées à capacité maximale).
7. Vérification par assertion que l’objectif est bien atteint.
8. Sauvegarde d’une figure du réseau final optimisé.
9. Simulation d’un objectif irréaliste pour illustrer les limites du système.

Modules requis :
----------------
- `matplotlib.pyplot` : pour la visualisation.
- `copy` : pour la duplication profonde des objets.
- `data` : contient les classes `Noeud`, `Liaison`, `ReseauHydraulique` ainsi que les fonctions `optimiser_liaisons` et `satisfaction`.
- `affichage` : contient la fonction `afficherCarte`.

Auteurs :
---------
Ce script est généralement utilisé à des fins pédagogiques pour illustrer :
- Les algorithmes de flot maximal.
- L'optimisation incrémentale de capacités de transport.
- La visualisation de graphes orientés pondérés.

Utilisation :
-------------
Exécuter directement ce script depuis un environnement compatible avec l'affichage graphique (Jupyter, terminal avec interface graphique, etc.) :

    python demo.py

Résultats :
-----------
Le script affiche plusieurs visualisations du réseau et imprime les informations de flot et d’optimisation dans la console.
Une figure est également sauvegardée (`reseau_satisfaction_finale.png`).

"""

import sys
import os
import matplotlib.pyplot as plt
import copy

# 📁 Ajout du chemin vers le dossier 'src' pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data import Noeud, Liaison, ReseauHydraulique, optimiser_liaisons, satisfaction
from affichage import afficherCarte, afficherCarteEnoncer

# === Étape 1 : Définition des noeuds et liaisons ===

ListeNoeuds = [
    Noeud("A", "source", 15),
    Noeud("B", "source", 15),
    Noeud("C", "source", 15),
    Noeud("D", "source", 10),
    Noeud("E", "intermediaire"),
    Noeud("F", "intermediaire"),
    Noeud("G", "intermediaire"),
    Noeud("H", "intermediaire"),
    Noeud("I", "intermediaire"),
    Noeud("J", "ville", 15),
    Noeud("K", "ville", 20),
    Noeud("L", "ville", 15),
]

ListeLiaisons = [
    Liaison("A", "E", 7),
    Liaison("B", "F", 10),
    Liaison("B", "G", 7),
    Liaison("C", "A", 5),
    Liaison("C", "F", 5),
    Liaison("D", "G", 10),
    Liaison("E", "F", 5),
    Liaison("E", "H", 4),
    Liaison("E", "I", 15),
    Liaison("F", "G", 5),
    Liaison("F", "I", 15),
    Liaison("G", "I", 15),
    Liaison("H", "J", 7),
    Liaison("I", "K", 30),
    Liaison("I", "L", 4),
    Liaison("K", "J", 10),
]

# === Étape 2 : Création du réseau hydraulique ===

reseau_demo = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
result, index_noeuds = reseau_demo.calculerFlotMaximal()

print(f"Flot maximal initial : {result.flow_value} unités")
fig = afficherCarteEnoncer(result=result,
                    noeuds=ListeNoeuds,
                    liaisons=ListeLiaisons)
plt.show()

# === Étape 3 : Optimisation ciblée de liaisons ===

liaisons_a_optimiser = [("A", "E"), ("I", "L")]
print("\n--- Optimisation des liaisons B->F et E->I ---")

liaisons_copie = copy.deepcopy(ListeLiaisons)
config_finale, travaux = optimiser_liaisons(ListeNoeuds, liaisons_copie, liaisons_a_optimiser)

for i, (liaison, capacite, flot) in enumerate(travaux):
    u, v = liaison
    print(f"Travaux #{i+1}: Liaison {u} -> {v}, capacité choisie : {capacite}, nouveau flot maximal : {flot}")

# Affichage après optimisation
reseau_opt = ReseauHydraulique(ListeNoeuds, config_finale)
result_opt, index_noeuds_opt = reseau_opt.calculerFlotMaximal()

print(f"Flot maximal après optimisation : {result_opt.flow_value} unités")

# === Étape 4 : Visualisation comparative ===
fig1 = afficherCarte(
    result=result,
    index_noeuds=index_noeuds,
    noeuds=ListeNoeuds,
    liaisons=ListeLiaisons,
    montrer_saturees=True
)
fig1.suptitle("Avant optimisation", y=0.7)
plt.show()

fig2 = afficherCarte(
    result=result_opt,
    index_noeuds=index_noeuds_opt,
    noeuds=ListeNoeuds,
    liaisons=config_finale,
    montrer_saturees=True
)
fig2.suptitle("Après optimisation",y=0.7)

plt.show()

# === Étape 5 : Satisfaction à 100% des villes ===

# === Objectif : satisfaire toutes les villes ===
objectif = sum(noeud.capaciteMax for noeud in ListeNoeuds if noeud.type == "ville")

# === Appel à la fonction satisfaction ===
nouvelle_config, travaux = satisfaction(
    noeuds=ListeNoeuds,
    liaisons=ListeLiaisons,
    optimiser_fonction=optimiser_liaisons,
    objectif=objectif,
    cap_max=25,
    max_travaux=5
)

# === Résultat final ===
reseau_final = ReseauHydraulique(ListeNoeuds, nouvelle_config)
resultat_final, index_noeuds = reseau_final.calculerFlotMaximal()

# === Affichage des résultats ===
print(f"\nFlot final obtenu : {resultat_final.flow_value} / {objectif}\n")
print("✅ Travaux réalisés :")
for (u, v), cap, flot in travaux:
    print(f"  - Liaison {u} ➝ {v} portée à {cap} unités, nouveau flot = {flot}")

# === Visualisation satisfaction des villes  ===
fig = afficherCarte(resultat_final,
                    index_noeuds=index_noeuds,
                    noeuds=ListeNoeuds,
                    liaisons=nouvelle_config,
                    montrer_saturees=True)
plt.title("Réseau après satisfaction des villes")
plt.show()

# === Étape 6 : Affichage final + liaisons saturées ===

# Affichage manuel des liaisons saturées (en plus de l'affichage graphique)
# ✅ Affichage manuel des liaisons saturées
print("\n🔴 Liaisons saturées après satisfaction :")
reseau_satis = ReseauHydraulique(ListeNoeuds, nouvelle_config)
result_satis, index_noeuds_satis = reseau_satis.calculerFlotMaximal()
for u, v, cap in reseau_satis.liaisons_saturees(result_satis):
    flow = result_satis.flow[reseau_satis.index_noeuds[u], reseau_satis.index_noeuds[v]]
    print(f"{u} -> {v} : {flow} / {cap} (saturée)")

# === Étape 7 : Vérification par assertion ===

assert result_satis.flow_value >= objectif, "⚠️ Objectif non atteint : toutes les villes ne sont pas satisfaites"

# === Étape 8 : Sauvegarde de la figure (facultatif) ===
plt.savefig("reseau_satisfaction_finale.png")
plt.show()

# === Étape 9 : Simulation d’un cas irréaliste (bonus) ===

objectif_echec = 1000
print(f"\n--- Test avec un objectif irréaliste ({objectif_echec} unités) ---")
_, travaux_impossibles = satisfaction(
    noeuds=ListeNoeuds,
    liaisons=ListeLiaisons,
    optimiser_fonction=optimiser_liaisons,
    objectif=objectif_echec
)
if travaux_impossibles:
    dernier_flot = travaux_impossibles[-1][2]
    print(f"Flot maximum atteint malgré les efforts : {dernier_flot} unités (objectif non atteint)")
else:
    print("Aucun ajustement possible avec ce niveau d’objectif.")
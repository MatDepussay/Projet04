import sys
import os
import matplotlib.pyplot as plt
import copy

# 📁 Ajout du chemin vers le dossier 'src' pour importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from data import Noeud, Liaison, ReseauHydraulique, optimiser_liaisons, satisfaction
from affichage import afficherCarte

# === Données ===

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

# === Création du réseau hydraulique ===

reseau_demo = ReseauHydraulique(ListeNoeuds, ListeLiaisons)

# === Calcul du flot maximal initial ===

result, index_noeuds = reseau_demo.calculerFlotMaximal()

print(f"Flot maximal initial : {result.flow_value} unités")
afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=ListeNoeuds, liaisons=ListeLiaisons, montrer_saturees=True)

plt.pause(1)

# === Exemple d’optimisation : on optimise les liaisons B->F et E->I ===

liaisons_a_optimiser = [("A", "E"), ("I", "L")]

print("\n--- Optimisation des liaisons B->F et E->I ---")

# Attention : faire une copie des liaisons car optimiser_liaisons modifie potentiellement
liaisons_copie = copy.deepcopy(ListeLiaisons)

config_finale, travaux = optimiser_liaisons(ListeNoeuds, liaisons_copie, liaisons_a_optimiser)

for i, (liaison, capacite, flot) in enumerate(travaux):
    u, v = liaison
    print(f"Travaux #{i+1}: Liaison {u} -> {v}, capacité choisie : {capacite}, nouveau flot maximal : {flot}")

# Affichage après optimisation
reseau_opt = ReseauHydraulique(ListeNoeuds, config_finale)
result_opt, index_noeuds_opt = reseau_opt.calculerFlotMaximal()

print(f"Flot maximal après optimisation : {result_opt.flow_value} unités")
afficherCarte(result=result_opt, index_noeuds=index_noeuds_opt, noeuds=ListeNoeuds, liaisons=config_finale)

plt.pause(1)

# === Satisfaction : approvisionnement 100% des villes ===

objectif = sum(noeud.capaciteMax for noeud in ListeNoeuds if noeud.type == "ville")
print(f"\n--- Satisfaction : Approvisionner {objectif} unités (100% des villes) ---")

# On considère toutes les liaisons comme modifiables pour la satisfaction
liaisons_modifiables = [(liaison.depart, liaison.arrivee) for liaison in ListeLiaisons]

nouvelle_config, travaux_satisfaction = satisfaction(
    noeuds=ListeNoeuds,
    liaisons=ListeLiaisons,
    optimiser_fonction=optimiser_liaisons,  # ou la fonction d’optimisation que tu utilises
    objectif=objectif  # optionnel : si tu veux forcer une valeur
)

print("Travaux réalisés pour la satisfaction :")
for (u, v), cap, flot in travaux_satisfaction:
    print(f"Liaison {u} -> {v} ajustée à {cap} unités, flot = {flot}")

reseau_satis = ReseauHydraulique(ListeNoeuds, nouvelle_config)
result_satis, index_noeuds_satis = reseau_satis.calculerFlotMaximal()

print(f"Flot maximal après satisfaction : {result_satis.flow_value} unités")
afficherCarte(result=result_satis, index_noeuds=index_noeuds_satis, noeuds=ListeNoeuds, liaisons=nouvelle_config, montrer_saturees=False)

plt.show()
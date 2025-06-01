import streamlit as st
from affichage import afficherCarte, afficherCarteEnoncer
from data import (
    Liaison, Noeud,
    creer_liaison, creer_noeud, GestionReseau,
    ReseauHydraulique, optimiser_liaisons,
    satisfaction, liaison_existe
)
import copy
import random
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Réseau Hydraulique", layout="wide")

# Initialisation de l'objet réseau dans le session state
if "reseau" not in st.session_state:
    st.session_state.reseau = GestionReseau()
if "liste_noeuds" not in st.session_state:
    st.session_state.liste_noeuds = []
if "liste_liaisons" not in st.session_state:
    st.session_state.liste_liaisons = []

def main():
    st.title("🚰 Réseau Hydraulique – Optimisation et Simulation")

    menu = st.sidebar.selectbox("📋 Menu", [
        "Accueil",
        "Créer un nouveau réseau",
        "Charger un réseau",
        "Supprimer un réseau",
        "Afficher carte (énoncé)",
        "Afficher carte (flux max)",
        "Optimisation de travaux",
        "Généralisation",
    ])

    if menu == "Accueil":
        st.markdown("Bienvenue ! Utilisez le menu à gauche pour commencer.")

    elif menu == "Créer un nouveau réseau":
        creer_reseau()

    elif menu == "Charger un réseau":
        charger_reseau_ui()

    elif menu == "Supprimer un réseau":
        supprimer_reseau_ui()

    elif menu == "Afficher carte (énoncé)":
        afficher_carte_enonce_ui()

    elif menu == "Afficher carte (flux max)":
        afficher_carte_flux_max_ui()

    elif menu == "Optimisation de travaux":
        optimisation_travaux_ui()

    elif menu == "Généralisation":
        generalisation_ui()

    st.sidebar.markdown("---")

def creer_reseau():
    st.header("🔧 Création d’un nouveau réseau")
    
    # Réinitialisation du réseau
    if st.button("Réinitialiser réseau"):
        st.session_state.reseau = GestionReseau()
        st.session_state.liste_noeuds.clear()
        st.session_state.liste_liaisons.clear()
        st.success("Réseau réinitialisé.")

    with st.expander("➕ Ajouter des noeuds"):
        type_noeud = st.selectbox("Type de noeud", ["source", "ville", "intermediaire"])
        nom = st.text_input("Nom du noeud")
        capacite = st.number_input("Capacité", min_value=0, value=10)
        submit_noeud = st.form_submit_button("Ajouter noeud")
        if submit_noeud:
            if nom:
                try:
                    noeud = creer_noeud(nom, type_noeud, capacite)
                    st.session_state.liste_noeuds.append(noeud)
                    st.success(f"Noeud {nom} ajouté.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("Le nom du noeud est obligatoire.")

    with st.expander("🔗 Ajouter des liaisons"):
        depart = st.text_input("Départ", key="depart")
        arrivee = st.text_input("Arrivée", key="arrivee")
        l_capacite = st.number_input("Capacité de la liaison", min_value=1, value=5)
        submit_liaison = st.form_submit_button("Ajouter liaison")
        if submit_liaison:
            if depart and arrivee:
                try:
                    liaison = creer_liaison(depart, arrivee, l_capacite)
                    st.session_state.liste_liaisons.append(liaison)
                    st.success(f"Liaison {depart} ➝ {arrivee} ajoutée.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.error("Les deux sommets sont requis.")

    nom_fichier = st.text_input("Nom du fichier de sauvegarde", "reseau.json")
    if st.button("💾 Sauvegarder réseau"):
        if nom_fichier:
            try:
                st.session_state.reseau.sauvegarder_reseau(nom_fichier)
                st.success("Réseau sauvegardé !")
            except Exception as e:
                st.error(f"Erreur lors de la sauvegarde : {e}")
        else:
            st.error("Le nom du fichier est obligatoire.")

def charger_reseau_ui():
    st.header("📂 Charger un réseau existant")
    nom_fichier = st.text_input("Nom du fichier à charger", "reseau.json")
    if st.button("Charger"):
        try:
            st.session_state.reseau.charger_reseau(nom_fichier)
            st.success("Réseau chargé avec succès.")
        except FileNotFoundError:
            st.error("Fichier introuvable.")
        except Exception as e:
            st.error(f"Erreur : {e}")

def supprimer_reseau_ui():
    st.header("🗑️ Supprimer un réseau")
    nom_fichier = st.text_input("Nom du fichier à supprimer", "reseau.json")
    if st.button("Supprimer"):
        try:
            st.session_state.reseau.supprimer_reseaux(nom_fichier)
            st.success(f"Le fichier '{nom_fichier}' a été supprimé.")
        except Exception as e:
            st.error(f"Erreur : {e}")

def afficher_carte_enonce_ui():
    st.header("🗺️ Carte de l’énoncé")
    reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, st.session_state.liste_liaisons)
    result, index_noeuds = reseau_temp.calculerFlotMaximal()
    fig = afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liste_liaisons)
    st.pyplot(fig)

def afficher_carte_flux_max_ui():
    st.header("💧 Carte avec flux maximal")
    reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, st.session_state.liste_liaisons)
    result, index_noeuds = reseau_temp.calculerFlotMaximal()
    fig = afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liste_liaisons)
    st.pyplot(fig)
    st.success(f"Flot maximal : {result.flow_value} unités")

def optimisation_travaux_ui():
    st.header("🛠️ Optimisation des travaux")
    st.markdown("Sélectionnez manuellement les liaisons à optimiser")
    
    selected = []
    # Afficher une checkbox pour chaque liaison
    for l in st.session_state.liste_liaisons:
        if st.checkbox(f"{l.depart} ➝ {l.arrivee}", key=f"opt_{l.depart}_{l.arrivee}"):
            selected.append((l.depart, l.arrivee))
    if st.button("Lancer optimisation"):
        config_finale, travaux = optimiser_liaisons(st.session_state.liste_noeuds, st.session_state.liste_liaisons, selected)
        for i, (liaison, cap, flot) in enumerate(travaux):
            st.info(f"Travaux #{i+1}: {liaison[0]} ➝ {liaison[1]} | Capacité = {cap} | Flot = {flot}")
        reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, config_finale)
        result, index_noeuds = reseau_temp.calculerFlotMaximal()
        fig = afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
        st.pyplot(fig)

def generalisation_ui():
    st.header("🔬 Généralisation")
    choix = st.radio("Scénario", [
        "Optimiser pour alimenter toutes les villes",
        "Assèchement aléatoire d’une source",
    ])
    if choix == "Optimiser pour alimenter toutes les villes":
        objectif = sum(n.capaciteMax for n in st.session_state.liste_noeuds if n.type == "ville")
        st.info(f"🎯 Objectif : {objectif} unités")
        liaisons_modifiables = [(l.depart, l.arrivee) for l in st.session_state.liste_liaisons]
        nouvelle_config, travaux = satisfaction(st.session_state.liste_noeuds, st.session_state.liste_liaisons, liaisons_modifiables, objectif)
        for (u, v), cap, flot in travaux:
            st.success(f"Liaison {u} ➝ {v} ajustée à {cap} unités → Flot : {flot}")
        reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, nouvelle_config)
        result, index_noeuds = reseau_temp.calculerFlotMaximal()
        fig = afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=nouvelle_config)
        st.pyplot(fig)

    elif choix == "Assèchement aléatoire d’une source":
        sources = [n for n in st.session_state.liste_noeuds if n.type == "source"]
        if not sources:
            st.warning("Aucune source trouvée.")
            return
        source = random.choice(sources)
        source.capaciteMax = 0
        st.warning(f"💧 La source {source.nom} est asséchée.")
        reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, st.session_state.liste_liaisons)
        result, index_noeuds = reseau_temp.calculerFlotMaximal()
        fig = afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liste_liaisons)
        st.pyplot(fig)
        
        st.markdown("🔧 Choisissez une liaison à renforcer de +5 :")
        u = st.selectbox("Départ", [l.depart for l in st.session_state.liste_liaisons])
        v = st.selectbox("Arrivée", [l.arrivee for l in st.session_state.liste_liaisons])
        if st.button("Renforcer la liaison"):
            for l in st.session_state.liste_liaisons:
                if l.depart == u and l.arrivee == v:
                    l.capacite += 5
                    st.success(f"Liaison {u} ➝ {v} renforcée de +5 unités.")
                    break
            reseau_temp = ReseauHydraulique(st.session_state.liste_noeuds, st.session_state.liste_liaisons)
            result, index_noeuds = reseau_temp.calculerFlotMaximal()
            fig = afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liste_liaisons)
            st.pyplot(fig)
            st.success(f"Nouveau flot maximal : {result.flow_value} unités")

if __name__ == "__main__":
    main()

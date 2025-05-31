import streamlit as st
from affichage import afficherCarte, afficherCarteEnoncer
from data import ListeNoeuds, ListeLiaisons, ReseauHydraulique, optimiser_liaisons, satisfaction, liaison_existe
import copy
import random
import matplotlib.pyplot as plt

st.set_page_config(page_title="Réseau Hydraulique", layout="wide")

st.title("💧 Réseau Hydraulique - Optimisation et Simulation")

# Stocker les liaisons modifiables de manière persistante
if "liaisons_actuelles" not in st.session_state:
    st.session_state.liaisons_actuelles = copy.deepcopy(ListeLiaisons)

# Onglets principaux
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Carte de l'énoncé",
    "📊 Carte avec flot maximal",
    "🛠 Travaux manuels",
    "🧪 Généralisation"
])

# === TAB 1 : Carte de l'énoncé ===
with tab1:
    st.header("Carte de l'énoncé (sans flot maximal)")
    reseau = ReseauHydraulique(ListeNoeuds, st.session_state.liaisons_actuelles)
    result, index_noeuds = reseau.calculerFlotMaximal()
    afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liaisons_actuelles)

# === TAB 2 : Flot maximal ===
with tab2:
    st.header("Carte avec flot maximal")
    reseau = ReseauHydraulique(ListeNoeuds, st.session_state.liaisons_actuelles)
    result, index_noeuds = reseau.calculerFlotMaximal()
    afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=st.session_state.liaisons_actuelles)
    st.success(f"💧 Flot maximal : {result.flow_value} unités")

# === TAB 3 : Travaux manuels ===
with tab3:
    st.header("Optimisation ciblée de liaisons")

    liaisons_a_optimiser = []
    with st.form("selection_liaisons"):
        st.write("👉 Sélectionne des liaisons à optimiser :")
        u = st.text_input("Noeud de départ").strip().upper()
        v = st.text_input("Noeud d’arrivée").strip().upper()
        submitted = st.form_submit_button("Ajouter cette liaison")

        if submitted:
            if u == v:
                st.error("La liaison ne peut pas être entre un même sommet.")
            elif not liaison_existe(u, v, st.session_state.liaisons_actuelles):
                st.error("Cette liaison n’existe pas.")
            else:
                liaisons_a_optimiser.append((u, v))
                st.success(f"Liaison ajoutée : {u} ➝ {v}")

    if liaisons_a_optimiser:
        if st.button("🚀 Lancer optimisation des travaux"):
            config_finale, travaux = optimiser_liaisons(
                ListeNoeuds,
                st.session_state.liaisons_actuelles,
                liaisons_a_optimiser
            )

            for i, (liaison, cap, flot) in enumerate(travaux):
                u, v = liaison
                st.markdown(f"🔧 **Travaux #{i+1} :** `{u} ➝ {v}` | Capacité : `{cap}` | Flot max : `{flot}`")

            reseau_final = ReseauHydraulique(ListeNoeuds, config_finale)
            result, index_noeuds = reseau_final.calculerFlotMaximal()
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=config_finale)
            st.session_state.liaisons_actuelles = config_finale

# === TAB 4 : Généralisation ===
with tab4:
    option = st.radio("Choisir un scénario :", ["Optimisation 100% villes", "Assèchement source + renfort liaison"])

    if option == "Optimisation 100% villes":
        objectif = sum(n.capaciteMax for n in ListeNoeuds if n.type == "ville")
        st.info(f"🎯 Objectif : approvisionner {objectif} unités")

        liaisons_modifiables = [(liaison.depart, liaison.arrivee) for liaison in ListeLiaisons]
        nouvelle_config, travaux = satisfaction(
            noeuds=ListeNoeuds,
            liaisons_actuelles=ListeLiaisons,
            liaisons_possibles=liaisons_modifiables,
            objectif_flot=objectif
        )

        for (u, v), cap, flot in travaux:
            st.markdown(f"🔧 `{u} ➝ {v}` ajustée à `{cap}` u. → Flot = `{flot}` u.")

        reseau_opt = ReseauHydraulique(ListeNoeuds, nouvelle_config)
        result, index_noeuds = reseau_opt.calculerFlotMaximal()
        afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=nouvelle_config)

    else:
        sources = [n for n in ListeNoeuds if n.type == "source"]
        if not sources:
            st.error("❌ Aucune source détectée.")
        else:
            source_choisie = random.choice(sources)
            st.warning(f"💥 Source asséchée aléatoirement : {source_choisie.nom}")

            for n in ListeNoeuds:
                if n.nom == source_choisie.nom:
                    n.capaciteMax = 0

            reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
            result, index_noeuds = reseau.calculerFlotMaximal()
            afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=ListeLiaisons)

            u = st.text_input("Noeud de départ (liaison à renforcer)").strip().upper()
            v = st.text_input("Noeud d’arrivée").strip().upper()

            if st.button("🔧 Renforcer de +5 unités"):
                for liaison in ListeLiaisons:
                    if liaison.depart == u and liaison.arrivee == v:
                        liaison.capacite += 5
                        break

                reseau = ReseauHydraulique(ListeNoeuds, ListeLiaisons)
                result, index_noeuds = reseau.calculerFlotMaximal()
                afficherCarte(result=result, index_noeuds=index_noeuds, liaisons=ListeLiaisons)
                st.success(f"Nouveau flot : {result.flow_value} unités")


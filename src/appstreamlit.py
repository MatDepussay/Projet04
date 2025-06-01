import streamlit as st
import copy
from data import (
    GestionReseau, ReseauHydraulique, optimiser_liaisons, satisfaction, liaison_existe, Noeud, Liaison
)
from affichage import afficherCarte, afficherCarteEnoncer
import matplotlib.pyplot as plt

st.set_page_config(page_title="Réseau Hydraulique", layout="wide")

if "reseau" not in st.session_state:
    st.session_state["reseau"] = GestionReseau()
if "reseau_valide" not in st.session_state:
    st.session_state["reseau_valide"] = False

reseau = st.session_state["reseau"]

def reset_reseau():
    st.session_state["reseau"] = GestionReseau()
    st.session_state["reseau_valide"] = False

def menu_demarrage():
    st.title("🚰 Gestion de Réseau Hydraulique")
    choix = st.radio("Démarrage", ["Saisir un nouveau réseau", "Charger un réseau existant"])
    if choix == "Saisir un nouveau réseau":
        if st.button("Réinitialiser le réseau"):
            reset_reseau()
            st.experimental_rerun()
        menu_saisie_reseau()
    else:
        fichier = st.text_input("Nom du fichier à charger", value="reseaux.json")
        if st.button("Charger le réseau"):
            try:
                reseaux = GestionReseau().charger_reseau(fichier)
                if reseaux:
                    nom_reseau = st.selectbox("Choisir un réseau", list(reseaux.keys()))
                    if st.button("Valider le chargement"):
                        noeuds, liaisons = reseaux[nom_reseau]
                        st.session_state["reseau"] = GestionReseau(noeuds, liaisons)
                        st.session_state["reseau_valide"] = True
                        st.success("Réseau chargé avec succès.")
                        st.experimental_rerun()
                else:
                    st.warning("Aucun réseau trouvé dans ce fichier.")
            except Exception as e:
                st.error(f"Erreur lors du chargement : {e}")

def menu_saisie_reseau():
    st.header("Saisie du réseau")
    with st.expander("Ajouter des sources"):
        ajouter_noeuds("source")
    with st.expander("Ajouter des villes"):
        ajouter_noeuds("ville")
    with st.expander("Ajouter des intermédiaires"):
        ajouter_noeuds("intermediaire")
    with st.expander("Ajouter des liaisons"):
        ajouter_liaisons()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Valider le réseau"):
            if reseau.ListeNoeuds and reseau.ListeLiaisons:
                st.session_state["reseau_valide"] = True
                st.success("Réseau validé. Vous pouvez maintenant afficher ou optimiser le réseau.")
            else:
                st.warning("Veuillez ajouter au moins un noeud et une liaison.")
    with col2:
        if st.button("Sauvegarder ce réseau"):
            nom_fichier = st.text_input("Nom du fichier de sauvegarde", value="reseau1.json")
            if nom_fichier:
                reseau.sauvegarder_reseau(nom_fichier)
                st.success(f"Réseau sauvegardé dans {nom_fichier}")

def ajouter_noeuds(type_noeud):
    noms_existants = {n.nom for n in reseau.ListeNoeuds}
    nom = st.text_input(f"Nom de la {type_noeud}", key=f"{type_noeud}_nom")
    capacite = 0
    if type_noeud != "intermediaire":
        capacite = st.number_input("Capacité maximale", min_value=1, value=10, key=f"{type_noeud}_cap")
    if st.button(f"Ajouter {type_noeud}", key=f"btn_{type_noeud}"):
        try:
            noeud = Noeud(nom.upper(), type_noeud, capacite) if type_noeud != "intermediaire" else Noeud(nom.upper(), type_noeud)
            if nom.upper() in noms_existants:
                st.warning("Ce nom est déjà utilisé.")
            else:
                reseau.ListeNoeuds.append(noeud)
                st.success(f"{type_noeud.capitalize()} ajoutée : {nom.upper()}")
        except Exception as e:
            st.error(str(e))

def ajouter_liaisons():
    noms_noeuds = {n.nom for n in reseau.ListeNoeuds}
    depart = st.text_input("Départ de la liaison", key="liaison_depart")
    arrivee = st.text_input("Arrivée de la liaison", key="liaison_arrivee")
    capacite = st.number_input("Capacité de la liaison", min_value=1, value=5, key="liaison_cap")
    if st.button("Ajouter la liaison"):
        try:
            if depart.upper() == arrivee.upper():
                st.warning("Une liaison ne peut pas relier un noeud à lui-même.")
            elif depart.upper() not in noms_noeuds or arrivee.upper() not in noms_noeuds:
                st.warning("Noeud de départ ou d’arrivée introuvable.")
            elif any(l.depart == depart.upper() and l.arrivee == arrivee.upper() for l in reseau.ListeLiaisons):
                st.warning("Cette liaison existe déjà.")
            else:
                liaison = Liaison(depart.upper(), arrivee.upper(), capacite)
                reseau.ListeLiaisons.append(liaison)
                st.success(f"Liaison ajoutée : {depart.upper()} ➝ {arrivee.upper()}")
        except Exception as e:
            st.error(str(e))

def menu_terminal():
    st.header("Menu principal")
    choix = st.selectbox("Choisissez une action", [
        "Afficher la carte de l'énoncé",
        "Afficher la carte avec flot maximal",
        "Travaux (optimisation manuelle)",
        "Généralisation (optimisation globale)",
        "Ajouter un élément",
        "Réinitialiser le réseau"
    ])
    if choix == "Afficher la carte de l'énoncé":
        afficher_carte_enoncer()
    elif choix == "Afficher la carte avec flot maximal":
        afficher_carte_flot()
    elif choix == "Travaux (optimisation manuelle)":
        menu_travaux()
    elif choix == "Généralisation (optimisation globale)":
        menu_generalisation()
    elif choix == "Ajouter un élément":
        menu_ajout_elements()
    elif choix == "Réinitialiser le réseau":
        reset_reseau()
        st.experimental_rerun()

def afficher_carte_enoncer():
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'afficher la carte.")
        return
    if not reseau.ListeNoeuds or not reseau.ListeLiaisons:
        st.warning("Veuillez d'abord saisir des noeuds et des liaisons.")
        return
    reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
    result, index_noeuds = reseau_hydro.calculerFlotMaximal()
    fig = afficherCarteEnoncer(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons)
    st.pyplot(fig)

def afficher_carte_flot():
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'afficher la carte.")
        return
    if not reseau.ListeNoeuds or not reseau.ListeLiaisons:
        st.warning("Veuillez d'abord saisir des noeuds et des liaisons.")
        return
    reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
    result, index_noeuds = reseau_hydro.calculerFlotMaximal()
    fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons)
    st.pyplot(fig)

def menu_ajout_elements():
    st.subheader("Ajouter un élément au réseau")
    with st.expander("Ajouter une source"):
        ajouter_noeuds("source")
    with st.expander("Ajouter une ville"):
        ajouter_noeuds("ville")
    with st.expander("Ajouter un intermédiaire"):
        ajouter_noeuds("intermediaire")
    with st.expander("Ajouter une liaison"):
        ajouter_liaisons()

def menu_travaux():
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    st.subheader("Optimisation manuelle des travaux")
    liaisons_possibles = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
    selection = st.multiselect(
        "Sélectionnez les liaisons à optimiser (format : Départ ➝ Arrivée)",
        options=[f"{u} ➝ {v}" for u, v in liaisons_possibles]
    )
    liaisons_a_optimiser = []
    for s in selection:
        u, v = s.split("➝")
        liaisons_a_optimiser.append((u.strip(), v.strip()))
    if st.button("Lancer l'optimisation"):
        if not liaisons_a_optimiser:
            st.warning("Aucune liaison sélectionnée.")
            return
        config_finale, travaux = optimiser_liaisons(reseau.ListeNoeuds, reseau.ListeLiaisons, liaisons_a_optimiser)
        st.success("Optimisation terminée.")
        for i, (liaison, cap, flot) in enumerate(travaux):
            u, v = liaison
            st.write(f"Travaux #{i+1} : Liaison {u} ➝ {v}, capacité {cap} unités, flot atteint : {flot} unités")
        reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, config_finale)
        result, index_noeuds = reseau_hydro.calculerFlotMaximal()
        fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=config_finale)
        st.pyplot(fig)

def menu_generalisation():
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    st.subheader("Optimisation globale / généralisation")
    choix = st.radio("Scénario", [
        "Optimiser pour approvisionner 100% des villes",
        "Assèchement aléatoire d'une source"
    ])
    if choix == "Optimiser pour approvisionner 100% des villes":
        objectif = sum(n.capaciteMax for n in reseau.ListeNoeuds if n.type == "ville")
        st.write(f"Objectif : {objectif} unités (100% des villes)")
        liaisons_modifiables = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
        if st.button("Lancer l'optimisation globale"):
            nouvelle_config, travaux = satisfaction(
                noeuds=reseau.ListeNoeuds,
                liaisons_actuelles=reseau.ListeLiaisons,
                liaisons_possibles=liaisons_modifiables,
                objectif_flot=objectif
            )
            st.success("Optimisation globale terminée.")
            for (depart, arrivee), cap, new_flot in travaux:
                st.write(f"Liaison {depart} ➝ {arrivee} ajustée à {cap} u. → Flot = {new_flot} u.")
            reseau_opt = ReseauHydraulique(reseau.ListeNoeuds, nouvelle_config)
            result, index_noeuds = reseau_opt.calculerFlotMaximal()
            fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=nouvelle_config)
            st.pyplot(fig)
    else:
        import random
        sources = [n for n in reseau.ListeNoeuds if n.type == "source"]
        if not sources:
            st.warning("Aucune source trouvée.")
            return
        if st.button("Assécher une source aléatoirement"):
            source_choisie = random.choice(sources)
            st.write(f"Source choisie : {source_choisie.nom}")
            for n in reseau.ListeNoeuds:
                if n.nom == source_choisie.nom:
                    n.capaciteMax = 0
            reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
            result, index_noeuds = reseau_hydro.calculerFlotMaximal()
            fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons)
            st.pyplot(fig)
            liaisons_possibles = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
            liaison_str = st.selectbox("Sélectionnez une liaison à renforcer (+5 unités)", [f"{u} ➝ {v}" for u, v in liaisons_possibles])
            if st.button("Renforcer la liaison sélectionnée"):
                u, v = liaison_str.split("➝")
                u, v = u.strip(), v.strip()
                for liaison in reseau.ListeLiaisons:
                    if liaison.depart == u and liaison.arrivee == v:
                        liaison.capacite += 5
                        st.write(f"Liaison {u} ➝ {v} renforcée à {liaison.capacite} unités.")
                        break
                reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
                result_modifie, index_noeuds_modifie = reseau_hydro.calculerFlotMaximal()
                fig = afficherCarte(result=result_modifie, index_noeuds=index_noeuds_modifie, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons)
                st.pyplot(fig)
                st.write(f"Nouveau flot maximal : {result_modifie.flow_value} u.")

def menu_chargement():
    st.title("🚰 Gestion de Réseau Hydraulique")
    fichier = st.text_input("Nom du fichier à charger", value="reseaux.json")

    # Charger les réseaux une seule fois et les garder en mémoire
    if "reseaux_charges" not in st.session_state or st.session_state.get("dernier_fichier_charge") != fichier:
        if st.button("Charger le réseau"):
            try:
                reseaux = GestionReseau().charger_reseau(fichier)
                st.session_state["reseaux_charges"] = reseaux
                st.session_state["dernier_fichier_charge"] = fichier
                if not reseaux:
                    st.warning("Aucun réseau trouvé dans ce fichier.")
            except Exception as e:
                st.error(f"Erreur lors du chargement : {e}")

    reseaux = st.session_state.get("reseaux_charges", {})
    if reseaux:
        nom_reseau = st.selectbox("Choisir un réseau", list(reseaux.keys()))
        if st.button("Valider le chargement"):
            noeuds, liaisons = reseaux[nom_reseau]
            st.session_state["reseau"] = GestionReseau(noeuds, liaisons)
            st.session_state["reseau_valide"] = False  # On force la validation manuelle
            st.success("Réseau chargé. Cliquez sur 'Valider le réseau' pour continuer.")

    # Ajout du bouton de validation ici aussi
    if st.button("Valider le réseau"):
        reseau = st.session_state["reseau"]
        if reseau.ListeNoeuds and reseau.ListeLiaisons:
            st.session_state["reseau_valide"] = True
            st.success("Réseau validé. Vous pouvez maintenant afficher ou optimiser le réseau.")
        else:
            st.warning("Veuillez charger un réseau contenant au moins un noeud et une liaison.")

# === MENU LATERAL PRINCIPAL ===
menu = st.sidebar.radio(
    "Navigation",
    [
        "Créer un réseau",
        "Charger un réseau",
        "Afficher la carte de l'énoncé",
        "Afficher la carte avec flot maximal",
        "Travaux (optimisation manuelle)",
        "Généralisation (optimisation globale)",
        "Ajouter un élément",
        "Réinitialiser le réseau"
    ]
)

if menu == "Créer un réseau":
    menu_saisie_reseau()
elif menu == "Charger un réseau":
    menu_chargement()
elif menu == "Afficher la carte de l'énoncé":
    afficher_carte_enoncer()
elif menu == "Afficher la carte avec flot maximal":
    afficher_carte_flot()
elif menu == "Travaux (optimisation manuelle)":
    menu_travaux()
elif menu == "Généralisation (optimisation globale)":
    menu_generalisation()
elif menu == "Ajouter un élément":
    menu_ajout_elements()
elif menu == "Réinitialiser le réseau":
    reset_reseau()
    st.experimental_rerun()
"""
appstreamlit.py – Module Streamlit pour l'application de gestion et d'optimisation de réseau hydraulique.

Ce module fournit une interface graphique interactive permettant :
- la création, la visualisation et la modification d'un réseau hydraulique (sources, villes, nœuds intermédiaires, liaisons),
- la sauvegarde et le chargement de réseaux depuis des fichiers JSON,
- l'affichage graphique du réseau et du flot maximal calculé,
- l'optimisation manuelle ou automatique des liaisons pour maximiser le flot,
- la simulation de scénarios (assèchement de source, optimisations globales, etc.).

Fonctionnalités principales :
    - menu_saisie_reseau() : Interface pour la saisie interactive des nœuds et liaisons.
    - ajouter_noeuds(type_noeud) : Ajout d’un nœud de type donné via l’interface.
    - ajouter_liaisons() : Ajout d’une liaison entre deux nœuds via l’interface.
    - menu_ajout_elements() : Ajout dynamique d’éléments à un réseau existant.
    - afficher_carte_enoncer() : Affichage graphique du réseau sans calcul de flot.
    - afficher_carte_flot() : Affichage graphique du réseau avec calcul du flot maximal.
    - menu_travaux() : Optimisation manuelle des liaisons sélectionnées.
    - menu_generalisation() : Optimisation automatique selon différents scénarios prédéfinis.
    - menu_chargement() : Chargement d’un réseau existant depuis un fichier.
    - reset_reseau() : Réinitialisation complète du réseau en cours.

Utilisation :
    L'utilisateur navigue via la barre latérale pour accéder aux différentes fonctionnalités.
    Les modifications et optimisations sont visualisées en temps réel sur la carte du réseau.

Exemple d'utilisation :
    >>> # Terminal : lancer l'application
    >>> streamlit run appstreamlit.py

    # Depuis l’interface Streamlit :
    - Créer un réseau (ajout de sources, villes, intermédiaires, liaisons)
    - Valider et afficher la carte
    - Optimiser manuellement ou automatiquement
    - Sauvegarder ou charger un réseau

Pré-requis :
    - Python >= 3.9
    - streamlit, networkx, matplotlib (voir requirements.txt)

Notes :
    - Toutes les modifications sont stockées dans st.session_state pour garantir la persistance entre les interactions.
    - Les calculs de flot maximal et d’optimisation utilisent les fonctions du module data.py.
    - L'affichage graphique s'appuie sur matplotlib et networkx via le module affichage.py.
"""

import sys
import os
import streamlit as st
import copy

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
)
from data import (
    GestionReseau,
    ReseauHydraulique,
    optimiser_liaisons,
    satisfaction,
    Noeud,
    Liaison,
)
from affichage import afficherCarte, afficherCarteEnoncer

st.set_page_config(page_title="AquaFlow", layout="wide", page_icon="🚰")

# Bandeau d'accueil
st.markdown(
    """
    <style>
    .big-title {
        font-size:2.2em !important;
        color:#0072B5;
        font-weight:bold;
        margin-bottom:0.2em;
    }
    .subtitle {
        font-size:1.2em !important;
        color:#444;
        margin-bottom:1em;
    }
    .stButton>button {
        background-color: #0072B5;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5em 1.2em;
        margin: 0.2em 0.2em 0.2em 0;
    }
    .stButton>button:hover {
        background-color: #005a8c;
        color: #fff;
    }
    .stSidebar {
        background-color: #f3f7fa;
    }
    </style>
    <div class="big-title">🚰 Gestion de Réseau Hydraulique</div>
    <div class="subtitle">Créez, visualisez et optimisez un réseau d'approvisionnement en eau de façon interactive.</div>
    """,
    unsafe_allow_html=True,
)

if "reseau" not in st.session_state:
    st.session_state["reseau"] = GestionReseau()
if "reseau_valide" not in st.session_state:
    st.session_state["reseau_valide"] = False

reseau = st.session_state["reseau"]


def reset_reseau():
    if (
        "reseau_original_noeuds" in st.session_state
        and "reseau_original_liaisons" in st.session_state
    ):
        # Recharge la copie initiale
        st.session_state["reseau"].ListeNoeuds = copy.deepcopy(
            st.session_state["reseau_original_noeuds"]
        )
        st.session_state["reseau"].ListeLiaisons = copy.deepcopy(
            st.session_state["reseau_original_liaisons"]
        )
        st.session_state["reseau_valide"] = True  # Ou False selon ce que tu souhaites
        st.success("Le réseau a été réinitialisé à son état validé initial.")
    else:
        st.warning("Impossible de réinitialiser : état initial non trouvé.")


def menu_saisie_reseau():
    st.header("🛠️ Création d'un nouveau réseau")
    st.info(
        "Ajoutez vos sources, villes, intermédiaires et liaisons pour construire votre réseau hydraulique."
    )
    with st.expander("💧 Ajouter des sources"):
        ajouter_noeuds("source")
    with st.expander("🏙️ Ajouter des villes"):
        ajouter_noeuds("ville")
    with st.expander("🔵 Ajouter des intermédiaires"):
        ajouter_noeuds("intermediaire")
    with st.expander("🔗 Ajouter des liaisons"):
        ajouter_liaisons()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Valider le réseau"):
            if reseau.ListeNoeuds and reseau.ListeLiaisons:
                st.session_state["reseau_valide"] = True
                # Sauvegarde de la version initiale du réseau
                st.session_state["reseau_original_noeuds"] = copy.deepcopy(
                    reseau.ListeNoeuds
                )
                st.session_state["reseau_original_liaisons"] = copy.deepcopy(
                    reseau.ListeLiaisons
                )
                st.success("Votre réseau est prêt à être utilisé.")
                st.success(
                    "Réseau validé. Vous pouvez maintenant afficher ou optimiser le réseau."
                )
            else:
                st.warning("Veuillez ajouter au moins un noeud et une liaison.")
    with col2:
        nom_fichier = st.text_input(
            "Nom du fichier de sauvegarde", value="reseau1.json"
        )
        if st.button("💾 Sauvegarder ce réseau"):
            if nom_fichier:
                reseau.sauvegarder_reseaux(nom_fichier)
                st.success(f"Réseau sauvegardé dans {nom_fichier}")


def ajouter_noeuds(type_noeud):
    icones = {"source": "💧", "ville": "🏙️", "intermediaire": "🔵"}
    noms_existants = {n.nom for n in reseau.ListeNoeuds}
    nom = st.text_input(
        f"{icones[type_noeud]} Nom de la {type_noeud}", key=f"{type_noeud}_nom"
    )

    # Message d'info sur la conversion en majuscules
    if nom:
        st.info(
            "⚠️ Le nom sera converti automatiquement en MAJUSCULES. Évitez les doublons."
        )

    capacite = 0
    if type_noeud != "intermediaire":
        capacite = st.number_input(
            "Capacité maximale", min_value=1, value=10, key=f"{type_noeud}_cap"
        )

    if st.button(f"Ajouter {type_noeud}", key=f"btn_{type_noeud}"):
        nom_upper = nom.strip().upper()
        if nom.strip() == "":
            st.warning("Le nom ne peut pas être vide.")
            return
        if nom_upper in noms_existants:
            st.warning("Ce nom est déjà utilisé.")
        else:
            try:
                noeud = (
                    Noeud(nom_upper, type_noeud, capacite)
                    if type_noeud != "intermediaire"
                    else Noeud(nom_upper, type_noeud)
                )
                reseau.ListeNoeuds.append(noeud)
                st.success(f"{type_noeud.capitalize()} ajoutée : {nom_upper}")
            except Exception as e:
                st.error(str(e))


def ajouter_liaisons():
    st.markdown("Ajoutez une liaison entre deux nœuds existants.")
    noms_noeuds = {n.nom for n in reseau.ListeNoeuds}
    depart = st.text_input("Départ de la liaison", key="liaison_depart")
    arrivee = st.text_input("Arrivée de la liaison", key="liaison_arrivee")
    capacite = st.number_input(
        "Capacité de la liaison", min_value=1, value=5, key="liaison_cap"
    )

    if st.button("Ajouter la liaison"):
        depart_upper = depart.strip().upper()
        arrivee_upper = arrivee.strip().upper()
        if depart.strip() == "" or arrivee.strip() == "":
            st.warning("Les noms de départ et d'arrivée ne peuvent pas être vides.")
            return
        if depart_upper == arrivee_upper:
            st.warning("Une liaison ne peut pas relier un noeud à lui-même.")
        elif depart_upper not in noms_noeuds or arrivee_upper not in noms_noeuds:
            st.warning("Noeud de départ ou d’arrivée introuvable.")
        elif any(
            liaison.depart == depart_upper and liaison.arrivee == arrivee_upper
            for liaison in reseau.ListeLiaisons
        ):
            st.warning("Cette liaison existe déjà.")
        else:
            try:
                liaison = Liaison(depart_upper, arrivee_upper, capacite)
                reseau.ListeLiaisons.append(liaison)
                st.success(f"Liaison ajoutée : {depart_upper} ➝ {arrivee_upper}")
            except Exception as e:
                st.error(str(e))


def menu_ajout_elements():
    st.header("➕ Ajouter un élément au réseau")
    st.info(
        "Ajoutez dynamiquement des sources, villes, intermédiaires ou liaisons à votre réseau existant."
    )
    with st.expander("💧 Ajouter une source"):
        ajouter_noeuds("source")
    with st.expander("🏙️ Ajouter une ville"):
        ajouter_noeuds("ville")
    with st.expander("🔵 Ajouter un intermédiaire"):
        ajouter_noeuds("intermediaire")
    with st.expander("🔗 Ajouter une liaison"):
        ajouter_liaisons()


def afficher_carte_enoncer():
    st.header("🗺️ Carte de l'énoncé")
    st.info("Visualisez un premier aperçu de votre réseau sans analyse")
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'afficher la carte.")
        return
    if not reseau.ListeNoeuds or not reseau.ListeLiaisons:
        st.warning("Veuillez d'abord saisir des noeuds et des liaisons.")
        return
    reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
    result, index_noeuds = reseau_hydro.calculerFlotMaximal()
    fig = afficherCarteEnoncer(
        result=result,
        index_noeuds=index_noeuds,
        noeuds=reseau.ListeNoeuds,
        liaisons=reseau.ListeLiaisons,
    )
    st.pyplot(fig)


def afficher_carte_flot():
    st.header("💦 Carte avec flot maximal")
    st.info(
        "Visualisez la circulation d'eau dans votre réseau et les liaisons saturées."
    )

    reseau = st.session_state.get("reseau", None)
    if not reseau:
        st.warning("Aucun réseau n’a été chargé.")
        return

    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'afficher la carte.")
        return

    if not reseau.ListeNoeuds or not reseau.ListeLiaisons:
        st.warning("Veuillez d'abord saisir des noeuds et des liaisons.")
        return

    try:
        reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
        result, index_noeuds = reseau_hydro.calculerFlotMaximal()

        fig = afficherCarte(
            result=result,
            index_noeuds=index_noeuds,
            noeuds=reseau.ListeNoeuds,
            liaisons=reseau.ListeLiaisons,
            montrer_saturees=True,
        )
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Erreur lors du calcul ou de l'affichage de la carte : {e}")


def menu_travaux():
    st.header("🛠️ Optimisation manuelle des travaux")
    st.info(
        "Sélectionnez les liaisons de votre choix pour améliorer le flot de votre réseau."
    )
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    liaisons_possibles = [
        (liaison.depart, liaison.arrivee) for liaison in reseau.ListeLiaisons
    ]
    selection = st.multiselect(
        "Sélectionnez les liaisons à optimiser (format : Départ ➝ Arrivée)",
        options=[f"{u} ➝ {v}" for u, v in liaisons_possibles],
    )
    liaisons_a_optimiser = []
    for s in selection:
        u, v = s.split("➝")
        liaisons_a_optimiser.append((u.strip(), v.strip()))
    if st.button("🚀 Lancer l'optimisation"):
        if not liaisons_a_optimiser:
            st.warning("Aucune liaison sélectionnée.")
            return
        config_finale, travaux = optimiser_liaisons(
            reseau.ListeNoeuds, reseau.ListeLiaisons, liaisons_a_optimiser
        )
        st.success("Optimisation terminée.")
        for i, (liaison, cap, flot) in enumerate(travaux):
            u, v = liaison
            # Cherche l'ancienne capacité dans la config initiale
            ancienne_cap = next(
                (
                    liaison_obj.capacite
                    for liaison_obj in reseau.ListeLiaisons
                    if liaison_obj.depart == u and liaison_obj.arrivee == v
                ),
                None,
            )
            if ancienne_cap is not None:
                st.write(
                    f"Travaux #{i+1} : Liaison {u} ➝ {v}, capacité {ancienne_cap} ➔ {cap} unités, flot atteint : {flot} unités"
                )
            else:
                st.write(
                    f"Travaux #{i+1} : Liaison {u} ➝ {v}, capacité {cap} unités (nouvelle liaison), flot atteint : {flot} unités"
                )
        reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, config_finale)
        result, index_noeuds = reseau_hydro.calculerFlotMaximal()
        fig = afficherCarte(
            result=result,
            index_noeuds=index_noeuds,
            noeuds=reseau.ListeNoeuds,
            liaisons=config_finale,
            montrer_saturees=True,
        )
        st.pyplot(fig)


def menu_generalisation():
    st.header("🌍 Optimisation globale / généralisation")
    st.info(
        "Optimisez automatiquement votre réseau pour répondre à différents scénarios."
    )

    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    choix = st.radio(
        "Scénario",
        ["Optimiser pour approvisionner 100% des villes", "Assèchement d'une source"],
    )

    if choix == "Optimiser pour approvisionner 100% des villes":
        # Crée une copie propre du réseau pour l’optimisation
        noeuds_copie = copy.deepcopy(reseau.ListeNoeuds)
        liaisons_copie = copy.deepcopy(reseau.ListeLiaisons)

        objectif_defaut = sum(n.capaciteMax for n in noeuds_copie if n.type == "ville")
        st.write(f"🎯 Objectif : {objectif_defaut} unités (100% des villes)")
        objectif = st.number_input(
            "Saisissez l'objectif de flot à atteindre (en unités) :",
            min_value=1,
            max_value=objectif_defaut,
            value=objectif_defaut,
            step=1,
        )
        capacite_maximale = st.number_input(
            "Capacité maximale des liaisons (par défaut 10)",
            min_value=1,
            value=25,
            step=1,
        )
        if st.button("🔧 Lancer l'optimisation globale"):
            nouvelle_config, travaux = satisfaction(
                noeuds=noeuds_copie,
                liaisons=liaisons_copie,
                objectif=objectif,
                cap_max=capacite_maximale,
                max_travaux=10,
            )
            if not travaux:
                st.warning(
                    "⚠️ Objectif non atteignable avec la configuration actuelle du réseau et les capacités testées."
                )
            else:
                st.success("Optimisation globale terminée.")

                # Résumé des travaux par liaison
                resume_travaux = {}
                for (depart, arrivee), cap, new_flot in travaux:
                    key = (depart, arrivee)
                    if key not in resume_travaux:
                        # Capacité de départ dans la config initiale
                        cap_depart = next(
                            (
                                liaison_obj.capacite
                                for liaison_obj in liaisons_copie
                                if liaison_obj.depart == depart
                                and liaison_obj.arrivee == arrivee
                            ),
                            None,
                        )
                        resume_travaux[key] = {
                            "cap_depart": cap_depart,
                            "cap_fin": cap,
                            "flot": new_flot,
                        }
                    else:
                        resume_travaux[key]["cap_fin"] = cap
                        resume_travaux[key]["flot"] = new_flot

                st.markdown("**Résumé des travaux par liaison :**")
                # Trie les travaux par valeur du flot maximal atteint lors du dernier changement (ordre croissant)
                for (depart, arrivee), infos in sorted(
                    resume_travaux.items(), key=lambda x: x[1]['flot']
                ):
                    st.write(
                        f"Liaison {depart} ➝ {arrivee} : capacité {infos['cap_depart']} ➔ {infos['cap_fin']} unités, "
                        f"flot maximal atteint lors du dernier changement : {infos['flot']} unités"
                    )

                # Affichage de la carte finale (une seule fois)
                reseau_opt = ReseauHydraulique(noeuds_copie, nouvelle_config)
                result, index_noeuds = reseau_opt.calculerFlotMaximal()
                fig = afficherCarte(
                    result=result,
                    index_noeuds=index_noeuds,
                    noeuds=noeuds_copie,
                    liaisons=nouvelle_config,
                    montrer_saturees=True,
                )
                st.pyplot(fig)

            if travaux:
                flot_final = travaux[-1][2]
            else:
                reseau_opt = ReseauHydraulique(noeuds_copie, nouvelle_config)
                result, _ = reseau_opt.calculerFlotMaximal()
                flot_final = result.flow_value

            st.markdown(
                f"**Flot maximal obtenu : <span style='color:#0072B5;font-weight:bold'>{flot_final}</span> unités**",
                unsafe_allow_html=True,
            )
    else:
        import random

        sources = [n for n in reseau.ListeNoeuds if n.type == "source"]
        if not sources:
            st.warning("Aucune source trouvée.")
            return

        if "source_assechee" not in st.session_state:
            st.session_state["source_assechee"] = None

        mode_choix = st.radio(
            "Méthode d’assèchement :", ["🔀 Aléatoire", "🎯 Manuel"], horizontal=True
        )

        if mode_choix == "🔀 Aléatoire":
            if st.button("💣 Assécher une source aléatoirement"):
                source_choisie = random.choice(sources)
                st.session_state["source_assechee"] = source_choisie.nom
                for n in reseau.ListeNoeuds:
                    if n.nom == source_choisie.nom:
                        n.capaciteMax = 0

        elif mode_choix == "🎯 Manuel":
            source_noms = [n.nom for n in sources]
            source_select = st.selectbox(
                "Choisissez une source à assécher :", source_noms
            )
            if st.button("💣 Assécher la source sélectionnée"):
                st.session_state["source_assechee"] = source_select
                for n in reseau.ListeNoeuds:
                    if n.nom == source_select:
                        n.capaciteMax = 0

        if st.session_state["source_assechee"]:
            st.write(
                f"Source choisie : <span style='color:#d62728;font-weight:bold'>{st.session_state['source_assechee']}</span>",
                unsafe_allow_html=True,
            )
            reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
            result, index_noeuds = reseau_hydro.calculerFlotMaximal()
            fig = afficherCarte(
                result=result,
                index_noeuds=index_noeuds,
                noeuds=reseau.ListeNoeuds,
                liaisons=reseau.ListeLiaisons,
                montrer_saturees=True,
            )
            st.pyplot(fig)
            liaisons_possibles = [
                (liaison.depart, liaison.arrivee) for liaison in reseau.ListeLiaisons
            ]
            liaison_str = st.selectbox(
                "Sélectionnez une liaison à renforcer (+5 unités)",
                [f"{u} ➝ {v}" for u, v in liaisons_possibles],
            )
            if st.button("💪 Renforcer la liaison sélectionnée"):
                u, v = liaison_str.split("➝")
                u, v = u.strip(), v.strip()
                for liaison in reseau.ListeLiaisons:
                    if liaison.depart == u and liaison.arrivee == v:
                        liaison.capacite += 5
                        st.write(
                            f"Liaison {u} ➝ {v} renforcée à {liaison.capacite} unités."
                        )
                        break
                reseau_hydro = ReseauHydraulique(
                    reseau.ListeNoeuds, reseau.ListeLiaisons
                )
                result_modifie, index_noeuds_modifie = (
                    reseau_hydro.calculerFlotMaximal()
                )
                fig = afficherCarte(
                    result=result_modifie,
                    index_noeuds=index_noeuds_modifie,
                    noeuds=reseau.ListeNoeuds,
                    liaisons=reseau.ListeLiaisons,
                    montrer_saturees=True,
                )
                st.pyplot(fig)
                st.write(f"Nouveau flot maximal : {result_modifie.flow_value} u.")

            # Ajouter un bouton pour réinitialiser l'état si besoin
            if st.button("🔄 Réinitialiser l'assèchement"):
                st.session_state["source_assechee"] = None

                if (
                    "reseau_original_noeuds" in st.session_state
                    and "reseau_original_liaisons" in st.session_state
                ):
                    reseau.ListeNoeuds = copy.deepcopy(
                        st.session_state["reseau_original_noeuds"]
                    )
                    reseau.ListeLiaisons = copy.deepcopy(
                        st.session_state["reseau_original_liaisons"]
                    )
                    st.success("Le réseau a été restauré à son état initial.")
                else:
                    st.warning(
                        "Impossible de restaurer : données initiales non trouvées."
                    )


def menu_chargement():
    st.header("📂 Chargement d'un réseau existant")
    st.info("Chargez un réseau sauvegardé pour le visualiser ou l'optimiser.")
    fichier = st.text_input("Nom du fichier à charger", value="reseaux.json")

    # Charger les réseaux une seule fois et les garder en mémoire

    if st.button("🔄 Charger le réseau"):
        try:
            reseaux = GestionReseau.charger_reseaux(fichier)
            if not reseaux:
                st.warning("Aucun réseau trouvé dans ce fichier.")
            else:
                st.session_state["reseaux_charges"] = reseaux
                st.session_state["dernier_fichier_charge"] = fichier
                st.success("Réseaux chargés avec succès.")
        except Exception as e:
            st.error(f"Erreur lors du chargement : {e}")

    reseaux = st.session_state.get("reseaux_charges", {})
    if reseaux:
        nom_reseau = st.selectbox("Choisir un réseau", list(reseaux.keys()))
        if st.button("✅ Valider le chargement"):
            noeuds, liaisons = reseaux[nom_reseau]
            st.session_state["reseau"] = GestionReseau(noeuds, liaisons)
            st.session_state["reseau_valide"] = False  # On force la validation manuelle
            st.success("Réseau chargé. Cliquez sur 'Valider le réseau' pour continuer.")

    # Ajout du bouton de validation ici aussi
    if st.button("✅ Valider le réseau"):
        reseau = st.session_state["reseau"]
        if reseau.ListeNoeuds and reseau.ListeLiaisons:
            st.session_state["reseau_valide"] = True
            # Sauvegarde de la version initiale du réseau
            st.session_state["reseau_original_noeuds"] = copy.deepcopy(
                reseau.ListeNoeuds
            )
            st.session_state["reseau_original_liaisons"] = copy.deepcopy(
                reseau.ListeLiaisons
            )
            st.success("Votre réseau est prêt à être utilisé.")
        else:
            st.warning(
                "Veuillez charger un réseau contenant au moins un noeud et une liaison."
            )


# === MENU LATERAL PRINCIPAL ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933884.png", width=80)
    st.markdown("<h3 style='color:#0072B5'>Menu principal</h3>", unsafe_allow_html=True)
    menu = st.selectbox(
        "Navigation",
        [
            "Créer un réseau",
            "Charger un réseau",
            "Afficher le réseau initial",
            "Visualiser les flux",
            "Simuler des travaux",
            "Préparer votre réseau aux défis multiples",
            "Ajouter un élément",
            "Réinitialiser le réseau",
        ],
    )
    st.markdown(
        """
        <hr>
        <div style='font-size:0.95em;color:#555'>
        <b>Astuce :</b> Validez votre réseau avant d'accéder aux fonctionnalités d'affichage ou d'optimisation.<br>
        <b>Couleurs :</b> <span style='color:#d62728'>Sources</span>, <span style='color:#2ca02c'>Villes</span>, <span style='color:#1f77b4'>Intermédiaires</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if menu == "Créer un réseau":
    menu_saisie_reseau()
elif menu == "Charger un réseau":
    menu_chargement()
elif menu == "Afficher le réseau initial":
    afficher_carte_enoncer()
elif menu == "Visualiser les flux":
    afficher_carte_flot()
elif menu == "Simuler des travaux":
    menu_travaux()
elif menu == "Préparer votre réseau aux défis multiples":
    menu_generalisation()
elif menu == "Ajouter un élément":
    menu_ajout_elements()
elif menu == "Réinitialiser le réseau":
    if st.button("🔄 Confirmer la réinitialisation du réseau"):
        reset_reseau()
        st.success("Le réseau a été réinitialisé.")
        st.rerun()

import streamlit as st
from data import (
    GestionReseau, ReseauHydraulique, optimiser_liaisons, satisfaction, Noeud, Liaison
)
from affichage import afficherCarte, afficherCarteEnoncer



st.set_page_config(page_title="Réseau Hydraulique", layout="wide", page_icon="🚰")

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
    unsafe_allow_html=True
)

if "reseau" not in st.session_state:
    st.session_state["reseau"] = GestionReseau()
if "reseau_valide" not in st.session_state:
    st.session_state["reseau_valide"] = False

reseau = st.session_state["reseau"]

def reset_reseau():
    st.session_state["reseau"] = GestionReseau()
    st.session_state["reseau_valide"] = False

def menu_saisie_reseau():
    st.header("🛠️ Création d'un nouveau réseau")
    st.info("Ajoutez vos sources, villes, intermédiaires et liaisons pour construire votre réseau hydraulique.")
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
                st.success("Réseau validé. Vous pouvez maintenant afficher ou optimiser le réseau.")
            else:
                st.warning("Veuillez ajouter au moins un noeud et une liaison.")
    with col2:
        if st.button("💾 Sauvegarder ce réseau"):
            nom_fichier = st.text_input("Nom du fichier de sauvegarde", value="reseau1.json")
            if nom_fichier:
                reseau.sauvegarder_reseau(nom_fichier)
                st.success(f"Réseau sauvegardé dans {nom_fichier}")

def ajouter_noeuds(type_noeud):
    icones = {"source": "💧", "ville": "🏙️", "intermediaire": "🔵"}
    noms_existants = {n.nom for n in reseau.ListeNoeuds}
    nom = st.text_input(f"{icones[type_noeud]} Nom de la {type_noeud}", key=f"{type_noeud}_nom")
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
    st.markdown("Ajoutez une liaison entre deux nœuds existants.")
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

def menu_ajout_elements():
    st.header("➕ Ajouter un élément au réseau")
    st.info("Ajoutez dynamiquement des sources, villes, intermédiaires ou liaisons à votre réseau existant.")
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
    st.info("Visualisez la structure de votre réseau sans calcul de flot maximal.")
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
    st.header("💦 Carte avec flot maximal")
    st.info("Visualisez le flot maximal calculé sur votre réseau hydraulique.")
    
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
            montrer_saturees=True
        )
        st.pyplot(fig)
    except Exception as e:
            st.error(f"Erreur lors du calcul ou de l'affichage de la carte : {e}")

def menu_travaux():
    st.header("🛠️ Optimisation manuelle des travaux")
    st.info("Sélectionnez les liaisons à optimiser pour améliorer le flot de votre réseau.")
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    liaisons_possibles = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
    selection = st.multiselect(
        "Sélectionnez les liaisons à optimiser (format : Départ ➝ Arrivée)",
        options=[f"{u} ➝ {v}" for u, v in liaisons_possibles]
    )
    liaisons_a_optimiser = []
    for s in selection:
        u, v = s.split("➝")
        liaisons_a_optimiser.append((u.strip(), v.strip()))
    if st.button("🚀 Lancer l'optimisation"):
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
        fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=config_finale, montrer_saturees=True)
        st.pyplot(fig)

def menu_generalisation():
    st.header("🌍 Optimisation globale / généralisation")
    st.info("Optimisez automatiquement votre réseau pour répondre à différents scénarios.")
    if not st.session_state.get("reseau_valide", False):
        st.warning("Veuillez valider le réseau avant d'utiliser cette fonctionnalité.")
        return
    choix = st.radio("Scénario", [
        "Optimiser pour approvisionner 100% des villes",
        "Assèchement d'une source"
    ])
    if choix == "Optimiser pour approvisionner 100% des villes":
        objectif_defaut = sum(n.capaciteMax for n in reseau.ListeNoeuds if n.type == "ville")
        st.write(f"🎯 Objectif : {objectif_defaut} unités (100% des villes)")
        objectif = st.number_input(
            "Saisissez l'objectif de flot à atteindre (en unités) :",
            min_value=1,
            max_value=objectif_defaut,
            value=objectif_defaut,
            step=1
        )
        liaisons_modifiables = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
        capacite_maximale = st.number_input("Capacité maximale des liaisons (par défaut 10)", min_value=1, value=10, step=1)
        if st.button("🔧 Lancer l'optimisation globale"):
            nouvelle_config, travaux = satisfaction(
                noeuds=reseau.ListeNoeuds,
                liaisons=reseau.ListeLiaisons,
                objectif=objectif,
                cap_max=capacite_maximale,   # transmis depuis le number_input
                max_travaux=10                # ou un autre nombre si tu veux le rendre paramétrable
            )
            if not travaux:
                st.warning("⚠️ Objectif non atteignable avec la configuration actuelle du réseau et les capacités testées.")
            else:
                st.success("Optimisation globale terminée.")
                for (depart, arrivee), cap, new_flot in travaux:
                    st.write(f"Liaison {depart} ➝ {arrivee} ajustée à {cap} u. → Flot = {new_flot} u.")
                reseau_opt = ReseauHydraulique(reseau.ListeNoeuds, nouvelle_config)
                result, index_noeuds = reseau_opt.calculerFlotMaximal()
                fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=nouvelle_config, montrer_saturees=True)
                st.pyplot(fig)
    else:
        import random
        sources = [n for n in reseau.ListeNoeuds if n.type == "source"]
        if not sources:
            st.warning("Aucune source trouvée.")
            return
        
        if "source_assechee" not in st.session_state:
            st.session_state["source_assechee"] = None

        mode_choix = st.radio("Méthode d’assèchement :", ["🔀 Aléatoire", "🎯 Manuel"], horizontal=True)

        if mode_choix == "🔀 Aléatoire":
            if st.button("💣 Assécher une source aléatoirement"):
                source_choisie = random.choice(sources)
                st.session_state["source_assechee"] = source_choisie.nom
                for n in reseau.ListeNoeuds:
                    if n.nom == source_choisie.nom:
                        n.capaciteMax = 0
        
        elif mode_choix == "🎯 Manuel":
            source_noms = [n.nom for n in sources]
            source_select = st.selectbox("Choisissez une source à assécher :", source_noms)
            if st.button("💣 Assécher la source sélectionnée"):
                st.session_state["source_assechee"] = source_select
                for n in reseau.ListeNoeuds:
                    if n.nom == source_select:
                        n.capaciteMax = 0

        if st.session_state["source_assechee"]:
            st.write(f"Source choisie : <span style='color:#d62728;font-weight:bold'>{st.session_state['source_assechee']}</span>",unsafe_allow_html=True)
            reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
            result, index_noeuds = reseau_hydro.calculerFlotMaximal()
            fig = afficherCarte(result=result, index_noeuds=index_noeuds, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons, montrer_saturees=True)
            st.pyplot(fig)
            liaisons_possibles = [(l.depart, l.arrivee) for l in reseau.ListeLiaisons]
            liaison_str = st.selectbox("Sélectionnez une liaison à renforcer (+5 unités)", [f"{u} ➝ {v}" for u, v in liaisons_possibles])
            if st.button("💪 Renforcer la liaison sélectionnée"):
                u, v = liaison_str.split("➝")
                u, v = u.strip(), v.strip()
                for liaison in reseau.ListeLiaisons:
                    if liaison.depart == u and liaison.arrivee == v:
                        liaison.capacite += 5
                        st.write(f"Liaison {u} ➝ {v} renforcée à {liaison.capacite} unités.")
                        break
                reseau_hydro = ReseauHydraulique(reseau.ListeNoeuds, reseau.ListeLiaisons)
                result_modifie, index_noeuds_modifie = reseau_hydro.calculerFlotMaximal()
                fig = afficherCarte(result=result_modifie, index_noeuds=index_noeuds_modifie, noeuds=reseau.ListeNoeuds, liaisons=reseau.ListeLiaisons, montrer_saturees=True)
                st.pyplot(fig)
                st.write(f"Nouveau flot maximal : {result_modifie.flow_value} u.")

            # Ajouter un bouton pour réinitialiser l'état si besoin
            if st.button("🔄 Réinitialiser l'assèchement"):
                st.session_state["source_assechee"] = None

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
            st.success("Réseau validé. Vous pouvez maintenant afficher ou optimiser le réseau.")
        else:
            st.warning("Veuillez charger un réseau contenant au moins un noeud et une liaison.")

# === MENU LATERAL PRINCIPAL ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2933/2933884.png", width=80)
    st.markdown("<h3 style='color:#0072B5'>Menu principal</h3>", unsafe_allow_html=True)
    menu = st.selectbox(
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
    st.markdown(
        """
        <hr>
        <div style='font-size:0.95em;color:#555'>
        <b>Astuce :</b> Validez votre réseau avant d'accéder aux fonctionnalités d'affichage ou d'optimisation.<br>
        <b>Couleurs :</b> <span style='color:#d62728'>Sources</span>, <span style='color:#2ca02c'>Villes</span>, <span style='color:#1f77b4'>Intermédiaires</span>
        </div>
        """,
        unsafe_allow_html=True
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
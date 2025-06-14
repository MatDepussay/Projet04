# Sujet 04 : Adduction d'eau

Trois villes J, K, L sont alimentées en eau grâce à quatre réserves A, B, C, D.
Les réserves journalières disponibles sont

- de 15 milliers de $m^3$ pour A,B et C
- de 10 milliers de $m^3$ pour D.

Le réseau historique comporte même quelques aqueducs romains.
Il emprunte cinq anciens noeuds E, F, G, H, I.
Voici le tableau des capacités de débits du réseau.
La ligne x colonne y est le flux maximal du noeud x vers le noeud y.

|     | A   | B   | C   | D   | E   | F   | G   | H   | I   | J   | K   | L   |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A   |     |     |     |     | 7   |     |     |     |     |     |     |     |
| B   |     |     |     |     |     | 10  | 7   |     |     |     |     |     |
| C   | 5   |     |     |     |     | 5   |     |     |     |     |     |     |
| D   |     |     |     |     |     |     | 10  |     |     |     |     |     |
| E   |     |     |     |     |     | 5   |     | 4   | 15  |     |     |     |
| F   |     |     |     |     |     |     | 5   |     | 15  |     |     |     |
| G   |     |     |     |     |     |     |     |     | 15  |     |     |     |
| H   |     |     |     |     |     |     |     |     |     | 7   |     |     |
| I   |     |     |     |     |     |     |     |     |     |     | 30  | 4   |
| J   |     |     |     |     |     |     |     |     |     |     |     |     |
| K   |     |     |     |     |     |     |     |     |     | 10  |     |     |
| L   |     |     |     |     |     |     |     |     |     |     |     |     |

Ces trois villes sont en pleine évolution.
Elles désirent améliorer leur réseau d'alimentation afin de satisfaire
des besoins futurs.
Les prévisions des demandes journalières maximales sont de

- 15 milliers de m^3 pour les villes J et L
- 20 milliers de m^3 pour la ville K.

1. Dessiner le graphe de ce réseau.
   Déterminer la valeur du flot maximal pouvant passer dans le réseau actuel.
2. La valeur de ce flot est jugée nettement insuffisante.
   La région décide de refaire les canalisations (AE) et (IL).
   Déterminer les capacités à prévoir pour ces deux canalisations.
   Déterminer aussi la valeur du nouveau flot optimal.
3. Devant l'importance des travaux, la région décide de faire les travaux
   en deux temps.
   Déterminer l'ordre de la réfection des canalisations permettant d'augmenter
   le flot maximal après chaque travaux.
   Calculer ce flot maximal à chaque étape.

4. Generalisation
   Dans un premier temps on cherche a approvisioner les villes a 100% de leurs demandent. 
   Selection aléatoire d'une source qui s'asseches comment la charge se repartie pour faire des travaux. 

Questions à l'oral :
- dans optimiser_liaison_pour_approvisionnement différence si on fait in range(1:21) et si on fait [5, 10, 15, 20]. On ne retrouve pas le meme résultat. 

Retour du prof : 
Saisie manuelle du réseau
Sauvegarder le reseau
Impact de l'assechement des villes plus généraliser
appli avec streamlit
Outil d'analyse du reseau
Peu importe la ligne brisée mais les villes doivent être alimenter à 100%

Commande : 
uv run streamlit run src/appstreamlit.py
uv run ruff check .
uv run --check --fix
uv run -m pyinstrument 
uv run pytest tests/test_data.py
uv run coverage report
uv run coverage run --source=src -m pytest
coverage report -m | grep affichage

---

# 🚰 AquaFlow – Application de gestion et d'optimisation de réseau hydraulique

**AquaFlow** est une application interactive développée avec Streamlit permettant de modéliser, visualiser et optimiser un réseau hydraulique (sources, villes, nœuds intermédiaires, liaisons). Elle est conçue pour faciliter l'expérimentation, la simulation de scénarios et la prise de décision dans des contextes d'approvisionnement en eau.

---

## 🌟 Fonctionnalités principales

- **Création interactive du réseau** : ajout de sources, villes, nœuds intermédiaires et liaisons.
- **Affichage graphique** :
  - Carte simple du réseau.
  - Carte avec affichage des flots et des liaisons saturées.
- **Optimisations** :
  - Manuelle : sélection de liaisons à améliorer.
  - Automatique : satisfaction de contraintes ou scénarios simulés.
- **Persistance** :
  - Sauvegarde/chargement des réseaux via des fichiers JSON.
- **Simulations avancées** :
  - Assèchement de sources.
  - Objectifs personnalisés (ex. : 100% des villes alimentées).

---

## 🚀 Lancer l'application

Assurez-vous d'avoir Python ≥ 3.9 installé, puis :

```bash
uv run streamlit run src/appstreamlit.py
streamlit run appstreamlit.py
```

L'interface web se lance dans votre navigateur. Vous pouvez alors :

- Créer un réseau (ajouter des éléments) ou charger un réseau existant (json).
- Valider et visualiser le réseau pour une analyse.
- Lancer des optimisations pour anticiper des aléas et/ou réfléchir à des travaux, optimisations et améliorations de votre réseau hydraulique.
- Sauvegarder et réinitialiser les réseaux.

---

## Installation

Clonez le dépôt et installez les dépendances :
```bash
git clone https://github.com/MatDepussay/Projet04
cd Projet04
pip install -r requirements.txt4
```

--- 

## Architecture du projet 

```bash
Projet04/
│
├── src/                            ← Code source principal
│   ├── __init__.py
│   ├── appstramlit.py              ← Fichier principal pour lancer Streamlit
│   ├── data.py                     ← Fonctions de traitement des données
│   └── affichage.py                ← Fonctions pour afficher les graphes
│
├── tests/                          ← Tests unitaires
│   ├── __init__.py
│   ├── test_affichage.py
│   ├── test_data.py
│   └── test_function.py
│
├── assets/                         ← Images, fichiers statiques
│   └── reseau_satisfaction_finale.png
│
├── requirements.txt               ← Dépendances installables
├── README.md                      ← Documentation
├── .coveragerc                    ← Config couverture de test
├── pyproject.toml                 ← Fichier de config (Black, isort, etc.)
└── streamlit_app.sh               ← Script de lancement (optionnel)
```


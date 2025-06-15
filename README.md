# 🚰 Sujet 04 - AquaFlow – Application de gestion et d'optimisation de réseau hydraulique

**AquaFlow** est une application interactive développée avec Streamlit permettant de modéliser, visualiser et optimiser un réseau hydraulique (sources, villes, nœuds intermédiaires, liaisons). Elle permet de simuler des scénarios réalistes d'approvisionnement, de test de résilience du réseau, et d'analyse d'optimisation des infrastructures hydrauliques.

---

## 🌟 Fonctionnalités principales

- **Création interactive du réseau** :
    - ajout de sources, villes, nœuds intermédiaires et liaisons.
    - Chargement/Sauvegarde d'un réseau au format JSON (reseau.json fourni dans le projet)

- **Affichage graphique** :
  - Visualisation simple du réseau (flots, capacités, noeuds colorés par type).
  - Visualisation des flots circulants dans le réseaux et des liaisons saturées.

- **Optimisations et Simulations** :
  - Sélection manuelle du nombre maximal de travaux à réaliser pour renforcer le réseau.
  - Satisfaction automatique des villes à 100% (approvisionnement complet).
  - Simulation de l’assèchement d’une ou plusieurs sources (choix aléatoire ou manuel).
  - Possibilité de relancer la satisfaction des villes après que les sources voulues soient asséchées sans réinitialiser le réseau afin d'observer les effets cumulés.

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
│   ├── appstreamlit.py             ← Interface Streamlit
│   ├── data.py                     ← Logique métier 
│   └── affichage.py                ← Fonctions de visualisation avec NetworkX
│
├── tests/                          ← Tests unitaires Pytest
│   ├── test_affichage.py
│   ├── test_data.py
│   └── test_function.py
│
├── exemples/                       
│   └── demo.py
│
├── reseau.json                     ← Réseau de test (fichier chargeable)
├── requirements.txt                ← Dépendances Python
├── pyproject.toml                  ← Configuration du projet
└── README.md                       ← Documentation
```

## Consigne

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

Questions à l'oral :
- dans optimiser_liaison_pour_approvisionnement différence si on fait in range(1:21) et si on fait [5, 10, 15, 20]. On ne retrouve pas le meme résultat. 

Retour du prof : 
Saisie manuelle du réseau
Sauvegarder le reseau
Impact de l'assechement des villes plus généralisé
interface avec streamlit
Outil d'analyse du reseau
Peu importe la ligne brisée, les villes doivent être alimentées

---

## Utilisation du fichier reseau.json

Un fichier reseau.json est disponible à la racine du projet. Il contient un exemple complet de réseau correspondant aux données disponibles dans la partie **Consigne**.

➕ Pour l’utiliser :
    Dans l'application Streamlit, cliquez sur "Charger un réseau", puis sélectionnez reseau.json puis Demo. Cela permet de tester directement l’ensemble des fonctionnalités.

---

## Partie généralisation

Notre application permet de visualiser votre réseau mais également d'explorer des scénarios plus complexes : 

- 💧 **Assèchement de sources** : sélectionnez une ou plusieurs sources à désactiver et visualisez l'impact sur le réseau.

- 🛠️ **Nombre variable de travaux** : choisissez autant de liaisons que vous voulez améliorer.

- 📈 Objectif : **satisfaire à 100% les villes** :
Vous pouvez tester si le réseau actuel permet de répondre à la demande.
Sinon, une optimisation automatique vous proposera les meilleurs travaux à effectuer.

- 🔁 **Tests en cascade** :
Si vous ne réinitialisez pas le réseau, vous pouvez appliquer plusieurs scénarios successifs (par exemple : assèchement + ajouter des nouveaux agents + satisfaction à 100%).
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

## Commandes utiles (environnement uv)

```bash
uv run streamlit run src/appstreamlit.py
uv run ruff check .
uv run --check --fix
uv run -m pyinstrument -m pytest .\src\data.py
uv run pytest tests/test_data.py
uv run coverage report
uv run coverage run --source=src -m pytest
coverage report -m | grep affichage
uv run -m pyinstrument -m pytest Test/test_data.py
```
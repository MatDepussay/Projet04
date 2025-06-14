import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from data import ReseauHydraulique, Liaison, Noeud, creer_liaison, creer_noeud, GestionReseau, satisfaction, demander_cap_max
from main import main

def test_main_output(capfd):
    main()
    out, _ = capfd.readouterr()
    assert "Hello from AquaFlow!" in out

# Tests class Noeud

def test_creation_noeud():
    noeud = Noeud("A", "source", 10)
    assert noeud.nom == "A"
    assert noeud.type == "source"
    assert noeud.capaciteMax == 10

def test_creation_inter():
    n1 = Noeud("N1", "intermediaire")
    assert n1.capaciteMax == 0

def test_str_representationNoeud():
    noeud = Noeud("L", "ville", 150)
    rep = str(noeud)
    print(f"Représentation __str__ : '{rep}'")
    assert "Nom : L" in rep
    assert "Type : ville" in rep
    assert "Capacite max : 150" in rep
    
def test_noeud_to_dict():
    noeuds = Noeud("A", "source", 100)
    d = noeuds.to_dict()
    assert d == {"nom": "A", "type": "source", "capaciteMax": 100}
    assert not d == {"nom": "A", "type": "source", "capaciteMax": 90}
    assert not d == {"nom": "A", "type": "ville", "capaciteMax": 100}
    assert not d == {"nom": "B", "type": "source", "capaciteMax": 100}

def test_from_dict_complet():
    d = {"nom": "K", "type": "ville", "capaciteMax": 120}
    noeud = Noeud.from_dict(d)
    assert isinstance(noeud, Noeud)
    assert noeud.nom == "K"
    assert noeud.type == "ville"
    assert noeud.capaciteMax == 120

# Tests class Liaison

def test_creation_liaison():
    liaison = Liaison("P", "L", 300)
    assert liaison.depart == "P"
    assert liaison.arrivee == "L"
    assert liaison.capacite == 300

def test_str_representationLiaison():
    liaison = Liaison("T", "N", 150)
    rep = str(liaison)
    assert "Départ : T" in rep
    assert "Arrivée : N" in rep
    assert "Capacite : 150" in rep

def test_liaison_to_dict():
    liaison = Liaison("A", "B", 50)
    d = liaison.to_dict()
    assert d == {"depart": "A", "arrivee": "B", "capacite": 50}
    assert not d == {"depart": "A", "arrivee": "B", "capacite": 100}
    assert not d == {"depart": "B", "arrivee": "A", "capacite": 50}
    assert not d == {"depart": "C", "arrivee": "C", "capacite": 50}

def test_from_dict():
    d = {"depart": "N", "arrivee": "L", "capacite": 100}
    liaison = Liaison.from_dict(d)
    assert isinstance(liaison, Liaison)
    assert liaison.depart == "N"
    assert liaison.arrivee == "L"
    assert liaison.capacite == 100

def test_from_dict_invalide():
    d = {"depart": "Nice", "capacite": 50}  # Il manque "arrivee"
    with pytest.raises(KeyError):
        Liaison.from_dict(d)

### Tests pour creer_noeud ###

def test_creer_noeud_valide_source():
    noeud = creer_noeud("A", "source", 100, noms_existants={"B", "C"})
    assert isinstance(noeud, Noeud)
    assert noeud.nom == "A"
    assert noeud.type == "source"
    assert noeud.capaciteMax == 100

def test_creer_noeud_valide_intermediaire():
    noeud = creer_noeud("X", "intermediaire", noms_existants=set())
    assert noeud.capaciteMax == 0

def test_creer_noeud_nom_deja_utilise():
    with pytest.raises(ValueError, match="nom est déjà utilisé"):
        creer_noeud("D", "ville", 50, noms_existants={"D", "E"})

def test_creer_noeud_type_invalide():
    with pytest.raises(ValueError, match="Type de noeud invalide"):
        creer_noeud("F", "invalide", 50, noms_existants=set())

def test_creer_noeud_capacite_invalide():
    with pytest.raises(ValueError, match="capacité doit être un entier positif"):
        creer_noeud("G", "source", 0, noms_existants=set())

def test_saisir_noeuds_source(monkeypatch):
    ListeNoeuds = []
    ListeLiaisons = []
    reseau = GestionReseau(ListeNoeuds, ListeLiaisons)
    inputs = iter([
        "A",            # nom 1
        "10",           # capacité valide
        "o",            # continuer
        "A",            # doublon
        "B",            # nom 2
        "-5",           # capacité invalide
        "B",            # re-saisie du nom 2
        "abc",          # capacité invalide (non entier)
        "B",            # re-saisie du nom 2
        "15",           # capacité valide
        "n"             # ne pas continuer
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    
    reseau.saisir_noeuds("source")

    assert len(reseau.ListeNoeuds) == 2
    noms = {n.nom for n in reseau.ListeNoeuds}
    assert "A" in noms
    assert "B" in noms
    assert reseau.ListeNoeuds[0].capaciteMax == 10
    assert reseau.ListeNoeuds[1].capaciteMax == 15

### Tests pour creer_liaison ###

def test_creer_liaison_valide():
    liaison = creer_liaison("A", "B", 50, noms_noeuds={"A", "B", "C"}, liaisons_existantes=[])
    assert isinstance(liaison, Liaison)
    assert liaison.depart == "A"
    assert liaison.arrivee == "B"
    assert liaison.capacite == 50

def test_saisir_liaisons(monkeypatch):
    ListeNoeuds = [
        Noeud("A", "source", 10),
        Noeud("B", "ville", 15),
        Noeud("C", "intermediaire", 0)
    ]
    ListeLiaisons = []

    reseau = GestionReseau(ListeNoeuds, ListeLiaisons)

    inputs = iter([
        "A", "A", "50",           # ❌ même noeud
        "A", "Z", "50",           # ❌ noeud inexistant
        "A", "B", "-20",          # ❌ capacité invalide
        "A", "B", "abc",          # ❌ capacité invalide
        "A", "B", "30", "o",      # ✅ Valide
        "A", "B", "40",           # ❌ doublon
        "B", "C", "60", "n"       # ✅ Valide + arrêt
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    reseau.saisir_liaisons()

    assert len(reseau.ListeLiaisons) == 2
    liaison1 = reseau.ListeLiaisons[0]
    liaison2 = reseau.ListeLiaisons[1]

    assert liaison1.depart == "A"
    assert liaison1.arrivee == "B"
    assert liaison1.capacite == 30

    assert liaison2.depart == "B"
    assert liaison2.arrivee == "C"
    assert liaison2.capacite == 60

def test_creer_liaison_meme_noeud():
    with pytest.raises(ValueError, match="relier un noeud à lui-même"):
        creer_liaison("A", "A", 50, noms_noeuds={"A", "B"}, liaisons_existantes=[])

def test_creer_liaison_noeud_inexistant():
    with pytest.raises(ValueError, match="Noeud de départ ou d’arrivée introuvable"):
        creer_liaison("A", "Z", 50, noms_noeuds={"A", "B"}, liaisons_existantes=[])

def test_creer_liaison_capacite_non_positive():
    with pytest.raises(ValueError, match="capacité de la liaison doit être un entier positif"):
        creer_liaison("A", "B", 0, noms_noeuds={"A", "B"}, liaisons_existantes=[])

def test_creer_liaison_doublon():
    liaison1 = Liaison("A", "B", 100)
    with pytest.raises(ValueError, match="liaison existe déjà"):
        creer_liaison("A", "B", 80, noms_noeuds={"A", "B"}, liaisons_existantes=[liaison1])

@pytest.fixture
def noeuds_et_liaisons():
    noeuds = [
        Noeud("A", "source", 100),
        Noeud("B", "ville", 50)
    ]
    liaisons = [
        Liaison("A", "B", 70)
    ]
    return noeuds, liaisons

def test_str_affichage(noeuds_et_liaisons):
    noeuds, liaisons = noeuds_et_liaisons
    gr = GestionReseau(noeuds, liaisons)
    res = str(gr)
    assert "Nom : A" in res
    assert "Départ : A, Arrivée : B" in res

def test_sauvegarder_et_charger_reseaux(tmp_path, noeuds_et_liaisons):
    fichier = tmp_path / "reseaux.json"
    noeuds, liaisons = noeuds_et_liaisons
    GestionReseau.sauvegarder_reseaux(noeuds, liaisons, str(fichier), "reseau_test")

    assert os.path.exists(fichier)

    reseaux = GestionReseau.charger_reseaux(str(fichier))
    assert "reseau_test" in reseaux
    noeuds_charges, liaisons_charges = reseaux["reseau_test"]
    assert isinstance(noeuds_charges[0], Noeud)
    assert isinstance(liaisons_charges[0], Liaison)
    assert noeuds_charges[0].nom == "A"

def test_supprimer_reseaux(tmp_path, noeuds_et_liaisons):
    fichier = tmp_path / "reseaux.json"
    noeuds, liaisons = noeuds_et_liaisons
    GestionReseau.sauvegarder_reseaux(noeuds, liaisons, str(fichier), "test")
    assert os.path.exists(fichier)

    GestionReseau.supprimer_reseaux(str(fichier))
    assert not os.path.exists(fichier)

def test_charger_reseau_inexistant(tmp_path):
    with pytest.raises(FileNotFoundError):
        GestionReseau.charger_reseaux(str(tmp_path / "inexistant.json"))

## Tests class Reseau_hydraulique

def test_str_reseau_vide():
    reseau = ReseauHydraulique([], [])
    rep = str(reseau)
    assert "--- Noeuds ---" in rep
    assert "--- Liaisons ---" in rep

def test_reseau_hydraulique_str():
    noeuds = [Noeud("A", "source", 100), Noeud("B", "ville", 50)]
    liaisons = [Liaison("A", "B", 70)]
    reseau = ReseauHydraulique(noeuds, liaisons)

    rep = str(reseau)
    assert "--- Noeuds ---" in rep
    assert "Nom : A" in rep
    assert "--- Liaisons ---" in rep
    assert "Départ : A" in rep


liaison_existe = GestionReseau.liaison_existe

def test_satisfaction_ameliore():
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = [Liaison("A", "B", 5)]
    config_finale, travaux = satisfaction(noeuds, liaisons, cap_max=10, max_travaux=2)
    assert travaux  # Il doit y avoir au moins un travaux
    assert config_finale[0].capacite > 5


def test_satisfaction_aucune_amelioration():
    noeuds = [Noeud("A", "source", 5), Noeud("B", "ville", 5)]
    liaisons = [Liaison("A", "B", 5)]
    config_finale, travaux = satisfaction(noeuds, liaisons, cap_max=5, max_travaux=2)
    assert travaux == []
    assert config_finale[0].capacite == 5

def test_demander_cap_max_valeur(monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "30")
        assert demander_cap_max(valeur_defaut=25) == 30
    
def test_demander_cap_max_defaut(monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        assert demander_cap_max(valeur_defaut=25) == 25

def test_liaisons_saturees():
    noeuds = [Noeud("A", "source", 10), Noeud("B", "ville", 10)]
    liaisons = [Liaison("A", "B", 10)]
    reseau = ReseauHydraulique(noeuds, liaisons)
    result, _ = reseau.calculerFlotMaximal()
    saturees = reseau.liaisons_saturees(result)
    assert ("A", "B", 10) in saturees

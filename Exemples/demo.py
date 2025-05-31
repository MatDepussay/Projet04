import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from app import Noeud, Liaison

# Définition des noeuds
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
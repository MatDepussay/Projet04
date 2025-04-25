import pytest
from src.data import ReseauHydraulique, ListeLiaison, liaison_existe, noeud, calculerFlotMaximal

def test_liaison_existe():
    assert liaison_existe("A","E", ListeLiaison) == True
    assert liaison_existe("A", "H", ListeLiaison) == False
    assert liaison_existe("E", "A", ListeLiaison) == False
from typing import List, Tuple
import scipy as sp
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow


ListeSommet: List[str] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


ListeLiaison: List[Tuple[str, str, int]] = [
    ("A", "E", 7),
    ("B", "F", 10),
    ("B", "G", 7),
    ("C", "A", 5),
    ("C", "F", 5),
    ("D", "G", 10),
    ("E", "F", 5),
    ("E", "H", 4),
    ("E", "I", 15),
    ("F", "G", 5),
    ("F", "I", 15),
    ("G", "I", 15),
    ("H", "J", 7),
    ("I", "K", 30),
    ("I", "L", 4),
    ("K", "J", 10),
]


def calculerFlotMaximal():
    noeuds = ListeSommet + ['super_source', 'super_puits']
    index_noeuds = {nom: i for i, nom in enumerate(noeuds)}
    n = len(noeuds)

    matrice = [[0] * n for _ in range(n)]

    for u, v, cap in ListeLiaison:
        i, j = index_noeuds[u], index_noeuds[v]
        matrice[i][j] = cap

    sources = {"A": 15, "B": 15, "C": 15, "D": 10}
    for s, cap in sources.items():
        matrice[index_noeuds['super_source']][index_noeuds[s]] = cap

    puits = {"J": 15, "K": 15, "L": 20}
    for p, cap in puits.items():
        matrice[index_noeuds[p]][index_noeuds['super_puits']] = cap

    matrice_sparse = sp.sparse.csr_matrix(matrice)

    result = sp.sparse.csgraph.maximum_flow(matrice_sparse, index_noeuds['super_source'], index_noeuds['super_puits'])

    return result, index_noeuds  

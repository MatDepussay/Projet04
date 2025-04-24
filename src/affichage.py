import networkx as nx
import matplotlib.pyplot as plt
from data import *

def afficherCarte(flot_maximal=None):
    G = nx.DiGraph()  # Utiliser DiGraph si tu veux visualiser le sens du flux

    G.add_nodes_from(ListeSommet)
    for u, v, cap in ListeLiaison:
        G.add_edge(u, v, weight=cap)

    pos = nx.spring_layout(G, seed=42)

    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, font_weight='bold')
    
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if flot_maximal is not None:
        # Afficher le flot en bas à droite
        plt.text(1.0, -0.1, f"Flot maximal : {flot_maximal}", fontsize=12, color='darkred',
                 ha='right', va='top', transform=plt.gca().transAxes,
                 bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons avec Flot Maximal")
    plt.axis('off')
    plt.show()

result, index_noeuds = calculerFlotMaximal()
flot_total = result.flow_value

# Répartition sur les puits
for p in ['J', 'K', 'L']:
    flot_recu = result.flow[index_noeuds[p], index_noeuds['super_puits']]
    print(f"{p} reçoit : {flot_recu}")

afficherCarte(flot_total)

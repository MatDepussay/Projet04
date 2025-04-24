import networkx as nx
import matplotlib.pyplot as plt
from data import *

def afficherCarte(flot_maximal=None, liaisons=None):
    if liaisons is None:
        liaisons = ListeLiaison  

    G = nx.DiGraph()
    G.add_nodes_from(ListeSommet)

    for u, v, cap in liaisons:
        G.add_edge(u, v, weight=cap)

    pos = nx.spring_layout(G, seed=42)

    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=800, font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    if flot_maximal is not None:
        plt.gcf().text(0.95, 0.05, f"Flot maximal : {flot_maximal}", fontsize=12,
                       color='darkred', ha='right', va='bottom',
                       bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons avec Flot Maximal")
    plt.axis('off')
    plt.show()



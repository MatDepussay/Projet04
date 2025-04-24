from matplotlib import pyplot as plt
import networkx as nx
from data import *

def afficherCarte():
    G = nx.Graph()

    # Ajouter les sommets
    G.add_nodes_from(ListeSommet)

    # Ajouter les arêtes avec les poids
    for liaison in ListeLiaison:
        G.add_edge(liaison[0], liaison[1], weight=liaison[2])

    # Positionnement automatique
    pos = nx.spring_layout(G, seed=42)  # ou kamada_kawai_layout, shell_layout...

    # Afficher les labels des sommets
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=800, font_size=12, font_weight='bold')

    # Afficher les poids sur les arêtes
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Carte des liaisons")
    plt.axis('off')
    plt.show()

# Appeler la fonction
afficherCarte()
import networkx as nx
import matplotlib.pyplot as plt
from data import *

def afficherCarte(result=None, index_noeuds=None):
    G = nx.DiGraph()

    G = nx.DiGraph()
    G.add_nodes_from(ListeSommet)

    for u, v, cap in liaison:
        G.add_edge(u, v, weight=cap)

    pos = nx.spring_layout(G, seed=42)

    # Préparation des couleurs et labels
    node_colors = []
    labels = {}
    appro = {}

    if result and index_noeuds:
        for p in ['J', 'K', 'L']:
            flux = result.flow[index_noeuds[p], index_noeuds['super_puits']]
            appro[p] = flux

    for node in G.nodes:
        if node in appro:
            node_colors.append('lightgreen')
            labels[node] = f"{node}\n({appro[node]} u.)"
        else:
            node_colors.append('skyblue')
            labels[node] = node

    # Affichage du graphe
    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    if result:
        flot_maximal = result.flow_value
        plt.gcf().text(0.95, 0.05, f"Flot maximal : {flot_maximal} u.",
                    fontsize=12, color='darkred', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons avec Flot Maximal")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

result, index_noeuds = calculerFlotMaximal()

# Répartition sur les puits
for p in ['J', 'K', 'L']:
    flot_recu = result.flow[index_noeuds[p], index_noeuds['super_puits']]
    print(f"{p} reçoit : {flot_recu} u.")

# Affichage du graphe avec les données
afficherCarte(result=result, index_noeuds=index_noeuds)

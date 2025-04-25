import networkx as nx
import matplotlib.pyplot as plt
from data import *

def afficherCarte(result=None, index_noeuds=None, liaisons=None):
    # Par défaut, si aucune liaison n'est donnée, on utilise ListeLiaison
    if liaisons is None:
        liaisons = ListeLiaison
    
    # Créer le graphe dirigé
    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in ListeNoeuds])


    # Ajouter les arêtes avec leurs capacités
    for l in liaisons:
        u = l.depart
        v = l.arrivee
        cap = l.capacite
        G.add_edge(u, v, weight=cap)

    pos = nx.spring_layout(G, seed=42)

    # Préparation des couleurs et labels
    node_colors = []
    labels = {}
    appro = {}

    # Si le résultat et l'index des noeuds sont fournis
    if result and index_noeuds:
        # Calculer la répartition sur les puits
        for p in ['J', 'K', 'L']:
            flux = result.flow[index_noeuds[p], index_noeuds['super_puits']]
            appro[p] = flux

    # Affichage des nœuds et leurs labels
    for node in G.nodes:
        if node in appro:
            node_colors.append('lightgreen')  # Couleur pour les puits
            labels[node] = f"{node}\n({appro[node]} u.)"  # Afficher le flux reçu
        else:
            node_colors.append('skyblue')  # Autres nœuds
            labels[node] = node

    # Affichage du graphe
    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

    # Affichage des étiquettes des arêtes
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # Si un flot maximal est fourni, l'afficher
    if result:
        flot_maximal = result.flow_value
        plt.gcf().text(0.95, 0.05, f"Flot maximal : {flot_maximal} u.",
                    fontsize=12, color='darkred', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons avec Flot Maximal")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

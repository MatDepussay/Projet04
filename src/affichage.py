import networkx as nx
import matplotlib.pyplot as plt
from data import *

def afficherCarte(result=None, index_noeuds=None, liaisons=None):
    if liaisons is None:
        liaisons = ListeLiaison

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in ListeNoeuds])

    for l in liaisons:
        G.add_edge(l.depart, l.arrivee, weight=l.capacite)

    pos = nx.kamada_kawai_layout(G)

    node_colors = []
    labels = {}
    appro = {}
    sources = {}

    if result and index_noeuds:
        for p in ['J', 'K', 'L']:
            flux = result.flow[index_noeuds[p], index_noeuds['super_puits']]
            appro[p] = flux
        for s in ['A', 'B', 'C', 'D']:
            flux = result.flow[index_noeuds['super_source'], index_noeuds[s]]
            sources[s] = flux

    for node in G.nodes:
        if node in appro:
            node_colors.append('lightgreen')
            labels[node] = f"{node}\n({appro[node]} u.)"
        elif node in sources:
            node_colors.append('lightcoral')
            labels[node] = f"{node}\n({sources[node]} u.)"
        else:
            node_colors.append('skyblue')
            labels[node] = node

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

    # 👉 Création des étiquettes de flux sur les arêtes
    edge_labels = {}
    for u, v in G.edges:
        cap = G[u][v]['weight']
        if result and index_noeuds:
            try:
                flux = result.flow[index_noeuds[u], index_noeuds[v]]
                edge_labels[(u, v)] = f"{int(flux)} / {cap}"
            except KeyError:
                edge_labels[(u, v)] = f"0 / {cap}"
        else:
            edge_labels[(u, v)] = f"{cap}"

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    if result:
        flot_maximal = result.flow_value
        plt.gcf().text(0.95, 0.05, f"Flot maximal : {flot_maximal} u.",
                    fontsize=12, color='darkred', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons avec Flot Effectif sur les Arêtes")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def afficherCarteEnoncer(result=None, index_noeuds=None, liaisons=None):
    if liaisons is None:
        liaisons = ListeLiaison

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in ListeNoeuds])

    for l in liaisons:
        G.add_edge(l.depart, l.arrivee, weight=l.capacite)

    pos = nx.kamada_kawai_layout(G)

    node_colors = []
    labels = {}
    infos_noeuds = {n.nom: n for n in ListeNoeuds}

    for node in G.nodes:
        if node in ['A', 'B', 'C', 'D']:  # Sources
            cap = infos_noeuds[node].capaciteMax
            node_colors.append('lightcoral')
            labels[node] = f"{node}\n({cap} u.)"
        elif node in ['J', 'K', 'L']:  # Puits
            cap = infos_noeuds[node].capaciteMax
            node_colors.append('lightgreen')
            labels[node] = f"{node}\n({cap} u.)"
        else:  # Intermédiaires
            node_colors.append('skyblue')
            labels[node] = node

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

    # 👉 Afficher uniquement la capacité sur les arêtes
    edge_labels = {(u, v): f"{G[u][v]['weight']}" for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    if result:
        flot_maximal = result.flow_value
        plt.gcf().text(0.95, 0.05, f"Flot maximal : {flot_maximal} u.",
                    fontsize=12, color='darkred', ha='right', va='bottom',
                    bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    plt.title("Carte des Liaisons (Capacités maximales)")
    plt.axis('off')
    plt.tight_layout()
    plt.show()

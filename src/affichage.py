import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from data import *

def afficherCarte(result=None, index_noeuds=None, liaisons=None, frame=None):
    if liaisons is None:
        liaisons = ListeLiaison

    # Créer le graphe dirigé
    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in ListeNoeuds])

    for l in liaisons:
        u = l.depart
        v = l.arrivee
        cap = l.capacite
        G.add_edge(u, v, weight=cap)

    pos = nx.kamada_kawai_layout(G)

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

    # Supprimer anciens éléments du frame
    if frame:
        for widget in frame.winfo_children():
            widget.destroy()

    # Création d'une figure matplotlib
    fig = Figure(figsize=(7, 5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_title("Carte des Liaisons avec Flot Maximal")
    ax.axis("off")

    # Dessin avec NetworkX
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=1000, edgecolors='black')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20)
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=12, font_weight='bold')

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_color='red')

    if result:
        flot_maximal = result.flow_value
        ax.text(1.02, 0.02, f"Flot maximal : {flot_maximal} u.",
                transform=ax.transAxes, fontsize=12, color='darkred',
                bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    # Intégration dans Tkinter
    if frame:
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

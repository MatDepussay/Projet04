import networkx as nx
import matplotlib.pyplot as plt
from data import GestionReseau

reseau = GestionReseau()

def afficherCarte(result=None, index_noeuds=None, liaisons=None):
    """    
    Affiche une carte du réseau hydraulique en utilisant NetworkX et Matplotlib.

    Cette fonction trace les nœuds et les liaisons d’un graphe orienté représentant un réseau d’approvisionnement
    en eau. Si un flot a été calculé, les flux effectifs sont annotés sur les arêtes ainsi que les apports
    reçus par les villes et délivrés par les sources.


    Notes
        - Les nœuds de type **source** sont colorés en rouge clair avec leur contribution (u.).
        - Les nœuds de type **ville** sont colorés en vert clair avec leur réception (u.).
        - Les autres nœuds sont colorés en bleu ciel.
        - Les arêtes affichent les flux effectifs suivis de leur capacité maximale sous forme `flux / capacité`.

    Exemple
        >>> afficherCarte(result, index_noeuds, liaisons)
    """
    if liaisons is None:
        liaisons = reseau.ListeLiaisons

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in reseau.ListeNoeuds])

    for liaison in liaisons:
        G.add_edge(liaison.depart, liaison.arrivee, weight=liaison.capacite)

    pos = nx.kamada_kawai_layout(G)

    node_colors = []
    labels = {}
    appro = {}
    sources = {}
    
    # 🔍 Récupération dynamique des villes et sources
    villes = [n.nom for n in reseau.ListeNoeuds if n.type == "ville"]
    sources_liste = [n.nom for n in reseau.ListeNoeuds if n.type == "source"]

    if result and index_noeuds:
        for p in villes:
            if p in index_noeuds:
                flux = result.flow[index_noeuds[p], index_noeuds['super_puits']]
                appro[p] = int(flux)
        for s in sources_liste:
            if s in index_noeuds:
                flux = result.flow[index_noeuds['super_source'], index_noeuds[s]]
                sources[s] = int(flux)

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

    # ✅ NOUVEAU : créer la figure
    fig, ax = plt.subplots(figsize=(10, 7))

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20, ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold', ax=ax)

    edge_labels = {}
    for u, v in G.edges:
        cap = G[u][v]['weight']
        if result and index_noeuds:
            try:
                flux = int(result.flow[index_noeuds[u], index_noeuds[v]])
                edge_labels[(u, v)] = f"{int(flux)} / {cap}"
            except KeyError:
                edge_labels[(u, v)] = f"0 / {cap}"
        else:
            edge_labels[(u, v)] = f"{cap}"

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

    if result:
        ax.text(1.05, 0.05, f"Flot maximal : {result.flow_value} u.",
                fontsize=12, color='darkred', transform=ax.transAxes,
                bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    ax.set_title("Carte des Liaisons avec Flot Effectif sur les Arêtes")
    ax.axis('off')
    fig.tight_layout()

    return fig  # ✅ essentiel pour st.pyplot(fig)


def afficherCarteEnoncer(result=None, index_noeuds=None, liaisons=None):
    """
        Affiche une carte du réseau hydraulique en utilisant NetworkX et Matplotlib.

        Cette fonction trace les nœuds et les liaisons d’un graphe orienté représentant un réseau d’approvisionnement
        en eau.

    Notes
        - Les nœuds de type **source** sont colorés en rouge clair avec leur contribution (u.).
        - Les nœuds de type **ville** sont colorés en vert clair avec leur réception (u.).
        - Les autres nœuds sont colorés en bleu ciel.
        - Les arêtes affichent les flux effectifs suivis de leur capacité maximale sous forme `flux / capacité`.

    Exemple
        >>> afficherCarte(result, index_noeuds, liaisons)
    """
    if liaisons is None:
        liaisons = reseau.ListeLiaisons

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in reseau.ListeNoeuds])

    for liaison in liaisons:
        G.add_edge(liaison.depart, liaison.arrivee, weight=liaison.capacite)

    pos = nx.kamada_kawai_layout(G)

    node_colors = []
    labels = {}
    infos_noeuds = {n.nom: n for n in reseau.ListeNoeuds}

    for node in G.nodes:
        if node in infos_noeuds:
            noeud = infos_noeuds[node]
            cap = noeud.capaciteMax
            if noeud.type == "source":
                node_colors.append('lightcoral')
                labels[node] = f"{node}\n({cap} u.)"
            elif noeud.type == "ville" or noeud.type == "puits":
                # tu peux ajouter "puits" si tu veux le distinguer des villes
                node_colors.append('lightgreen')
                labels[node] = f"{node}\n({cap} u.)"
            else:  # intermediaire
                node_colors.append('skyblue')
                labels[node] = node
        else:
            # Noeud non reconnu dans infos_noeuds, couleur neutre
            node_colors.append('grey')
            labels[node] = node

    # ✅ Créer la figure et axes
    fig, ax = plt.subplots(figsize=(10, 7))

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1000, edgecolors='black', ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20, ax=ax)
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold', ax=ax)

    edge_labels = {(u, v): f"{G[u][v]['weight']}" for u, v in G.edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', ax=ax)

    if result:
        flot_maximal = result.flow_value
        ax.text(1.05, 0.05, f"Flot maximal : {flot_maximal} u.",
                fontsize=12, color='darkred', transform=ax.transAxes,
                bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'))

    ax.set_title("Carte des Liaisons (Capacités maximales)")
    ax.axis('off')
    fig.tight_layout()

    return fig  # ✅ Essentiel pour st.pyplot(fig)

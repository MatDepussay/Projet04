import networkx as nx
import matplotlib.pyplot as plt
from data import ReseauHydraulique


def afficherCarte(
    result=None, index_noeuds=None, noeuds=None, liaisons=None, montrer_saturees=False
):
    """
    Affiche une carte du réseau hydraulique en utilisant NetworkX et Matplotlib.

    Cette fonction trace les nœuds et les liaisons d’un graphe orienté représentant un réseau d’approvisionnement
    en eau. Si un flot a été calculé, les flux effectifs sont annotés sur les arêtes ainsi que les apports
    reçus par les villes et délivrés par les sources.

    Args:
        result: Résultat du calcul de flot (de maximum_flow).
        index_noeuds (dict): Dictionnaire nom -> index.
        noeuds (List[Noeud]): Liste des nœuds du réseau.
        liaisons (List[Liaison]): Liste des liaisons du réseau.
        montrer_saturees (bool): Si True, met en évidence les liaisons saturées.

    Notes
        - Les nœuds de type **source** sont colorés en rouge clair avec leur contribution (u.).
        - Les nœuds de type **ville** sont colorés en vert clair avec leur réception (u.).
        - Les autres nœuds sont colorés en bleu ciel.
        - Les arêtes affichent les flux effectifs suivis de leur capacité maximale sous forme `flux / capacité`.

    Returns
        >>> Matplotlib figure de la carte dessinée.
    Exemple
        >>> afficherCarte(result, index_noeuds, noeuds, liaisons, montrer_saturees=True)
    """
    if noeuds is None or liaisons is None:
        raise ValueError("Il faut fournir les noeuds et liaisons")

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in noeuds])
    infos_noeuds = {n.nom: n for n in noeuds}

    for liaison in liaisons:
        G.add_edge(liaison.depart, liaison.arrivee, weight=liaison.capacite)

    pos = nx.kamada_kawai_layout(G)
    node_colors = []
    labels = {}
    appro = {}
    sources = {}

    # Calcul des flux sources/villes si result est fourni
    if result:
        reseau_temp = ReseauHydraulique(noeuds, liaisons)
        index_noeuds = reseau_temp.index_noeuds

        for nom, noeud in infos_noeuds.items():
            if noeud.type == "ville":
                flux = result.flow[index_noeuds[nom], index_noeuds['super_puits']]
                appro[nom] = flux
            elif noeud.type == "source":
                flux = result.flow[index_noeuds['super_source'], index_noeuds[nom]]
                sources[nom] = flux

    # Couleurs et étiquettes des noeuds
    for node in G.nodes:
        n = infos_noeuds.get(node)
        if node in appro:
            node_colors.append('lightgreen')
            labels[node] = f"{node}\n({appro[node]} u.)"
        elif node in sources:
            node_colors.append('lightcoral')
            labels[node] = f"{node}\n({sources[node]} u.)"
        elif n:
            node_colors.append('skyblue')
            labels[node] = node
        else:
            node_colors.append('gray')
            labels[node] = node

    edges_normal = []
    edges_saturees = []

    # Détection des liaisons saturées
    saturees_set = set()
    if montrer_saturees and result:
        saturations = reseau_temp.liaisons_saturees(result=result)
        saturees_set = set((d, a) for d, a, _ in saturations)

    for u, v in G.edges:
        if (u, v) in saturees_set:
            edges_saturees.append((u, v))
        else:
            edges_normal.append((u, v))

    # Dessin du graphe
    fig, ax = plt.subplots(figsize=(10, 7))
    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=1000, edgecolors='black', ax=ax
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=edges_normal,
        edge_color='gray',
        arrows=True,
        arrowstyle='-|>',
        arrowsize=20,
        ax=ax,
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=edges_saturees,
        edge_color='red',
        width=3.5,
        arrows=True,
        arrowstyle='-|>',
        arrowsize=25,
        ax=ax,
    )
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold', ax=ax)

    # Étiquettes des arêtes
    edge_labels = {}
    for u, v in G.edges:
        cap = G[u][v]['weight']
        if result:
            try:
                flux = result.flow[index_noeuds[u], index_noeuds[v]]
                edge_labels[(u, v)] = f"{int(flux)} / {cap}"
            except KeyError:
                edge_labels[(u, v)] = f"0 / {cap}"
        else:
            edge_labels[(u, v)] = f"{cap}"

    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_color='red', ax=ax
    )

    # Flot maximal
    if result:
        fig.text(
            0.95,
            0.05,
            f"Flot maximal : {result.flow_value} u.",
            fontsize=12,
            color='darkred',
            ha='right',
            va='bottom',
            bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'),
        )

    ax.set_title(
        "Carte des Liaisons avec Flot Effectif sur les Arêtes"
        + (" (liaisons saturées en rouge)" if montrer_saturees else "")
    )
    ax.axis('off')
    fig.tight_layout()
    return fig


def afficherCarteEnoncer(result=None, index_noeuds=None, noeuds=None, liaisons=None):
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
        >>> afficherCarte(result, index_noeuds, noeuds, liaisons)
    """

    if noeuds is None or liaisons is None:
        raise ValueError("Il faut fournir les noeuds et liaisons")

    G = nx.DiGraph()
    G.add_nodes_from([n.nom for n in noeuds])

    for liaison in liaisons:
        G.add_edge(liaison.depart, liaison.arrivee, weight=liaison.capacite)

    pos = nx.kamada_kawai_layout(G)

    node_colors = []
    labels = {}
    infos_noeuds = {n.nom: n for n in noeuds}

    for node in G.nodes:
        n = infos_noeuds.get(node)
        if n is not None:
            if n.type == "source":
                node_colors.append('lightcoral')
                labels[node] = f"{node}\n({n.capaciteMax} u.)"
            elif n.type == "ville":
                node_colors.append('lightgreen')
                labels[node] = f"{node}\n({n.capaciteMax} u.)"
            else:
                node_colors.append('skyblue')
                labels[node] = node
        else:
            node_colors.append('skyblue')
            labels[node] = node

    fig, ax = plt.subplots(figsize=(10, 7))
    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=1000, edgecolors='black', ax=ax
    )
    nx.draw_networkx_edges(
        G, pos, edge_color='gray', arrows=True, arrowstyle='-|>', arrowsize=20, ax=ax
    )
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold', ax=ax)

    edge_labels = {(u, v): f"{G[u][v]['weight']}" for u, v in G.edges}
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_color='red', ax=ax
    )

    if result:
        flot_maximal = result.flow_value
        fig.text(
            0.95,
            0.05,
            f"Flot maximal : {flot_maximal} u.",
            fontsize=12,
            color='darkred',
            ha='right',
            va='bottom',
            bbox=dict(facecolor='white', edgecolor='darkred', boxstyle='round,pad=0.3'),
        )

    ax.set_title("Carte des Liaisons (Capacités maximales)")
    ax.axis('off')
    fig.tight_layout()
    return fig

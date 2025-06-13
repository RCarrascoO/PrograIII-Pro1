import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

def hierarchy_pos(G, root, width=1.0, vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None):
    """
    Recursively positions nodes in a hierarchy (tree layout).
    """
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    children = list(G.successors(root))
    if len(children) != 0:
        dx = width / len(children)
        nextx = xcenter - width / 2 - dx / 2
        for child in children:
            nextx += dx
            pos = hierarchy_pos(G, child, width=dx, vert_gap=vert_gap,
                                vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root)
    return pos

def avl_visualizer(avl_root):
    """
    Visualiza un árbol AVL como árbol jerárquico en Streamlit.
    """
    G = nx.DiGraph()
    def add_nodes(node):
        if node:
            G.add_node(node.key)
            if node.left:
                G.add_edge(node.key, node.left.key)
                add_nodes(node.left)
            if node.right:
                G.add_edge(node.key, node.right.key)
                add_nodes(node.right)
    add_nodes(avl_root)

    if G.number_of_nodes() > 0:
        root = avl_root.key
        pos = hierarchy_pos(G, root)
        plt.figure(figsize=(12, 6))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue',
                font_size=10, font_weight='bold', arrows=False)
        st.pyplot(plt)
    else:
        st.warning("AVL tree is empty")
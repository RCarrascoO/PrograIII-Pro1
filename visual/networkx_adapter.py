import networkx as nx
import matplotlib.pyplot as plt
from model import Graph

class NetworkXAdapter:
    @staticmethod
    def to_networkx(graph):
        nx_graph = nx.Graph()
        for vertex in graph.vertices():
            node_type = graph.get_node_type(vertex)
            nx_graph.add_node(str(vertex), type=node_type)
        for edge in graph.edges():
            u, v = edge.endpoints()
            nx_graph.add_edge(str(u), str(v), weight=edge.element())
        return nx_graph

    @staticmethod
    def draw_graph(graph, highlight_path=None, pos=None):
        nx_graph = NetworkXAdapter.to_networkx(graph)

        # Configurar colores según tipo de nodo
        node_colors = []
        for node in nx_graph.nodes():
            node_type = nx_graph.nodes[node]['type']
            if node_type == 'warehouse':
                node_colors.append('lightgreen')
            elif node_type == 'recharge':
                node_colors.append('lightblue')
            else:
                node_colors.append('pink')

        # Usar el layout proporcionado o calcular uno nuevo si no hay
        if pos is None:
            pos = nx.spring_layout(nx_graph, seed=42)

        # Dibuja todos los nodos y aristas en color base
        nx.draw_networkx_nodes(nx_graph, pos, node_color=node_colors)
        nx.draw_networkx_labels(nx_graph, pos)
        nx.draw_networkx_edges(nx_graph, pos, edge_color='gray', width=1)

        # Resaltar ruta si se especifica
        if highlight_path and len(highlight_path) > 1:
            # Convierte todos los nodos de la ruta a string
            path_edges = [
                (str(highlight_path[i]), str(highlight_path[i+1]))
                for i in range(len(highlight_path)-1)
            ]
            nx.draw_networkx_edges(
                nx_graph, pos, edgelist=path_edges,
                edge_color='r', width=3
            )

        plt.tight_layout()
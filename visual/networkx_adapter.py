import networkx as nx
import matplotlib.pyplot as plt
from model.graph_base import Graph

class NetworkXAdapter:
    @staticmethod
    def draw_graph(graph, highlight_path=None):
        nx_graph = nx.Graph()
        
        # Agregar nodos con atributos de tipo
        for vertex in graph.vertices():
            node_type = graph.get_node_type(vertex)
            nx_graph.add_node(str(vertex), type=node_type)
        
        # Agregar aristas
        for edge in graph.edges():
            u, v = edge.endpoints()
            nx_graph.add_edge(str(u), str(v), weight=edge.element())
        
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
        
        # Dibujar el grafo
        pos = nx.spring_layout(nx_graph)
        nx.draw(nx_graph, pos, with_labels=True, node_color=node_colors)
        
        # Resaltar ruta si se especifica
        if highlight_path:
            path_edges = [(str(highlight_path[i]), str(highlight_path[i+1])) 
                         for i in range(len(highlight_path)-1)]
            nx.draw_networkx_edges(nx_graph, pos, edgelist=path_edges, 
                                 edge_color='r', width=2)
        
        plt.show()
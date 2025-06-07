import random
from model.graph_base import Graph

class SimulationInitializer:
    @staticmethod
    def create_connected_graph(n_nodes, m_edges):
        """Crea un grafo conexo con roles asignados"""
        if m_edges < n_nodes - 1:
            raise ValueError("Aristas insuficientes para grafo conexo")
        
        g = Graph()
        nodes = []
        
        # Crear nodos con roles
        n_warehouses = int(n_nodes * 0.2)
        n_recharge = int(n_nodes * 0.2)
        n_clients = n_nodes - n_warehouses - n_recharge
        
        # Agregar nodos de almacenamiento
        for i in range(n_warehouses):
            node = g.insert_vertex(f"Warehouse_{i}", "warehouse")
            nodes.append(node)
        
        # Agregar nodos de recarga
        for i in range(n_recharge):
            node = g.insert_vertex(f"Recharge_{i}", "recharge")
            nodes.append(node)
        
        # Agregar nodos cliente
        for i in range(n_clients):
            node = g.insert_vertex(f"Client_{i}", "client")
            nodes.append(node)
        
        # Conectar el grafo para asegurar conexidad
        for i in range(1, n_nodes):
            weight = random.randint(1, 10)
            g.insert_edge(nodes[i-1], nodes[i], weight)
        
        # Agregar aristas adicionales aleatorias
        for _ in range(m_edges - (n_nodes - 1)):
            u, v = random.sample(nodes, 2)
            weight = random.randint(1, 10)
            if not g.get_edge(u, v):
                g.insert_edge(u, v, weight)
        
        return g
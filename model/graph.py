class Graph:
    """
    Implementación del grafo para representar la red de distribución de drones
    """
    
    def __init__(self):
        """
        Inicializa un nuevo grafo
        """
        self.vertices = set()  # Conjunto de vértices
        self.edges = []  # Lista de aristas con pesos (u, v, weight)
        self.adjacency_list = {}  # Lista de adyacencia {u: [(v, weight), ...]}
    
    def add_vertex(self, vertex):
        """
        Añade un vértice al grafo
        
        Args:
            vertex: ID del vértice a añadir
        """
        if vertex not in self.vertices:
            self.vertices.add(vertex)
            self.adjacency_list[vertex] = []
    
    def add_edge(self, u, v, weight):
        """
        Añade una arista al grafo
        
        Args:
            u: Vértice origen
            v: Vértice destino
            weight: Peso de la arista
        """
        # Asegurar que los vértices existen
        self.add_vertex(u)
        self.add_vertex(v)
        
        # Añadir la arista a la lista de adyacencia (grafo no dirigido)
        self.adjacency_list[u].append((v, weight))
        self.adjacency_list[v].append((u, weight))
        
        # Añadir a la lista de aristas
        self.edges.append((u, v, weight))
    
    def get_adjacents(self, vertex):
        """
        Obtiene los vértices adyacentes a un vértice dado
        
        Args:
            vertex: Vértice de origen
            
        Returns:
            Lista de tuplas (vértice_adyacente, peso)
        """
        if vertex in self.adjacency_list:
            return self.adjacency_list[vertex]
        return []
    
    def get_edge_weight(self, u, v):
        """
        Obtiene el peso de la arista entre dos vértices
        
        Args:
            u: Vértice origen
            v: Vértice destino
            
        Returns:
            Peso de la arista o None si no existe
        """
        for vertex, weight in self.adjacency_list.get(u, []):
            if vertex == v:
                return weight
        return None
import heapq
from typing import List, Dict, Tuple, Optional

class DijkstraRouter:
    """
    Implementación del algoritmo de Dijkstra para encontrar rutas más cortas
    """
    
    def __init__(self, graph):
        self.graph = graph
        self.adjacency_list = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> Dict:
        """Construye lista de adyacencia para Dijkstra"""
        adj_list = {}
        
        # Inicializar todos los nodos
        for vertex in self.graph.vertices():
            adj_list[vertex] = []
        
        # Agregar aristas con pesos
        for edge in self.graph.edges():
            u, v = edge.endpoints()
            weight = edge.element()
            
            # Grafo no dirigido - agregar en ambas direcciones
            adj_list[u].append((v, weight))
            adj_list[v].append((u, weight))
        
        return adj_list
    
    def find_shortest_path(self, start, end) -> Optional[Tuple[List, float]]:
        """
        Encuentra la ruta más corta entre dos nodos usando Dijkstra
        
        Returns:
            Tupla (path, distance) o None si no hay ruta
        """
        if start not in self.adjacency_list or end not in self.adjacency_list:
            return None
        
        if start == end:
            return ([start], 0.0)
        
        # Inicializar distancias y predecesores
        distances = {node: float('inf') for node in self.adjacency_list}
        predecessors = {node: None for node in self.adjacency_list}
        visited = set()
        
        distances[start] = 0
        
        # Cola de prioridad: (distancia, contador_único, nodo)
        # El contador_único evita comparaciones entre nodos
        pq = [(0, 0, start)]
        counter = 1
        
        while pq:
            current_dist, _, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Si llegamos al destino, reconstruir ruta
            if current_node == end:
                path = self._reconstruct_path(predecessors, start, end)
                return (path, distances[end])
            
            # Explorar vecinos
            for neighbor, weight in self.adjacency_list[current_node]:
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        predecessors[neighbor] = current_node
                        heapq.heappush(pq, (new_dist, counter, neighbor))
                        counter += 1
        
        return None
    
    def _reconstruct_path(self, predecessors: Dict, start, end) -> List:
        """Reconstruye la ruta desde los predecesores"""
        path = []
        current = end
        
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        path.reverse()
        return path
    
    def find_shortest_paths_from_source(self, start) -> Dict:
        """
        Encuentra las rutas más cortas desde un nodo fuente a todos los demás
        
        Args:
            start: Nodo fuente
            
        Returns:
            Diccionario {nodo_destino: (path, distance)}
        """
        if start not in self.adjacency_list:
            return {}
        
        # Inicializar distancias y predecesores
        distances = {node: float('inf') for node in self.adjacency_list}
        predecessors = {node: None for node in self.adjacency_list}
        visited = set()
        
        distances[start] = 0
        
        # Cola de prioridad con contador único
        pq = [(0, 0, start)]
        counter = 1
        
        while pq:
            current_dist, _, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Explorar vecinos
            for neighbor, weight in self.adjacency_list[current_node]:
                if neighbor not in visited:
                    new_dist = current_dist + weight
                    
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        predecessors[neighbor] = current_node
                        heapq.heappush(pq, (new_dist, counter, neighbor))
                        counter += 1
        
        # Construir rutas para todos los nodos alcanzables
        results = {}
        for end_node in self.adjacency_list:
            if distances[end_node] != float('inf'):
                path = self._reconstruct_path(predecessors, start, end_node)
                results[end_node] = (path, distances[end_node])
        
        return results
    
    def get_distance_matrix(self) -> Dict[Tuple, float]:
        """
        Calcula matriz de distancias entre todos los pares de nodos
        
        Returns:
            Diccionario {(origen, destino): distancia}
        """
        distance_matrix = {}
        
        for start_node in self.adjacency_list:
            paths = self.find_shortest_paths_from_source(start_node)
            
            for end_node, (path, distance) in paths.items():
                distance_matrix[(start_node, end_node)] = distance
        
        return distance_matrix
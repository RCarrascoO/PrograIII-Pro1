import heapq
import numpy as np
from math import inf

def dijkstra(graph, start_vertex):
    """
    Implementa el algoritmo de Dijkstra para encontrar la ruta más corta desde un nodo origen
    
    Args:
        graph: Grafo con nodos y aristas con pesos
        start_vertex: Vértice de inicio
        
    Returns:
        Diccionario con distancias mínimas y diccionario de predecesores
    """
    distances = {vertex: float('infinity') for vertex in graph.vertices}
    distances[start_vertex] = 0
    predecessors = {vertex: None for vertex in graph.vertices}
    pq = [(0, start_vertex)]
    
    while pq:
        current_distance, current_vertex = heapq.heappop(pq)
        
        if current_distance > distances[current_vertex]:
            continue
        
        for neighbor, weight in graph.get_adjacents(current_vertex):
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))
    
    return distances, predecessors

def reconstruct_path(start, end, predecessors):
    """
    Reconstruye la ruta desde el origen hasta el destino usando el diccionario de predecesores
    
    Args:
        start: Vértice de inicio
        end: Vértice final
        predecessors: Diccionario de predecesores
        
    Returns:
        Lista con la secuencia de vértices que forman la ruta
    """
    path = []
    current = end
    
    while current != start:
        path.append(current)
        current = predecessors[current]
        if current is None:
            return []  # No hay ruta
    
    path.append(start)
    return path[::-1]  # Invertir para obtener ruta desde start a end

def floyd_warshall(graph):
    """
    Implementa el algoritmo de Floyd-Warshall para encontrar todas las rutas mínimas
    
    Args:
        graph: Grafo con nodos y aristas con pesos
        
    Returns:
        Matriz de distancias y matriz de predecesores
    """
    # Preparar el mapeo de vértices a índices
    vertices = list(graph.vertices)
    n = len(vertices)
    vertex_to_index = {vertices[i]: i for i in range(n)}
    
    # Inicializar matrices
    distances = np.full((n, n), inf)
    predecessors = np.full((n, n), None, dtype=object)
    
    # Configurar valores iniciales
    for i in range(n):
        distances[i, i] = 0
    
    # Agregar aristas
    for u in graph.vertices:
        for v, weight in graph.get_adjacents(u):
            u_idx = vertex_to_index[u]
            v_idx = vertex_to_index[v]
            distances[u_idx, v_idx] = weight
            predecessors[u_idx, v_idx] = u
    
    # Algoritmo principal
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distances[i, j] > distances[i, k] + distances[k, j]:
                    distances[i, j] = distances[i, k] + distances[k, j]
                    predecessors[i, j] = predecessors[k, j]
    
    return distances, predecessors, vertex_to_index, vertices
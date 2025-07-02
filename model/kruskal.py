def kruskal_mst(graph):
    """
    Implementa el algoritmo de Kruskal para encontrar el MST
    
    Args:
        graph: Grafo con nodos y aristas con pesos
        
    Returns:
        Lista de aristas que forman el MST
    """
    # Ordenar aristas por peso
    edges = []
    for u in graph.vertices:
        for v, weight in graph.get_adjacents(u):
            if (v, u, weight) not in edges:  # Evitar duplicados (grafo no dirigido)
                edges.append((u, v, weight))
    edges.sort(key=lambda x: x[2])  # Ordenar por peso (tercer elemento)
    
    # Inicializar estructuras para Union-Find
    parent = {}
    rank = {}
    for vertex in graph.vertices:
        parent[vertex] = vertex
        rank[vertex] = 0
    
    # Función para encontrar el representante de un conjunto
    def find(vertex):
        if parent[vertex] != vertex:
            parent[vertex] = find(parent[vertex])
        return parent[vertex]
    
    # Función para unir dos conjuntos
    def union(vertex1, vertex2):
        root1 = find(vertex1)
        root2 = find(vertex2)
        if root1 != root2:
            if rank[root1] < rank[root2]:
                parent[root1] = root2
            else:
                parent[root2] = root1
                if rank[root1] == rank[root2]:
                    rank[root1] += 1
    
    # Construir MST
    mst = []
    for u, v, weight in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, weight))
    
    return mst
from collections import deque
import random
from AVL_base import Node, insert, pre_order
from graph_base import Graph
from vertex_base import Vertex
from edge_base import Edge

class RouteManager:
    def __init__(self, graph, battery_limit=50):
        self.graph = graph
        self.battery_limit = battery_limit
        self.recharge_stations = set()

    def add_recharge_station(self, vertex):
        """Agrega una estación de recarga al grafo"""
        self.recharge_stations.add(vertex)

    def find_nearest_recharge(self, current_vertex, visited):
        """Encuentra la estación de recarga más cercana usando BFS"""
        queue = deque([(current_vertex, [current_vertex])])
        visited_recharge = set()

        while queue:
            vertex, path = queue.popleft()
            if vertex in self.recharge_stations:
                return path

            for neighbor in self.graph.neighbors(vertex):
                if neighbor not in visited_recharge:
                    visited_recharge.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))
        return None

    def find_route(self, start, end):
        """BFS modificado que considera el límite de batería y estaciones de recarga"""
        queue = deque()
        queue.append((start, [start], 0))  # (vertex, path, current_battery)
        visited = set()

        while queue:
            current_vertex, path, current_battery = queue.popleft()

            if current_vertex == end:
                return path

            if current_vertex not in visited:
                visited.add(current_vertex)

                for neighbor in self.graph.neighbors(current_vertex):
                    edge = self.graph.get_edge(current_vertex, neighbor)
                    edge_cost = edge.element() if edge else 1

                    if current_battery + edge_cost <= self.battery_limit:
                        queue.append((neighbor, path + [neighbor], current_battery + edge_cost))
                    else:
                        recharge_path = self.find_nearest_recharge(current_vertex, visited)
                        if recharge_path:
                            full_path = path[:-1] + recharge_path
                            queue.append((recharge_path[-1], full_path + [neighbor], edge_cost))
        return None

class RouteTracker:
    def __init__(self):
        self.route_frequency = {}
        self.node_visits = {}
        self.route_costs = {}

    def register_route(self, route_path, cost):
        """Registra una ruta en las estadísticas"""
        route_str = "->".join(str(v.element()) if hasattr(v, 'element') else str(v) for v in route_path)
        
        self.route_frequency[route_str] = self.route_frequency.get(route_str, 0) + 1
        self.route_costs[route_str] = cost
        
        for node in route_path:
            node_str = str(node.element()) if hasattr(node, 'element') else str(node)
            self.node_visits[node_str] = self.node_visits.get(node_str, 0) + 1

    def get_most_frequent_routes(self, top_n=None):
        """Retorna las N rutas más utilizadas"""
        sorted_routes = sorted(self.route_frequency.items(), key=lambda x: x[1], reverse=True)
        
        if top_n is None:
            return [(route, freq, self.route_costs[route]) for route, freq in sorted_routes]
        try:
            top_n_int = int(top_n)
            return [(route, freq, self.route_costs[route]) for route, freq in sorted_routes[:top_n_int]]
        except (ValueError, TypeError):
            return [(route, freq, self.route_costs[route]) for route, freq in sorted_routes]

    def get_node_visit_stats(self):
        """Estadísticas de visitas por nodo"""
        return sorted(self.node_visits.items(), key=lambda x: x[1], reverse=True)

    def create_custom_hashmap(self, initial_size=10):
        """Implementa un HashMap básico usando listas"""
        class HashMap:
            def __init__(self, size):
                self.size = size
                self.buckets = [[] for _ in range(size)]
            
            def _hash(self, key):
                return hash(key) % self.size
            
            def put(self, key, value):
                h = self._hash(key)
                bucket = self.buckets[h]
                for i, (k, v) in enumerate(bucket):
                    if k == key:
                        bucket[i] = (key, value)
                        return
                bucket.append((key, value))
            
            def get(self, key):
                h = self._hash(key)
                bucket = self.buckets[h]
                for k, v in bucket:
                    if k == key:
                        return v
                return None
            
            def __str__(self):
                return str(self.buckets)
        
        return HashMap(initial_size)

class RouteOptimizer:
    def __init__(self, route_tracker, route_manager):
        self.tracker = route_tracker
        self.manager = route_manager
        self.optimization_reports = []

    def suggest_optimized_route(self, origin_id, destination_id):
        """Sugiere ruta basada en patrones históricos"""
        origin = Vertex(origin_id) if not isinstance(origin_id, Vertex) else origin_id
        destination = Vertex(destination_id) if not isinstance(destination_id, Vertex) else destination_id
        
        # 1. Buscar ruta exacta frecuente
        all_routes = self.tracker.get_most_frequent_routes()
        for route_str, freq, cost in all_routes:
            nodes_str = route_str.split('->')
            if nodes_str[0] == str(origin.element()) and nodes_str[-1] == str(destination.element()):
                # Reconstruir la ruta con objetos Vertex
                route_vertices = []
                for node_name in nodes_str:
                    route_vertices.append(Vertex(node_name))
                self.optimization_reports.append(f"Usando ruta frecuente: {route_str}")
                return route_vertices, cost
        
        # 2. Buscar segmentos parciales
        for route_str, freq, cost in all_routes:
            nodes_str = route_str.split('->')
            if str(origin.element()) in nodes_str and str(destination.element()) in nodes_str:
                idx_origin = nodes_str.index(str(origin.element()))
                idx_dest = nodes_str.index(str(destination.element()))
                if idx_origin < idx_dest:
                    segment_str = nodes_str[idx_origin:idx_dest+1]
                    segment_vertices = [Vertex(node) for node in segment_str]
                    self.optimization_reports.append(f"Usando segmento de ruta frecuente: {'->'.join(segment_str)}")
                    return segment_vertices, sum(1 for _ in segment_str) - 1
        
        # 3. Calcular nueva ruta
        new_route = self.manager.find_route(origin, destination)
        if new_route:
            cost = len(new_route) - 1  # Costo estimado (1 por cada arista)
            route_str = "->".join(str(v.element()) for v in new_route)
            self.tracker.register_route(new_route, cost)
            self.optimization_reports.append(f"Nueva ruta calculada: {route_str}")
            return new_route, cost
        
        return None, 0

    def analyze_route_patterns(self):
        """Analiza patrones en las rutas más frecuentes"""
        frequent_routes = self.tracker.get_most_frequent_routes(5)
        node_stats = self.tracker.get_node_visit_stats()
        
        patterns = {
            'top_routes': frequent_routes,
            'top_nodes': node_stats,
            'observations': []
        }
        
        for route, freq, cost in frequent_routes:
            if any('R' in node for node in route.split('->')):
                patterns['observations'].append("Las rutas frecuentes suelen incluir estaciones de recarga")
                break
        
        if node_stats and node_stats[0][1] > sum(v for k, v in node_stats[1:]):
            patterns['observations'].append(f"El nodo {node_stats[0][0]} es el más visitado con diferencia")
        
        return patterns

    def get_optimization_report(self):
        """Genera reporte de optimizaciones aplicadas"""
        return "\n".join(self.optimization_reports)

class OrderSimulator:
    def __init__(self, graph, battery_limit=50):
        self.graph = graph
        self.route_manager = RouteManager(graph, battery_limit)
        self.route_tracker = RouteTracker()
        self.route_optimizer = RouteOptimizer(self.route_tracker, self.route_manager)
        self.warehouses = set()
        self.clients = set()
    
    def add_warehouse(self, vertex):
        self.warehouses.add(vertex)
    
    def add_client(self, vertex):
        self.clients.add(vertex)
    
    def process_orders(self, num_orders=10):
        """Simula procesamiento de órdenes de entrega"""
        if not self.warehouses or not self.clients:
            print("Error: No hay almacenes o clientes definidos")
            return
        
        for i in range(1, num_orders+1):
            origin = random.choice(list(self.warehouses))
            destination = random.choice(list(self.clients))
            
            print(f"\nOrden #{i}: {origin} → {destination}")
            
            route, cost = self.route_optimizer.suggest_optimized_route(origin, destination)
            
            if route:
                route_str = " → ".join(str(v) for v in route)
                recharge_stops = [str(v) for v in route if v in self.route_manager.recharge_stations]
                
                print(f"Ruta: {route_str}")
                print(f"Costo: {cost} | Paradas de recarga {recharge_stops} | Estado: Entregado")
                
                self.route_tracker.register_route(route, cost)
            else:
                print("No se pudo encontrar una ruta válida")

if __name__ == "__main__":
    # Crear grafo de ejemplo
    g = Graph()
    
    # Crear vértices
    a = g.insert_vertex("Almacen_A")
    b = g.insert_vertex("B")
    c = g.insert_vertex("C")
    d = g.insert_vertex("D")
    r1 = g.insert_vertex("R1")
    client_x = g.insert_vertex("Client_X")
    client_y = g.insert_vertex("Client_Y")
    
    # Crear aristas con costos
    g.insert_edge(a, b, 10)
    g.insert_edge(b, c, 15)
    g.insert_edge(c, client_x, 20)
    g.insert_edge(a, r1, 5)
    g.insert_edge(r1, b, 10)
    g.insert_edge(b, d, 5)
    g.insert_edge(d, client_y, 10)
    
    # Configurar simulador
    simulator = OrderSimulator(g, battery_limit=25)
    simulator.add_warehouse(a)
    simulator.add_client(client_x)
    simulator.add_client(client_y)
    simulator.route_manager.add_recharge_station(r1)
    
    # Procesar órdenes
    simulator.process_orders(5)
    
    # Mostrar estadísticas
    print("\nEstadísticas:")
    print("Rutas más frecuentes:")
    for route, freq, cost in simulator.route_tracker.get_most_frequent_routes(3):
        print(f"- {route}: {freq} veces (costo: {cost})")
    
    print("\nNodos más visitados:")
    for node, visits in simulator.route_tracker.get_node_visit_stats()[:3]:
        print(f"- {node}: {visits} visitas")
    
    print("\nReporte de optimización:")
    print(simulator.route_optimizer.get_optimization_report())
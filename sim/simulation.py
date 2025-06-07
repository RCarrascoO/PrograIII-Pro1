import random
from collections import deque
from tda.AVL_base import AVL
from tda.hash_map import HashMap
from domain.route import Route
from domain.order import Order
from datetime import datetime, timedelta

class Simulation:
    def __init__(self, graph):
        self.graph = graph
        self.route_avl = AVL()  # AVL para rutas frecuentes
        self.orders_map = HashMap()  # Mapa de órdenes
        self.active_orders = []
        self.completed_orders = []
        self.battery_limit = 50
        self.recharge_stations = [v for v in self.graph.vertices() 
                                if self.graph.get_node_type(v) == 'recharge']
    
    def generate_order(self, origin=None, destination=None, priority=None):
        """Genera una nueva orden con parámetros opcionales o aleatorios"""
        order_id = f"ORD_{len(self.orders_map) + 1}"
        
        warehouses = [v for v in self.graph.vertices() 
                    if self.graph.get_node_type(v) == 'warehouse']
        clients = [v for v in self.graph.vertices() 
                 if self.graph.get_node_type(v) == 'client']
        
        origin = origin or random.choice(warehouses)
        destination = destination or random.choice(clients)
        priority = priority or random.randint(1, 5)
        
        new_order = Order(order_id, origin, destination, priority)
        self.active_orders.append(new_order)
        self.orders_map.put(order_id, new_order)
        return new_order
    
    def process_orders(self, n_orders=10):
        """Procesa un lote de órdenes"""
        for _ in range(n_orders):
            self.generate_order()
        
        for order in self.active_orders[:]:
            route = self.find_route_with_recharge(order.origin, order.destination)
            if route:
                self._register_route(route)
                order.complete(route.cost)
                self.completed_orders.append(order)
                self.active_orders.remove(order)
    
    def _register_route(self, route):
        """Registra una ruta en el AVL y actualiza frecuencias"""
        route_str = route.path_str()
        existing = self.route_avl.search(route_str)
        
        if existing:
            existing.value.increment_frequency()
        else:
            self.route_avl.insert(route_str, route)
    
    def find_route_with_recharge(self, start, end):
        """BFS modificado que considera estaciones de recarga"""
        queue = deque()
        queue.append((start, [start], 0))  # (current, path, battery_used)
        visited = set()
        
        while queue:
            current, path, battery_used = queue.popleft()
            
            if current == end:
                return Route(path, battery_used)
            
            if current not in visited:
                visited.add(current)
                
                for neighbor in self.graph.neighbors(current):
                    edge = self.graph.get_edge(current, neighbor)
                    edge_cost = edge.element()
                    new_battery = battery_used + edge_cost
                    
                    if new_battery <= self.battery_limit:
                        queue.append((neighbor, path + [neighbor], new_battery))
                    else:
                        # Buscar ruta a estación de recarga más cercana
                        recharge_path = self._find_path_to_recharge(current, visited)
                        if recharge_path:
                            full_path = path[:-1] + recharge_path
                            last_node = recharge_path[-1]
                            queue.append((last_node, full_path + [neighbor], edge_cost))
        return None
    
    def _find_path_to_recharge(self, current, visited):
        """BFS para encontrar la estación de recarga más cercana"""
        queue = deque()
        queue.append((current, [current]))
        local_visited = set(visited)
        
        while queue:
            node, path = queue.popleft()
            
            if node in self.recharge_stations:
                return path
            
            if node not in local_visited:
                local_visited.add(node)
                
                for neighbor in self.graph.neighbors(node):
                    if neighbor not in local_visited:
                        queue.append((neighbor, path + [neighbor]))
        return None
    
    def get_most_frequent_routes(self, n=5):
        """Obtiene las n rutas más frecuentes"""
        return self.route_avl.get_most_frequent(n)
    
    def get_node_visit_stats(self):
        """Estadísticas de visitas por nodo"""
        node_stats = {}
        
        def process_route(node):  # 👈 Aceptar nodo completo
            route = node.value    # 👈 Extraer el valor tipo Route
            for v in route.path:
                v_str = str(v)
                node_stats[v_str] = node_stats.get(v_str, 0) + 1

        self.route_avl.inorder_traversal(process_route)
        return sorted(node_stats.items(), key=lambda x: x[1], reverse=True)

import random
from collections import deque
from tda.AVL_base import AVL
from tda.hash_map import HashMap
from domain.client import Client
from domain.order import Order
from domain.route import Route
from sim.dijkstra import DijkstraRouter  # 👈 NUEVA IMPORTACIÓN

class Simulation:
    def __init__(self, graph):
        self.graph = graph
        self.clients = []
        self.route_avl = AVL()  # AVL para rutas frecuentes
        self.orders_map = HashMap()  # Mapa de órdenes
        self.active_orders = []
        self.completed_orders = []
        self.battery_limit = 50
        self.recharge_stations = [v for v in self.graph.vertices() 
                                if self.graph.get_node_type(v) == 'recharge']
        
        # 👈 NUEVA LÍNEA: Inicializar router de Dijkstra
        self.dijkstra_router = DijkstraRouter(graph)
    
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
    
    def generate_clients(self, client_id=None, name=None, type_=None, total_orders=0):
        """Genera un nuevo cliente con parámetros opcionales o aleatorios"""
        if client_id is None:
            client_id = f"CLI_{len(self.clients) + 1}"
        
        if name is None:
            names = ["Juan Pérez", "María González", "Pedro Rodríguez", "Ana Martínez"]
            name = random.choice(names)
        
        if type_ is None:
            types = ["premium", "standard", "basic"]
            type_ = random.choice(types)
        
        client = Client(client_id, name, type_, total_orders)
        self.clients.append(client)
        return client
    
    def process_orders(self, n_orders=10):
        """Procesa un lote de órdenes"""
        for _ in range(n_orders):
            self.generate_order()
    
    def _register_route(self, route):
        """Registra una ruta en el AVL y actualiza frecuencias"""
        route_str = route.path_str()
        existing = self.route_avl.search(route_str)
        
        if existing:
            existing.value.increment_frequency()
        else:
            self.route_avl.insert(route_str, route)
    
    # 👈 NUEVA FUNCIÓN: Reemplaza find_route_with_recharge con Dijkstra
    def find_route_with_recharge(self, start, end):
        """Encuentra ruta usando Dijkstra con consideración de batería"""
        # Primero intentar ruta directa con Dijkstra
        result = self.dijkstra_router.find_shortest_path(start, end)
        
        if result:
            path, cost = result
            
            # Verificar si la ruta es factible con batería
            if self._is_route_feasible(path, cost):
                route = Route(path, cost)
                self._register_route(route)
                return route
            else:
                # Si no es factible, buscar ruta con recarga
                return self._find_route_with_recharge_dijkstra(start, end)
        
        return None
    
    def _is_route_feasible(self, path, cost):
        """Verifica si la ruta es factible con la batería disponible"""
        return cost <= self.battery_limit
    
    def _find_route_with_recharge_dijkstra(self, start, end):
        """Busca ruta con recarga usando Dijkstra"""
        best_route = None
        best_cost = float('inf')
        
        # Probar cada estación de recarga
        for recharge_station in self.recharge_stations:
            # Ruta: start -> recharge_station -> end
            
            # Primera parte: start -> recharge_station
            result1 = self.dijkstra_router.find_shortest_path(start, recharge_station)
            if not result1:
                continue
                
            path1, cost1 = result1
            if not self._is_route_feasible(path1, cost1):
                continue
            
            # Segunda parte: recharge_station -> end
            result2 = self.dijkstra_router.find_shortest_path(recharge_station, end)
            if not result2:
                continue
                
            path2, cost2 = result2
            if not self._is_route_feasible(path2, cost2):
                continue
            
            # Combinar rutas
            combined_path = path1 + path2[1:]  # Evitar duplicar recharge_station
            combined_cost = cost1 + cost2
            
            if combined_cost < best_cost:
                best_cost = combined_cost
                best_route = Route(combined_path, combined_cost)
        
        if best_route:
            self._register_route(best_route)
        
        return best_route
    
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
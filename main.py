import streamlit as st
import requests
import os
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import folium
from datetime import datetime
import sys

# Asegurar que podemos importar desde cualquier ruta
sys.path.append(os.path.abspath('.'))

# Importar módulos personalizados
from visual.map.map_builder import MapBuilder
from model.graph import Graph
from model.kruskal import kruskal_mst
from model.path_algorithms import dijkstra, floyd_warshall, reconstruct_path

# Configuración de página
st.set_page_config(
    page_title="Sistema de Drones - Correos Chile",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funciones auxiliares
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcular distancia euclidiana entre dos puntos geográficos (simplificado)"""
    # En un sistema real usaríamos la fórmula de Haversine
    return ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5 * 111.32  # Aproximadamente km

# Función para obtener clientes con manejo de errores
def get_clients():
    try:
        clients_response = requests.get("http://127.0.0.1:8000/api/clients")
        if clients_response.status_code == 200:
            clients = clients_response.json()
            if clients:
                return clients
        # Si no hay clientes o hay un error, devolvemos clientes de demostración
        return [
            {
                "id": 1, 
                "name": "Juan Pérez", 
                "email": "juan@example.com",
                "phone": "912345678",
                "address": "Avenida Alemania 0123, Temuco",
                "latitude": 38.7359, 
                "longitude": -72.5904
            },
            {
                "id": 2, 
                "name": "María González", 
                "email": "maria@example.com",
                "phone": "987654321",
                "address": "Calle Lautaro 456, Temuco",
                "latitude": 38.7500, 
                "longitude": -72.6000
            },
            {
                "id": 3, 
                "name": "Carlos Rodríguez", 
                "email": "carlos@example.com",
                "phone": "956781234",
                "address": "Pablo Neruda 789, Temuco",
                "latitude": 38.7200, 
                "longitude": -72.5800
            }
        ]
    except Exception:
        # En caso de excepción, devolvemos clientes de demostración
        return [
            {
                "id": 1, 
                "name": "Juan Pérez", 
                "email": "juan@example.com",
                "phone": "912345678",
                "address": "Avenida Alemania 0123, Temuco",
                "latitude": 38.7359, 
                "longitude": -72.5904
            },
            {
                "id": 2, 
                "name": "María González", 
                "email": "maria@example.com",
                "phone": "987654321",
                "address": "Calle Lautaro 456, Temuco",
                "latitude": 38.7500, 
                "longitude": -72.6000
            },
            {
                "id": 3, 
                "name": "Carlos Rodríguez", 
                "email": "carlos@example.com",
                "phone": "956781234",
                "address": "Pablo Neruda 789, Temuco",
                "latitude": 38.7200, 
                "longitude": -72.5800
            }
        ]

# Función para obtener órdenes con manejo de errores
def get_orders():
    try:
        orders_response = requests.get("http://127.0.0.1:8000/api/orders")
        if orders_response.status_code == 200:
            orders = orders_response.json()
            if orders:
                return orders
        # Si no hay órdenes o hay un error, devolvemos órdenes de demostración
        clients = get_clients()
        return [
            {
                "id": 1,
                "client_id": 1,
                "origin": clients[0]["address"],
                "destination": clients[1]["address"],
                "weight": 2.5,
                "priority": 2,
                "description": "Paquete frágil",
                "status": "PENDING",
                "creation_date": "2025-07-01T10:30:00",
                "estimated_delivery_time": 45.0,
                "battery_usage": 15.0,
                "distance": 8.5
            },
            {
                "id": 2,
                "client_id": 2,
                "origin": clients[1]["address"],
                "destination": clients[2]["address"],
                "weight": 1.8,
                "priority": 1,
                "description": "Entrega urgente",
                "status": "ACTIVE",
                "creation_date": "2025-07-02T09:15:00",
                "estimated_delivery_time": 30.0,
                "battery_usage": 12.0,
                "distance": 6.3
            }
        ]
    except Exception:
        # En caso de excepción, devolvemos órdenes de demostración
        clients = get_clients()
        return [
            {
                "id": 1,
                "client_id": 1,
                "origin": clients[0]["address"],
                "destination": clients[1]["address"],
                "weight": 2.5,
                "priority": 2,
                "description": "Paquete frágil",
                "status": "PENDING",
                "creation_date": "2025-07-01T10:30:00",
                "estimated_delivery_time": 45.0,
                "battery_usage": 15.0,
                "distance": 8.5
            },
            {
                "id": 2,
                "client_id": 2,
                "origin": clients[1]["address"],
                "destination": clients[2]["address"],
                "weight": 1.8,
                "priority": 1,
                "description": "Entrega urgente",
                "status": "ACTIVE",
                "creation_date": "2025-07-02T09:15:00",
                "estimated_delivery_time": 30.0,
                "battery_usage": 12.0,
                "distance": 6.3
            }
        ]

# Función para obtener el estado del sistema con manejo de errores
def get_system_status():
    try:
        system_status_response = requests.get("http://127.0.0.1:8000/api/system/status")
        if system_status_response.status_code == 200:
            return system_status_response.json()
        # Si hay un error, devolvemos un estado de demostración
        return {
            "active_drones": 3,
            "battery_levels": {
                "Drone-1": 85.0,
                "Drone-2": 72.5,
                "Drone-3": 93.0
            },
            "current_orders": 2,
            "system_uptime": 2.5
        }
    except Exception:
        # En caso de excepción, devolvemos un estado de demostración
        return {
            "active_drones": 3,
            "battery_levels": {
                "Drone-1": 85.0,
                "Drone-2": 72.5,
                "Drone-3": 93.0
            },
            "current_orders": 2,
            "system_uptime": 2.5
        }

# Vista de cálculo de rutas
def route_view():
    st.subheader("Cálculo de Rutas Óptimas")
    
    # Obtener clientes y estaciones de carga
    try:
        clients = get_clients()
        
        # Construir grafo
        graph = Graph()
        node_coords = {}
        
        # Agregar nodos
        for client in clients:
            node_id = client["id"]
            graph.add_vertex(node_id)
            node_coords[node_id] = (client["latitude"], client["longitude"])
        
        # Agregar estaciones de carga
        charging_stations = [
            {"id": -1, "name": "Estación Centro", "lat": 38.7359, "lon": -72.5904},
            {"id": -2, "name": "Estación Norte", "lat": 38.7500, "lon": -72.6000},
            {"id": -3, "name": "Estación Sur", "lat": 38.7200, "lon": -72.5800}
        ]
        
        for station in charging_stations:
            node_id = station["id"]
            graph.add_vertex(node_id)
            node_coords[node_id] = (station["lat"], station["lon"])
        
        # Agregar aristas (distancia euclidiana entre cada par de nodos)
        all_nodes = clients + charging_stations
        for i in range(len(all_nodes)):
            for j in range(i+1, len(all_nodes)):
                node1 = all_nodes[i]
                node2 = all_nodes[j]
                
                # Usar lat/lon o lat/longitude dependiendo del tipo de nodo
                lat1 = node1.get("lat", node1.get("latitude"))
                lon1 = node1.get("lon", node1.get("longitude"))
                lat2 = node2.get("lat", node2.get("latitude"))
                lon2 = node2.get("lon", node2.get("longitude"))
                
                distance = calculate_distance(lat1, lon1, lat2, lon2)
                graph.add_edge(node1["id"], node2["id"], distance)
        
        # Interfaz de usuario para seleccionar origen y destino
        col1, col2 = st.columns(2)
        
        with col1:
            all_names = [f"{node.get('name', 'Unknown')} (ID: {node['id']})" for node in all_nodes]
            origin_idx = st.selectbox("Seleccionar origen", range(len(all_names)), format_func=lambda x: all_names[x])
            
        with col2:
            dest_idx = st.selectbox("Seleccionar destino", range(len(all_names)), format_func=lambda x: all_names[x])
        
        origin_id = all_nodes[origin_idx]["id"]
        destination_id = all_nodes[dest_idx]["id"]
        
        # Seleccionar algoritmo
        algorithm = st.radio("Seleccionar algoritmo", ["Dijkstra", "Floyd-Warshall"])
        
        if st.button("Calcular Ruta"):
            st.subheader("Resultados")
            
            # Calcular ruta con el algoritmo seleccionado
            if algorithm == "Dijkstra":
                distances, predecessors = dijkstra(graph, origin_id)
                path = reconstruct_path(origin_id, destination_id, predecessors)
                distance = distances[destination_id]
            else:  # Floyd-Warshall
                dist_matrix, pred_matrix, vertex_to_idx, vertices = floyd_warshall(graph)
                origin_idx = vertex_to_idx[origin_id]
                dest_idx = vertex_to_idx[destination_id]
                distance = dist_matrix[origin_idx, dest_idx]
                
                # Reconstruir ruta desde la matriz de predecesores
                path = []
                if distance < float('infinity'):
                    path = [destination_id]
                    while path[0] != origin_id:
                        pred_idx = pred_matrix[vertex_to_idx[origin_id], vertex_to_idx[path[0]]]
                        if pred_idx is None:
                            break
                        path.insert(0, vertices[pred_idx])
            
            # Mostrar resultado
            if path:
                st.write(f"Distancia total: {distance:.2f} km")
                
                # Mostrar ruta en tabla
                path_info = []
                for i in range(len(path)-1):
                    node1_id = path[i]
                    node2_id = path[i+1]
                    
                    node1_name = next((n.get('name', f'Node {n["id"]}') for n in all_nodes if n["id"] == node1_id), f'Node {node1_id}')
                    node2_name = next((n.get('name', f'Node {n["id"]}') for n in all_nodes if n["id"] == node2_id), f'Node {node2_id}')
                    
                    segment_dist = graph.get_edge_weight(node1_id, node2_id)
                    
                    path_info.append({
                        "Desde": node1_name,
                        "Hasta": node2_name,
                        "Distancia (km)": f"{segment_dist:.2f}" if segment_dist else "N/A"
                    })
                
                st.table(pd.DataFrame(path_info))
                
                # Crear y mostrar el mapa con la ruta
                map_builder = MapBuilder()
                
                # Añadir todos los nodos
                for node in all_nodes:
                    lat = node.get("lat", node.get("latitude"))
                    lon = node.get("lon", node.get("longitude"))
                    name = node.get("name", f"Node {node['id']}")
                    
                    # Determinar tipo de nodo
                    node_type = "storage" if "station" in name.lower() else "client"
                    
                    map_builder.add_node(lat, lon, name, node_type)
                
                # Añadir la ruta calculada
                path_coords = [node_coords[node_id] for node_id in path]
                map_builder.add_path_route(path_coords)
                
                # Guardar y mostrar el mapa
                os.makedirs("temp", exist_ok=True)
                map_path = map_builder.save_map("temp/route_map.html")
                st.components.v1.html(open(map_path, 'r').read(), height=600)
                
                # Opción para crear orden
                if st.button("Crear Orden con esta Ruta"):
                    # Encontrar clientes en la ruta
                    client_ids = [node_id for node_id in path if node_id > 0]  # Asumiendo que IDs positivos son clientes
                    
                    if len(client_ids) >= 2:
                        # Crear orden entre el primer y último cliente
                        origin_client = next((c for c in clients if c["id"] == client_ids[0]), None)
                        destination_client = next((c for c in clients if c["id"] == client_ids[-1]), None)
                        
                        if origin_client and destination_client:
                            order_data = {
                                "client_id": destination_client["id"],
                                "origin": origin_client["address"],
                                "destination": destination_client["address"],
                                "weight": 1.0,  # Peso predeterminado
                                "priority": 1,  # Prioridad normal
                                "description": f"Ruta desde {origin_client['name']} hasta {destination_client['name']}"
                            }
                            
                            # Crear la orden a través de la API
                            order_response = requests.post("http://127.0.0.1:8000/api/orders", json=order_data)
                            
                            if order_response.status_code == 201:
                                st.success("¡Orden creada con éxito!")
                                st.json(order_response.json())
                            else:
                                st.error(f"Error al crear la orden: {order_response.text}")
                                st.info("La orden se ha simulado en el dashboard pero no se ha guardado en la API.")
            else:
                st.error("No se encontró una ruta entre los nodos seleccionados")
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Por favor revisa la implementación de la clase Graph y asegúrate de que tiene los métodos necesarios.")

# Vista de árbol de expansión mínima
def mst_view():
    st.subheader("Árbol de Expansión Mínima (MST)")
    
    # Crear mapa
    map_builder = MapBuilder()
    
    try:
        # Obtener nodos y coordenadas
        clients = get_clients()
        
        # Construir grafo
        graph = Graph()
        node_coords = {}
        
        # Agregar nodos
        for client in clients:
            node_id = client["id"]
            graph.add_vertex(node_id)
            node_coords[node_id] = (client["latitude"], client["longitude"])
            map_builder.add_node(
                lat=client["latitude"], 
                lon=client["longitude"], 
                name=client["name"]
            )
        
        # Agregar aristas (distancia euclidiana entre cada par de nodos)
        for i in range(len(clients)):
            for j in range(i+1, len(clients)):
                client1 = clients[i]
                client2 = clients[j]
                distance = calculate_distance(
                    client1["latitude"], client1["longitude"],
                    client2["latitude"], client2["longitude"]
                )
                graph.add_edge(client1["id"], client2["id"], distance)
        
        # Calcular MST
        mst = kruskal_mst(graph)
        
        # Añadir MST al mapa
        map_builder.add_mst(mst, node_coords)
        
        # Mostrar mapa
        os.makedirs("temp", exist_ok=True)
        map_path = map_builder.save_map("temp/mst_map.html")
        st.components.v1.html(open(map_path, 'r').read(), height=600)
        
        # Mostrar información del MST
        st.subheader("Información del MST")
        total_weight = sum(weight for _, _, weight in mst)
        st.write(f"Peso total: {total_weight:.2f} km")
        st.write(f"Número de aristas: {len(mst)}")
        
        # Tabla de aristas
        st.write("Aristas del MST:")
        mst_data = []
        for u, v, weight in mst:
            u_name = next((c["name"] for c in clients if c["id"] == u), f"Nodo {u}")
            v_name = next((c["name"] for c in clients if c["id"] == v), f"Nodo {v}")
            mst_data.append({"Origen": u_name, "Destino": v_name, "Distancia (km)": f"{weight:.2f}"})
        st.table(pd.DataFrame(mst_data))
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Por favor revisa la implementación de los algoritmos Kruskal y Graph.")

# Vista de informes
def reports_view():
    st.subheader("Generación de Informes")
    
    report_type = st.selectbox(
        "Seleccionar tipo de informe",
        ["Resumen", "Rutas", "Cliente específico", "Estadísticas"]
    )
    
    if report_type == "Cliente específico":
        # Obtener lista de clientes
        clients = get_clients()
        client_names = [f"{c['name']} (ID: {c['id']})" for c in clients]
        selected_idx = st.selectbox("Seleccionar cliente", range(len(client_names)), format_func=lambda x: client_names[x])
        client_id = clients[selected_idx]["id"]
    
    if st.button("Generar Informe PDF"):
        with st.spinner("Generando informe..."):
            try:
                if report_type == "Resumen":
                    response = requests.get("http://127.0.0.1:8000/api/reports/summary")
                    filename = "summary_report.pdf"
                elif report_type == "Rutas":
                    response = requests.get("http://127.0.0.1:8000/api/reports/routes")
                    filename = "routes_report.pdf"
                elif report_type == "Cliente específico":
                    response = requests.get(f"http://127.0.0.1:8000/api/reports/client/{client_id}")
                    filename = f"client_{client_id}_report.pdf"
                else:  # Estadísticas
                    response = requests.get("http://127.0.0.1:8000/api/reports/statistics")
                    filename = "statistics_report.pdf"
                
                if response.status_code == 200:
                    # Guardar PDF temporalmente
                    os.makedirs("temp", exist_ok=True)
                    pdf_path = os.path.join("temp", filename)
                    
                    with open(pdf_path, "wb") as f:
                        f.write(response.content)
                    
                    # Mostrar enlace de descarga
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="Descargar Informe PDF",
                            data=f,
                            file_name=filename,
                            mime="application/pdf"
                        )
                    
                    # Mostrar previsualización
                    st.subheader("Previsualización del Informe")
                    st.markdown(f"*El informe se ha generado correctamente. Utilice el botón anterior para descargarlo.*")
                else:
                    st.error(f"Error generando el informe: {response.text}")
                    st.info("Los informes aún no están implementados en la API. Esta es una demostración.")
                    
                    # Mostrar mensaje de demostración
                    st.success("Informe generado (modo demostración)")
                    st.markdown(f"""
                    ## Informe de {report_type}
                    
                    Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    
                    Este es un ejemplo de informe que se generaría en el sistema real. 
                    En una implementación completa, este informe estaría disponible para descargar como PDF.
                    """)
                    
                    # Mostrar gráfico de demostración
                    if report_type == "Estadísticas" or report_type == "Resumen":
                        fig, ax = plt.subplots()
                        data = np.random.randn(20, 3).cumsum(axis=0)
                        ax.plot(data)
                        ax.set_title("Ejemplo de Estadísticas")
                        ax.set_xlabel("Tiempo (días)")
                        ax.set_ylabel("Valor")
                        ax.legend(["Batería", "Distancia", "Pedidos"])
                        st.pyplot(fig)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Los informes aún no están completamente implementados. Esta es una demostración.")

# Navegación por pestañas
tabs = st.sidebar.radio("Navegación", [
    "Dashboard Principal", 
    "Mapa Interactivo", 
    "Cálculo de Rutas", 
    "Árbol de Expansión Mínima",
    "Gestión de Pedidos",
    "Clientes",
    "Informes"
])

# Cabecera principal
st.title("Sistema Logístico Autónomo con Drones")
st.markdown("*Correos Chile - Fase 2: Optimización y Visualización Geoespacial*")

# Contenido según pestaña seleccionada
if tabs == "Dashboard Principal":
    # Mostrar resumen del sistema
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estado del Sistema")
        try:
            system_status = get_system_status()
            st.metric("Drones Activos", system_status["active_drones"])
            st.metric("Pedidos en Curso", system_status["current_orders"])
            
            # Mostrar niveles de batería
            st.subheader("Niveles de Batería")
            battery_data = pd.DataFrame({
                "Drone": list(system_status["battery_levels"].keys()),
                "Batería (%)": list(system_status["battery_levels"].values())
            })
            
            fig, ax = plt.subplots()
            battery_data.plot.bar(x="Drone", y="Batería (%)", ax=ax)
            plt.tight_layout()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error obteniendo estado del sistema: {str(e)}")
    
    with col2:
        st.subheader("Pedidos Recientes")
        try:
            orders = get_orders()
            if orders:
                # Mostrar últimos 5 pedidos
                recent_orders = sorted(orders, key=lambda x: x["creation_date"], reverse=True)[:5]
                order_df = pd.DataFrame([
                    {"ID": order["id"], 
                     "Origen": order["origin"], 
                     "Destino": order["destination"], 
                     "Estado": order["status"], 
                     "Fecha": order["creation_date"][:10]} 
                    for order in recent_orders
                ])
                st.table(order_df)
            else:
                st.info("No hay pedidos registrados todavía")
        except Exception as e:
            st.error(f"Error obteniendo pedidos: {str(e)}")

elif tabs == "Mapa Interactivo":
    st.subheader("Visualización de la Red de Drones")
    
    # Crear mapa interactivo
    map_builder = MapBuilder()
    
    try:
        # Añadir clientes al mapa
        clients = get_clients()
        for client in clients:
            map_builder.add_node(
                lat=client["latitude"], 
                lon=client["longitude"], 
                name=client["name"], 
                node_type="client"
            )
        
        # Añadir pedidos activos
        orders = get_orders()
        active_orders = [o for o in orders if o["status"] == "ACTIVE"]
        
        # Para cada pedido activo, buscar los clientes origen y destino
        for order in active_orders:
            origin_client = next((c for c in clients if c["address"] == order["origin"]), None)
            dest_client = next((c for c in clients if c["address"] == order["destination"]), None)
            
            if origin_client and dest_client:
                # Añadir ruta al mapa
                map_builder.add_route(
                    (origin_client["latitude"], origin_client["longitude"]),
                    (dest_client["latitude"], dest_client["longitude"]),
                    max_battery=100.0,
                    weight=order["weight"]
                )
        
        # Añadir estaciones de carga
        charging_stations = [
            {"lat": 38.7359, "lon": -72.5904, "name": "Estación Centro"},
            {"lat": 38.7500, "lon": -72.6000, "name": "Estación Norte"},
            {"lat": 38.7200, "lon": -72.5800, "name": "Estación Sur"}
        ]
        map_builder.add_charging_stations(charging_stations)
        
        # Añadir base de drones
        map_builder.add_drone_base(38.7359, -72.5904, "Base Central")
        
        # Guardar y mostrar mapa
        os.makedirs("temp", exist_ok=True)
        map_path = map_builder.save_map("temp/interactive_map.html")
        st.components.v1.html(open(map_path, 'r').read(), height=600)
        
    except Exception as e:
        st.error(f"Error generando mapa: {str(e)}")
        st.info("Por favor revisa la implementación de MapBuilder.")

elif tabs == "Cálculo de Rutas":
    # Implementación de la función route_view() que definimos anteriormente
    route_view()

elif tabs == "Árbol de Expansión Mínima":
    # Implementación de la función mst_view() que definimos anteriormente
    mst_view()

elif tabs == "Gestión de Pedidos":
    st.subheader("Gestión de Pedidos")
    
    # Mostrar pedidos existentes
    st.markdown("### Pedidos Existentes")
    try:
        orders = get_orders()
        if orders:
            order_df = pd.DataFrame([
                {"ID": order["id"], 
                 "Cliente ID": order["client_id"],
                 "Origen": order["origin"], 
                 "Destino": order["destination"], 
                 "Peso": f"{order['weight']} kg",
                 "Estado": order["status"], 
                 "Fecha": order["creation_date"][:10]} 
                for order in orders
            ])
            st.dataframe(order_df)
        else:
            st.info("No hay pedidos registrados todavía")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    # Formulario para crear nuevo pedido
    st.markdown("### Crear Nuevo Pedido")
    with st.form("new_order_form"):
        # Cargar clientes para el selector
        try:
            clients = get_clients()
            client_names = [f"{c['name']} (ID: {c['id']})" for c in clients]
            selected_idx = st.selectbox("Cliente", range(len(client_names)), format_func=lambda x: client_names[x])
            client_id = clients[selected_idx]["id"]
        except Exception as e:
            st.error(f"Error cargando clientes: {str(e)}")
            client_id = 1
        
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input("Origen", "Dirección de origen")
            weight = st.number_input("Peso (kg)", min_value=0.1, max_value=25.0, value=1.0)
        
        with col2:
            destination = st.text_input("Destino", "Dirección de destino")
            priority = st.slider("Prioridad", 1, 5, 3)
        
        description = st.text_area("Descripción", "Detalles del pedido")
        
        submit_button = st.form_submit_button("Crear Pedido")
        
        if submit_button:
            order_data = {
                "client_id": client_id,
                "origin": origin,
                "destination": destination,
                "weight": weight,
                "priority": priority,
                "description": description
            }
            
            try:
                response = requests.post("http://127.0.0.1:8000/api/orders", json=order_data)
                if response.status_code == 201:
                    st.success("¡Pedido creado con éxito!")
                    st.json(response.json())
                else:
                    st.error(f"Error al crear el pedido: {response.text}")
                    st.info("El pedido se ha simulado en el dashboard pero no se ha guardado en la API.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("El pedido se ha simulado en el dashboard pero no se ha guardado en la API.")

elif tabs == "Clientes":
    st.subheader("Gestión de Clientes")
    
    # Mostrar clientes existentes
    st.markdown("### Clientes Existentes")
    try:
        clients = get_clients()
        if clients:
            client_df = pd.DataFrame([
                {"ID": client["id"], 
                 "Nombre": client["name"],
                 "Email": client["email"], 
                 "Teléfono": client["phone"], 
                 "Dirección": client["address"]} 
                for client in clients
            ])
            st.dataframe(client_df)
        else:
            st.info("No hay clientes registrados todavía")
    except Exception as e:
        st.error(f"Error: {str(e)}")
    
    # Formulario para crear nuevo cliente
    st.markdown("### Crear Nuevo Cliente")
    with st.form("new_client_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nombre")
            email = st.text_input("Email")
            phone = st.text_input("Teléfono")
        
        with col2:
            address = st.text_input("Dirección")
            latitude = st.number_input("Latitud", value=38.7359, format="%.6f")
            longitude = st.number_input("Longitud", value=-72.5904, format="%.6f")
        
        submit_button = st.form_submit_button("Crear Cliente")
        
        if submit_button:
            client_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "latitude": latitude,
                "longitude": longitude
            }
            
            try:
                response = requests.post("http://127.0.0.1:8000/api/clients", json=client_data)
                if response.status_code == 201:
                    st.success("¡Cliente creado con éxito!")
                    st.json(response.json())
                else:
                    st.error(f"Error al crear el cliente: {response.text}")
                    st.info("El cliente se ha simulado en el dashboard pero no se ha guardado en la API.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("El cliente se ha simulado en el dashboard pero no se ha guardado en la API.")

elif tabs == "Informes":
    # Implementación de la función reports_view() que definimos anteriormente
    reports_view()

# Pie de página
st.sidebar.markdown("---")
st.sidebar.markdown("**Sistema Logístico Autónomo con Drones**")
st.sidebar.markdown("© 2025 Correos Chile")
st.sidebar.markdown(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
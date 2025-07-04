import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from visual.networkx_adapter import NetworkXAdapter
from datetime import datetime
from visual.avl_visualizer import avl_visualizer
from visual.map.map_builder import MapBuilder
import time
from visual.pdf_generator import PDFReportGenerator


def init_session_state():
    """Inicializa el estado de la sesión con valores por defecto"""
    if 'sim' not in st.session_state:
        st.session_state.sim = None
    if 'graph' not in st.session_state:
        st.session_state.graph = None
    if 'simulation_generated' not in st.session_state:
        st.session_state.simulation_generated = False
    if 'map_builder' not in st.session_state:
        st.session_state.map_builder = MapBuilder()
    if 'node_coordinates' not in st.session_state:
        st.session_state.node_coordinates = {}
    # Estados de mapas
    if 'main_map_data' not in st.session_state:
        st.session_state.main_map_data = None
    if 'explore_map_data' not in st.session_state:
        st.session_state.explore_map_data = None

def display_persistent_map(map_obj, container_key, width=700, height=500):
    """
    Muestra un mapa de forma persistente usando contenedores
    """
    try:
        from streamlit_folium import st_folium
        
        # Generar una key única pero consistente
        map_key = f"folium_{container_key}_{hash(str(map_obj._repr_html_()))}"
        
        # Renderizar el mapa
        map_data = st_folium(
            map_obj, 
            width=width, 
            height=height, 
            key=map_key,
            returned_objects=["last_object_clicked", "last_clicked"]
        )
        
        return map_data
        
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")
        return None

def run_simulation_tab():
    st.header("🏭 Run Simulation")
    
    # ========== INICIALIZAR SESSION STATE ==========
    init_session_state()
    
    # Mostrar información del algoritmo
    st.info("🔍 **Pathfinding Algorithm**: Using Dijkstra's algorithm for optimal route calculation")
    
    col1, col2 = st.columns(2)
    with col1:
        n_nodes = st.slider("Number of nodes", 10, 150, 15, key='nodes')
    with col2:
        min_edges = max(n_nodes - 1, 10)
        m_edges = st.slider("Number of edges", min_edges, 300, 20, key='edges')
    
    n_orders = st.slider("Number of orders", 10, 500, 10, key='orders')
    
    if st.button("🚀 Start Simulation"):
        try:
            # ========== LIMPIAR ESTADO PARA NUEVA SIMULACIÓN ==========
            keys_to_clear = [
                'node_coordinates', 'base_map', 'current_route_map',
                'show_route', 'last_route', 'route_message', 'graph_pos',
                'main_map_data', 'explore_map_data', 'route_algorithm'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # ========== GENERAR SIMULACIÓN ==========
            with st.spinner("Generating simulation with Dijkstra router..."):
                graph = SimulationInitializer.create_connected_graph(n_nodes, m_edges)
                sim = Simulation(graph)

                # Vincular clientes a nodos
                client_nodes = [v for v in graph.vertices() if graph.get_node_type(v) == "client"]
                sim.clients = []
                for idx, node in enumerate(client_nodes):
                    client_id = f"CLI_{idx}"
                    client = sim.generate_clients(client_id=client_id)
                    client.node_id = node

                sim.process_orders(n_orders)

                # Actualizar total_orders de cada cliente
                for client in sim.clients:
                    client.total_orders = sum(
                        1 for order in sim.active_orders + sim.completed_orders
                        if hasattr(client, "node_id") and order.destination == client.node_id
                    )

                # Guardar en session state
                st.session_state.graph = graph
                st.session_state.sim = sim
                st.session_state.simulation_generated = True
                
                # Calcular layout del grafo
                nx_graph = NetworkXAdapter.to_networkx(graph)
                pos = nx.spring_layout(nx_graph, seed=42)
                st.session_state.graph_pos = pos

                # ========== CREAR MAPA BASE CON MAPBUILDER ==========
                if 'map_builder' not in st.session_state:
                    st.session_state.map_builder = MapBuilder()
                
                map_builder = st.session_state.map_builder
                
                # Crear mapa completo con nodos y aristas
                interactive_map, coordinates = map_builder.create_full_map(graph)
                
                # Guardar coordenadas y mapa
                st.session_state.node_coordinates = coordinates
                st.session_state.base_map = interactive_map

            st.success("✅ Simulation completed successfully!")
            
            # Mostrar resumen
            st.subheader("Simulation Summary")
            cols = st.columns(4)
            cols[0].metric("Total Nodes", n_nodes)
            cols[1].metric("Total Edges", m_edges)
            cols[2].metric("Orders Processed", n_orders)
            cols[3].metric("Algorithm", "Dijkstra")
            
        except Exception as e:
            st.error(f"Error generating simulation: {str(e)}")
            st.error("Please make sure all required modules are installed.")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
    
    # ========== MOSTRAR MAPA SIEMPRE QUE ESTÉ DISPONIBLE ==========
    if st.session_state.get('simulation_generated', False) and 'base_map' in st.session_state:
        st.subheader("Interactive Map - Temuco")
        
        try:
            st.session_state.main_map_data = display_persistent_map(
                st.session_state.base_map, 
                "main_map"
            )
        except Exception as e:
            st.error(f"Error displaying map: {str(e)}")
            st.info("Map visualization requires streamlit-folium. Install with: pip install streamlit-folium")

def explore_network_tab():
    st.header("🗺️ Explore Network")
    init_session_state()
    
    if not st.session_state.get('simulation_generated', False):
        st.warning("⚠️ Please run a simulation first from the 'Run Simulation' tab")
        return
    
    # Mostrar información del algoritmo
    st.info("🔍 **Route Calculation**: Using Dijkstra's algorithm for optimal pathfinding")
    
    graph = st.session_state.graph
    sim = st.session_state.sim
    pos = st.session_state.get("graph_pos", None)
    
    if 'map_builder' not in st.session_state:
        st.session_state.map_builder = MapBuilder()
    
    map_builder = st.session_state.map_builder
    
    if pos is None:
        st.warning("No graph layout found. Please run a simulation first.")
        return

    # ========== SELECCIÓN DE RUTA ==========
    nodes = list(graph.vertices())
    
    # Filtrar nodos por tipo
    warehouse_nodes = [node for node in nodes if graph.get_node_type(node) == "warehouse"]
    all_nodes = nodes
    
    if not warehouse_nodes:
        st.error("No warehouse nodes found in the graph. Cannot create routes.")
        return
    
    warehouse_names = [str(v) for v in warehouse_nodes]
    all_node_names = [str(v) for v in all_nodes]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Origin** (Warehouse only)")
        origin = st.selectbox(
            "Select origin warehouse", 
            warehouse_names, 
            key='origin',
            help="Routes can only start from warehouse locations"
        )
    with col2:
        st.markdown("**Destination** (Any node)")
        destination = st.selectbox(
            "Select destination", 
            all_node_names, 
            key='destination',
            help="Routes can end at any node type"
        )

    # Mostrar información de los nodos seleccionados
    if origin and destination:
        origin_node = next(v for v in warehouse_nodes if str(v) == origin)
        dest_node = next(v for v in all_nodes if str(v) == destination)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Origin:** {origin} (Warehouse)")
        with col2:
            dest_type = graph.get_node_type(dest_node)
            st.info(f"**Destination:** {destination} ({dest_type.title()})")

    # ========== CALCULAR RUTA ==========
    if st.button("🔍 Calculate Route (Dijkstra)"):
        with st.spinner("Calculating optimal route using Dijkstra's algorithm..."):
            try:
                origin_node = next(v for v in warehouse_nodes if str(v) == origin)
                dest_node = next(v for v in all_nodes if str(v) == destination)
                
                if origin_node == dest_node:
                    st.warning("Origin and destination cannot be the same node.")
                    return
                
                route = sim.find_route_with_recharge(origin_node, dest_node)
                
                if route:
                    st.session_state.show_route = True
                    st.session_state.last_route = route
                    st.session_state.route_message = f"**Route:** {route.path_str()} | **Cost:** {route.cost:.2f}"
                    st.session_state.route_algorithm = "Dijkstra"
                    
                    coordinates = st.session_state.get('node_coordinates', {})
                    if coordinates:
                        interactive_map_with_route, _ = map_builder.create_full_map(
                            graph, 
                            highlight_route=route.path,
                            coordinates=coordinates
                        )
                        st.session_state.current_route_map = interactive_map_with_route
                    else:
                        interactive_map_with_route, coordinates = map_builder.create_full_map(
                            graph, 
                            highlight_route=route.path
                        )
                        st.session_state.current_route_map = interactive_map_with_route
                        st.session_state.node_coordinates = coordinates
                    
                else:
                    st.session_state.show_route = False
                    st.session_state.last_route = None
                    st.session_state.route_message = "No valid route found with current battery limit"
                    st.session_state.current_route_map = None
                    
            except Exception as e:
                st.error(f"Error calculating route: {str(e)}")
                st.session_state.show_route = False
                st.session_state.last_route = None
                st.session_state.route_message = f"Error: {str(e)}"

    # ========== MOSTRAR MAPA SIEMPRE ==========
    st.subheader("Interactive Map - Temuco")
    
    show_route = st.session_state.get("show_route", False)
    route = st.session_state.get("last_route", None)
    
    try:
        if show_route and route and 'current_route_map' in st.session_state:
            st.session_state.explore_map_data = display_persistent_map(
                st.session_state.current_route_map, 
                "explore_map_with_route"
            )
        elif 'base_map' in st.session_state:
            st.session_state.explore_map_data = display_persistent_map(
                st.session_state.base_map, 
                "explore_map_base"
            )
        else:
            st.info("No map available. Please run a simulation first.")
    except Exception as e:
        st.error(f"Error displaying map: {str(e)}")

    # ========== INFORMACIÓN DE RUTA ==========
    route_message = st.session_state.get("route_message", "")
    if route_message:
        if show_route and route:
            st.success(route_message)
        else:
            st.error(route_message)

    # ========== DETALLES DE RUTA ==========
    if show_route and route:
        st.subheader("Route Details")
        
        # Mostrar algoritmo usado
        algorithm_used = st.session_state.get('route_algorithm', 'Dijkstra')
        st.info(f"📊 **Algorithm Used**: {algorithm_used} - Guaranteed optimal path")
        
        cols = st.columns(4)
        cols[0].metric("Total Nodes", len(route.path))
        cols[1].metric("Total Cost", f"{route.cost:.2f}")
        
        recharge_stops = sum(1 for node in route.path 
                           if graph.get_node_type(node) == 'recharge')
        cols[2].metric("Recharge Stops", recharge_stops)
        
        client_visits = sum(1 for node in route.path 
                          if graph.get_node_type(node) == 'client')
        cols[3].metric("Client Visits", client_visits)

        # Mostrar el path de la ruta
        st.subheader("Route Path")
        route_path_display = []
        for i, node in enumerate(route.path):
            node_type = graph.get_node_type(node)
            if i == 0:
                route_path_display.append(f"🏠 **{node}** ({node_type}) - START")
            elif i == len(route.path) - 1:
                route_path_display.append(f"🎯 **{node}** ({node_type}) - END")
            else:
                icon = "👤" if node_type == "client" else "⚡" if node_type == "recharge" else "🏠"
                route_path_display.append(f"{icon} **{node}** ({node_type})")
        
        st.write(" → ".join(route_path_display))

        # ========== COMPLETAR ORDEN ==========
        matching_orders = [
            order for order in sim.active_orders
            if (str(order.origin) == origin and 
                str(order.destination) == destination and 
                order.status != "completed")
        ]
        
        if matching_orders:
            st.subheader("Complete Order")
            st.info(f"Found {len(matching_orders)} matching active order(s)")
            
            if st.button("✅ Complete Order", key="complete_order_btn"):
                try:
                    sorted_orders = sorted(matching_orders, key=lambda o: getattr(o, "priority", 9999))
                    
                    for order in sorted_orders:
                        order.route = route
                        order.complete(route.cost)
                        
                        sim.completed_orders.append(order)
                        sim.active_orders.remove(order)
                        
                        # Insertar ruta en AVL
                        sim.route_avl.insert(route.path_str(), route)
                        
                        st.success("✅ Order completed successfully!")
                        
                        # Limpiar estado de ruta
                        st.session_state.show_route = False
                        st.session_state.last_route = None
                        st.session_state.route_message = ""
                        st.session_state.current_route_map = None
                        
                        st.rerun()
                        break
                except Exception as e:
                    st.error(f"Error completing order: {str(e)}")
        else:
            st.info("ℹ️ No matching active orders for this route.")
            
    # ========== INFORMACIÓN DE NODOS ==========
    st.subheader("📊 Node Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        warehouse_count = len(warehouse_nodes)
        st.metric("Warehouses", warehouse_count)
    
    with col2:
        client_count = len([n for n in nodes if graph.get_node_type(n) == "client"])
        st.metric("Clients", client_count)
    
    with col3:
        recharge_count = len([n for n in nodes if graph.get_node_type(n) == "recharge"])
        st.metric("Recharge Stations", recharge_count)

def clients_orders_tab():
    st.header("📦 Clients & Orders")
    init_session_state()
    
    if not st.session_state.get('simulation_generated', False):
        st.warning("⚠️ Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    
    # ========== CLIENTES ==========
    st.subheader("👥 Clients")
    if hasattr(sim, "clients") and sim.clients:
        for i, client in enumerate(sim.clients, 1):
            with st.expander(f"Client {i} - {getattr(client, 'client_id', 'N/A')}"):
                if hasattr(client, "to_dict"):
                    st.json(client.to_dict(), expanded=True)
                elif hasattr(client, "__dict__"):
                    st.json(client.__dict__, expanded=True)
                else:
                    st.write(str(client))
    else:
        st.info("No clients found in simulation.")

    # ========== ÓRDENES ==========
    st.subheader("📋 Orders")
    
    all_orders = []
    if hasattr(sim, "active_orders"):
        all_orders.extend([(order, "Active") for order in sim.active_orders])
    if hasattr(sim, "completed_orders"):
        all_orders.extend([(order, "Completed") for order in sim.completed_orders])
    
    if all_orders:
        tab1, tab2 = st.tabs(["Active Orders", "Completed Orders"])
        
        with tab1:
            active_orders = [order for order, status in all_orders if status == "Active"]
            if active_orders:
                for i, order in enumerate(active_orders, 1):
                    with st.expander(f"Active Order {i}"):
                        if hasattr(order, "to_dict"):
                            st.json(order.to_dict(), expanded=True)
                        elif hasattr(order, "__dict__"):
                            st.json(order.__dict__, expanded=True)
                        else:
                            st.write(str(order))
            else:
                st.info("No active orders.")
        
        with tab2:
            completed_orders = [order for order, status in all_orders if status == "Completed"]
            if completed_orders:
                for i, order in enumerate(completed_orders, 1):
                    with st.expander(f"Completed Order {i}"):
                        if hasattr(order, "to_dict"):
                            st.json(order.to_dict(), expanded=True)
                        elif hasattr(order, "__dict__"):
                            st.json(order.__dict__, expanded=True)
                        else:
                            st.write(str(order))
            else:
                st.info("No completed orders.")
    else:
        st.info("No orders found in simulation.")

def route_analytics_tab():
    st.header("📊 Route Analytics")
    init_session_state()
    
    if not st.session_state.get('simulation_generated', False):
        st.warning("⚠️ Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    graph = st.session_state.graph
    
    # ========== INFORMACIÓN DEL ALGORITMO ==========
    st.info("🔍 **Route Analysis**: All routes calculated using Dijkstra's algorithm for optimal pathfinding")
    
    # ========== BOTÓN PARA GENERAR PDF ==========
    st.subheader("📄 Generate PDF Report")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("""
        **El reporte PDF incluye:**
        - 📊 Estadísticas generales del sistema
        - 🔥 Rutas más frecuentes con análisis de costos
        - 🎯 Distribución de tipos de nodo
        - 🚀 Nodos más visitados por categoría
        - 👥 Análisis de clientes y sus órdenes
        - 📈 Gráficos de torta y barras
        """)
    
    with col2:
        if st.button("📄 Generate PDF Report", type="primary"):
            try:
                with st.spinner("Generating comprehensive PDF report..."):
                    # Crear el generador de PDF
                    pdf_generator = PDFReportGenerator(sim, graph)
                    
                    # Generar el PDF
                    pdf_bytes = pdf_generator.generate_report()
                    
                    # Crear nombre del archivo con timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"drone_logistics_report_{timestamp}.pdf"
                    
                    # Botón de descarga
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="download_pdf"
                    )
                    
                    st.success("✅ PDF report generated successfully!")
                    st.balloons()
                    
            except Exception as e:
                st.error(f"Error generating PDF report: {str(e)}")
                st.error("Please make sure matplotlib is installed: pip install matplotlib")
    
    st.markdown("---")
    
    # ========== RUTAS MÁS FRECUENTES ==========
    st.subheader("🔥 Most Frequent Routes")
    try:
        top_routes = sim.get_most_frequent_routes(5)
        
        if top_routes:
            for i, route_data in enumerate(top_routes, 1):
                if isinstance(route_data, tuple) and len(route_data) == 2:
                    route_str, route = route_data
                    frequency = getattr(route, 'frequency', 1)
                    cost = getattr(route, 'cost', 0)
                    st.write(f"{i}. **{route_str}** - Used {frequency} times (Cost: {cost:.2f})")
                else:
                    st.write(f"{i}. **Route data**: {route_data}")
        else:
            st.info("No routes recorded yet. Complete some orders to see analytics.")
    except Exception as e:
        st.error(f"Error getting route analytics: {str(e)}")
        st.info("Complete some orders to see route analytics.")
    
    # ========== ESTADÍSTICAS DE RUTAS ==========
    st.subheader("📈 Route Statistics")
    try:
        completed_orders = sim.completed_orders
        total_routes = len(completed_orders)
        
        if total_routes > 0:
            total_distance = sum(getattr(order, 'cost', 0) for order in completed_orders)
            avg_distance = total_distance / total_routes if total_routes > 0 else 0
            
            # Contar paradas de recarga
            total_recharge_stops = 0
            for order in completed_orders:
                if hasattr(order, 'route') and order.route:
                    recharge_stops = sum(1 for node in order.route.path 
                                       if graph.get_node_type(node) == 'recharge')
                    total_recharge_stops += recharge_stops
            
            avg_recharge_stops = total_recharge_stops / total_routes if total_routes > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Routes", total_routes)
            
            with col2:
                st.metric("Total Distance", f"{total_distance:.2f}")
            
            with col3:
                st.metric("Avg Distance", f"{avg_distance:.2f}")
            
            with col4:
                st.metric("Avg Recharge Stops", f"{avg_recharge_stops:.2f}")
        else:
            st.info("No route statistics available yet. Complete some orders to see statistics.")
    except Exception as e:
        st.error(f"Error getting route statistics: {str(e)}")
    
    # ========== VISUALIZACIÓN AVL ==========
    st.subheader("🌳 AVL Tree Visualization")
    try:
        if hasattr(sim, 'route_avl') and sim.route_avl.root:
            st.info("AVL tree structure showing route storage organization")
            avl_visualizer(sim.route_avl.root)
        else:
            st.info("No routes in AVL tree yet. Complete some orders to populate the tree.")
    except Exception as e:
        st.error(f"Error visualizing AVL tree: {str(e)}")
        st.info("AVL tree visualization not available.")

def general_stats_tab():
    st.header("📈 General Statistics")
    init_session_state()
    
    if not st.session_state.get('simulation_generated', False):
        st.warning("⚠️ Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    graph = st.session_state.graph
    
    # ========== DISTRIBUCIÓN DE NODOS ==========
    st.subheader("🎯 Node Distribution")
    node_types = {}
    for node in graph.vertices():
        node_type = graph.get_node_type(node)
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    if node_types:
        try:
            fig1, ax1 = plt.subplots(figsize=(8, 6))
            colors = ['#ff6b6b', '#00FF00', '#45b7d1', '#96ceb4', '#ffeaa7']
            ax1.pie(node_types.values(), labels=node_types.keys(), autopct='%1.1f%%', colors=colors)
            ax1.set_title("Node Type Distribution")
            st.pyplot(fig1)
        except Exception as e:
            st.error(f"Error creating pie chart: {str(e)}")
    
    # ========== ESTADÍSTICAS DE VISITAS ==========
    st.subheader("🚀 Node Visit Statistics")
    try:
        visit_stats = sim.get_node_visit_stats()
        
        if visit_stats:
            role_visits = {"client": [], "warehouse": [], "recharge": []}
            visited_dict = {str(node): visits for node, visits in visit_stats}
            
            for node in graph.vertices():
                node_type = graph.get_node_type(node)
                if node_type in role_visits:
                    visits = visited_dict.get(str(node), 0)
                    role_visits[node_type].append((str(node), visits))
            
            for role in ["client", "warehouse", "recharge"]:
                nodes_visits = sorted(role_visits[role], key=lambda x: x[1], reverse=True)[:10]
                if nodes_visits and any(visits > 0 for _, visits in nodes_visits):
                    st.markdown(f"**{role.capitalize()} Nodes**")
                    nodes, visits = zip(*nodes_visits)
                    
                    try:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        bars = ax.barh(nodes, visits, color={'client': '#00FF00', 'warehouse': '#ff6b6b', 'recharge': '#45b7d1'}[role])
                        ax.set_xlabel("Number of Visits")
                        ax.set_title(f"Top 10 Most Visited {role.capitalize()} Nodes")
                        
                        for i, bar in enumerate(bars):
                            width = bar.get_width()
                            if width > 0:
                                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                                       f'{int(width)}', ha='left', va='center')
                        
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error creating bar chart for {role}: {str(e)}")
                    
                    st.markdown("---")
        else:
            st.info("No visit statistics available yet. Complete some routes to see visit data.")
    except Exception as e:
        st.error(f"Error getting visit statistics: {str(e)}")
        st.info("Visit statistics not available.")

def main():
    st.set_page_config(
        page_title="🚁 Drone Logistics System",
        page_icon="🚁",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session_state()
    
    st.sidebar.title("🚁 Navigation")
    st.sidebar.markdown("---")
    
    tabs = {
        "🏭 Run Simulation": run_simulation_tab,
        "🗺️ Explore Network": explore_network_tab,
        "📦 Clients & Orders": clients_orders_tab,
        "📊 Route Analytics": route_analytics_tab,
        "📈 General Statistics": general_stats_tab
    }
    
    selected_tab = st.sidebar.radio("Go to", list(tabs.keys()))
    
    st.sidebar.markdown("---")
    if st.session_state.get('simulation_generated', False):
        st.sidebar.success("✅ Simulation Ready")
        st.sidebar.info("🔍 **Algorithm**: Dijkstra")
        if 'graph' in st.session_state:
            graph = st.session_state.graph
            st.sidebar.info(f"📊 Nodes: {len(list(graph.vertices()))}")
            st.sidebar.info(f"🔗 Edges: {len(list(graph.edges()))}")
            
            sim = st.session_state.sim
            if hasattr(sim, 'completed_orders'):
                completed_count = len(sim.completed_orders)
                st.sidebar.info(f"✅ Completed Orders: {completed_count}")
                
                if hasattr(sim, 'active_orders'):
                    active_count = len(sim.active_orders)
                    st.sidebar.info(f"📋 Active Orders: {active_count}")
    else:
        st.sidebar.warning("⚠️ No Simulation")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ System Info")
    st.sidebar.info(
        "**Features:**\n"
        "- Interactive map visualization\n"
        "- Dijkstra optimal pathfinding\n"
        "- Route optimization with recharge\n"
        "- Real-time order tracking\n"
        "- Performance analytics\n"
        "- AVL tree route storage"
    )
    
    try:
        tabs[selected_tab]()
    except Exception as e:
        st.error(f"Error in tab {selected_tab}: {str(e)}")
        st.info("Please check that all required modules are properly installed.")
        import traceback
        with st.expander("Show full error details"):
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
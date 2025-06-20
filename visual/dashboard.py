import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from visual.networkx_adapter import NetworkXAdapter
from datetime import datetime
from visual.avl_visualizer import avl_visualizer

def init_session_state():
    if 'sim' not in st.session_state:
        st.session_state.sim = None
    if 'graph' not in st.session_state:
        st.session_state.graph = None

def run_simulation_tab():
    st.header("🏭 Run Simulation")
    
    col1, col2 = st.columns(2)
    with col1:
        n_nodes = st.slider("Number of nodes", 10, 150, 15, key='nodes')
    with col2:
        min_edges = max(n_nodes - 1, 10)
        m_edges = st.slider("Number of edges", min_edges, 300, 20, key='edges')
    
    n_orders = st.slider("Number of orders", 10, 500, 10, key='orders')
    
    if st.button("🚀 Start Simulation"):
        try:
            graph = SimulationInitializer.create_connected_graph(n_nodes, m_edges)
            sim = Simulation(graph)

            # Vincular clientes a nodos de tipo "cliente"
            client_nodes = [v for v in graph.vertices() if graph.get_node_type(v) == "client"]
            sim.clients = []
            for idx, node in enumerate(client_nodes):
                client_id = f"CLI_{idx}"
                client = sim.generate_clients(client_id=client_id)
                client.node_id = node  # Guarda el nodo asociado

            sim.process_orders(n_orders)

            # --- ACTUALIZAR total_orders de cada cliente ---
            for client in sim.clients:
                client.total_orders = sum(
                    1 for order in sim.active_orders + sim.completed_orders
                    if hasattr(client, "node_id") and order.destination == client.node_id
                )

            st.session_state.graph = graph
            st.session_state.sim = sim
            st.success("✅ Simulation completed successfully!")
            
            # Mostrar resumen
            st.subheader("Simulation Summary")
            cols = st.columns(3)
            cols[0].metric("Total Nodes", n_nodes)
            cols[1].metric("Total Edges", m_edges)
            cols[2].metric("Orders Processed", n_orders)
            
            # --- NUEVO: calcular y guardar el layout ---
            nx_graph = NetworkXAdapter.to_networkx(graph)
            pos = nx.spring_layout(nx_graph, seed=42)  # Usa un seed para que siempre sea igual
            st.session_state.graph_pos = pos  # Guardar posiciones en session_state

            # Mostrar gráfico del grafo (estilo base)
            fig = plt.figure(figsize=(10, 8))
            NetworkXAdapter.draw_graph(graph, pos=pos)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

def explore_network_tab():
    st.header("🗺️ Explore Network")
    init_session_state()
    
    if st.session_state.sim is None:
        st.warning("Please run a simulation first from the 'Run Simulation' tab")
        return
    
    graph = st.session_state.graph
    sim = st.session_state.sim

    pos = st.session_state.get("graph_pos", None)
    if pos is None:
        st.warning("No graph layout found. Please run a simulation first.")
        return

    nodes = list(graph.vertices())
    node_names = [str(v) for v in nodes]
    
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("Origin", node_names, key='origin')
    with col2:
        destination = st.selectbox("Destination", node_names, key='destination')

    # Botón para calcular ruta
    if st.button("🔍 Calculate Route"):
        origin_node = next(v for v in nodes if str(v) == origin)
        dest_node = next(v for v in nodes if str(v) == destination)    
        route = sim.find_route_with_recharge(origin_node, dest_node)
        if route:
            st.session_state.show_route = True
            st.session_state.last_route = route
            st.session_state.route_message = f"**Route:** {route.path_str()} | **Cost:** {route.cost}"
        else:
            st.session_state.show_route = False
            st.session_state.last_route = None
            st.session_state.route_message = "No valid route found with current battery limit"

    # Mostrar el grafo base o con la ruta resaltada según el estado
    route = st.session_state.get("last_route", None)
    show_route = st.session_state.get("show_route", False)
    route_message = st.session_state.get("route_message", "")

    st.subheader("Network Graph")
    fig = plt.figure(figsize=(10, 8))
    if show_route and route:
        NetworkXAdapter.draw_graph(graph, highlight_path=route.path, pos=pos)
    else:
        NetworkXAdapter.draw_graph(graph, highlight_path=None, pos=pos)
    st.pyplot(fig)

    # Mostrar mensaje de ruta
    if route_message:
        if show_route and route:
            st.success(route_message)
        else:
            st.error(route_message)

    # Mostrar detalles de la ruta si existe
    # --- BOTÓN COMPLETAR ORDEN SOLO SI HAY RUTA Y ORDEN ---
    if show_route and route:
        st.subheader("Route Details")
        cols = st.columns(3)
        cols[0].metric("Total Nodes", len(route.path))
        cols[1].metric("Total Cost", route.cost)
        recharge_stops = sum(1 for node in route.path 
                            if graph.get_node_type(node) == 'recharge')
        cols[2].metric("Recharge Stops", recharge_stops)

        # --- Mostrar botón solo si hay orden coincidente ---
        matching_orders = [
            order for order in sim.active_orders
            if str(order.origin) == origin and str(order.destination) == destination and order.status != "completed"
        ]
        if matching_orders:
            if st.button("✅ Completar Orden", key="complete_order_btn"):
                sorted_orders = sorted(
                    matching_orders,
                    key=lambda o: getattr(o, "priority", 9999)
                )
                for order in sorted_orders:
                    order.route = route
                    order.cost = route.cost
                    order.status = "completed"
                    order.completed_at = datetime.now()
                    sim.completed_orders.append(order)
                    sim.active_orders.remove(order)
                    # --- Insertar la ruta en el AVL ---
                    sim.route_avl.insert(route.path_str(), route)
                    st.success("Order marked as completed!")
                    st.session_state.show_route = False
                    st.session_state.last_route = None
                    st.session_state.route_message = ""
                    break
        else:
            st.info("No matching active orders for this route.")

def clients_orders_tab():
    st.header("📦 Clients & Orders")
    init_session_state()
    
    if st.session_state.sim is None:
        st.warning("Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    # --- Clients Section ---
    st.subheader("Clients")
    if hasattr(sim, "clients"):
        clients = sim.clients
        if clients:
            for client in clients:
                if hasattr(client, "to_dict"):
                    st.json(client.to_dict(), expanded=True)
                elif hasattr(client, "__dict__"):
                    st.json(client.__dict__, expanded=True)
                else:
                    st.json(str(client), expanded=True)
        else:
            st.info("No clients found.")
    else:
        st.info("No clients data available in simulation.")

    # --- Orders Section ---
    st.subheader("Orders")
    orders = []
    if hasattr(sim, "active_orders"):
        orders.extend(sim.active_orders)
    if hasattr(sim, "completed_orders"):
        orders.extend(sim.completed_orders)
    if orders:
        for order in orders:
            if hasattr(order, "to_dict"):
                st.json(order.to_dict(), expanded=True)
            elif hasattr(order, "__dict__"):
                st.json(order.__dict__, expanded=True)
            else:
                st.json(str(order), expanded=True)
    else:
        st.info("No orders found.")

def route_analytics_tab():
    st.header("📊 Route Analytics")
    init_session_state()
    
    if st.session_state.sim is None:
        st.warning("Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    
    st.subheader("Most Frequent Routes")
    top_routes = sim.get_most_frequent_routes(5)
    
    if not top_routes:
        st.info("No routes recorded yet")
    else:
        for i, (route_str, route) in enumerate(top_routes, 1):
            st.write(f"{i}. **{route_str}** (Used {route.frequency} times)")
        
        st.subheader("AVL Tree Visualization")
        st.info("This shows the structure of the AVL tree storing all routes")
        avl_visualizer(sim.route_avl.root)

def general_stats_tab():
    st.header("📈 General Statistics")
    init_session_state()
    
    if st.session_state.sim is None:
        st.warning("Please run a simulation first from the 'Run Simulation' tab")
        return
    
    sim = st.session_state.sim
    graph = st.session_state.graph
    
    # Estadísticas de nodos
    node_types = {}
    for node in graph.vertices():
        node_type = graph.get_node_type(node)
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    st.subheader("Node Distribution")
    fig1, ax1 = plt.subplots()
    ax1.pie(node_types.values(), labels=node_types.keys(), autopct='%1.1f%%')
    ax1.axis('equal')
    st.pyplot(fig1)
    
    # Estadísticas de visitas
    visit_stats = sim.get_node_visit_stats()
    
    st.subheader("Most Visited Nodes by Role")
    if not visit_stats:
        st.info("No node visit data available")
        return

    # Inicializar diccionario de visitas por rol con todos los nodos (aunque no hayan sido visitados)
    role_visits = {"client": [], "warehouse": [], "recharge": []}
    # Crear un set de nodos visitados para acceso rápido
    visited_dict = {str(node): visits for node, visits in visit_stats}
    for node in graph.vertices():
        node_type = graph.get_node_type(node)
        if node_type in role_visits:
            visits = visited_dict.get(str(node), 0)
            role_visits[node_type].append((str(node), visits))

    # Mostrar un gráfico para cada rol específico
    for role in ["client", "warehouse", "recharge"]:
        nodes_visits = sorted(role_visits[role], key=lambda x: x[1], reverse=True)[:10]  # Top 10 por rol
        if nodes_visits:
            nodes, visits = zip(*nodes_visits)
            st.markdown(f"**Role: {role.capitalize()}**")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.barh(nodes, visits)
            ax.set_xlabel("Number of Visits")
            ax.set_title(f"Top 10 Most Visited Nodes ({role.capitalize()})")
            st.pyplot(fig)
            st.markdown("---")
        else:
            st.info(f"No nodes of role: {role.capitalize()} in the graph.")

def main():
    st.set_page_config(
        page_title="Drone Logistics System",
        page_icon="🚁",
        layout="wide"
    )
    
    st.sidebar.title("Navigation")
    tabs = {
        "🏭 Run Simulation": run_simulation_tab,
        "🗺️ Explore Network": explore_network_tab,
        "📦 Clients & Orders": clients_orders_tab,
        "📊 Route Analytics": route_analytics_tab,
        "📈 General Statistics": general_stats_tab
    }
    
    selected_tab = st.sidebar.radio("Go to", list(tabs.keys()))
    tabs[selected_tab]()

if __name__ == "__main__":
    main()
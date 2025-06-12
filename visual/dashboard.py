import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from sim.simulation import Simulation
from sim.init_simulation import SimulationInitializer
from visual.networkx_adapter import NetworkXAdapter
from datetime import datetime

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
            sim.process_orders(n_orders)
            
            st.session_state.graph = graph
            st.session_state.sim = sim
            st.success("✅ Simulation completed successfully!")
            
            # Mostrar resumen
            st.subheader("Simulation Summary")
            cols = st.columns(3)
            cols[0].metric("Total Nodes", n_nodes)
            cols[1].metric("Total Edges", m_edges)
            cols[2].metric("Orders Processed", n_orders)
            
            # Mostrar gráfico del grafo
            fig = plt.figure(figsize=(10, 8))
            NetworkXAdapter.draw_graph(graph)
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
    
    nodes = list(graph.vertices())
    node_names = [str(v) for v in nodes]
    
    col1, col2 = st.columns(2)
    with col1:
        origin = st.selectbox("Origin", node_names, key='origin')
    with col2:
        destination = st.selectbox("Destination", node_names, key='destination')
    
    # --- Guardar selección en session_state ---
    if "last_route" not in st.session_state:
        st.session_state.last_route = None
    if "last_origin" not in st.session_state:
        st.session_state.last_origin = None
    if "last_destination" not in st.session_state:
        st.session_state.last_destination = None
    
    if st.button("🔍 Calculate Route"):
        origin_node = next(v for v in nodes if str(v) == origin)
        dest_node = next(v for v in nodes if str(v) == destination)    
        route = sim.find_route_with_recharge(origin_node, dest_node)
        
        if route:
            st.success(f"**Route:** {route.path_str()} | **Cost:** {route.cost}")
            
            # Mostrar gráfico con ruta resaltada
            fig = plt.figure(figsize=(10, 8))
            NetworkXAdapter.draw_graph(graph, route.path)
            st.pyplot(fig)
            
            # Mostrar detalles de la ruta
            st.subheader("Route Details")
            cols = st.columns(3)
            cols[0].metric("Total Nodes", len(route.path))
            cols[1].metric("Total Cost", route.cost)
            recharge_stops = sum(1 for node in route.path 
                               if graph.get_node_type(node) == 'recharge')
            cols[2].metric("Recharge Stops", recharge_stops)

            # Botón para completar la orden
            if st.button("✅ Completar Orden"):
                # Busca la orden activa correspondiente (puedes ordenar por prioridad si quieres)
                sorted_orders = sorted(
                    sim.active_orders,
                    key=lambda o: getattr(o, "priority", 9999)
                )
                for order in sorted_orders:
                    if (str(order.origin) == origin and str(order.destination) == destination and order.status != "completed"):
                        order.route = route
                        order.cost = route.cost
                        order.status = "completed"
                        order.completed_at = datetime.now()
                        sim.completed_orders.append(order)
                        sim.active_orders.remove(order)
                        st.success("Order marked as completed!")
                        break
        else:
            st.error("No valid route found with current battery limit")

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
                # Si client es un objeto, muestra su __dict__ o usa un método to_dict()
                st.json(client.__dict__ if hasattr(client, "__dict__") else str(client), expanded=True)
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
            # Si order es un objeto, muestra su __dict__ o usa un método to_dict()
            st.json(order.__dict__ if hasattr(order, "__dict__") else str(order), expanded=True)
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
        
        # Visualización del árbol AVL
        st.subheader("AVL Tree Visualization")
        st.info("This shows the structure of the AVL tree storing all routes")
        
        # Crear representación simplificada del AVL
        G = nx.Graph()
        nodes = []
        
        def add_nodes(node):
            if node:
                nodes.append(node.key)
                if node.left:
                    G.add_edge(node.key, node.left.key)
                    add_nodes(node.left)
                if node.right:
                    G.add_edge(node.key, node.right.key)
                    add_nodes(node.right)
        
        add_nodes(sim.route_avl.root)
        
        if nodes:
            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, with_labels=True, node_size=2000, node_color='lightblue', 
                   font_size=10, font_weight='bold')
            st.pyplot(plt)
        else:
            st.warning("AVL tree is empty")

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
    
    st.subheader("Most Visited Nodes")
    if not visit_stats:
        st.info("No node visit data available")
    else:
        top_nodes = visit_stats[:10]
        nodes, visits = zip(*top_nodes)
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        ax2.barh(nodes, visits)
        ax2.set_xlabel("Number of Visits")
        ax2.set_title("Top 10 Most Visited Nodes")
        st.pyplot(fig2)

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
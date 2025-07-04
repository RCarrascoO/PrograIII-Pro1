import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para generar PDFs
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from datetime import datetime
import io
import streamlit as st

class PDFReportGenerator:
    def __init__(self, sim, graph):
        self.sim = sim
        self.graph = graph
        self.fig_size = (10, 6)
        
    def generate_report(self):
        """
        Genera un reporte PDF completo con todas las estadísticas
        """
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        
        with PdfPages(buffer) as pdf:
            # Página 1: Portada
            self._create_cover_page(pdf)
            
            # Página 2: Estadísticas generales
            self._create_general_stats_page(pdf)
            
            # Página 3: Rutas más frecuentes
            self._create_frequent_routes_page(pdf)
            
            # Página 4: Distribución de nodos
            self._create_node_distribution_page(pdf)
            
            # Página 5: Estadísticas de visitas
            self._create_visit_stats_page(pdf)
            
            # Página 6: Análisis de clientes
            self._create_client_analysis_page(pdf)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_cover_page(self, pdf):
        """Crea la página de portada"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.axis('off')
        
        # Título principal
        ax.text(0.5, 0.8, '🚁 DRONE LOGISTICS SYSTEM', 
                fontsize=24, fontweight='bold', ha='center', va='center')
        
        # Subtítulo
        ax.text(0.5, 0.7, 'Reporte de Análisis de Rutas', 
                fontsize=18, ha='center', va='center', style='italic')
        
        # Información del algoritmo
        ax.text(0.5, 0.6, 'Algoritmo: Dijkstra (Rutas Óptimas)', 
                fontsize=14, ha='center', va='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        
        # Fecha y hora
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(0.5, 0.4, f'Generado: {current_time}', 
                fontsize=12, ha='center', va='center')
        
        # Estadísticas básicas
        total_nodes = len(list(self.graph.vertices()))
        total_edges = len(list(self.graph.edges()))
        completed_orders = len(self.sim.completed_orders)
        active_orders = len(self.sim.active_orders)
        
        stats_text = f"""RESUMEN EJECUTIVO:
        
• Total de Nodos: {total_nodes}
• Total de Aristas: {total_edges}  
• Órdenes Completadas: {completed_orders}
• Órdenes Activas: {active_orders}
• Algoritmo de Enrutamiento: Dijkstra"""
        
        ax.text(0.5, 0.2, stats_text, 
                fontsize=11, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray'))
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_general_stats_page(self, pdf):
        """Crea la página de estadísticas generales"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
        
        # Estadísticas de órdenes
        completed_orders = len(self.sim.completed_orders)
        active_orders = len(self.sim.active_orders)
        
        if completed_orders > 0:
            total_distance = sum(getattr(order, 'cost', 0) for order in self.sim.completed_orders)
            avg_distance = total_distance / completed_orders
            
            # Contar paradas de recarga
            total_recharge_stops = 0
            for order in self.sim.completed_orders:
                if hasattr(order, 'route') and order.route:
                    recharge_stops = sum(1 for node in order.route.path 
                                       if self.graph.get_node_type(node) == 'recharge')
                    total_recharge_stops += recharge_stops
            
            avg_recharge_stops = total_recharge_stops / completed_orders
        else:
            total_distance = 0
            avg_distance = 0
            avg_recharge_stops = 0
        
        # Gráfico 1: Estado de órdenes
        if completed_orders > 0 or active_orders > 0:
            orders_data = ['Completadas', 'Activas']
            orders_values = [completed_orders, active_orders]
            colors1 = ['#00FF00', '#ff6b6b']
            ax1.pie(orders_values, labels=orders_data, autopct='%1.1f%%', colors=colors1)
            ax1.set_title('Estado de Órdenes', fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'No hay órdenes disponibles', ha='center', va='center')
            ax1.set_title('Estado de Órdenes', fontweight='bold')
        
        # Gráfico 2: Métricas de rendimiento
        metrics = ['Dist. Total', 'Dist. Prom.', 'Recarga Prom.']
        values = [total_distance, avg_distance, avg_recharge_stops]
        
        bars = ax2.bar(metrics, values, color=['#45b7d1', '#96ceb4', '#ffeaa7'])
        ax2.set_title('Métricas de Rendimiento', fontweight='bold')
        ax2.set_ylabel('Valores')
        
        # Agregar valores en las barras
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.2f}', ha='center', va='bottom')
        
        # Gráfico 3: Distribución de tipos de nodo
        node_types = {}
        for node in self.graph.vertices():
            node_type = self.graph.get_node_type(node)
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        if node_types:
            colors3 = ['#ff6b6b', '#00FF00', '#45b7d1', '#96ceb4', '#ffeaa7']
            ax3.pie(node_types.values(), labels=node_types.keys(), 
                   autopct='%1.1f%%', colors=colors3[:len(node_types)])
            ax3.set_title('Distribución de Tipos de Nodo', fontweight='bold')
        
        # Gráfico 4: Información del algoritmo
        ax4.axis('off')
        algorithm_info = """ALGORITMO DIJKSTRA

✓ Garantiza rutas óptimas
✓ Considera restricciones de batería
✓ Optimiza paradas de recarga
✓ Minimiza costos totales

BENEFICIOS:
• Eficiencia energética
• Menor tiempo de entrega
• Optimización de recursos
• Reducción de costos operativos"""
        
        ax4.text(0.1, 0.9, algorithm_info, 
                fontsize=10, ha='left', va='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcyan'))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_frequent_routes_page(self, pdf):
        """Crea la página de rutas más frecuentes"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Obtener rutas más frecuentes
        try:
            top_routes = self.sim.get_most_frequent_routes(10)
            
            if top_routes:
                route_names = []
                frequencies = []
                costs = []
                
                for i, route_data in enumerate(top_routes):
                    if isinstance(route_data, tuple) and len(route_data) == 2:
                        route_str, route = route_data
                        frequency = getattr(route, 'frequency', 1)
                        cost = getattr(route, 'cost', 0)
                        
                        # Acortar nombres de rutas para mejor visualización
                        short_name = f"Ruta {i+1}"
                        route_names.append(short_name)
                        frequencies.append(frequency)
                        costs.append(cost)
                
                if route_names:
                    # Gráfico de frecuencias
                    bars1 = ax1.bar(route_names, frequencies, color='#00FF00')
                    ax1.set_title('Rutas Más Frecuentes', fontweight='bold')
                    ax1.set_xlabel('Rutas')
                    ax1.set_ylabel('Frecuencia de Uso')
                    
                    # Agregar valores en las barras
                    for bar, freq in zip(bars1, frequencies):
                        height = bar.get_height()
                        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{freq}', ha='center', va='bottom')
                    
                    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
                    
                    # Gráfico de costos
                    bars2 = ax2.bar(route_names, costs, color='#45b7d1')
                    ax2.set_title('Costos de Rutas Frecuentes', fontweight='bold')
                    ax2.set_xlabel('Rutas')
                    ax2.set_ylabel('Costo')
                    
                    # Agregar valores en las barras
                    for bar, cost in zip(bars2, costs):
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{cost:.1f}', ha='center', va='bottom')
                    
                    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                else:
                    ax1.text(0.5, 0.5, 'No hay datos de rutas disponibles', 
                            ha='center', va='center', transform=ax1.transAxes)
                    ax2.text(0.5, 0.5, 'No hay datos de costos disponibles', 
                            ha='center', va='center', transform=ax2.transAxes)
            else:
                ax1.text(0.5, 0.5, 'No hay rutas frecuentes registradas', 
                        ha='center', va='center', transform=ax1.transAxes)
                ax2.text(0.5, 0.5, 'Complete algunas órdenes para ver datos', 
                        ha='center', va='center', transform=ax2.transAxes)
                
        except Exception as e:
            ax1.text(0.5, 0.5, f'Error al obtener rutas: {str(e)}', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, 'No se pudieron cargar los datos', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_node_distribution_page(self, pdf):
        """Crea la página de distribución de nodos"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Contar tipos de nodos
        node_types = {}
        for node in self.graph.vertices():
            node_type = self.graph.get_node_type(node)
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        if node_types:
            colors = ['#ff6b6b', '#00FF00', '#45b7d1', '#96ceb4', '#ffeaa7']
            wedges, texts, autotexts = ax.pie(node_types.values(), 
                                             labels=node_types.keys(), 
                                             autopct='%1.1f%%', 
                                             colors=colors[:len(node_types)],
                                             startangle=90)
            
            ax.set_title('Distribución de Tipos de Nodo', fontweight='bold', fontsize=16)
            
            # Mejorar la apariencia del texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Agregar leyenda con conteos
            legend_labels = [f'{k}: {v} nodos' for k, v in node_types.items()]
            ax.legend(wedges, legend_labels, title="Tipos de Nodo", 
                     loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_visit_stats_page(self, pdf):
        """Crea la página de estadísticas de visitas"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        
        try:
            visit_stats = self.sim.get_node_visit_stats()
            
            if visit_stats:
                # Organizar datos por tipo de nodo
                role_visits = {"client": [], "warehouse": [], "recharge": []}
                visited_dict = {str(node): visits for node, visits in visit_stats}
                
                for node in self.graph.vertices():
                    node_type = self.graph.get_node_type(node)
                    if node_type in role_visits:
                        visits = visited_dict.get(str(node), 0)
                        role_visits[node_type].append((str(node), visits))
                
                # Crear gráficos para cada tipo de nodo
                colors = {'client': '#00FF00', 'warehouse': '#ff6b6b', 'recharge': '#45b7d1'}
                titles = {'client': 'Nodos Cliente Más Visitados', 
                         'warehouse': 'Nodos Warehouse Más Visitados', 
                         'recharge': 'Estaciones de Recarga Más Visitadas'}
                
                for idx, (role, ax) in enumerate(zip(["client", "warehouse", "recharge"], axes)):
                    nodes_visits = sorted(role_visits[role], key=lambda x: x[1], reverse=True)[:10]
                    
                    if nodes_visits and any(visits > 0 for _, visits in nodes_visits):
                        nodes, visits = zip(*nodes_visits)
                        
                        bars = ax.barh(nodes, visits, color=colors[role])
                        ax.set_xlabel("Número de Visitas")
                        ax.set_title(titles[role], fontweight='bold')
                        
                        # Agregar valores en las barras
                        for i, bar in enumerate(bars):
                            width = bar.get_width()
                            if width > 0:
                                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                                       f'{int(width)}', ha='left', va='center')
                    else:
                        ax.text(0.5, 0.5, f'No hay datos de visitas para {role}', 
                               ha='center', va='center', transform=ax.transAxes)
                        ax.set_title(titles[role], fontweight='bold')
            else:
                for ax, title in zip(axes, ["Cliente", "Warehouse", "Recarga"]):
                    ax.text(0.5, 0.5, f'No hay estadísticas de visitas para {title}', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(f'Nodos {title} Más Visitados', fontweight='bold')
                    
        except Exception as e:
            for ax in axes:
                ax.text(0.5, 0.5, f'Error al obtener estadísticas: {str(e)}', 
                       ha='center', va='center', transform=ax.transAxes)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    def _create_client_analysis_page(self, pdf):
        """Crea la página de análisis de clientes"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Análisis de clientes
        if hasattr(self.sim, 'clients') and self.sim.clients:
            # Distribución por tipo de cliente
            client_types = {}
            client_orders = []
            
            for client in self.sim.clients:
                client_type = getattr(client, 'type_', 'unknown')
                client_types[client_type] = client_types.get(client_type, 0) + 1
                
                total_orders = getattr(client, 'total_orders', 0)
                client_orders.append(total_orders)
            
            # Gráfico 1: Distribución por tipo de cliente
            if client_types:
                colors = ['#ff6b6b', '#00FF00', '#45b7d1', '#96ceb4', '#ffeaa7']
                ax1.pie(client_types.values(), labels=client_types.keys(), 
                       autopct='%1.1f%%', colors=colors[:len(client_types)])
                ax1.set_title('Distribución por Tipo de Cliente', fontweight='bold')
            
            # Gráfico 2: Estadísticas de órdenes por cliente
            if client_orders:
                # Crear rangos de órdenes
                order_ranges = {'0 órdenes': 0, '1-5 órdenes': 0, '6-10 órdenes': 0, '11+ órdenes': 0}
                
                for orders in client_orders:
                    if orders == 0:
                        order_ranges['0 órdenes'] += 1
                    elif 1 <= orders <= 5:
                        order_ranges['1-5 órdenes'] += 1
                    elif 6 <= orders <= 10:
                        order_ranges['6-10 órdenes'] += 1
                    else:
                        order_ranges['11+ órdenes'] += 1
                
                # Filtrar rangos con valores > 0
                filtered_ranges = {k: v for k, v in order_ranges.items() if v > 0}
                
                if filtered_ranges:
                    bars = ax2.bar(filtered_ranges.keys(), filtered_ranges.values(), 
                                  color='#45b7d1')
                    ax2.set_title('Distribución de Órdenes por Cliente', fontweight='bold')
                    ax2.set_xlabel('Rango de Órdenes')
                    ax2.set_ylabel('Número de Clientes')
                    
                    # Agregar valores en las barras
                    for bar, value in zip(bars, filtered_ranges.values()):
                        height = bar.get_height()
                        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{value}', ha='center', va='bottom')
                    
                    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                else:
                    ax2.text(0.5, 0.5, 'No hay datos de órdenes de clientes', 
                            ha='center', va='center', transform=ax2.transAxes)
            else:
                ax2.text(0.5, 0.5, 'No hay datos de órdenes de clientes', 
                        ha='center', va='center', transform=ax2.transAxes)
        else:
            ax1.text(0.5, 0.5, 'No hay datos de clientes disponibles', 
                    ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, 'No hay datos de clientes disponibles', 
                    ha='center', va='center', transform=ax2.transAxes)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
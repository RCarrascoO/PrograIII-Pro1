import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para generar PDFs
from matplotlib.backends.backend_pdf import PdfPages
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
            
            # Página 2: Información del algoritmo y distribución de nodos
            self._create_algorithm_and_nodes_page(pdf)
            
            # Página 3: Estadísticas de visitas por nodo
            self._create_visit_stats_page(pdf)
            
            # Página 4: Análisis de clientes
            self._create_client_analysis_page(pdf)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_cover_page(self, pdf):
        """Crea la página de portada"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        ax.axis('off')
        
        # Título principal
        ax.text(0.5, 0.8, 'DRONE LOGISTICS SYSTEM', 
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
    
    def _create_algorithm_and_nodes_page(self, pdf):
        """Crea la página con información del algoritmo y distribución de nodos"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Lado izquierdo: Información del algoritmo
        ax1.axis('off')
        algorithm_info = """ALGORITMO DIJKSTRA

✓ Garantiza rutas óptimas
✓ Considera restricciones de batería
✓ Optimiza paradas de recarga
✓ Minimiza costos totales

BENEFICIOS:
• Eficiencia energética
• Menor tiempo de entrega
• Optimización de recursos
• Reducción de costos operativos

CARACTERÍSTICAS:
• Complejidad: O((V + E) log V)
• Grafo no dirigido
• Soporte para múltiples destinos
• Manejo de restricciones de batería"""
        
        ax1.text(0.1, 0.9, algorithm_info, 
                fontsize=11, ha='left', va='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='lightcyan'))
        
        ax1.set_title('Información del Algoritmo', fontweight='bold', fontsize=14)
        
        # Lado derecho: Distribución de tipos de nodo
        node_types = {}
        for node in self.graph.vertices():
            node_type = self.graph.get_node_type(node)
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        if node_types:
            colors = ['#ff6b6b', '#00FF00', '#45b7d1', '#96ceb4', '#ffeaa7']
            wedges, texts, autotexts = ax2.pie(node_types.values(), 
                                             labels=node_types.keys(), 
                                             autopct='%1.1f%%', 
                                             colors=colors[:len(node_types)],
                                             startangle=90)
            
            ax2.set_title('Distribución de Tipos de Nodo', fontweight='bold', fontsize=14)
            
            # Mejorar la apariencia del texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Agregar leyenda con conteos
            legend_labels = [f'{k}: {v} nodos' for k, v in node_types.items()]
            ax2.legend(wedges, legend_labels, title="Tipos de Nodo", 
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
        """Crea la página de análisis de clientes - SOLO distribución de órdenes"""
        fig, ax = plt.subplots(figsize=self.fig_size)
        
        # Análisis de clientes
        if hasattr(self.sim, 'clients') and self.sim.clients:
            client_orders = []
            
            for client in self.sim.clients:
                total_orders = getattr(client, 'total_orders', 0)
                client_orders.append(total_orders)
            
            # Estadísticas de órdenes por cliente
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
                    bars = ax.bar(filtered_ranges.keys(), filtered_ranges.values(), 
                                  color='#45b7d1')
                    ax.set_title('Distribución de Órdenes por Cliente', fontweight='bold', fontsize=16)
                    ax.set_xlabel('Rango de Órdenes')
                    ax.set_ylabel('Número de Clientes')
                    
                    # Agregar valores en las barras
                    for bar, value in zip(bars, filtered_ranges.values()):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'{value}', ha='center', va='bottom')
                    
                    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                    
                    # Agregar información estadística
                    total_clients = len(client_orders)
                    avg_orders = sum(client_orders) / total_clients if total_clients > 0 else 0
                    max_orders = max(client_orders) if client_orders else 0
                    
                    stats_text = f"""ESTADÍSTICAS DE CLIENTES:
                    
• Total de Clientes: {total_clients}
• Promedio de Órdenes: {avg_orders:.2f}
• Máximo de Órdenes: {max_orders}
• Clientes Activos: {sum(1 for o in client_orders if o > 0)}"""
                    
                    ax.text(0.98, 0.98, stats_text, 
                           transform=ax.transAxes,
                           fontsize=10, ha='right', va='top',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow'))
                else:
                    ax.text(0.5, 0.5, 'No hay datos de órdenes de clientes', 
                            ha='center', va='center', transform=ax.transAxes)
                    ax.set_title('Distribución de Órdenes por Cliente', fontweight='bold', fontsize=16)
            else:
                ax.text(0.5, 0.5, 'No hay datos de órdenes de clientes', 
                        ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Distribución de Órdenes por Cliente', fontweight='bold', fontsize=16)
        else:
            ax.text(0.5, 0.5, 'No hay datos de clientes disponibles', 
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Distribución de Órdenes por Cliente', fontweight='bold', fontsize=16)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
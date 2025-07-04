import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from typing import List, Dict, Optional, Tuple

class FlightSummary:
    """Calculadora de resumen de trayectos de vuelo"""
    
    def __init__(self, simulation):
        """
        Inicializa el calculador de resumen de vuelos
        
        Args:
            simulation: Objeto de simulación con órdenes completadas
        """
        self.sim = simulation
        self.graph = getattr(simulation, 'graph', None)
    
    def calculate_route_metrics(self, route) -> Optional[Dict]:
        """
        Calcula métricas detalladas de una ruta específica
        
        Args:
            route: Objeto ruta con path y cost
            
        Returns:
            Diccionario con métricas o None si no hay datos
        """
        if not route or not hasattr(route, 'path') or not route.path:
            return None
        
        # Calcular métricas básicas
        total_nodes = len(route.path)
        total_distance = getattr(route, 'cost', 0)
        
        # Contar tipos de nodos si hay grafo disponible
        recharge_stops = 0
        client_visits = 0
        warehouse_visits = 0
        
        if self.graph:
            for node in route.path:
                node_type = self.graph.get_node_type(node)
                if node_type == 'recharge':
                    recharge_stops += 1
                elif node_type == 'client':
                    client_visits += 1
                elif node_type == 'warehouse':
                    warehouse_visits += 1
        
        # Calcular eficiencia
        useful_nodes = client_visits + warehouse_visits
        efficiency_score = (useful_nodes / total_distance * 100) if total_distance > 0 else 0
        
        # Calcular velocidad promedio (asumiendo tiempo proporcional a distancia)
        estimated_time = total_distance * 0.1  # 10 minutos por unidad de distancia
        avg_speed = total_distance / estimated_time if estimated_time > 0 else 0
        
        metrics = {
            'total_distance': round(total_distance, 2),
            'total_nodes': total_nodes,
            'recharge_stops': recharge_stops,
            'client_visits': client_visits,
            'warehouse_visits': warehouse_visits,
            'useful_nodes': useful_nodes,
            'efficiency_score': round(efficiency_score, 2),
            'estimated_time': round(estimated_time, 2),
            'avg_speed': round(avg_speed, 2),
            'path_string': route.path_str() if hasattr(route, 'path_str') else str(route.path),
            'complexity': self._calculate_complexity(route)
        }
        
        return metrics
    
    def _calculate_complexity(self, route) -> str:
        """
        Calcula la complejidad de una ruta
        
        Args:
            route: Objeto ruta
            
        Returns:
            String indicando complejidad: 'Simple', 'Medium', 'Complex'
        """
        if not route or not route.path:
            return 'Unknown'
        
        total_nodes = len(route.path)
        
        if total_nodes <= 3:
            return 'Simple'
        elif total_nodes <= 6:
            return 'Medium'
        else:
            return 'Complex'
    
    def get_flight_summary_data(self) -> List[Dict]:
        """
        Obtiene datos resumidos de todos los vuelos completados
        
        Returns:
            Lista de diccionarios con datos de vuelos
        """
        if not hasattr(self.sim, 'completed_orders'):
            return []
        
        summary_data = []
        
        for i, order in enumerate(self.sim.completed_orders, 1):
            if hasattr(order, 'route') and order.route:
                metrics = self.calculate_route_metrics(order.route)
                
                if metrics:
                    flight_data = {
                        'Flight #': i,
                        'Order ID': getattr(order, 'order_id', f'ORD_{i}'),
                        'Origin': str(order.origin),
                        'Destination': str(order.destination),
                        'Total Distance': metrics['total_distance'],
                        'Total Nodes': metrics['total_nodes'],
                        'Recharge Stops': metrics['recharge_stops'],
                        'Client Visits': metrics['client_visits'],
                        'Warehouse Visits': metrics['warehouse_visits'],
                        'Useful Nodes': metrics['useful_nodes'],
                        'Efficiency Score': metrics['efficiency_score'],
                        'Estimated Time (min)': metrics['estimated_time'],
                        'Avg Speed': metrics['avg_speed'],
                        'Complexity': metrics['complexity'],
                        'Route Path': metrics['path_string'],
                        'Completed At': getattr(order, 'completed_at', datetime.now()),
                        'Priority': getattr(order, 'priority', 'Normal')
                    }
                    
                    summary_data.append(flight_data)
        
        return summary_data
    
    def display_summary_table(self):
        """Muestra tabla resumida de vuelos con métricas"""
        st.subheader("✈️ Flight Summary Table")
        
        data = self.get_flight_summary_data()
        
        if not data:
            st.info("🚁 No completed flights found. Complete some orders to see flight data.")
            return
        
        df = pd.DataFrame(data)
        
        # Mostrar métricas generales en columnas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Flights", 
                len(data),
                help="Total number of completed flights"
            )
        
        with col2:
            avg_distance = df['Total Distance'].mean()
            st.metric(
                "Avg Distance", 
                f"{avg_distance:.2f}",
                help="Average distance per flight"
            )
        
        with col3:
            total_recharge = df['Recharge Stops'].sum()
            st.metric(
                "Total Recharge Stops", 
                total_recharge,
                help="Total recharge stops across all flights"
            )
        
        with col4:
            avg_efficiency = df['Efficiency Score'].mean()
            st.metric(
                "Avg Efficiency", 
                f"{avg_efficiency:.2f}%",
                help="Average efficiency score"
            )
        
        # Métricas adicionales
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            total_time = df['Estimated Time (min)'].sum()
            st.metric(
                "Total Flight Time", 
                f"{total_time:.1f} min",
                help="Total estimated flight time"
            )
        
        with col6:
            avg_speed = df['Avg Speed'].mean()
            st.metric(
                "Avg Speed", 
                f"{avg_speed:.2f}",
                help="Average flight speed"
            )
        
        with col7:
            complex_flights = len(df[df['Complexity'] == 'Complex'])
            st.metric(
                "Complex Routes", 
                complex_flights,
                help="Number of complex routes"
            )
        
        with col8:
            total_useful = df['Useful Nodes'].sum()
            st.metric(
                "Total Useful Stops", 
                total_useful,
                help="Total useful stops (clients + warehouses)"
            )
        
        # Tabla interactiva con configuración de columnas
        st.subheader("📊 Detailed Flight Data")
        
        # Seleccionar columnas a mostrar
        display_cols = st.multiselect(
            "Select columns to display:",
            options=df.columns.tolist(),
            default=[
                'Flight #', 'Origin', 'Destination', 'Total Distance',
                'Recharge Stops', 'Efficiency Score', 'Complexity'
            ]
        )
        
        if display_cols:
            display_df = df[display_cols]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Flight #": st.column_config.NumberColumn("Flight #", format="%d"),
                    "Total Distance": st.column_config.NumberColumn("Distance", format="%.2f"),
                    "Efficiency Score": st.column_config.NumberColumn("Efficiency %", format="%.2f%%"),
                    "Estimated Time (min)": st.column_config.NumberColumn("Time (min)", format="%.1f"),
                    "Avg Speed": st.column_config.NumberColumn("Speed", format="%.2f"),
                    "Completed At": st.column_config.DatetimeColumn("Completed", format="DD/MM/YYYY HH:mm")
                }
            )
    
    def display_flight_charts(self):
        """Muestra gráficos de análisis de vuelos"""
        data = self.get_flight_summary_data()
        
        if not data:
            st.info("No flight data available for charts.")
            return
        
        df = pd.DataFrame(data)
        
        # Crear tabs para diferentes tipos de gráficos
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Efficiency Analysis", 
            "🔋 Distance vs Recharge", 
            "🎯 Stop Distribution", 
            "⚡ Performance Metrics"
        ])
        
        with tab1:
            st.subheader("Flight Efficiency Analysis")
            
            # Gráfico de eficiencia por vuelo
            fig_efficiency = px.bar(
                df, 
                x='Flight #', 
                y='Efficiency Score',
                color='Complexity',
                title="Flight Efficiency Score by Flight Number",
                hover_data=['Origin', 'Destination', 'Total Distance']
            )
            fig_efficiency.update_layout(height=400)
            st.plotly_chart(fig_efficiency, use_container_width=True)
            
            # Distribución de eficiencia
            fig_dist = px.histogram(
                df,
                x='Efficiency Score',
                nbins=20,
                title="Distribution of Efficiency Scores"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with tab2:
            st.subheader("Distance vs Recharge Analysis")
            
            # Scatter plot distancia vs recargas
            fig_scatter = px.scatter(
                df,
                x='Total Distance',
                y='Recharge Stops',
                size='Total Nodes',
                color='Efficiency Score',
                hover_data=['Flight #', 'Complexity'],
                title="Distance vs Recharge Stops (Size = Total Nodes)"
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Box plot por complejidad
            fig_box = px.box(
                df,
                x='Complexity',
                y='Total Distance',
                title="Distance Distribution by Route Complexity"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        
        with tab3:
            st.subheader("Stop Type Distribution")
            
            # Gráfico de barras apiladas
            fig_stops = go.Figure()
            
            fig_stops.add_trace(go.Bar(
                name='Client Visits',
                x=df['Flight #'],
                y=df['Client Visits'],
                marker_color='#4ecdc4'
            ))
            
            fig_stops.add_trace(go.Bar(
                name='Warehouse Visits',
                x=df['Flight #'],
                y=df['Warehouse Visits'],
                marker_color='#ff6b6b'
            ))
            
            fig_stops.add_trace(go.Bar(
                name='Recharge Stops',
                x=df['Flight #'],
                y=df['Recharge Stops'],
                marker_color='#45b7d1'
            ))
            
            fig_stops.update_layout(
                barmode='stack',
                title="Stop Type Distribution by Flight",
                xaxis_title="Flight Number",
                yaxis_title="Number of Stops",
                height=400
            )
            
            st.plotly_chart(fig_stops, use_container_width=True)
        
        with tab4:
            st.subheader("Performance Metrics")
            
            # Métricas de tiempo vs distancia
            fig_time = px.scatter(
                df,
                x='Total Distance',
                y='Estimated Time (min)',
                color='Avg Speed',
                size='Useful Nodes',
                title="Distance vs Estimated Time (Color = Avg Speed)"
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
            # Radar chart de métricas normalizadas
            if len(df) > 0:
                # Normalizar métricas para radar chart
                metrics_for_radar = [
                    'Total Distance', 'Efficiency Score', 'Avg Speed', 
                    'Useful Nodes', 'Total Nodes'
                ]
                
                # Tomar el primer vuelo como ejemplo
                first_flight = df.iloc[0]
                
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        first_flight['Total Distance'] / df['Total Distance'].max() * 100,
                        first_flight['Efficiency Score'],
                        first_flight['Avg Speed'] / df['Avg Speed'].max() * 100,
                        first_flight['Useful Nodes'] / df['Useful Nodes'].max() * 100,
                        first_flight['Total Nodes'] / df['Total Nodes'].max() * 100
                    ],
                    theta=['Distance', 'Efficiency', 'Speed', 'Useful Stops', 'Total Stops'],
                    fill='toself',
                    name=f'Flight #{first_flight["Flight #"]}'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Flight Performance Radar (First Flight Example)"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
    
    def get_best_worst_flights(self) -> Tuple[Optional[pd.Series], Optional[pd.Series]]:
        """
        Obtiene los mejores y peores vuelos por eficiencia
        
        Returns:
            Tuple (mejor_vuelo, peor_vuelo)
        """
        data = self.get_flight_summary_data()
        
        if not data:
            return None, None
        
        df = pd.DataFrame(data)
        
        # Mejor vuelo (mayor eficiencia)
        best_flight = df.loc[df['Efficiency Score'].idxmax()]
        
        # Peor vuelo (menor eficiencia)
        worst_flight = df.loc[df['Efficiency Score'].idxmin()]
        
        return best_flight, worst_flight
    
    def display_flight_comparison(self):
        """Muestra comparación detallada de mejor vs peor vuelo"""
        best, worst = self.get_best_worst_flights()
        
        if best is None or worst is None:
            st.info("Need at least one completed flight for comparison.")
            return
        
        st.subheader("🏆 Flight Performance Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("**🥇 Best Flight (Highest Efficiency)**")
            
            # Métricas del mejor vuelo
            best_metrics = [
                ("Flight #", best['Flight #']),
                ("Route", f"{best['Origin']} → {best['Destination']}"),
                ("Efficiency", f"{best['Efficiency Score']:.2f}%"),
                ("Distance", f"{best['Total Distance']:.2f}"),
                ("Estimated Time", f"{best['Estimated Time (min)']:.1f} min"),
                ("Avg Speed", f"{best['Avg Speed']:.2f}"),
                ("Recharge Stops", best['Recharge Stops']),
                ("Useful Nodes", best['Useful Nodes']),
                ("Complexity", best['Complexity'])
            ]
            
            for label, value in best_metrics:
                st.write(f"**{label}:** {value}")
            
            with st.expander("View Route Path"):
                st.code(best['Route Path'])
        
        with col2:
            st.error("**⚠️ Worst Flight (Lowest Efficiency)**")
            
            # Métricas del peor vuelo
            worst_metrics = [
                ("Flight #", worst['Flight #']),
                ("Route", f"{worst['Origin']} → {worst['Destination']}"),
                ("Efficiency", f"{worst['Efficiency Score']:.2f}%"),
                ("Distance", f"{worst['Total Distance']:.2f}"),
                ("Estimated Time", f"{worst['Estimated Time (min)']:.1f} min"),
                ("Avg Speed", f"{worst['Avg Speed']:.2f}"),
                ("Recharge Stops", worst['Recharge Stops']),
                ("Useful Nodes", worst['Useful Nodes']),
                ("Complexity", worst['Complexity'])
            ]
            
            for label, value in worst_metrics:
                st.write(f"**{label}:** {value}")
            
            with st.expander("View Route Path"):
                st.code(worst['Route Path'])
        
        # Comparación side-by-side
        st.subheader("📊 Side-by-Side Comparison")
        
        comparison_data = {
            'Metric': [
                'Efficiency Score', 'Total Distance', 'Estimated Time (min)',
                'Avg Speed', 'Recharge Stops', 'Useful Nodes', 'Total Nodes'
            ],
            'Best Flight': [
                best['Efficiency Score'], best['Total Distance'], 
                best['Estimated Time (min)'], best['Avg Speed'],
                best['Recharge Stops'], best['Useful Nodes'], best['Total Nodes']
            ],
            'Worst Flight': [
                worst['Efficiency Score'], worst['Total Distance'], 
                worst['Estimated Time (min)'], worst['Avg Speed'],
                worst['Recharge Stops'], worst['Useful Nodes'], worst['Total Nodes']
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Efficiency Score": st.column_config.NumberColumn("Efficiency %", format="%.2f%%"),
                "Total Distance": st.column_config.NumberColumn("Distance", format="%.2f"),
                "Estimated Time (min)": st.column_config.NumberColumn("Time (min)", format="%.1f"),
                "Avg Speed": st.column_config.NumberColumn("Speed", format="%.2f")
            }
        )
    
    def export_summary_data(self) -> Optional[pd.DataFrame]:
        """
        Exporta los datos de resumen como DataFrame
        
        Returns:
            DataFrame con datos de vuelos o None si no hay datos
        """
        data = self.get_flight_summary_data()
        
        if not data:
            return None
        
        return pd.DataFrame(data)
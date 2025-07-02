from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt
import numpy as np
import os
import requests
import datetime
import tempfile

def generate_report(report_type, client_id=None):
    """
    Genera un informe PDF según el tipo solicitado
    
    Args:
        report_type: Tipo de informe ('summary', 'routes', 'client', 'statistics')
        client_id: ID del cliente (solo para informe de tipo 'client')
        
    Returns:
        Ruta del archivo PDF generado
    """
    # Crear carpeta de reportes si no existe
    os.makedirs("reports", exist_ok=True)
    
    # Nombre del archivo según el tipo de informe
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if report_type == "client" and client_id:
        filename = f"reports/client_{client_id}_{timestamp}.pdf"
    else:
        filename = f"reports/{report_type}_{timestamp}.pdf"
    
    # Crear documento PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Estilos personalizados
    title_style = styles["Heading1"]
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Título del informe
    title_text = ""
    if report_type == "summary":
        title_text = "Informe de Resumen del Sistema de Drones"
    elif report_type == "routes":
        title_text = "Informe de Rutas de Drones"
    elif report_type == "client":
        title_text = f"Informe del Cliente (ID: {client_id})"
    elif report_type == "statistics":
        title_text = "Estadísticas del Sistema de Drones"
    
    elements.append(Paragraph(title_text, title_style))
    elements.append(Spacer(1, 12))
    
    # Fecha y hora de generación
    elements.append(Paragraph(f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Contenido según tipo de informe
    try:
        if report_type == "summary":
            generate_summary_content(elements, styles)
        elif report_type == "routes":
            generate_routes_content(elements, styles)
        elif report_type == "client" and client_id:
            generate_client_content(elements, styles, client_id)
        elif report_type == "statistics":
            generate_statistics_content(elements, styles)
        
        # Construir PDF
        doc.build(elements)
        return filename
    
    except Exception as e:
        # En caso de error, generar un informe de error
        elements = []
        elements.append(Paragraph("Error al generar informe", title_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Tipo de error: {str(e)}", normal_style))
        
        doc.build(elements)
        return filename

def generate_summary_content(elements, styles):
    """
    Genera el contenido para el informe de resumen
    
    Args:
        elements: Lista de elementos del PDF
        styles: Estilos de texto
    """
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # Sección: Estado del Sistema
    elements.append(Paragraph("Estado del Sistema", subtitle_style))
    elements.append(Spacer(1, 12))
    
    try:
        # Obtener datos de la API
        system_status = requests.get("http://127.0.0.1:8000/api/system/status").json()
        
        # Crear tabla de estado del sistema
        system_data = [
            ["Métrica", "Valor"],
            ["Drones Activos", str(system_status["active_drones"])],
            ["Pedidos en Curso", str(system_status["current_orders"])],
            ["Tiempo de Actividad", f"{system_status['system_uptime']:.2f} horas"]
        ]
        
        system_table = Table(system_data, colWidths=[200, 150])
        system_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(system_table)
        elements.append(Spacer(1, 24))
        
        # Gráfico de niveles de batería
        elements.append(Paragraph("Niveles de Batería de los Drones", subtitle_style))
        elements.append(Spacer(1, 12))
        
        # Crear gráfico temporal
        fig, ax = plt.subplots(figsize=(7, 4))
        drones = list(system_status["battery_levels"].keys())
        battery_levels = list(system_status["battery_levels"].values())
        
        ax.bar(drones, battery_levels, color='skyblue')
        ax.set_xlabel('Drone')
        ax.set_ylabel('Nivel de Batería (%)')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Guardar gráfico temporalmente
        img_path = os.path.join(tempfile.gettempdir(), "battery_levels.png")
        plt.savefig(img_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        # Añadir gráfico al PDF
        elements.append(Image(img_path, width=400, height=250))
        elements.append(Spacer(1, 24))
        
    except Exception as e:
        elements.append(Paragraph(f"Error obteniendo estado del sistema: {str(e)}", normal_style))
        elements.append(Spacer(1, 12))
    
    # Sección: Resumen de Pedidos
    elements.append(Paragraph("Resumen de Pedidos", subtitle_style))
    elements.append(Spacer(1, 12))
    
    try:
        # Obtener datos de la API
        orders = requests.get("http://127.0.0.1:8000/api/orders").json()
        
        if orders:
            # Crear tabla de resumen de pedidos
            orders_data = [
                ["ID", "Origen", "Destino", "Estado", "Fecha"]
            ]
            
            # Incluir hasta 10 pedidos más recientes
            recent_orders = sorted(orders, key=lambda x: x["creation_date"], reverse=True)[:10]
            for order in recent_orders:
                orders_data.append([
                    str(order["id"]),
                    order["origin"],
                    order["destination"],
                    order["status"],
                    order["creation_date"][:10]
                ])
            
            orders_table = Table(orders_data, colWidths=[40, 140, 140, 80, 80])
            orders_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(orders_table)
            elements.append(Spacer(1, 12))
            
            # Estadísticas de pedidos
            pending = sum(1 for order in orders if order["status"] == "PENDING")
            active = sum(1 for order in orders if order["status"] == "ACTIVE")
            completed = sum(1 for order in orders if order["status"] == "COMPLETED")
            
            elements.append(Paragraph(f"Total de pedidos: {len(orders)}", normal_style))
            elements.append(Paragraph(f"Pedidos pendientes: {pending}", normal_style))
            elements.append(Paragraph(f"Pedidos activos: {active}", normal_style))
            elements.append(Paragraph(f"Pedidos completados: {completed}", normal_style))
            
            # Gráfico de distribución de estados
            fig, ax = plt.subplots(figsize=(6, 6))
            status_counts = [pending, active, completed]
            labels = ['Pendiente', 'Activo', 'Completado']
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            ax.pie(status_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            
            # Guardar gráfico temporalmente
            img_path = os.path.join(tempfile.gettempdir(), "order_status.png")
            plt.savefig(img_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            # Añadir gráfico al PDF
            elements.append(Spacer(1, 12))
            elements.append(Image(img_path, width=300, height=300))
        else:
            elements.append(Paragraph("No hay pedidos registrados", normal_style))
    
    except Exception as e:
        elements.append(Paragraph(f"Error obteniendo pedidos: {str(e)}", normal_style))

def generate_routes_content(elements, styles):
    """
    Genera el contenido para el informe de rutas
    
    Args:
        elements: Lista de elementos del PDF
        styles: Estilos de texto
    """
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    elements.append(Paragraph("Análisis de Rutas", subtitle_style))
    elements.append(Spacer(1, 12))
    
    try:
        # Obtener datos de la API
        orders = requests.get("http://127.0.0.1:8000/api/orders").json()
        
        if orders:
            # Filtrar pedidos con información de distancia y batería
            orders_with_data = [order for order in orders if order.get("distance") is not None and order.get("battery_usage") is not None]
            
            if orders_with_data:
                # Datos para gráficos
                distances = [order["distance"] for order in orders_with_data]
                battery_usages = [order["battery_usage"] for order in orders_with_data]
                ids = [order["id"] for order in orders_with_data]
                
                # Gráfico de distancias
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.bar(range(len(ids)), distances, color='skyblue')
                ax.set_xlabel('ID de Pedido')
                ax.set_ylabel('Distancia (km)')
                ax.set_title('Distancia de Rutas por Pedido')
                ax.set_xticks(range(len(ids)))
                ax.set_xticklabels(ids, rotation=45)
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Añadir valor sobre cada barra
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.1f}',
                            ha='center', va='bottom', rotation=0)
                
                # Guardar gráfico temporalmente
                img_path = os.path.join(tempfile.gettempdir(), "distances.png")
                plt.tight_layout()
                plt.savefig(img_path, dpi=100)
                plt.close(fig)
                
                # Añadir gráfico al PDF
                elements.append(Image(img_path, width=450, height=280))
                elements.append(Spacer(1, 24))
                
                # Gráfico de uso de batería
                fig, ax = plt.subplots(figsize=(8, 5))
                bars = ax.bar(range(len(ids)), battery_usages, color='lightgreen')
                ax.set_xlabel('ID de Pedido')
                ax.set_ylabel('Uso de Batería (%)')
                ax.set_title('Consumo de Batería por Ruta')
                ax.set_xticks(range(len(ids)))
                ax.set_xticklabels(ids, rotation=45)
                ax.set_ylim(0, max(battery_usages) * 1.2)
                ax.grid(axis='y', linestyle='--', alpha=0.7)
                
                # Añadir valor sobre cada barra
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                            f'{height:.1f}%',
                            ha='center', va='bottom', rotation=0)
                
                # Guardar gráfico temporalmente
                img_path = os.path.join(tempfile.gettempdir(), "battery_usage.png")
                plt.tight_layout()
                plt.savefig(img_path, dpi=100)
                plt.close(fig)
                
                # Añadir gráfico al PDF
                elements.append(Image(img_path, width=450, height=280))
                elements.append(Spacer(1, 24))
                
                # Tabla detallada de rutas
                elements.append(Paragraph("Detalle de Rutas", subtitle_style))
                elements.append(Spacer(1, 12))
                
                routes_data = [
                    ["ID", "Origen", "Destino", "Distancia (km)", "Uso Batería (%)"]
                ]
                
                for order in orders_with_data:
                    routes_data.append([
                        str(order["id"]),
                        order["origin"],
                        order["destination"],
                        f"{order['distance']:.2f}" if order["distance"] else "N/A",
                        f"{order['battery_usage']:.2f}" if order["battery_usage"] else "N/A"
                    ])
                
                routes_table = Table(routes_data, colWidths=[40, 130, 130, 100, 100])
                routes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(routes_table)
                
                # Resumen estadístico
                elements.append(Spacer(1, 24))
                elements.append(Paragraph("Resumen Estadístico", subtitle_style))
                elements.append(Spacer(1, 12))
                
                avg_distance = sum(distances) / len(distances)
                max_distance = max(distances)
                min_distance = min(distances)
                avg_battery = sum(battery_usages) / len(battery_usages)
                max_battery = max(battery_usages)
                
                stats_data = [
                    ["Métrica", "Valor"],
                    ["Distancia promedio", f"{avg_distance:.2f} km"],
                    ["Distancia máxima", f"{max_distance:.2f} km"],
                    ["Distancia mínima", f"{min_distance:.2f} km"],
                    ["Uso promedio de batería", f"{avg_battery:.2f}%"],
                    ["Uso máximo de batería", f"{max_battery:.2f}%"]
                ]
                
                stats_table = Table(stats_data, colWidths=[200, 150])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.gray),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(stats_table)
            else:
                elements.append(Paragraph("No hay pedidos con datos de ruta completos", normal_style))
        else:
            elements.append(Paragraph("No hay pedidos registrados", normal_style))
    
    except Exception as e:
        elements.append(Paragraph(f"Error obteniendo datos de rutas: {str(e)}", normal_style))

def generate_client_content(elements, styles, client_id):
    """
    Genera el contenido para el informe de cliente
    
    Args:
        elements: Lista de elementos del PDF
        styles: Estilos de texto
        client_id: ID del cliente
    """
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    try:
        # Obtener datos del cliente
        client_response = requests.get(f"http://127.0.0.1:8000/api/clients/{client_id}")
        
        if client_response.status_code == 200:
            client = client_response.json()
            
            # Información del cliente
            elements.append(Paragraph("Información del Cliente", subtitle_style))
            elements.append(Spacer(1, 12))
            
            client_data = [
                ["Campo", "Valor"],
                ["ID", str(client["id"])],
                ["Nombre", client["name"]],
                ["Email", client["email"]],
                ["Teléfono", client["phone"]],
                ["Dirección", client["address"]],
                ["Coordenadas", f"Lat: {client['latitude']}, Lon: {client['longitude']}"]
            ]
            
            client_table = Table(client_data, colWidths=[150, 300])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(client_table)
            elements.append(Spacer(1, 24))
            
            # Pedidos del cliente
            elements.append(Paragraph("Historial de Pedidos", subtitle_style))
            elements.append(Spacer(1, 12))
            
            # Obtener todos los pedidos
            orders_response = requests.get("http://127.0.0.1:8000/api/orders")
            
            if orders_response.status_code == 200:
                all_orders = orders_response.json()
                # Filtrar pedidos del cliente
                client_orders = [order for order in all_orders if order["client_id"] == client_id]
                
                if client_orders:
                    orders_data = [
                        ["ID", "Origen", "Destino", "Estado", "Fecha", "Peso (kg)"]
                    ]
                    
                    for order in client_orders:
                        orders_data.append([
                            str(order["id"]),
                            order["origin"],
                            order["destination"],
                            order["status"],
                            order["creation_date"][:10],
                            str(order["weight"])
                        ])
                    
                    orders_table = Table(orders_data, colWidths=[40, 110, 110, 80, 80, 70])
                    orders_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(orders_table)
                    elements.append(Spacer(1, 24))
                    
                    # Estadísticas del cliente
                    elements.append(Paragraph("Estadísticas del Cliente", subtitle_style))
                    elements.append(Spacer(1, 12))
                    
                    total_orders = len(client_orders)
                    completed_orders = sum(1 for order in client_orders if order["status"] == "COMPLETED")
                    pending_orders = sum(1 for order in client_orders if order["status"] == "PENDING")
                    active_orders = sum(1 for order in client_orders if order["status"] == "ACTIVE")
                    total_weight = sum(order["weight"] for order in client_orders)
                    
                    stats_data = [
                        ["Métrica", "Valor"],
                        ["Total de pedidos", str(total_orders)],
                        ["Pedidos completados", str(completed_orders)],
                        ["Pedidos pendientes", str(pending_orders)],
                        ["Pedidos activos", str(active_orders)],
                        ["Peso total transportado", f"{total_weight:.2f} kg"]
                    ]
                    
                    stats_table = Table(stats_data, colWidths=[200, 150])
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (1, 0), colors.gray),
                        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    elements.append(stats_table)
                    
                    # Gráfico de estado de pedidos
                    if total_orders > 0:
                        fig, ax = plt.subplots(figsize=(6, 6))
                        status_counts = [pending_orders, active_orders, completed_orders]
                        labels = ['Pendiente', 'Activo', 'Completado']
                        colors = ['#ff9999', '#66b3ff', '#99ff99']
                        
                        ax.pie(status_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                        ax.axis('equal')
                        
                        # Guardar gráfico temporalmente
                        img_path = os.path.join(tempfile.gettempdir(), "client_order_status.png")
                        plt.savefig(img_path, dpi=100, bbox_inches='tight')
                        plt.close(fig)
                        
                        # Añadir gráfico al PDF
                        elements.append(Spacer(1, 12))
                        elements.append(Image(img_path, width=300, height=300))
                else:
                    elements.append(Paragraph("El cliente no tiene pedidos registrados", normal_style))
            else:
                elements.append(Paragraph("Error obteniendo pedidos", normal_style))
        else:
            elements.append(Paragraph(f"No se encontró al cliente con ID {client_id}", normal_style))
    
    except Exception as e:
        elements.append(Paragraph(f"Error generando informe del cliente: {str(e)}", normal_style))

def generate_statistics_content(elements, styles):
    """
    Genera el contenido para el informe de estadísticas
    
    Args:
        elements: Lista de elementos del PDF
        styles: Estilos de texto
    """
    subtitle_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    elements.append(Paragraph("Estadísticas Generales del Sistema", subtitle_style))
    elements.append(Spacer(1, 12))
    
    try:
        # Obtener datos
        system_status = requests.get("http://127.0.0.1:8000/api/system/status").json()
        orders = requests.get("http://127.0.0.1:8000/api/orders").json()
        clients = requests.get("http://127.0.0.1:8000/api/clients").json()
        
        # Resumen general
        summary_data = [
            ["Métrica", "Valor"],
            ["Total de clientes", str(len(clients))],
            ["Total de pedidos", str(len(orders))],
            ["Drones activos", str(system_status["active_drones"])],
            ["Tiempo de actividad", f"{system_status['system_uptime']:.2f} horas"]
        ]
        
        summary_table = Table(summary_data, colWidths=[200, 150])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.gray),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 24))
        
        # Análisis de pedidos por estado
        if orders:
            elements.append(Paragraph("Análisis de Pedidos por Estado", subtitle_style))
            elements.append(Spacer(1, 12))
            
            pending = sum(1 for order in orders if order["status"] == "PENDING")
            active = sum(1 for order in orders if order["status"] == "ACTIVE")
            completed = sum(1 for order in orders if order["status"] == "COMPLETED")
            
            # Gráfico de estado de pedidos
            fig, ax = plt.subplots(figsize=(7, 7))
            status_counts = [pending, active, completed]
            labels = ['Pendiente', 'Activo', 'Completado']
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            ax.pie(status_counts, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribución de Pedidos por Estado')
            ax.axis('equal')
            
            # Guardar gráfico temporalmente
            img_path = os.path.join(tempfile.gettempdir(), "order_status_stats.png")
            plt.savefig(img_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            # Añadir gráfico al PDF
            elements.append(Image(img_path, width=350, height=350))
            elements.append(Spacer(1, 24))
        
            # Análisis de peso por pedido
            elements.append(Paragraph("Análisis de Peso por Pedido", subtitle_style))
            elements.append(Spacer(1, 12))
            
            weights = [order["weight"] for order in orders]
            
            # Histograma de distribución de pesos
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.hist(weights, bins=10, color='skyblue', edgecolor='black')
            ax.set_xlabel('Peso (kg)')
            ax.set_ylabel('Número de Pedidos')
            ax.set_title('Distribución de Pedidos por Peso')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Guardar gráfico temporalmente
            img_path = os.path.join(tempfile.gettempdir(), "weight_distribution.png")
            plt.tight_layout()
            plt.savefig(img_path, dpi=100)
            plt.close(fig)
            
            # Añadir gráfico al PDF
            elements.append(Image(img_path, width=450, height=280))
            elements.append(Spacer(1, 24))
            
            # Estadísticas de peso
            avg_weight = sum(weights) / len(weights)
            max_weight = max(weights)
            min_weight = min(weights)
            
            weight_stats = [
                ["Estadística", "Valor (kg)"],
                ["Peso promedio", f"{avg_weight:.2f}"],
                ["Peso máximo", f"{max_weight:.2f}"],
                ["Peso mínimo", f"{min_weight:.2f}"]
            ]
            
            weight_table = Table(weight_stats, colWidths=[200, 150])
            weight_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.gray),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(weight_table)
        else:
            elements.append(Paragraph("No hay pedidos registrados para analizar", normal_style))
    
    except Exception as e:
        elements.append(Paragraph(f"Error generando estadísticas: {str(e)}", normal_style))
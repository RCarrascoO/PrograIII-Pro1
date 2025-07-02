from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import sys
import os

# Ajustar el path para importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from visual.report_generator import generate_report

router = APIRouter()

@router.get("/reports/summary", response_class=FileResponse)
async def generate_summary_report():
    """
    Genera un informe PDF con resumen de actividad del sistema
    """
    try:
        # Generar el informe con la función del módulo visual
        report_path = generate_report(report_type="summary")
        return FileResponse(
            path=report_path, 
            filename="reporte_resumen.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {str(e)}")

@router.get("/reports/routes", response_class=FileResponse)
async def generate_routes_report():
    """
    Genera un informe PDF con las rutas más frecuentes
    """
    try:
        # Generar el informe con la función del módulo visual
        report_path = generate_report(report_type="routes")
        return FileResponse(
            path=report_path, 
            filename="reporte_rutas.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {str(e)}")

@router.get("/reports/deliveries/{client_id}", response_class=FileResponse)
async def generate_client_report(client_id: int):
    """
    Genera un informe PDF con los envíos de un cliente específico
    """
    try:
        # Generar el informe con la función del módulo visual
        report_path = generate_report(report_type="client", client_id=client_id)
        return FileResponse(
            path=report_path, 
            filename=f"reporte_cliente_{client_id}.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {str(e)}")

@router.get("/reports/statistics", response_class=FileResponse)
async def generate_statistics_report():
    """
    Genera un informe PDF con estadísticas del sistema
    """
    try:
        # Generar el informe con la función del módulo visual
        report_path = generate_report(report_type="statistics")
        return FileResponse(
            path=report_path, 
            filename="reporte_estadisticas.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando el reporte: {str(e)}")
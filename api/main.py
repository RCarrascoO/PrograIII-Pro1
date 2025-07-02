from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Importar controladores
from api.controllers import orders_controller, clients_controller, reports_controller, system_controller

app = FastAPI(
    title="Drone Delivery API",
    description="API para sistema de entrega con drones",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers de los controladores
app.include_router(orders_controller.router, prefix="/api", tags=["Pedidos"])
app.include_router(clients_controller.router, prefix="/api", tags=["Clientes"])
app.include_router(reports_controller.router, prefix="/api", tags=["Reportes"])
app.include_router(system_controller.router, prefix="/api", tags=["Sistema"])

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Drone Delivery. Accede a /docs para ver la documentación."}

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
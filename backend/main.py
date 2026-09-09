from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.produits import router as produits_router
from app.routes.ventes import router as ventes_router
from app.routes.websocket import router as websocket_router
from app.routes.connexion import router as connexion_router
from app.db import init_database
from app.services.network import get_server_info
from app.services.mdns import mdns_announcer

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialiser la base de données au démarrage
    init_database()
    
    # Démarrer l'annonce mDNS
    server_info = get_server_info()
    if server_info["ip"]:
        host = "stock-server"  # Nom d'hôte pour mDNS (pas 0.0.0.0)
        port = 8000
        mdns_announcer.announce(host, port, server_info["ip"])
    
    yield
    
    # Cleanup : arrêter l'annonce mDNS
    mdns_announcer.stop()

app = FastAPI(title="Gestion de Stock API", version="0.1.0", lifespan=lifespan)

# Inclure les routes
app.include_router(produits_router)
app.include_router(ventes_router)
app.include_router(websocket_router)
app.include_router(connexion_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

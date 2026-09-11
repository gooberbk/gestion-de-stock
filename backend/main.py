from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from app.routes.produits import router as produits_router
from app.routes.ventes import router as ventes_router
from app.routes.websocket import router as websocket_router
from app.routes.connexion import router as connexion_router
from app.routes.statistiques import router as statistiques_router
from app.routes.transactions import router as transactions_router
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

# Configuration CORS pour permettre les requêtes depuis l'application mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permet toutes les origines (pour le développement local)
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP
    allow_headers=["*"],  # Permet tous les headers
)

# Servir les fichiers statiques
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Inclure les routes
app.include_router(produits_router)
app.include_router(ventes_router)
app.include_router(websocket_router)
app.include_router(connexion_router)
app.include_router(statistiques_router)
app.include_router(transactions_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def pos_interface():
    """Servir l'interface de point de vente"""
    pos_file = Path(__file__).parent / "static" / "pos.html"
    return FileResponse(pos_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

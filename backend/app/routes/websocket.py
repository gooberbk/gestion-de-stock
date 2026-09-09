from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.websocket import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Endpoint WebSocket pour la connexion des clients mobiles.
    
    Les clients peuvent se connecter pour recevoir des événements en temps réel :
    - ventes : Notification de nouvelle vente avec détails
    - marge_du_jour : Mise à jour des statistiques du jour
    
    La connexion persiste tant que le client reste connecté.
    """
    await manager.connect(websocket)
    
    try:
        # Envoyer un message de bienvenue
        await websocket.send_json({
            "type": "connection",
            "message": "Connecté au serveur WebSocket",
            "clients_connectes": manager.get_connection_count()
        })
        
        # Maintenir la connexion ouverte et écouter les messages du client
        while True:
            # Recevoir des messages du client (optionnel, pour ping/pong ou commandes)
            data = await websocket.receive_text()
            
            # Pour l'instant, on peut simplement faire écho ou ignorer
            # Dans le futur, on pourrait traiter des commandes spécifiques
            await websocket.send_json({
                "type": "echo",
                "message": f"Message reçu: {data}"
            })
            
    except WebSocketDisconnect:
        # Gérer la déconnexion propre du client
        await manager.disconnect(websocket)
    except Exception as e:
        # Gérer les erreurs imprévues
        await manager.disconnect(websocket)
        raise e

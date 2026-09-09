from fastapi import WebSocket
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gestionnaire de connexions WebSocket pour la diffusion d'événements en temps réel.
    """
    
    def __init__(self):
        # Liste des connexions WebSocket actives
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Accepter une nouvelle connexion WebSocket.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nouvelle connexion WebSocket. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """
        Déconnecter un client WebSocket.
        Gère proprement les déconnexions abruptes.
        """
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(f"Déconnexion WebSocket. Total: {len(self.active_connections)}")
        except Exception as e:
            logger.warning(f"Erreur lors de la déconnexion WebSocket: {e}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Diffuser un message JSON à tous les clients connectés.
        
        Args:
            message: Dictionnaire à convertir en JSON et diffuser
        """
        if not self.active_connections:
            logger.debug("Aucune connexion WebSocket active pour diffusion")
            return
        
        message_json = json.dumps(message)
        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.warning(f"Erreur d'envoi à un client WebSocket: {e}")
                disconnected_clients.append(connection)
        
        # Nettoyer les connexions déconnectées
        for client in disconnected_clients:
            await self.disconnect(client)
    
    async def broadcast_evenement(self, type_evenement: str, payload: Dict[str, Any]):
        """
        Diffuser un événement structuré à tous les clients connectés.
        
        Args:
            type_evenement: Type de l'événement (ex: "vente", "marge_du_jour")
            payload: Données de l'événement
        """
        message = {
            "type": type_evenement,
            **payload
        }
        logger.info(f"Diffusion événement {type_evenement} à {len(self.active_connections)} clients")
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """
        Retourner le nombre de connexions actives.
        """
        return len(self.active_connections)


# Instance globale du gestionnaire de connexions
manager = ConnectionManager()

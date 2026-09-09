import logging
import socket
from zeroconf import ServiceInfo, Zeroconf
from typing import Optional

logger = logging.getLogger(__name__)


class MDNSAnnouncer:
    """
    Gestionnaire d'annonce mDNS pour la découverte automatique du serveur
    sur le réseau WiFi local.
    """
    
    def __init__(self, service_name: str = "stock-magasin"):
        """
        Initialise l'annonceur mDNS.
        
        Args:
            service_name: Nom du service (sans .local)
        """
        self.service_name = service_name
        self.service_type = "_http._tcp.local."
        self.zeroconf: Optional[Zeroconf] = None
        self.service_info: Optional[ServiceInfo] = None
        self.is_announced = False
    
    def announce(self, host: str, port: int, ip: str) -> bool:
        """
        Annonce le service sur le réseau local via mDNS.
        
        Args:
            host: Nom d'hôte ou adresse IP
            port: Port du service
            ip: Adresse IP locale
            
        Returns:
            bool: True si l'annonce a réussi, False sinon
        """
        try:
            # Créer l'instance Zeroconf
            self.zeroconf = Zeroconf()
            
            # Construire le nom complet du service
            service_name_full = f"{self.service_name}.{self.service_type}"
            
            # Créer les informations du service avec la syntaxe correcte pour zeroconf
            self.service_info = ServiceInfo(
                type_=self.service_type,
                name=service_name_full,
                server=f"{host}.local.",
                port=port,
                addresses=[self._ip_to_bytes(ip)]
            )
            
            # Annoncer le service
            self.zeroconf.register_service(self.service_info)
            self.is_announced = True
            
            logger.info(f"✓ Service mDNS annoncé: {service_name_full} sur {ip}:{port}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de l'annonce mDNS: {e}")
            logger.info("ℹ️  Le serveur fonctionne sans mDNS (connexion via QR code)")
            return False
    
    def stop(self):
        """
        Arrête l'annonce mDNS et nettoie les ressources.
        """
        try:
            if self.is_announced and self.service_info and self.zeroconf:
                self.zeroconf.unregister_service(self.service_info)
                self.is_announced = False
                logger.info("✓ Service mDNS désannoncé")
            
            if self.zeroconf:
                self.zeroconf.close()
                self.zeroconf = None
                
        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de l'arrêt de l'annonce mDNS: {e}")
    
    def _ip_to_bytes(self, ip: str) -> bytes:
        """
        Convertit une adresse IP en bytes pour mDNS.
        
        Args:
            ip: Adresse IP en format string
            
        Returns:
            bytes: Adresse IP en format bytes
        """
        try:
            return socket.inet_aton(ip)
        except Exception:
            # Fallback pour IPv6 ou formats non supportés
            import ipaddress
            return ipaddress.ip_address(ip).packed


# Instance globale de l'annonceur mDNS
mdns_announcer = MDNSAnnouncer()

import socket
import logging
from typing import Optional
try:
    import netifaces
except ImportError:
    netifaces = None

logger = logging.getLogger(__name__)


def get_local_ip() -> Optional[str]:
    """
    Détecte automatiquement l'adresse IP locale de la machine sur le réseau WiFi.
    
    Évite de retourner 127.0.0.1 (localhost) et cherche une adresse IP
    sur une interface réseau réelle (eth0, wlan0, etc.).
    
    Returns:
        str: Adresse IP locale ou None si aucune trouvée
    """
    try:
        # Créer une socket UDP pour ne pas établir de connexion réelle
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Tenter de se connecter à une adresse IP publique (Google DNS)
        # Cela force le système à choisir l'interface réseau appropriée
        s.connect(("8.8.8.8", 80))
        
        # Récupérer l'adresse IP locale utilisée pour cette connexion
        local_ip = s.getsockname()[0]
        
        s.close()
        
        # Vérifier que ce n'est pas localhost
        if local_ip == "127.0.0.1":
            logger.warning("⚠️  Adresse IP détectée est localhost, tentative alternative...")
            return get_local_ip_alternative()
        
        logger.info(f"✓ Adresse IP locale détectée: {local_ip}")
        return local_ip
        
    except Exception as e:
        logger.warning(f"⚠️  Erreur lors de la détection IP principale: {e}")
        return get_local_ip_alternative()


def get_local_ip_alternative() -> Optional[str]:
    """
    Méthode alternative pour détecter l'IP locale en listant les interfaces.
    
    Returns:
        str: Adresse IP locale ou None si aucune trouvée
    """
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        if local_ip != "127.0.0.1":
            logger.info(f"✓ Adresse IP alternative détectée: {local_ip}")
            return local_ip
            
        # Si toujours localhost, essayer de lister les interfaces
        if netifaces:
            for interface in netifaces.interfaces():
                if interface in ['lo', 'lo0']:  # Ignorer loopback
                    continue
                    
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        ip = addr_info['addr']
                        if ip != '127.0.0.1':
                            logger.info(f"✓ Adresse IP via interface {interface}: {ip}")
                            return ip
        else:
            logger.warning("⚠️  netifaces non disponible, méthode alternative limitée")
                        
    except Exception as e:
        logger.warning(f"⚠️  Erreur lors de la détection IP alternative: {e}")
    
    return None


def get_server_info(host: str = "0.0.0.0", port: int = 8000) -> dict:
    """
    Génère les informations de connexion du serveur.
    
    Args:
        host: Hôte sur lequel le serveur écoute
        port: Port sur lequel le serveur écoute
        
    Returns:
        dict: Informations de connexion (ip, port)
    """
    local_ip = get_local_ip()
    
    # Si host est 0.0.0.0, utiliser l'IP locale détectée
    if host == "0.0.0.0" and local_ip:
        server_ip = local_ip
    else:
        server_ip = host
    
    logger.info(f"ℹ️  Informations serveur: {server_ip}:{port}")
    
    return {
        "ip": server_ip,
        "port": port
    }

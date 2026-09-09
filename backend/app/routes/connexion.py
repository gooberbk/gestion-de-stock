from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import qrcode
import json
import io
from ..services.network import get_server_info

router = APIRouter(tags=["Connexion"])


@router.get("/connexion-info")
async def get_connexion_qr():
    """
    Génère un QR code contenant les informations de connexion du serveur.
    
    Le QR code encode l'adresse IP locale et le port du serveur au format JSON:
    {"ip": "192.168.1.42", "port": 8000}
    
    Retourne l'image du QR code en PNG, utilisable en solution de repli
    si la découverte mDNS échoue sur certains routeurs.
    """
    try:
        # Récupérer les informations de connexion du serveur
        server_info = get_server_info()
        
        if not server_info["ip"]:
            raise HTTPException(
                status_code=500,
                detail="Impossible de détecter l'adresse IP locale"
            )
        
        # Encoder les informations en JSON
        connexion_data = json.dumps(server_info)
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(connexion_data)
        qr.make(fit=True)
        
        # Créer l'image du QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir l'image en bytes PNG
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Retourner l'image avec le content-type approprié
        return Response(
            content=img_byte_arr,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=connexion_qr.png",
                "X-Connexion-Info": connexion_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du QR code: {str(e)}"
        )


@router.get("/connexion-info/json")
async def get_connexion_info_json():
    """
    Retourne les informations de connexion au format JSON.
    
    Endpoint utilitaire pour tester ou pour les clients qui ne peuvent pas
    scanner de QR code.
    """
    server_info = get_server_info()
    
    if not server_info["ip"]:
        raise HTTPException(
            status_code=500,
            detail="Impossible de détecter l'adresse IP locale"
        )
    
    return server_info

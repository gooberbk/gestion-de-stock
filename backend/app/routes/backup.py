from fastapi import APIRouter, HTTPException, status
from typing import Optional
from ..services.backup import get_backup_service

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_backup(custom_name: Optional[str] = None):
    """
    Créer une sauvegarde manuelle de la base de données.
    
    Args:
        custom_name: Nom personnalisé pour le backup (optionnel)
    
    Returns:
        Informations sur le backup créé
    """
    try:
        backup_service = get_backup_service()
        result = backup_service.create_backup(custom_name)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du backup: {str(e)}"
        )


@router.get("/list")
async def list_backups():
    """
    Lister tous les backups disponibles.
    
    Returns:
        Liste des backups avec leurs informations
    """
    try:
        backup_service = get_backup_service()
        backups = backup_service.list_backups()
        return {
            "backups": backups,
            "total": len(backups)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la liste des backups: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_old_backups():
    """
    Supprimer les backups plus anciens que la période de rétention.
    
    Returns:
        Informations sur les backups supprimés
    """
    try:
        backup_service = get_backup_service()
        result = backup_service.cleanup_old_backups()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du nettoyage des backups: {str(e)}"
        )


@router.post("/restore/{backup_name}")
async def restore_backup(backup_name: str):
    """
    Restaurer un backup spécifique.
    
    Args:
        backup_name: Nom du fichier de backup à restaurer
    
    Returns:
        Informations sur la restauration
    """
    try:
        backup_service = get_backup_service()
        result = backup_service.restore_backup(backup_name)
        return result
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la restauration: {str(e)}"
        )

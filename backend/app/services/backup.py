import shutil
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupService:
    """Service de sauvegarde de la base de données SQLite."""
    
    def __init__(self, db_path: str, backup_dir: str = "backups", retention_days: int = 30):
        """
        Initialiser le service de backup.
        
        Args:
            db_path: Chemin vers le fichier de base de données
            backup_dir: Dossier où stocker les backups
            retention_days: Nombre de jours à conserver les backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        
        # Créer le dossier de backup s'il n'existe pas
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, custom_name: Optional[str] = None) -> dict:
        """
        Créer une sauvegarde de la base de données.
        
        Args:
            custom_name: Nom personnalisé pour le backup (optionnel)
            
        Returns:
            dict: Informations sur le backup créé
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Base de données introuvable: {self.db_path}")
        
        # Générer le nom du fichier de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if custom_name:
            backup_name = f"{custom_name}_{timestamp}.db"
        else:
            backup_name = f"backup_{timestamp}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Copier le fichier de base de données
            shutil.copy2(self.db_path, backup_path)
            
            # Obtenir la taille du fichier
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            logger.info(f"Backup créé: {backup_path} ({size_mb:.2f} MB)")
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_name": backup_name,
                "timestamp": timestamp,
                "size_mb": round(size_mb, 2),
                "original_db": str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la création du backup: {e}")
            raise
    
    def cleanup_old_backups(self) -> dict:
        """
        Supprimer les backups plus anciens que retention_days.
        
        Returns:
            dict: Informations sur les backups supprimés
        """
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_files = []
        
        for backup_file in self.backup_dir.glob("*.db"):
            # Extraire la date du nom du fichier
            try:
                # Format attendu: backup_YYYYMMDD_HHMMSS.db ou custom_YYYYMMDD_HHMMSS.db
                parts = backup_file.stem.split('_')
                if len(parts) >= 2:
                    date_str = parts[-2] + parts[-1]  # YYYYMMDD + HHMMSS
                    backup_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")
                    
                    if backup_date < cutoff_date:
                        backup_file.unlink()
                        deleted_files.append(str(backup_file))
                        logger.info(f"Backup supprimé: {backup_file}")
            except (ValueError, IndexError):
                # Si le format du nom n'est pas reconnu, ignorer le fichier
                continue
        
        return {
            "success": True,
            "deleted_count": len(deleted_files),
            "deleted_files": deleted_files,
            "retention_days": self.retention_days
        }
    
    def list_backups(self) -> list:
        """
        Lister tous les backups disponibles.
        
        Returns:
            list: Liste des backups avec leurs informations
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("*.db"), reverse=True):
            stat = backup_file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            # Extraire la date du nom du fichier
            try:
                parts = backup_file.stem.split('_')
                if len(parts) >= 2:
                    date_str = parts[-2] + parts[-1]
                    backup_date = datetime.strptime(date_str, "%Y%m%d%H%M%S")
                    date_str_formatted = backup_date.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    date_str_formatted = "Inconnu"
            except (ValueError, IndexError):
                date_str_formatted = "Inconnu"
            
            backups.append({
                "name": backup_file.name,
                "path": str(backup_file),
                "size_mb": round(size_mb, 2),
                "date": date_str_formatted,
                "created_at": stat.st_ctime
            })
        
        return backups
    
    def restore_backup(self, backup_name: str) -> dict:
        """
        Restaurer un backup.
        
        Args:
            backup_name: Nom du fichier de backup à restaurer
            
        Returns:
            dict: Informations sur la restauration
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup introuvable: {backup_path}")
        
        try:
            # Créer un backup de la base actuelle avant restauration
            safety_backup = self.create_backup("pre_restore")
            
            # Restaurer le backup
            shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Base de données restaurée depuis: {backup_path}")
            
            return {
                "success": True,
                "restored_from": str(backup_path),
                "safety_backup": safety_backup["backup_path"],
                "current_db": str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            raise


# Instance globale du service de backup
def get_backup_service() -> BackupService:
    """Obtenir l'instance du service de backup."""
    from ..db.config import get_db_path
    return BackupService(db_path=str(get_db_path()))

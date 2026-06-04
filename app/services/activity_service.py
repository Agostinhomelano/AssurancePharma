"""
Service pour la gestion des activités et l'audit trail
"""

from datetime import datetime
from app import db
from app.models import Activity

class ActivityService:
    """Service pour enregistrer et gérer les activités"""
    
    @staticmethod
    def log_activity(user_id, action, details=None, employee_id=None):
        """
        Enregistre une activité
        
        Args:
            user_id: ID de l'utilisateur (gérant)
            action: Description de l'action
            details: Détails supplémentaires (JSON)
            employee_id: ID de l'employé (si l'action vient d'un employé)
        """
        try:
            activity = Activity(
                user_id=user_id,
                employee_id=employee_id,
                action=action,
                details=details
            )
            db.session.add(activity)
            db.session.commit()
            return activity
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de l'enregistrement de l'activité: {e}")
            return None
    
    @staticmethod
    def get_user_activities(user_id, limit=50):
        """
        Récupère les activités d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre d'activités à récupérer
        
        Returns:
            Liste des activités
        """
        return Activity.query.filter_by(user_id=user_id).order_by(
            Activity.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_activities_by_date_range(user_id, start_date, end_date):
        """
        Récupère les activités d'un utilisateur dans une plage de dates
        
        Args:
            user_id: ID de l'utilisateur
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Liste des activités
        """
        return Activity.query.filter(
            Activity.user_id == user_id,
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        ).order_by(Activity.created_at.desc()).all()
    
    @staticmethod
    def get_all_activities(limit=100):
        """
        Récupère toutes les activités du système
        
        Args:
            limit: Nombre d'activités à récupérer
        
        Returns:
            Liste de toutes les activités
        """
        return Activity.query.order_by(
            Activity.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def clear_old_activities(days=90):
        """
        Supprime les activités plus anciennes que N jours
        
        Args:
            days: Nombre de jours à conserver
        
        Returns:
            Nombre d'activités supprimées
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        count = Activity.query.filter(
            Activity.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return count

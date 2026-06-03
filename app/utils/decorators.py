"""
Décorateurs personnalisés
"""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def gerant_required(f):
    """
    Décorateur pour les routes réservées aux gérants
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not hasattr(current_user, 'role') or current_user.role not in ('gerant', 'co-gerant'):
            flash("Vous n'avez pas accès à cette ressource", 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def employee_required(f):
    """
    Décorateur pour les routes réservées aux employés
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if not hasattr(current_user, 'fonction') or current_user.fonction is None:
            flash("Vous n'avez pas accès à cette ressource", 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(role):
    """
    Décorateur générique pour les rôles
    
    Args:
        role: Le rôle requis ('gerant', 'co-gerant', ou 'employee')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            if role == 'gerant':
                if not hasattr(current_user, 'role') or current_user.role not in ('gerant', 'co-gerant'):
                    flash("Accès refusé", 'error')
                    return redirect(url_for('dashboard.index'))
            elif role == 'employee':
                if not hasattr(current_user, 'fonction'):
                    flash("Accès refusé", 'error')
                    return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

def active_user_required(f):
    """
    Décorateur pour vérifier que l'utilisateur est actif
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        if hasattr(current_user, 'actif') and not current_user.actif:
            flash("Votre compte a été désactivé", 'error')
            return redirect(url_for('auth.logout'))
        
        return f(*args, **kwargs)
    
    return decorated_function

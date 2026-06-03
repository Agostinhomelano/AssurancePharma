"""
Fonctions d'aide utiles
"""

from datetime import datetime
import os

def format_currency(amount, currency='FC'):
    """Formate un montant en devise"""
    return f"{amount:,.2f} {currency}".replace(',', ' ')

def format_date(date_obj, format='%d/%m/%Y'):
    """Formate une date"""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj)
    return date_obj.strftime(format)

def format_datetime(dt_obj, format='%d/%m/%Y %H:%M'):
    """Formate une date et heure"""
    if isinstance(dt_obj, str):
        dt_obj = datetime.fromisoformat(dt_obj)
    return dt_obj.strftime(format)

def days_until(date_obj):
    """Calcule le nombre de jours jusqu'à une date"""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj).date()
    
    delta = date_obj - datetime.now().date()
    return delta.days

def is_low_stock(quantity, minimum):
    """Vérifie si le stock est faible"""
    return quantity <= minimum

def is_expiring_soon(date_obj, days=30):
    """Vérifie si un produit expire bientôt"""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj).date()
    
    days_left = (date_obj - datetime.now().date()).days
    return 0 <= days_left <= days

def is_expired(date_obj):
    """Vérifie si un produit a expiré"""
    if isinstance(date_obj, str):
        date_obj = datetime.fromisoformat(date_obj).date()
    
    return (date_obj - datetime.now().date()).days < 0

def calculate_profit_margin(cost, price):
    """Calcule la marge bénéficiaire en pourcentage"""
    if cost == 0:
        return 0
    return ((price - cost) / cost) * 100

def generate_filename(prefix, extension):
    """Génère un nom de fichier unique"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.{extension}"

def get_file_extension(filename):
    """Récupère l'extension d'un fichier"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename, allowed_extensions):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           get_file_extension(filename).lstrip('.') in allowed_extensions

def truncate_text(text, length=50):
    """Tronque un texte"""
    if len(text) <= length:
        return text
    return text[:length-3] + '...'

def get_pagination_info(page, per_page, total):
    """Calcule les infos de pagination"""
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page + 1
    end = min(page * per_page, total)
    
    return {
        'current_page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'start': start,
        'end': end,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }

def batch_list(lst, batch_size):
    """Divise une liste en lots"""
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]

class Status:
    """Statuts et messages courants"""
    
    @staticmethod
    def success(message):
        return {'status': 'success', 'message': message}
    
    @staticmethod
    def error(message):
        return {'status': 'error', 'message': message}
    
    @staticmethod
    def warning(message):
        return {'status': 'warning', 'message': message}
    
    @staticmethod
    def info(message):
        return {'status': 'info', 'message': message}

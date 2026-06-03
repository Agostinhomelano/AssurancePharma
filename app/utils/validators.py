"""
Utilitaires de validation
"""

import re
from datetime import datetime

class Validators:
    """Classe avec des méthodes de validation"""
    
    @staticmethod
    def validate_email(email):
        """Valide une adresse email"""
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Valide un numéro de téléphone"""
        # Accepte les formats: +xxx, xxx xxx xxxx, (xxx) xxx-xxxx, etc.
        cleaned = re.sub(r'\D', '', phone)
        return len(cleaned) >= 7
    
    @staticmethod
    def validate_password(password):
        """
        Valide un mot de passe
        - Au moins 6 caractères
        - Au moins une majuscule
        - Au moins un chiffre
        """
        if len(password) < 6:
            return False, "Le mot de passe doit contenir au moins 6 caractères"
        
        if not re.search(r'[A-Z]', password):
            return False, "Le mot de passe doit contenir au moins une majuscule"
        
        if not re.search(r'[0-9]', password):
            return False, "Le mot de passe doit contenir au moins un chiffre"
        
        return True, "Mot de passe valide"
    
    @staticmethod
    def validate_date_format(date_str, format='%Y-%m-%d'):
        """Valide le format d'une date"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_positive_number(value):
        """Valide qu'un nombre est positif"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_required_fields(data, fields):
        """
        Valide que les champs requis sont présents
        
        Args:
            data: Dictionnaire des données
            fields: Liste des champs requis
        
        Returns:
            Tuple (is_valid, missing_fields)
        """
        missing = [f for f in fields if f not in data or not data[f]]
        return len(missing) == 0, missing
    
    @staticmethod
    def validate_medicine_data(data):
        """Valide les données d'un médicament"""
        errors = []
        
        if not data.get('nom') or not data['nom'].strip():
            errors.append("Le nom du médicament est requis")
        
        if not data.get('categorie') or not data['categorie'].strip():
            errors.append("La catégorie est requise")
        
        try:
            prix_achat = float(data.get('prix_achat', 0))
            if prix_achat < 0:
                errors.append("Le prix d'achat doit être positif")
        except ValueError:
            errors.append("Le prix d'achat doit être un nombre")
        
        try:
            prix_vente = float(data.get('prix_vente', 0))
            if prix_vente < 0:
                errors.append("Le prix de vente doit être positif")
        except ValueError:
            errors.append("Le prix de vente doit être un nombre")
        
        try:
            quantite = int(data.get('quantite', 0))
            if quantite < 0:
                errors.append("La quantité doit être positive")
        except ValueError:
            errors.append("La quantité doit être un nombre entier")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_supplier_data(data):
        """Valide les données d'un fournisseur"""
        errors = []
        
        if not data.get('nom') or not data['nom'].strip():
            errors.append("Le nom du fournisseur est requis")
        
        if data.get('email') and not Validators.validate_email(data['email']):
            errors.append("L'email n'est pas valide")
        
        if data.get('telephone') and not Validators.validate_phone(data['telephone']):
            errors.append("Le téléphone n'est pas valide")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_employee_data(data):
        """Valide les données d'un employé"""
        errors = []
        
        if not data.get('nom') or not data['nom'].strip():
            errors.append("Le nom est requis")
        
        if not data.get('prenom') or not data['prenom'].strip():
            errors.append("Le prénom est requis")
        
        if not data.get('email') or not Validators.validate_email(data['email']):
            errors.append("L'email n'est pas valide")
        
        if not data.get('fonction') or not data['fonction'].strip():
            errors.append("La fonction est requise")
        
        if data.get('password'):
            is_valid, msg = Validators.validate_password(data['password'])
            if not is_valid:
                errors.append(msg)
        
        return len(errors) == 0, errors

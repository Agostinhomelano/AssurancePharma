"""
Initialisation de l'application Flask - AssurancePharma
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='development'):
    """Factory function pour créer l'application Flask"""
    
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    if config_name == 'development':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assurance_pharma.db'
        app.config['DEBUG'] = True
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///assurance_pharma.db')
        app.config['DEBUG'] = False
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit
    
    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter'
    
    # Contexte global pour les templates
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now}

    # Enregistrement des blueprints
    from app.routes import auth_bp, dashboard_bp, medicines_bp, suppliers_bp, employees_bp, sales_bp, reports_bp, activities_bp, employee_bp, categories_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(medicines_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(categories_bp)
    
    # Création des tables
    with app.app_context():
        db.create_all()
        init_database()
    
    return app

def init_database():
    """Initialise la base de données avec des données de test"""
    from app.models import User, Medicine, Supplier, Employee, Activity, Category
    
    # Vérifier si la BD est vide
    if User.query.first() is None:
        # Créer l'utilisateur gérant
        gerant = User(
            email='gerant@pharma.com',
            nom='Admin',
            prenom='Gérant',
            role='gerant'
        )
        gerant.set_password('admin123')
        
        db.session.add(gerant)
        db.session.commit()
        
        # Créer des employés de test
        emp1 = Employee(
            nom='Dupont',
            prenom='Jean',
            email='jean.dupont@pharma.com',
            telephone='+33612345678',
            fonction='Vendeur',
            gerant_id=gerant.id
        )
        emp1.set_password('emp123')
        
        emp2 = Employee(
            nom='Martin',
            prenom='Marie',
            email='marie.martin@pharma.com',
            telephone='+33687654321',
            fonction='Vendeur',
            gerant_id=gerant.id
        )
        emp2.set_password('emp123')
        
        db.session.add_all([emp1, emp2])
        
        # Créer des catégories par défaut
        default_categories = ['Antalgiques', 'Antibiotiques', 'Vitamines', 'Anti-inflammatoires', 'Antihistaminiques', 'Digestifs']
        for cat_name in default_categories:
            db.session.add(Category(nom=cat_name, gerant_id=gerant.id))
        
        # Créer des fournisseurs
        suppliers_data = [
            {'nom': 'Pharma Plus', 'telephone': '+33123456789', 'email': 'contact@pharmaplus.fr', 'adresse': 'Paris'},
            {'nom': 'MediLab', 'telephone': '+33234567890', 'email': 'info@medilab.fr', 'adresse': 'Lyon'},
            {'nom': 'Health Care', 'telephone': '+33345678901', 'email': 'sales@healthcare.fr', 'adresse': 'Marseille'},
        ]
        
        for sup_data in suppliers_data:
            supplier = Supplier(**sup_data, gerant_id=gerant.id)
            db.session.add(supplier)
        
        db.session.commit()
        
        # Créer des médicaments de test
        from datetime import date as date_type
        medicines_data = [
            {'nom': 'Doliprane 500mg', 'categorie': 'Antalgiques', 'description': 'Paracétamol', 
             'prix_achat': 2.50, 'prix_vente': 5.50, 'quantite': 100, 'stock_minimum': 20, 'fournisseur_id': 1,
             'date_expiration': date_type(2026, 12, 31)},
            {'nom': 'Amoxicilline 500mg', 'categorie': 'Antibiotiques', 'description': 'Antibiotique', 
             'prix_achat': 3.20, 'prix_vente': 8.20, 'quantite': 50, 'stock_minimum': 10, 'fournisseur_id': 2,
             'date_expiration': date_type(2026, 6, 30)},
            {'nom': 'Vitamine C 500mg', 'categorie': 'Vitamines', 'description': 'Complément alimentaire', 
             'prix_achat': 1.80, 'prix_vente': 3.80, 'quantite': 150, 'stock_minimum': 30, 'fournisseur_id': 1,
             'date_expiration': date_type(2027, 3, 15)},
            {'nom': 'Paracétamol 1g', 'categorie': 'Antalgiques', 'description': 'Paracétamol fort', 
             'prix_achat': 3.50, 'prix_vente': 6.50, 'quantite': 80, 'stock_minimum': 15, 'fournisseur_id': 3,
             'date_expiration': date_type(2025, 8, 20)},
            {'nom': 'Ibuprofène 400mg', 'categorie': 'Anti-inflammatoires', 'description': 'Inflammatoire', 
             'prix_achat': 2.70, 'prix_vente': 7.20, 'quantite': 120, 'stock_minimum': 25, 'fournisseur_id': 2,
             'date_expiration': date_type(2026, 11, 10)},
        ]
        
        for med_data in medicines_data:
            medicine = Medicine(**med_data, gerant_id=gerant.id)
            db.session.add(medicine)
        
        db.session.commit()
        
        # Journaliser l'initialisation
        activity = Activity(
            user_id=gerant.id,
            action='Initialisation de la base de données',
            details='Base de données initialisée avec données de test'
        )
        db.session.add(activity)
        db.session.commit()
        
        print("Base de donnees initialisee avec succes!")

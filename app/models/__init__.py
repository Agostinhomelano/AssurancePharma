from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='gerant', nullable=False)
    actif = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @property
    def effective_gerant_id(self):
        return self.parent_id or self.id

    medicines = db.relationship('Medicine', backref='gerant', lazy=True)
    suppliers = db.relationship('Supplier', backref='gerant', lazy=True)
    employees = db.relationship('Employee', backref='gerant', lazy=True)
    activities = db.relationship('Activity', backref='user', lazy=True)
    categories = db.relationship('Category', backref='gerant', lazy=True)
    photo = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {'id': self.id, 'email': self.email, 'nom': self.nom, 'prenom': self.prenom, 'role': self.role}

class Employee(UserMixin, db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    postnom = db.Column(db.String(100))
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telephone = db.Column(db.String(20))
    fonction = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    gerant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    photo = db.Column(db.String(255))
    sales = db.relationship('Sale', backref='employee', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return 'E' + str(self.id)

    def to_dict(self):
        return {
            'id': self.id, 'nom': self.nom, 'postnom': self.postnom,
            'prenom': self.prenom, 'email': self.email,
            'telephone': self.telephone, 'fonction': self.fonction,
            'actif': self.actif, 'created_at': self.created_at.isoformat()
        }

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('E'):
        return Employee.query.get(int(user_id[1:]))
    return User.query.get(int(user_id))

class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False, index=True)
    categorie = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    prix_achat = db.Column(db.Float, nullable=False)
    prix_vente = db.Column(db.Float, nullable=False)
    quantite = db.Column(db.Integer, default=0)
    stock_minimum = db.Column(db.Integer, default=10)
    date_expiration = db.Column(db.Date)
    gerant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fournisseur = db.relationship('Supplier', backref='medicines')
    sales_items = db.relationship('SaleItem', backref='medicine', lazy=True)

    @property
    def stock_faible(self):
        return self.quantite < self.stock_minimum

    @property
    def proche_expiration(self):
        if self.date_expiration:
            return (self.date_expiration - datetime.now().date()).days < 30
        return False

    @property
    def benefice_unitaire(self):
        return self.prix_vente - self.prix_achat

    def to_dict(self):
        return {
            'id': self.id, 'nom': self.nom, 'categorie': self.categorie,
            'description': self.description, 'prix_achat': self.prix_achat,
            'prix_vente': self.prix_vente, 'quantite': self.quantite,
            'stock_minimum': self.stock_minimum,
            'date_expiration': self.date_expiration.isoformat() if self.date_expiration else None,
            'fournisseur_id': self.fournisseur_id,
            'stock_faible': self.stock_faible, 'proche_expiration': self.proche_expiration,
            'benefice_unitaire': self.benefice_unitaire
        }

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False, index=True)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.Text)
    responsable = db.Column(db.String(150))
    gerant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'nom': self.nom, 'telephone': self.telephone,
            'email': self.email, 'adresse': self.adresse,
            'responsable': self.responsable, 'created_at': self.created_at.isoformat()
        }

class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'employee_id': self.employee_id,
            'employee_name': self.employee.prenom + ' ' + self.employee.nom if self.employee else 'N/A',
            'total_amount': self.total_amount, 'total_cost': self.total_cost,
            'profit': self.profit, 'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat(), 'items_count': len(self.items)
        }

class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.nom if self.medicine else 'N/A',
            'quantity': self.quantity, 'unit_price': self.unit_price,
            'unit_cost': self.unit_cost,
            'subtotal': self.quantity * self.unit_price,
            'subtotal_cost': self.quantity * self.unit_cost,
            'profit': (self.unit_price - self.unit_cost) * self.quantity
        }

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': (self.user.prenom + ' ' + self.user.nom) if self.user else 'Système',
            'action': self.action, 'details': self.details,
            'created_at': self.created_at.isoformat()
        }

class DailyReport(db.Model):
    __tablename__ = 'daily_reports'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    total_sales = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Float, default=0)
    total_profit = db.Column(db.Float, default=0)
    medicines_out_of_stock = db.Column(db.Integer, default=0)
    medicines_expiring = db.Column(db.Integer, default=0)
    pdf_path = db.Column(db.String(255))
    gerant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'date': self.date.isoformat(),
            'total_sales': self.total_sales, 'total_amount': self.total_amount,
            'total_profit': self.total_profit,
            'medicines_out_of_stock': self.medicines_out_of_stock,
            'medicines_expiring': self.medicines_expiring
        }

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    gerant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'nom': self.nom}

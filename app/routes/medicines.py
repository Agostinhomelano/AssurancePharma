"""
Routes Médicaments - AssurancePharma
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Medicine, Supplier, Category
from app.utils import Validators, gerant_required
from app.services import ActivityService

medicines_bp = Blueprint('medicines', __name__, url_prefix='/medicines')

@medicines_bp.route('/')
@login_required
@gerant_required
def list_medicines():
    """Liste tous les médicaments"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Medicine.query.filter_by(gerant_id=current_user.effective_gerant_id)
    
    if search:
        query = query.filter(Medicine.nom.ilike(f'%{search}%'))
    
    medicines = query.paginate(page=page, per_page=20)
    return render_template('medicines/list.html', medicines=medicines, search=search)

@medicines_bp.route('/api/list')
@login_required
@gerant_required
def api_list_medicines():
    """API: Liste des médicaments"""
    medicines = Medicine.query.filter_by(gerant_id=current_user.effective_gerant_id).all()
    return jsonify([m.to_dict() for m in medicines])

@medicines_bp.route('/create', methods=['GET', 'POST'])
@login_required
@gerant_required
def create_medicine():
    """Créer un nouveau médicament"""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Validation
        is_valid, errors = Validators.validate_medicine_data(data)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('medicines.create_medicine'))

        nom = data.get('nom', '').strip()
        if Medicine.query.filter_by(nom=nom, gerant_id=current_user.effective_gerant_id).first():
            flash(f'Le médicament "{nom}" existe déjà.', 'error')
            return redirect(url_for('medicines.create_medicine'))

        try:
            medicine = Medicine(
                nom=nom,
                categorie=data.get('categorie'),
                description=data.get('description', ''),
                prix_achat=float(data.get('prix_achat')),
                prix_vente=float(data.get('prix_vente')),
                quantite=int(data.get('quantite')),
                stock_minimum=int(data.get('stock_minimum', 10)),
                date_expiration=datetime.strptime(data.get('date_expiration'), '%Y-%m-%d').date() if data.get('date_expiration') else None,
                gerant_id=current_user.effective_gerant_id,
                fournisseur_id=data.get('fournisseur_id') if data.get('fournisseur_id') else None
            )
            
            db.session.add(medicine)
            db.session.commit()
            
            ActivityService.log_activity(
                current_user.id,
                f"Créé le médicament: {medicine.nom}",
                f"Prix: {medicine.prix_vente} FC"
            )
            
            flash(f"Médicament {medicine.nom} créé avec succès", 'success')
            return redirect(url_for('medicines.list_medicines'))
        
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de la création. Veuillez réessayer.", 'error')
            return redirect(url_for('medicines.create_medicine'))
    
    suppliers = Supplier.query.filter_by(gerant_id=current_user.effective_gerant_id).all()
    categories = Category.query.filter_by(gerant_id=current_user.effective_gerant_id).order_by(Category.nom).all()
    return render_template('medicines/form.html', suppliers=suppliers, categories=categories)

@medicines_bp.route('/<int:medicine_id>/edit', methods=['GET', 'POST'])
@login_required
@gerant_required
def edit_medicine(medicine_id):
    """Modifier un médicament"""
    medicine = Medicine.query.get_or_404(medicine_id)
    
    if medicine.gerant_id != current_user.effective_gerant_id:
        flash("Non autorisé", 'error')
        return redirect(url_for('medicines.list_medicines'))
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        new_nom = data.get('nom', '').strip()
        if new_nom != medicine.nom:
            if Medicine.query.filter_by(nom=new_nom, gerant_id=current_user.effective_gerant_id).first():
                flash(f'Le médicament "{new_nom}" existe déjà.', 'error')
                return redirect(url_for('medicines.edit_medicine', medicine_id=medicine.id))

        try:
            medicine.nom = new_nom
            medicine.categorie = data.get('categorie')
            medicine.description = data.get('description', '')
            medicine.prix_achat = float(data.get('prix_achat'))
            medicine.prix_vente = float(data.get('prix_vente'))
            medicine.quantite = int(data.get('quantite'))
            medicine.stock_minimum = int(data.get('stock_minimum', 10))
            medicine.date_expiration = datetime.strptime(data.get('date_expiration'), '%Y-%m-%d').date() if data.get('date_expiration') else None
            medicine.fournisseur_id = data.get('fournisseur_id') if data.get('fournisseur_id') else None
            medicine.updated_at = datetime.now()
            
            db.session.commit()
            
            ActivityService.log_activity(
                current_user.id,
                f"Modifié le médicament: {medicine.nom}",
                f"Nouveau prix: {medicine.prix_vente} FC"
            )
            
            flash(f"Médicament {medicine.nom} modifié avec succès", 'success')
            return redirect(url_for('medicines.list_medicines'))
        
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de la modification. Veuillez réessayer.", 'error')
    
    suppliers = Supplier.query.filter_by(gerant_id=current_user.effective_gerant_id).all()
    categories = Category.query.filter_by(gerant_id=current_user.effective_gerant_id).order_by(Category.nom).all()
    return render_template('medicines/form.html', medicine=medicine, suppliers=suppliers, categories=categories)

@medicines_bp.route('/<int:medicine_id>/delete', methods=['POST'])
@login_required
@gerant_required
def delete_medicine(medicine_id):
    """Supprimer un médicament"""
    medicine = Medicine.query.get_or_404(medicine_id)
    
    if medicine.gerant_id != current_user.effective_gerant_id:
        flash("Non autorisé", 'error')
        return redirect(url_for('medicines.list_medicines'))
    
    nom = medicine.nom
    try:
        db.session.delete(medicine)
        db.session.commit()
        
        ActivityService.log_activity(
            current_user.id,
            f"Supprimé le médicament: {nom}",
            ""
        )
        
        flash(f"Médicament {nom} supprimé avec succès", 'success')
    except Exception:
        db.session.rollback()
        flash("Impossible de supprimer ce médicament car il est lié à des ventes.", 'error')
    
    return redirect(url_for('medicines.list_medicines'))

@medicines_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_medicine():
    """API: Créer un médicament (gérant + employé)"""
    if hasattr(current_user, 'fonction'):
        gerant_id = current_user.gerant_id
        employee_id = current_user.id
    else:
        gerant_id = current_user.id
        employee_id = None
        if current_user.role not in ('gerant', 'co-gerant'):
            return jsonify({'error': 'Non autorisé'}), 403

    data = request.form.to_dict()
    is_valid, errors = Validators.validate_medicine_data(data)
    if not is_valid:
        flash('; '.join(errors), 'error')
        return redirect(url_for('employee.medicines' if hasattr(current_user, 'fonction') else 'medicines.list_medicines'))

    nom = data.get('nom', '').strip()
    existing = Medicine.query.filter_by(nom=nom, gerant_id=gerant_id).first()
    if existing:
        flash(f'Le médicament "{nom}" existe déjà.', 'error')
        return redirect(url_for('employee.medicines' if hasattr(current_user, 'fonction') else 'medicines.list_medicines'))

    try:
        medicine = Medicine(
            nom=nom,
            categorie=data.get('categorie'),
            description=data.get('description', ''),
            prix_achat=float(data.get('prix_achat')),
            prix_vente=float(data.get('prix_vente')),
            quantite=int(data.get('quantite', 0)),
            stock_minimum=int(data.get('stock_minimum', 10)),
            date_expiration=datetime.strptime(data.get('date_expiration'), '%Y-%m-%d').date() if data.get('date_expiration') else None,
            gerant_id=gerant_id
        )
        db.session.add(medicine)
        db.session.commit()

        ActivityService.log_activity(
            gerant_id,
            f"Créé le médicament: {medicine.nom}",
            f"Prix: {medicine.prix_vente} FC",
            employee_id=employee_id
        )
        flash(f"Médicament {medicine.nom} créé", 'success')
    except Exception:
        db.session.rollback()
        flash("Une erreur est survenue lors de l'ajout. Veuillez réessayer.", 'error')

    if hasattr(current_user, 'fonction'):
        return redirect(url_for('employee.medicines'))
    return redirect(url_for('medicines.list_medicines'))


@medicines_bp.route('/api/<int:medicine_id>')
@login_required
@gerant_required
def get_medicine(medicine_id):
    """API: Récupère un médicament"""
    medicine = Medicine.query.get_or_404(medicine_id)
    
    if medicine.gerant_id != current_user.effective_gerant_id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    return jsonify(medicine.to_dict())
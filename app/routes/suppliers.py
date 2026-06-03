"""
Routes Fournisseurs - AssurancePharma
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Supplier
from app.utils import Validators, gerant_required
from app.services import ActivityService

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

@suppliers_bp.route('/')
@login_required
@gerant_required
def list_suppliers():
    """Liste tous les fournisseurs"""
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.filter_by(gerant_id=current_user.id).paginate(page=page, per_page=20)
    return render_template('suppliers/list.html', suppliers=suppliers)

@suppliers_bp.route('/api/list')
@login_required
@gerant_required
def api_list_suppliers():
    """API: Liste des fournisseurs"""
    suppliers = Supplier.query.filter_by(gerant_id=current_user.id).all()
    return jsonify([s.to_dict() for s in suppliers])

@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
@gerant_required
def create_supplier():
    """Créer un nouveau fournisseur"""
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Validation
        is_valid, errors = Validators.validate_supplier_data(data)
        if not is_valid:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('suppliers.create_supplier'))
        
        try:
            supplier = Supplier(
                nom=data.get('nom'),
                telephone=data.get('telephone', ''),
                email=data.get('email', ''),
                adresse=data.get('adresse', ''),
                responsable=data.get('responsable', ''),
                gerant_id=current_user.id
            )
            
            db.session.add(supplier)
            db.session.commit()
            
            ActivityService.log_activity(
                current_user.id,
                f"Créé le fournisseur: {supplier.nom}",
                f"Email: {supplier.email}"
            )
            
            flash(f"Fournisseur {supplier.nom} créé avec succès", 'success')
            return redirect(url_for('suppliers.list_suppliers'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur: {str(e)}", 'error')
            return redirect(url_for('suppliers.create_supplier'))
    
    return render_template('suppliers/form.html')

@suppliers_bp.route('/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
@gerant_required
def edit_supplier(supplier_id):
    """Modifier un fournisseur"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if supplier.gerant_id != current_user.id:
        flash("Non autorisé", 'error')
        return redirect(url_for('suppliers.list_suppliers'))
    
    if request.method == 'POST':
        data = request.form.to_dict()
        
        try:
            supplier.nom = data.get('nom')
            supplier.telephone = data.get('telephone', '')
            supplier.email = data.get('email', '')
            supplier.adresse = data.get('adresse', '')
            supplier.responsable = data.get('responsable', '')
            supplier.updated_at = datetime.now()
            
            db.session.commit()
            
            ActivityService.log_activity(
                current_user.id,
                f"Modifié le fournisseur: {supplier.nom}",
                ""
            )
            
            flash(f"Fournisseur {supplier.nom} modifié avec succès", 'success')
            return redirect(url_for('suppliers.list_suppliers'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur: {str(e)}", 'error')
    
    return render_template('suppliers/form.html', supplier=supplier)

@suppliers_bp.route('/<int:supplier_id>/delete', methods=['POST'])
@login_required
@gerant_required
def delete_supplier(supplier_id):
    """Supprimer un fournisseur"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if supplier.gerant_id != current_user.id:
        flash("Non autorisé", 'error')
        return redirect(url_for('suppliers.list_suppliers'))
    
    nom = supplier.nom
    try:
        db.session.delete(supplier)
        db.session.commit()
        
        ActivityService.log_activity(
            current_user.id,
            f"Supprimé le fournisseur: {nom}",
            ""
        )
        
        flash(f"Fournisseur {nom} supprimé avec succès", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {str(e)}", 'error')
    
    return redirect(url_for('suppliers.list_suppliers'))

@suppliers_bp.route('/api/<int:supplier_id>')
@login_required
@gerant_required
def get_supplier(supplier_id):
    """API: Récupère un fournisseur"""
    supplier = Supplier.query.get_or_404(supplier_id)
    
    if supplier.gerant_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    return jsonify(supplier.to_dict())

"""
Routes Ventes - AssurancePharma
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Employee, Medicine, Sale, SaleItem
from app.utils import gerant_required
from app.services import SalesService, ActivityService

sales_bp = Blueprint('sales', __name__, url_prefix='/sales')

@sales_bp.route('/')
@login_required
def sales_interface():
    """Interface de vente"""
    if hasattr(current_user, 'fonction'):
        gerant_id = current_user.gerant_id
    else:
        gerant_id = current_user.effective_gerant_id

    medicines = Medicine.query.filter_by(gerant_id=gerant_id).all()
    return render_template('sales/index.html', medicines=medicines)

@sales_bp.route('/api/medicines')
@login_required
def api_get_medicines():
    """API: Récupère les médicaments disponibles"""
    gerant_id = current_user.gerant_id if hasattr(current_user, 'gerant_id') else current_user.effective_gerant_id
    medicines = Medicine.query.filter_by(gerant_id=gerant_id).all()
    return jsonify([{
        'id': m.id,
        'nom': m.nom,
        'prix_vente': m.prix_vente,
        'quantite': m.quantite,
        'categorie': m.categorie,
        'disponible': m.quantite > 0
    } for m in medicines])

@sales_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_sale():
    """API: Créer une nouvelle vente"""
    if hasattr(current_user, 'fonction'):
        user_id = current_user.gerant_id
        employee_id = current_user.id
    else:
        user_id = current_user.id
        emp = Employee.query.filter_by(gerant_id=current_user.effective_gerant_id, actif=True).first()
        if not emp:
            return jsonify({'error': 'Aucun employé actif pour enregistrer la vente'}), 400
        employee_id = emp.id

    data = request.get_json()
    items = data.get('items', [])
    payment_method = data.get('payment_method', 'Espèces')

    if not items:
        return jsonify({'error': 'Pas d\'articles'}), 400

    sale = SalesService.create_sale(employee_id, items, payment_method)

    if sale:
        ActivityService.log_activity(
            user_id,
            f"Nouvelle vente ({len(items)} articles)",
            f"Total: {sale.total_amount} FC, Bénéfice: {sale.profit} FC"
        )

        return jsonify({
            'success': True,
            'sale_id': sale.id,
            'total_amount': sale.total_amount,
            'profit': sale.profit,
            'message': 'Vente enregistrée avec succès'
        })
    else:
        return jsonify({'error': 'Erreur lors de la création de la vente'}), 500

@sales_bp.route('/list')
@login_required
@gerant_required
def list_sales():
    """Liste des ventes (gérant seulement)"""
    page = request.args.get('page', 1, type=int)
    
    sales = Sale.query.join(
        Employee
    ).filter(
        Employee.gerant_id == current_user.effective_gerant_id
    ).order_by(Sale.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('sales/list.html', sales=sales)

@sales_bp.route('/api/sales-stats')
@login_required
@gerant_required
def api_sales_stats():
    """API: Statistiques de vente"""
    sales = Sale.query.join(Employee).filter(
        Employee.gerant_id == current_user.effective_gerant_id
    ).all()
    
    return jsonify({
        'total_sales': len(sales),
        'total_amount': sum(s.total_amount for s in sales),
        'total_profit': sum(s.profit for s in sales),
        'average_sale': sum(s.total_amount for s in sales) / len(sales) if sales else 0
    })

@sales_bp.route('/<int:sale_id>/details')
@login_required
def sale_details(sale_id):
    """Détails d'une vente"""
    sale = Sale.query.get_or_404(sale_id)
    
    # Vérifier les permissions
    if sale.employee.gerant_id != current_user.effective_gerant_id and sale.employee_id != current_user.id:
        flash("Non autorisé", 'error')
        return redirect(url_for('dashboard.index'))
    
    return render_template('sales/details.html', sale=sale)

@sales_bp.route('/<int:sale_id>/delete', methods=['POST'])
@login_required
@gerant_required
def delete_sale(sale_id):
    """Supprimer une vente"""
    sale = Sale.query.get_or_404(sale_id)
    if sale.employee.gerant_id != current_user.effective_gerant_id:
        flash("Non autorisé", 'error')
        return redirect(url_for('sales.list_sales'))

    try:
        db.session.delete(sale)
        db.session.commit()
        ActivityService.log_activity(
            current_user.id,
            f"Supprimé la vente #{sale.id}",
            f"Montant: {sale.total_amount} FC"
        )
        flash("Vente supprimée", 'success')
    except Exception:
        db.session.rollback()
        flash("Impossible de supprimer cette vente. Veuillez réessayer.", 'danger')
    return redirect(url_for('sales.list_sales'))

@sales_bp.route('/api/<int:sale_id>')
@login_required
def api_get_sale(sale_id):
    """API: Récupère les détails d'une vente"""
    sale = Sale.query.get_or_404(sale_id)
    
    # Vérifier les permissions
    gerant_id = sale.employee.gerant_id if hasattr(sale.employee, 'gerant_id') else None
    if gerant_id != current_user.effective_gerant_id and sale.employee_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    return jsonify(sale.to_dict())

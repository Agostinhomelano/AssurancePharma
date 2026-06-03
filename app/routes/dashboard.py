"""
Routes Dashboard - AssurancePharma
"""

from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models import Medicine, Supplier, Employee, Sale, Activity, DailyReport

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Page principale du tableau de bord"""
    # Vérifier que c'est un gérant
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        return redirect(url_for('auth.login'))
    
    return render_template('dashboard/index.html')

@dashboard_bp.route('/api/dashboard/stats')
@login_required
def get_stats():
    """Récupère les statistiques du tableau de bord"""
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        return jsonify({'error': 'Non autorisé'}), 403
    
    # Statistiques
    total_medicines = Medicine.query.filter_by(gerant_id=current_user.id).count()
    medicines_low_stock = Medicine.query.filter_by(gerant_id=current_user.id).filter(
        Medicine.quantite < Medicine.stock_minimum
    ).count()
    
    # Ventes du jour
    today = datetime.now().date()
    today_sales = Sale.query.join(Employee).filter(
        db.func.date(Sale.created_at) == today,
        Employee.gerant_id == current_user.id
    ).all()
    
    total_sales_today = len(today_sales)
    total_amount_today = sum(s.total_amount for s in today_sales)
    total_profit_today = sum(s.profit for s in today_sales)
    
    # Employés et fournisseurs
    total_employees = Employee.query.filter_by(gerant_id=current_user.id).count()
    total_suppliers = Supplier.query.filter_by(gerant_id=current_user.id).count()
    
    # Produits proches de l'expiration
    medicines_expiring = Medicine.query.filter_by(gerant_id=current_user.id).filter(
        Medicine.date_expiration <= datetime.now().date() + timedelta(days=30)
    ).count()
    
    return jsonify({
        'total_medicines': total_medicines,
        'medicines_low_stock': medicines_low_stock,
        'medicines_expiring': medicines_expiring,
        'total_sales_today': total_sales_today,
        'total_amount_today': total_amount_today,
        'total_profit_today': total_profit_today,
        'total_employees': total_employees,
        'total_suppliers': total_suppliers
    })

@dashboard_bp.route('/api/dashboard/sales-evolution')
@login_required
def get_sales_evolution():
    """Évolution des ventes sur les 7 derniers jours"""
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        return jsonify({'error': 'Non autorisé'}), 403
    
    data = []
    for i in range(6, -1, -1):
        date = (datetime.now().date() - timedelta(days=i))
        sales = Sale.query.join(Employee).filter(
            db.func.date(Sale.created_at) == date,
            Employee.gerant_id == current_user.id
        ).all()
        
        total = sum(s.total_amount for s in sales)
        data.append({
            'date': date.strftime('%a'),
            'amount': total
        })
    
    return jsonify(data)

@dashboard_bp.route('/api/dashboard/top-medicines')
@login_required
def get_top_medicines():
    """Top 5 des médicaments vendus"""
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        return jsonify({'error': 'Non autorisé'}), 403
    
    # TODO: Implémenter
    return jsonify([])

@dashboard_bp.route('/api/dashboard/activities')
@login_required
def get_recent_activities():
    """Activités récentes"""
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        return jsonify({'error': 'Non autorisé'}), 403
    
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(
        Activity.created_at.desc()
    ).limit(10).all()
    
    return jsonify([a.to_dict() for a in activities])

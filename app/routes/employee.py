from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from app import db
from app.models import Sale, SaleItem, Medicine, Employee, Activity, DailyReport, Category
from app.services.report_service import ReportService
from app.services.activity_service import ActivityService
from flask import send_file

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/')
@login_required
def index():
    if hasattr(current_user, 'role'):
        return redirect(url_for('dashboard.index'))

    gerant_id = current_user.gerant_id
    today = date.today()
    today_sales = Sale.query.filter(
        db.func.date(Sale.created_at) == today,
        Sale.employee_id == current_user.id
    ).all()

    medicines = Medicine.query.filter_by(gerant_id=gerant_id).filter(Medicine.quantite > 0).all()
    low_stock = Medicine.query.filter_by(gerant_id=gerant_id).filter(Medicine.quantite < Medicine.stock_minimum).count()

    stats = {
        'sales_count': len(today_sales),
        'total_amount': sum(s.total_amount for s in today_sales),
        'total_profit': sum(s.profit for s in today_sales),
        'total_medicines': len(medicines),
        'low_stock': low_stock
    }

    return render_template('employee/index.html', stats=stats, medicines=medicines)


@employee_bp.route('/medicaments')
@login_required
def medicines():
    if hasattr(current_user, 'role'):
        return redirect(url_for('dashboard.index'))

    medicines = Medicine.query.filter_by(gerant_id=current_user.gerant_id).all()
    categories = Category.query.filter_by(gerant_id=current_user.gerant_id).order_by(Category.nom).all()
    return render_template('employee/medicines.html', medicines=medicines, categories=categories)


@employee_bp.route('/medicaments/api/list')
@login_required
def api_medicines_list():
    if hasattr(current_user, 'role'):
        return jsonify({'error': 'Non autorisé'}), 403

    medicines = Medicine.query.filter_by(gerant_id=current_user.gerant_id).all()
    return jsonify([{
        'id': m.id, 'nom': m.nom, 'categorie': m.categorie,
        'prix_vente': m.prix_vente, 'quantite': m.quantite,
        'stock_minimum': m.stock_minimum, 'stock_faible': m.stock_faible
    } for m in medicines])


@employee_bp.route('/activites')
@login_required
def activities():
    if hasattr(current_user, 'role'):
        return redirect(url_for('dashboard.index'))

    today = date.today()
    recent_activities = Activity.query.filter(
        db.func.date(Activity.created_at) == today
    ).order_by(Activity.created_at.desc()).limit(50).all()

    return render_template('employee/activities.html', activities=recent_activities, today=today)


@employee_bp.route('/rapport')
@login_required
def report():
    if hasattr(current_user, 'role'):
        return redirect(url_for('dashboard.index'))

    gerant_id = current_user.gerant_id
    today = date.today()

    today_sales = Sale.query.filter(
        db.func.date(Sale.created_at) == today,
        Sale.employee_id == current_user.id
    ).all()

    report_data = DailyReport.query.filter_by(gerant_id=gerant_id, date=today).first()

    stats = {
        'sales_count': len(today_sales),
        'total_amount': sum(s.total_amount for s in today_sales),
        'total_cost': sum(s.total_cost for s in today_sales),
        'total_profit': sum(s.profit for s in today_sales),
    }

    sold_items = []
    for sale in today_sales:
        for item in sale.items:
            sold_items.append({
                'nom': item.medicine.nom if item.medicine else 'N/A',
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total': item.quantity * item.unit_price
            })

    sold_items.sort(key=lambda x: x['nom'])

    return render_template('employee/report.html', stats=stats, report_data=report_data, today=today, sold_items=sold_items)


@employee_bp.route('/api/stats')
@login_required
def api_stats():
    if hasattr(current_user, 'role'):
        return jsonify({'error': 'Non autorisé'}), 403

    today = date.today()
    today_sales = Sale.query.filter(
        db.func.date(Sale.created_at) == today,
        Employee.id == current_user.id
    ).all()

    medicines = Medicine.query.filter_by(gerant_id=current_user.gerant_id).all()

    return jsonify({
        'sales_count': len(today_sales),
        'total_amount': sum(s.total_amount for s in today_sales),
        'total_profit': sum(s.profit for s in today_sales),
        'total_medicines': len(medicines),
        'low_stock': len([m for m in medicines if m.stock_faible])
    })


@employee_bp.route('/telecharger-rapport')
@login_required
def download_report():
    if hasattr(current_user, 'role'):
        return redirect(url_for('dashboard.index'))

    try:
        output, filename = ReportService.generate_daily_excel(current_user.gerant_id, date.today())
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('employee.report'))

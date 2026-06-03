from flask import Blueprint, render_template, jsonify, request, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from app import db
from app.models import DailyReport, Sale, Employee, Medicine
from app.utils import gerant_required
from app.services.report_service import ReportService

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
@gerant_required
def index():
    reports = DailyReport.query.filter_by(gerant_id=current_user.effective_gerant_id).order_by(DailyReport.date.desc()).limit(30).all()
    today = date.today()
    today_report = DailyReport.query.filter_by(gerant_id=current_user.effective_gerant_id, date=today).first()
    return render_template('reports/index.html', reports=reports, today_report=today_report, today=today)

@reports_bp.route('/generate/daily', methods=['POST'])
@login_required
@gerant_required
def generate_daily():
    try:
        report_date_str = request.form.get('date', str(date.today()))
        report_date = datetime.strptime(report_date_str, '%Y-%m-%d').date()

        existing = DailyReport.query.filter_by(gerant_id=current_user.effective_gerant_id, date=report_date).first()
        if existing:
            flash(f'Un rapport existe déjà pour le {report_date.strftime("%d/%m/%Y")}', 'warning')
            return redirect(url_for('reports.index'))

        output, filename = ReportService.generate_daily_excel(current_user.id, report_date)
        flash(f'Rapport du {report_date.strftime("%d/%m/%Y")} généré avec succès !', 'success')
        return redirect(url_for('reports.index'))
    except Exception as e:
        flash(f'Erreur lors de la génération du rapport: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))

@reports_bp.route('/download/daily/<int:report_id>')
@login_required
@gerant_required
def download_daily(report_id):
    report = DailyReport.query.get_or_404(report_id)
    if report.gerant_id != current_user.effective_gerant_id:
        flash('Non autorisé', 'danger')
        return redirect(url_for('reports.index'))

    try:
        output, filename = ReportService.generate_daily_excel(current_user.id, report.date)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))

@reports_bp.route('/download/today')
@login_required
@gerant_required
def download_today():
    try:
        output, filename = ReportService.generate_daily_excel(current_user.id, date.today())
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))

@reports_bp.route('/generate/period', methods=['POST'])
@login_required
@gerant_required
def generate_period():
    try:
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        if not start_str or not end_str:
            flash('Les dates de début et fin sont requises', 'danger')
            return redirect(url_for('reports.index'))

        start = datetime.strptime(start_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_str, '%Y-%m-%d').date()

        if start > end:
            flash('La date de début doit être antérieure à la date de fin', 'danger')
            return redirect(url_for('reports.index'))

        output, filename = ReportService.generate_period_excel(current_user.id, start, end)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Erreur: {str(e)}', 'danger')
        return redirect(url_for('reports.index'))

@reports_bp.route('/api/stats')
@login_required
@gerant_required
def api_stats():
    today = date.today()
    sales = Sale.query.join(Employee).filter(
        db.func.date(Sale.created_at) == today,
        Employee.gerant_id == current_user.effective_gerant_id
    ).all()

    return jsonify({
        'sales_count': len(sales),
        'total_amount': sum(s.total_amount for s in sales),
        'total_profit': sum(s.profit for s in sales)
    })

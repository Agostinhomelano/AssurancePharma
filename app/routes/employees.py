from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import Employee
from app.utils import Validators, gerant_required
from app.services import ActivityService

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/')
@login_required
@gerant_required
def list_employees():
    employees = Employee.query.filter_by(gerant_id=current_user.effective_gerant_id).all()
    return render_template('employees/list.html', employees=employees)

@employees_bp.route('/create', methods=['GET', 'POST'])
@login_required
@gerant_required
def create_employee():
    if request.method == 'POST':
        data = request.form.to_dict()
        is_valid, errors = Validators.validate_employee_data(data)
        if not is_valid:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('employees.create_employee'))

        if Employee.query.filter_by(email=data.get('email')).first():
            flash('Cet email est déjà utilisé', 'danger')
            return redirect(url_for('employees.create_employee'))

        try:
            employee = Employee(
                nom=data.get('nom'),
                postnom=data.get('postnom', ''),
                prenom=data.get('prenom'),
                email=data.get('email'),
                telephone=data.get('telephone', ''),
                fonction=data.get('fonction'),
                gerant_id=current_user.effective_gerant_id
            )
            password = data.get('password', 'Emp1234')
            employee.set_password(password)
            db.session.add(employee)
            db.session.commit()

            ActivityService.log_activity(
                current_user.id,
                f"Créé l'employé: {employee.prenom} {employee.nom}",
                f"Email: {employee.email}, Fonction: {employee.fonction}"
            )
            flash(f"Employé {employee.prenom} {employee.nom} créé avec succès", 'success')
            return redirect(url_for('employees.list_employees'))
        except IntegrityError:
            db.session.rollback()
            flash("Cet email est déjà utilisé par un autre employé.", 'danger')
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de la création. Veuillez réessayer.", 'danger')

    return render_template('employees/form.html')

@employees_bp.route('/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
@gerant_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.gerant_id != current_user.effective_gerant_id:
        flash('Non autorisé', 'danger')
        return redirect(url_for('employees.list_employees'))

    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            employee.nom = data.get('nom')
            employee.postnom = data.get('postnom', '')
            employee.prenom = data.get('prenom')
            employee.email = data.get('email')
            employee.telephone = data.get('telephone', '')
            employee.fonction = data.get('fonction')
            if data.get('password'):
                employee.set_password(data['password'])
            employee.actif = data.get('actif') == 'on'
            employee.updated_at = datetime.now()
            db.session.commit()

            ActivityService.log_activity(
                current_user.id,
                f"Modifié l'employé: {employee.prenom} {employee.nom}",
                ""
            )
            flash(f"Employé {employee.prenom} {employee.nom} modifié", 'success')
            return redirect(url_for('employees.list_employees'))
        except IntegrityError:
            db.session.rollback()
            flash("Cet email est déjà utilisé par un autre employé.", 'danger')
        except Exception:
            db.session.rollback()
            flash("Une erreur est survenue lors de la modification. Veuillez réessayer.", 'danger')

    return render_template('employees/form.html', employee=employee)

@employees_bp.route('/<int:employee_id>/toggle-status', methods=['POST'])
@login_required
@gerant_required
def toggle_status(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.gerant_id != current_user.effective_gerant_id:
        return jsonify({'error': 'Non autorisé'}), 403

    employee.actif = not employee.actif
    db.session.commit()
    status = "activé" if employee.actif else "désactivé"
    flash(f"Employé {employee.prenom} {employee.nom} {status}", 'success')
    return redirect(url_for('employees.list_employees'))

@employees_bp.route('/<int:employee_id>/delete', methods=['POST'])
@login_required
@gerant_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    if employee.gerant_id != current_user.effective_gerant_id:
        return jsonify({'error': 'Non autorisé'}), 403

    nom_complet = f"{employee.prenom} {employee.nom}"
    try:
        db.session.delete(employee)
        db.session.commit()
        ActivityService.log_activity(
            current_user.id,
            f"Supprimé l'employé: {nom_complet}",
            ""
        )
        flash(f"Employé {nom_complet} supprimé", 'success')
    except Exception:
        db.session.rollback()
        flash("Impossible de supprimer cet employé car il est lié à des ventes.", 'danger')
    return redirect(url_for('employees.list_employees'))

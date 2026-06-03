from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Employee
from app.utils import Validators
from app.services import ActivityService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if hasattr(current_user, 'role'):
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('employee.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if hasattr(current_user, 'role'):
            return redirect(url_for('dashboard.index'))
        else:
            return redirect(url_for('employee.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.actif:
                login_user(user, remember=request.form.get('remember'))
                return redirect(url_for('dashboard.index'))
            else:
                flash('Compte désactivé', 'danger')
        else:
            employee = Employee.query.filter_by(email=email).first()
            if employee and employee.check_password(password):
                if employee.actif:
                    login_user(employee, remember=request.form.get('remember'))
                    return redirect(url_for('employee.index'))
                else:
                    flash('Compte désactivé', 'danger')
            else:
                flash('Email ou mot de passe incorrect', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('auth.login'))

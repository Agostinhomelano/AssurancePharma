from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Employee, Activity
from app.utils import Validators
from app.services import ActivityService
import os

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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')
            if not current_user.check_password(old_pw):
                flash('Mot de passe actuel incorrect.', 'danger')
            elif len(new_pw) < 4:
                flash('Le nouveau mot de passe doit faire au moins 4 caractères.', 'danger')
            elif new_pw != confirm_pw:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Mot de passe modifié avec succès.', 'success')
            return redirect(url_for('auth.profil'))
        
        if action == 'photo':
            file = request.files.get('photo')
            if file and file.filename:
                if not allowed_file(file.filename):
                    flash('Format de fichier non autorisé. Utilisez PNG, JPG, JPEG, GIF ou WEBP.', 'danger')
                    return redirect(url_for('auth.profil'))
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                ext = file.filename.rsplit('.', 1)[1].lower()
                prefix = 'U' if hasattr(current_user, 'role') else 'E'
                filename = f'profile_{prefix}{current_user.id}.{ext}'
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                current_user.photo = filename
                db.session.commit()
                flash('Photo de profil mise à jour.', 'success')
            else:
                flash('Veuillez sélectionner une image.', 'danger')
            return redirect(url_for('auth.profil'))
    
    return render_template('auth/profil.html')

@auth_bp.route('/co-gerants')
@login_required
def list_co_gerants():
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        flash('Accès réservé au gérant principal.', 'danger')
        return redirect(url_for('dashboard.index'))
    co_gerants = User.query.filter_by(parent_id=current_user.id, role='co-gerant').all()
    return render_template('auth/co_gerants.html', co_gerants=co_gerants)

@auth_bp.route('/co-gerants/creer', methods=['GET', 'POST'])
@login_required
def create_co_gerant():
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        flash('Accès réservé au gérant principal.', 'danger')
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        nom = request.form.get('nom', '').strip()
        prenom = request.form.get('prenom', '').strip()
        password = request.form.get('password', '')
        if not email or not nom or not prenom or not password:
            flash('Tous les champs sont requis.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
        elif len(password) < 4:
            flash('Le mot de passe doit faire au moins 4 caractères.', 'danger')
        else:
            co = User(
                email=email, nom=nom, prenom=prenom,
                role='co-gerant', parent_id=current_user.id
            )
            co.set_password(password)
            db.session.add(co)
            db.session.add(Activity(
                user_id=current_user.id,
                action='Création co-gérant',
                details=f'Co-gérant "{prenom} {nom}" créé'
            ))
            db.session.commit()
            flash(f'Co-gérant "{prenom} {nom}" créé avec succès.', 'success')
            return redirect(url_for('auth.list_co_gerants'))
    return render_template('auth/co_gerant_form.html')

@auth_bp.route('/co-gerants/<int:id>/desactiver', methods=['POST'])
@login_required
def toggle_co_gerant(id):
    if not hasattr(current_user, 'role') or current_user.role != 'gerant':
        flash('Accès réservé au gérant principal.', 'danger')
        return redirect(url_for('dashboard.index'))
    co = User.query.filter_by(id=id, parent_id=current_user.id, role='co-gerant').first_or_404()
    co.actif = not co.actif
    db.session.commit()
    status = 'activé' if co.actif else 'désactivé'
    flash(f'Co-gérant "{co.prenom} {co.nom}" {status}.', 'success')
    return redirect(url_for('auth.list_co_gerants'))

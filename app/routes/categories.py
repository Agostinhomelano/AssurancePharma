from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models import Category, Activity

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')

@categories_bp.route('/')
@login_required
def list_categories():
    categories = Category.query.filter_by(gerant_id=current_user.effective_gerant_id).order_by(Category.nom).all()
    return render_template('categories/list.html', categories=categories)

@categories_bp.route('/add', methods=['POST'])
@login_required
def add_category():
    nom = request.form.get('nom', '').strip()
    if not nom:
        flash('Le nom de la catégorie est requis.', 'danger')
        return redirect(url_for('categories.list_categories'))
    existing = Category.query.filter_by(gerant_id=current_user.effective_gerant_id, nom=nom).first()
    if existing:
        flash('Cette catégorie existe déjà.', 'danger')
        return redirect(url_for('categories.list_categories'))
    cat = Category(nom=nom, gerant_id=current_user.effective_gerant_id)
    db.session.add(cat)
    db.session.add(Activity(user_id=current_user.id, action='Ajout catégorie', details=f'Catégorie "{nom}" créée'))
    db.session.commit()
    flash(f'Catégorie "{nom}" ajoutée.', 'success')
    return redirect(url_for('categories.list_categories'))

@categories_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    cat = Category.query.filter_by(id=id, gerant_id=current_user.effective_gerant_id).first_or_404()
    nom = cat.nom
    db.session.delete(cat)
    db.session.add(Activity(user_id=current_user.id, action='Suppression catégorie', details=f'Catégorie "{nom}" supprimée'))
    db.session.commit()
    flash(f'Catégorie "{nom}" supprimée.', 'success')
    return redirect(url_for('categories.list_categories'))

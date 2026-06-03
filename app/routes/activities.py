from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Activity
from app.utils import gerant_required

activities_bp = Blueprint('activities', __name__, url_prefix='/activities')

@activities_bp.route('/')
@login_required
@gerant_required
def list_activities():
    page = request.args.get('page', 1, type=int)
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(
        Activity.created_at.desc()
    ).paginate(page=page, per_page=50)
    return render_template('activities/list.html', activities=activities)

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.medicines import medicines_bp
from app.routes.suppliers import suppliers_bp
from app.routes.sales import sales_bp
from app.routes.employees import employees_bp
from app.routes.reports import reports_bp
from app.routes.activities import activities_bp
from app.routes.employee import employee_bp
from app.routes.categories import categories_bp

__all__ = [
    'auth_bp', 'dashboard_bp', 'medicines_bp', 'suppliers_bp',
    'employees_bp', 'sales_bp', 'reports_bp', 'activities_bp',
    'employee_bp', 'categories_bp'
]

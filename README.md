# AssurancePharma - Systeme de Gestion de Pharmacie

Application web de gestion de pharmacie avec double authentification (gerant/employe),
gestion des stocks, ventes, rapports et journal d'audit.

## Fonctionnalites

- **Authentification** : Connexion separate Gerant / Employe
- **Dashboard** : Statistiques, graphiques, activites recentes (gerant)
- **Medicaments** : CRUD, alertes stock faible, peremption
- **Fournisseurs** : Gestion des fournisseurs
- **Ventes** : Interface caisse rapide avec panier
- **Employes** : Creation et gestion des comptes employes
- **Espace employe** : Stats du jour, stock disponible, rapport journalier
- **Rapports** : Export PDF et Excel
- **Activites** : Journal d'audit complet

## Demarrage rapide

```bash
# 1. Creer l'environnement virtuel
python -m venv venv

# 2. Activer (Windows)
venv\Scripts\activate

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Lancer
python run.py
```

Ouvrir http://localhost:5000

## Identifiants de test

| Role | Email | Mot de passe |
|------|-------|-------------|
| Gerant | gerant@pharma.com | admin123 |
| Employe | jean.dupont@pharma.com | emp123 |
| Employe | marie.martin@pharma.com | emp123 |

## Architecture

```
AssurancePharma/
├── run.py                     # Point d'entree
├── requirements.txt           # Dependances
├── .env.example               # Configuration
│
├── app/                       # Application Flask
│   ├── __init__.py           # Factory, init DB, seed data
│   ├── models/               # Modeles SQLAlchemy
│   │   └── __init__.py      # User, Employee, Medicine, Supplier,
│   │                         # Sale, SaleItem, Activity, DailyReport
│   ├── routes/               # Blueprints
│   │   ├── auth.py          # Login/logout
│   │   ├── dashboard.py     # Dashboard gerant
│   │   ├── medicines.py     # CRUD medicaments
│   │   ├── suppliers.py     # CRUD fournisseurs
│   │   ├── sales.py         # Interface vente + API
│   │   ├── employees.py     # CRUD employes
│   │   ├── employee.py      # Espace employe (stats, rapport)
│   │   ├── reports.py       # Rapports
│   │   └── activities.py    # Journal d'audit
│   ├── services/            # Logique metier
│   │   ├── sales_service.py
│   │   ├── report_service.py
│   │   └── activity_service.py
│   ├── utils/               # Utilitaires
│   │   ├── decorators.py   # gerant_required, employee_required
│   │   ├── validators.py
│   │   └── helpers.py
│   ├── templates/           # Jinja2
│   │   ├── base.html       # Layout: sidebar gerant / simple employe
│   │   ├── auth/login.html
│   │   ├── dashboard/
│   │   ├── medicines/
│   │   ├── suppliers/
│   │   ├── sales/
│   │   ├── employees/
│   │   ├── employee/
│   │   ├── reports/
│   │   └── activities/
│   └── static/
│       ├── css/style.css   # Theme vert pharmacie (#198754)
│       ├── js/main.js
│       └── images/
│
├── instance/                 # Base de donnees SQLite
└── venv/                     # Environnement virtuel
```

## Modeles de donnees

- **User** : Gerant (id, email, nom, prenom, password_hash, role='gerant')
- **Employee** : Employe (id, nom, postnom, prenom, email, telephone, fonction, password_hash, gerant_id)
- **Medicine** : Medicament (nom, categorie, prix_achat, prix_vente, quantite, stock_minimum, code_barre, date_expiration, gerant_id, fournisseur_id)
- **Supplier** : Fournisseur (nom, telephone, email, adresse, responsable, gerant_id)
- **Sale** : Vente (employee_id, total_amount, total_cost, profit, payment_method)
- **SaleItem** : Article vendu (sale_id, medicine_id, quantity, unit_price, unit_cost)
- **Activity** : Journal (user_id, action, details)
- **DailyReport** : Rapport journalier (date, total_sales, total_amount, total_profit)

## Permissions

| Page | Gerant | Employe |
|------|--------|---------|
| /dashboard | Oui | Non |
| /medicines/ | Oui | Non |
| /suppliers/ | Oui | Non |
| /employees/ | Oui | Non |
| /reports/ | Oui | Non |
| /activities/ | Oui | Non |
| /sales/list | Oui | Non |
| /sales/ (interface) | Oui | Oui |
| /employee/ | Non | Oui |
| /sales/api/create | Oui | Oui |

L'employe peut uniquement : ajouter une vente, voir ses stats du jour,
voir le stock disponible, telecharger le rapport journalier.

## API Endpoints

### Authentification
- `POST /login` - Connexion
- `GET /logout` - Deconnexion

### Dashboard (gerant)
- `GET /api/dashboard/stats` - Statistiques
- `GET /api/dashboard/sales-evolution` - Evolution ventes
- `GET /api/dashboard/activities` - Activites recentes

### Medicaments
- `GET /medicines/api/list` - Liste
- `POST /medicines/api/create` - Creer
- `PUT /medicines/api/<id>/update` - Modifier
- `DELETE /medicines/api/<id>` - Supprimer

### Ventes
- `GET /sales/api/medicines` - Medicaments disponibles
- `POST /sales/api/create` - Creer une vente
- `GET /sales/<id>/details` - Details vente
- `POST /sales/<id>/delete` - Supprimer vente

### Employes (gerant)
- `GET /employees/api/list` - Liste
- `POST /employees/api/create` - Creer
- `POST /employees/<id>/delete` - Supprimer
- `POST /employees/<id>/toggle-status` - Activer/desactiver

## Technologies

- **Backend** : Flask 3.0, SQLAlchemy 2.0, Flask-Login, Flask-CORS
- **Base de donnees** : SQLite
- **Frontend** : Bootstrap 5, Font Awesome, Chart.js
- **Rapports** : ReportLab (PDF), OpenPyXL (Excel)

## Configuration

Dans `.env` :

```
FLASK_ENV=development
SECRET_KEY=cle-secrete
```

## Troubleshooting

```bash
# Database corrompue -> supprimer et relancer
del instance\assurance_pharma.db
python run.py

# Port deja utilise
python run.py  # change le port dans run.py
```

---

**Version** : 2.0.0  
**Theme** : Vert pharmacie (#198754)  
**Icone** : fa-mortar-pestle

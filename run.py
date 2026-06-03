#!/usr/bin/env python
"""
Point d'entrée de l'application AssurancePharma
"""

import os
from app import create_app

# Configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Mode développement
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )

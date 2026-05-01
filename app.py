import os
from datetime import timedelta

from flask import Flask
from routes import bp as main_bp
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-for-production')
    app.config['ADMIN_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'voodrok')
    app.config['API_ADD_KEY'] = os.environ.get('API_ADD_KEY', '')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL',
        'sqlite:///recipes.db',
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
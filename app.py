from flask import Flask
from routes import bp as main_bp
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(main_bp)  # Ensure the blueprint is registered

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
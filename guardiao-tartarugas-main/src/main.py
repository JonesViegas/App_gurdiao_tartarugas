import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_mail import Mail
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.ninhos import ninhos_bp
from src.routes.upload import upload_bp
from src.routes.ranking import ranking_bp
from src.routes.admin import admin_bp
from src.routes.relatorios import relatorios_bp
from src.routes.contact import contact_bp

# --- IMPORTAÇÃO DO MANAGE ATUALIZADA ---
from manage import register_commands

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'chave-local-padrao'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('EMAIL_USER'),
    MAIL_PASSWORD=os.environ.get('EMAIL_PASS'),
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

CORS(app)
mail = Mail(app)
db.init_app(app)

# --- REGISTRO DOS COMANDOS ATUALIZADO ---
register_commands(app)

# Registro dos Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ninhos_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(ranking_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(relatorios_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')

from src.models.ninho import Ninho

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = app.static_folder
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
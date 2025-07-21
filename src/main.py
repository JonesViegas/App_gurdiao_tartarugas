import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS  # <-- ESTA É A LINHA QUE FALTAVA
from flask_mail import Mail
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.ninhos import ninhos_bp
from src.routes.upload import upload_bp
from src.routes.ranking import ranking_bp
from src.routes.admin import admin_bp
from src.routes.relatorios import relatorios_bp
from src.routes.contact import contact_bp # 1. Importar a nova rota de contato

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
CORS(app)  # Agora esta linha funcionará

# --- CONFIGURAÇÃO DE E-MAIL (AGORA LÊ DO .ENV) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

# Configuração do Banco de Dados
db_path = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(db_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_path, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registro dos Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ninhos_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(ranking_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(relatorios_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api') # 2. Registrar o novo blueprint
# Importa modelos para criação das tabelas
from src.models.ninho import Ninho

# Cria tabelas se não existirem
with app.app_context():
    db.create_all()

# Rota para servir o frontend
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
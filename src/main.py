import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente
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
from src.routes.contact import contact_bp # Mantendo sua importação

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# --- CONFIGURAÇÃO CENTRALIZADA DA APLICAÇÃO ---
app.config.from_mapping(
    # Chave secreta para sessões e tokens. Lida a partir do .env
    SECRET_KEY=os.environ.get('SECRET_KEY', 'chave-secreta-padrao-para-desenvolvimento'),
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,

    # Configuração de E-mail (lê do .env)
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=os.environ.get('EMAIL_USER'),
    MAIL_PASSWORD=os.environ.get('EMAIL_PASS'),

    # --- LÓGICA DO BANCO DE DADOS ATUALIZADA ---
    # Em produção (no Render), a variável DATABASE_URL existirá e usará PostgreSQL.
    # Localmente, ela não existirá, e o app usará o arquivo SQLite.
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

# Inicialização das extensões
CORS(app)
mail = Mail(app)
db.init_app(app)

# --- REGISTRA OS COMANDOS DE GERENCIAMENTO (EX: promote-admin) ---
import manage

# Registro dos Blueprints (Rotas)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ninhos_bp, url_prefix='/api')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(ranking_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(relatorios_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api') # Mantendo o registro do seu blueprint

# Importa modelos para garantir a criação das tabelas
from src.models.ninho import Ninho

# Cria as tabelas do banco de dados se elas não existirem
with app.app_context():
    db.create_all()

# Rota principal para servir a aplicação frontend
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
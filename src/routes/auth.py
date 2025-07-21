from flask import Blueprint, request, jsonify, session, url_for, current_app
from src.models.user import User, db
from werkzeug.security import check_password_hash
from functools import wraps
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_mail import Message
# A linha 'from src.main import mail' foi REMOVIDA do topo

auth_bp = Blueprint('auth', __name__)

# Funções login_required e admin_required permanecem as mesmas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Login necessário'}), 401
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Acesso de administrador necessário'}), 403
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    # --- AQUI ESTÁ A CORREÇÃO ---
    # Importamos 'mail' localmente, apenas quando esta função é chamada.
    # Neste ponto, o app já está totalmente carregado e 'mail' existe.
    from src.main import mail

    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Se o e-mail estiver cadastrado, um link de recuperação será enviado.'}), 200

    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(user.email, salt='email-confirm-salt')
    reset_url = url_for('serve', path=f'reset.html?token={token}', _external=True)

    msg = Message('Redefinição de Senha - Guardião das Tartaruguinhas',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f'Para redefinir sua senha, clique no link a seguir: {reset_url}\n\nSe você não solicitou isso, ignore este e-mail.'
    mail.send(msg)

    return jsonify({'message': 'Se o e-mail estiver cadastrado, um link de recuperação será enviado.'}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    token = request.json.get('token')
    new_password = request.json.get('password')

    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({'error': 'O link de redefinição expirou.'}), 400
    except Exception:
        return jsonify({'error': 'Token inválido ou corrompido.'}), 400

    user = User.query.filter_by(email=email).first_or_404()
    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Sua senha foi redefinida com sucesso!'}), 200


# O resto das rotas (login, register, logout, me) permanecem as mesmas.
# ... (cole aqui suas rotas de login, register, logout e me se elas estiverem neste arquivo) ...
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and user.check_password(data.get('password')) and user.ativo:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': 'Login realizado com sucesso', 'user': user.to_dict()}), 200
    return jsonify({'error': 'Credenciais inválidas ou usuário inativo'}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username já existe'}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email já está cadastrado'}), 400

    new_user = User(
        username=data['username'], email=data['email'], nome_completo=data['nome_completo']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Usuário cadastrado com sucesso', 'user': new_user.to_dict()}), 201

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.ativo:
            return jsonify({'user': user.to_dict()}), 200
    return jsonify({'error': 'Usuário não autenticado'}), 401
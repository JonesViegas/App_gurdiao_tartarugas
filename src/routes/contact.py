from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def handle_contact_form():
    # Importa 'mail' localmente para evitar importações circulares
    from src.main import mail
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not all([name, email, message]):
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

    try:
        # O destinatário do e-mail será o e-mail configurado no seu arquivo .env
        recipient_email = current_app.config['MAIL_USERNAME']
        
        msg = Message(
            subject=f"Novo Contato do App Guardião: {name}",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[recipient_email]
        )
        
        msg.body = f"""
        Você recebeu uma nova mensagem de contato através do sistema Guardião das Tartaruguinhas.

        Nome: {name}
        E-mail de Contato: {email}

        Mensagem:
        --------------------------------------------------
        {message}
        --------------------------------------------------
        """
        
        mail.send(msg)
        
        return jsonify({'message': 'Mensagem enviada com sucesso! Obrigado pelo contato.'}), 200

    except Exception as e:
        print(f"Erro ao enviar e-mail de contato: {e}")
        return jsonify({'error': 'Ocorreu um erro ao tentar enviar a mensagem.'}), 500
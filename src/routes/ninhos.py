from flask import Blueprint, request, jsonify, session
from src.models.ninho import Ninho, db
from src.routes.auth import login_required
from sqlalchemy import func

ninhos_bp = Blueprint('ninhos', __name__)

@ninhos_bp.route('/ninhos', methods=['POST'])
@login_required
def criar_ninho():
    try:
        data = request.get_json()

        # Validações básicas (opcional, mas recomendado)
        required_fields = ['regiao', 'quantidade_ovos', 'status', 'risco', 'dias_para_eclosao']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400

        # ---- AQUI ESTÁ A CORREÇÃO ----
        # Converte a string 'true'/'false' do formulário para um booleano Python
        predadores_bool = str(data.get('predadores', 'false')).lower() == 'true'

        novo_ninho = Ninho(
            regiao=data['regiao'],
            quantidade_ovos=int(data['quantidade_ovos']),
            status=data['status'],
            risco=data['risco'],
            dias_para_eclosao=int(data['dias_para_eclosao']),
            predadores=predadores_bool,  # Usando o valor booleano corrigido
            latitude=float(data['latitude']) if data.get('latitude') else None,
            longitude=float(data['longitude']) if data.get('longitude') else None,
            foto_path=data.get('foto_path'),
            usuario_id=session['user_id']
        )
        
        db.session.add(novo_ninho)
        db.session.commit()
        
        return jsonify({'message': 'Ninho criado com sucesso', 'ninho': novo_ninho.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar ninho: {e}") # Log do erro no terminal para depuração
        return jsonify({'error': 'Ocorreu um erro interno ao salvar o ninho.'}), 500


@ninhos_bp.route('/ninhos', methods=['GET'])
@login_required
def listar_ninhos():
    query = Ninho.query.filter_by(usuario_id=session['user_id'])
    ninhos = query.order_by(Ninho.data_registro.desc()).all()
    return jsonify({'ninhos': [ninho.to_dict() for ninho in ninhos]}), 200


@ninhos_bp.route('/estatisticas', methods=['GET'])
@login_required
def obter_estatisticas():
    stats = {
        'total_ninhos': Ninho.query.count(),
        'ninhos_por_status': dict(db.session.query(Ninho.status, func.count(Ninho.id)).group_by(Ninho.status).all()),
        'ninhos_por_risco': dict(db.session.query(Ninho.risco, func.count(Ninho.id)).group_by(Ninho.risco).all()),
        'ninhos_prestes_eclodir': Ninho.query.filter(Ninho.dias_para_eclosao <= 5).count(),
        'media_ovos_critico': round(db.session.query(func.avg(Ninho.quantidade_ovos)).filter(Ninho.risco == 'crítico').scalar() or 0, 2),
        'regiao_mais_criticos': (db.session.query(Ninho.regiao).filter(Ninho.risco == 'crítico').group_by(Ninho.regiao).order_by(func.count(Ninho.id).desc()).first() or [None])[0],
        'ninhos_predadores_danificados': Ninho.query.filter(Ninho.predadores == True, Ninho.status == 'danificado').count()
    }
    return jsonify(stats), 200
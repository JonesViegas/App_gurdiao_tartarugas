from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.models.ninho import Ninho
from src.routes.auth import login_required
from sqlalchemy import func, case
from datetime import datetime, date

ranking_bp = Blueprint('ranking', __name__)

def get_ranking_data(periodo='geral'):
    """
    Busca e calcula os dados do ranking com base em um sistema de pontos.
    - Crítico: 10 pontos
    - Sob Observação: 5 pontos
    - Estável: 2 pontos
    - Bônus por Foto: +1 ponto
    """
    # Define a expressão de pontos usando a função CASE do SQL
    pontos_expression = case(
        (Ninho.risco == 'crítico', 10),
        (Ninho.risco == 'sob observação', 5),
        (Ninho.risco == 'estável', 2),
        else_=0
    ) + case(
        (Ninho.foto_path != None, 1),
        else_=0
    )

    # Inicia a consulta base
    query = db.session.query(
        User.id,
        User.username,
        User.nome_completo,
        func.count(Ninho.id).label('total_ninhos'),
        func.sum(pontos_expression).label('total_pontos')
    ).join(Ninho, User.id == Ninho.usuario_id).filter(User.ativo == True)

    # Aplica o filtro de período se for 'mes'
    if periodo == 'mes':
        today = date.today()
        start_of_month = today.replace(day=1)
        query = query.filter(Ninho.data_registro >= start_of_month)

    # Agrupa, ordena e executa a consulta
    ranking_data = query.group_by(User.id).order_by(
        func.sum(pontos_expression).desc(), 
        func.count(Ninho.id).desc()
    ).all()
    
    # Formata a lista de saída
    ranking_list = []
    for position, user_data in enumerate(ranking_data, 1):
        ranking_list.append({
            'posicao': position,
            'user_id': user_data.id,
            'username': user_data.username,
            'nome_completo': user_data.nome_completo,
            'total_ninhos': user_data.total_ninhos or 0,
            'total_pontos': int(user_data.total_pontos or 0) # Garante que seja inteiro
        })

    return ranking_list

@ranking_bp.route('/ranking', methods=['GET'])
@login_required
def get_ranking():
    """
    Rota principal do ranking, que pode retornar o ranking 'geral' ou do 'mes'.
    Exemplo de uso: /api/ranking?periodo=mes
    """
    try:
        periodo = request.args.get('periodo', 'geral') # 'geral' é o padrão
        if periodo not in ['geral', 'mes']:
            return jsonify({'error': "Período inválido. Use 'geral' ou 'mes'."}), 400

        ranking_list = get_ranking_data(periodo)

        return jsonify({
            'periodo': periodo,
            'ranking': ranking_list,
            'total_usuarios_no_ranking': len(ranking_list)
        }), 200

    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"Erro ao gerar ranking: {e}")
        return jsonify({'error': 'Ocorreu um erro interno ao gerar o ranking.'}), 500

# A rota de estatísticas continua a mesma e pode ser mantida ou removida se não for mais usada.
@ranking_bp.route('/ranking/estatisticas', methods=['GET'])
@login_required
def get_ranking_statistics():
    """Rota para obter estatísticas gerais do sistema."""
    try:
        # Total de usuários ativos
        total_usuarios = User.query.filter(User.ativo == True).count()
        # Total de ninhos catalogados
        total_ninhos = Ninho.query.count()
        # Distribuição por região (top 5)
        distribuicao_regioes = db.session.query(
            Ninho.regiao,
            func.count(Ninho.id).label('total_ninhos')
        ).group_by(Ninho.regiao)\
         .order_by(func.count(Ninho.id).desc())\
         .limit(5).all()

        regioes_top = [
            {'regiao': regiao, 'total_ninhos': total}
            for regiao, total in distribuicao_regioes
        ]
        return jsonify({
            'total_usuarios': total_usuarios,
            'total_ninhos': total_ninhos,
            'regioes_top': regioes_top
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
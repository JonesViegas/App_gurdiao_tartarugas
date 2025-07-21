import io
import csv
from flask import Blueprint, Response
from src.models.ninho import Ninho
from src.routes.auth import admin_required

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios/ninhos', methods=['GET'])
@admin_required
def exportar_ninhos_csv():
    # Busca todos os ninhos com informações do usuário
    ninhos = Ninho.query.join(Ninho.usuario).all()

    # Cria um arquivo CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)

    # Escreve o cabeçalho
    writer.writerow([
        'ID Ninho', 'Região', 'Qtd Ovos', 'Status', 'Risco',
        'Dias para Eclosão', 'Predadores', 'Latitude', 'Longitude',
        'Data Registro', 'ID Voluntário', 'Nome Voluntário'
    ])

    # Escreve os dados de cada ninho
    for ninho in ninhos:
        writer.writerow([
            ninho.id, ninho.regiao, ninho.quantidade_ovos, ninho.status, ninho.risco,
            ninho.dias_para_eclosao, 'Sim' if ninho.predadores else 'Não',
            ninho.latitude, ninho.longitude, ninho.data_registro.strftime('%Y-%m-%d %H:%M'),
            ninho.usuario.id, ninho.usuario.nome_completo
        ])

    output.seek(0)

    # Retorna o arquivo como um download
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=relatorio_ninhos.csv"}
    )
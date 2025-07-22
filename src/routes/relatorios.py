import io
from flask import Blueprint, Response, jsonify
from src.models.ninho import Ninho
from src.routes.auth import admin_required
from openpyxl import Workbook # Importa a biblioteca para criar Excel

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios/ninhos/data', methods=['GET'])
@admin_required
def get_ninhos_data():
    """Retorna uma lista completa de todos os ninhos para a tabela de relatórios."""
    try:
        ninhos = Ninho.query.join(Ninho.usuario).order_by(Ninho.data_registro.desc()).all()
        return jsonify([ninho.to_dict() for ninho in ninhos]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@relatorios_bp.route('/relatorios/ninhos/export', methods=['GET'])
@admin_required
def exportar_ninhos_excel():
    """NOVA VERSÃO: Gera e retorna um arquivo Excel (.xlsx) com todos os dados dos ninhos."""
    try:
        ninhos = Ninho.query.join(Ninho.usuario).all()
        
        # Cria um Workbook (arquivo Excel) em memória
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatorio de Ninhos"

        # Escreve o cabeçalho
        header = [
            'ID Ninho', 'Região', 'Qtd Ovos', 'Status', 'Risco',
            'Dias para Eclosão', 'Predadores', 'Latitude', 'Longitude',
            'Data Registro', 'ID Voluntário', 'Nome Voluntário'
        ]
        ws.append(header)

        # Escreve os dados de cada ninho
        for ninho in ninhos:
            row = [
                ninho.id, ninho.regiao, ninho.quantidade_ovos, ninho.status, ninho.risco,
                ninho.dias_para_eclosao, 'Sim' if ninho.predadores else 'Não',
                ninho.latitude, ninho.longitude, ninho.data_registro.strftime('%Y-%m-%d %H:%M'),
                ninho.usuario.id, ninho.usuario.nome_completo
            ]
            ws.append(row)

        # Salva o arquivo em um stream de bytes em memória
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        # Retorna o arquivo como um download
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=relatorio_ninhos.xlsx"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
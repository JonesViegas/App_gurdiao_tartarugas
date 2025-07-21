from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.routes.auth import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([user.to_dict() for user in users]), 200

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    if 'ativo' in data: user.ativo = data['ativo']
    if 'is_admin' in data: user.is_admin = data['is_admin']

    db.session.commit()
    return jsonify({'message': 'Usuário atualizado', 'user': user.to_dict()}), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_by_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get('user_id'):
        return jsonify({'error': 'Não é possível deletar a si mesmo.'}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200
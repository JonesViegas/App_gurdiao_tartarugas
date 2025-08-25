from src.models.user import db
from datetime import datetime

class Ninho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(100), nullable=False)
    quantidade_ovos = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    risco = db.Column(db.String(20), nullable=False)
    dias_para_eclosao = db.Column(db.Integer, nullable=False)
    predadores = db.Column(db.Boolean, nullable=False, default=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    foto_path = db.Column(db.String(255), nullable=True)
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    usuario = db.relationship('User', backref=db.backref('ninhos', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            'id': self.id,
            'regiao': self.regiao,
            'quantidade_ovos': self.quantidade_ovos,
            'status': self.status,
            'risco': self.risco,
            'dias_para_eclosao': self.dias_para_eclosao,
            'predadores': self.predadores,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'foto_path': self.foto_path,
            'data_registro': self.data_registro.isoformat(),
            'usuario_id': self.usuario_id,
            'usuario_nome': self.usuario.username if self.usuario else None
        }
# manage.py

from src.models.user import User, db

def register_commands(app):
    """Registra comandos CLI na aplicação Flask."""
    
    @app.cli.command("promote-admin")
    def promote_admin_command(email):
        """Promove um usuário a administrador pelo email."""
        with app.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"Erro: Usuário com email '{email}' não encontrado.")
                return

            user.is_admin = True
            db.session.commit()
            print(f"Sucesso! Usuário '{user.username}' ({user.email}) foi promovido a administrador.")
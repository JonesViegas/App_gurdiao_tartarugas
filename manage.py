from src.main import app, db
from src.models.user import User

@app.cli.command("promote-admin")
def promote_admin_command(email):
    """Promove um usuário a administrador pelo email."""
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"Erro: Usuário com email '{email}' não encontrado.")
        return

    user.is_admin = True
    db.session.commit()
    print(f"Sucesso! Usuário '{user.username}' ({user.email}) foi promovido a administrador.")

if __name__ == "__main__":
    app.cli()
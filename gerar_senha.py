from werkzeug.security import generate_password_hash

# Escolha a senha que você quer usar para todos os voluntários de teste
senha_plana = "senha123"

# Gera o hash
senha_criptografada = generate_password_hash(senha_plana)

# Imprime o resultado para você copiar
print("\n--- COPIE A LINHA ABAIXO (INCLUINDO 'scrypt:') ---\n")
print(senha_criptografada)
print("\n-------------------------------------------------\n")
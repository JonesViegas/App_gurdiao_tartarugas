# 🐢 Guardião das Tartaruguinhas

Sistema de monitoramento comunitário de ninhos de tartarugas desenvolvido em Python com Flask e SQLite.

## 📋 Descrição

O **Guardião das Tartaruguinhas** é um sistema web completo para auxiliar comunidades ribeirinhas no monitoramento e catalogação de ninhos de tartarugas. O projeto foi inspirado em iniciativas de conservação da Amazônia e permite que voluntários registrem, acompanhem e analisem dados sobre ninhos encontrados.

## ✨ Funcionalidades

### 🔐 Sistema de Autenticação
- Cadastro de voluntários
- Login seguro com hash de senhas
- Controle de sessão

### 🥚 Catalogação de Ninhos
- Formulário completo para registro de ninhos
- Campos: região, quantidade de ovos, status, risco, dias para eclosão, presença de predadores
- Upload de fotos do local
- Captura automática de coordenadas geográficas (GPS)
- Validação de dados

### 📊 Estatísticas e Análises
- Dashboard com estatísticas em tempo real
- Total de ninhos catalogados
- Ninhos prestes a eclodir
- Média de ovos por ninho crítico
- Região com mais ninhos em risco
- Ninhos com predadores e danificados

### 🏆 Sistema de Ranking
- Classificação de voluntários por número de ninhos catalogados
- Medalhas para os primeiros colocados
- Estatísticas de participação

### 📱 Interface Responsiva
- Design adaptável para desktop e mobile
- Interface intuitiva e amigável
- Suporte a touch para dispositivos móveis

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.11, Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Autenticação**: Werkzeug Security
- **Upload de Arquivos**: Flask File Upload
- **Geolocalização**: HTML5 Geolocation API

## 📦 Estrutura do Projeto

```
guardiao_tartarugas/
├── src/
│   ├── models/          # Modelos do banco de dados
│   │   ├── user.py      # Modelo de usuário
│   │   └── ninho.py     # Modelo de ninho
│   ├── routes/          # Rotas da API
│   │   ├── auth.py      # Autenticação
│   │   ├── ninhos.py    # Gerenciamento de ninhos
│   │   ├── ranking.py   # Sistema de ranking
│   │   ├── upload.py    # Upload de arquivos
│   │   └── user.py      # Gerenciamento de usuários
│   ├── static/          # Arquivos estáticos
│   │   ├── index.html   # Interface principal
│   │   ├── app.js       # JavaScript da aplicação
│   │   └── uploads/     # Pasta para fotos enviadas
│   ├── database/        # Banco de dados SQLite
│   └── main.py          # Arquivo principal da aplicação
├── venv/                # Ambiente virtual Python
├── requirements.txt     # Dependências do projeto
└── README.md           # Este arquivo
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd guardiao_tartarugas
```

2. **Ative o ambiente virtual**
```bash
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
python src/main.py
```

5. **Acesse no navegador**
```
http://localhost:5001
```

## 📱 Como Usar

### 1. Cadastro de Voluntário
- Acesse a página inicial
- Preencha o formulário "Cadastro de Voluntário"
- Informe: nome completo, usuário, email e senha
- Clique em "Cadastrar"

### 2. Login
- Use suas credenciais no formulário "Login"
- Clique em "Entrar"

### 3. Cadastrar Ninho
- No dashboard, vá para a aba "Cadastrar Ninho"
- Preencha todos os campos obrigatórios
- Use o botão "📍 Obter Localização Atual" para capturar GPS
- Adicione uma foto do local (opcional)
- Clique em "Cadastrar Ninho"

### 4. Visualizar Dados
- **Estatísticas**: Veja dados gerais na aba "Estatísticas"
- **Meus Ninhos**: Visualize seus ninhos cadastrados
- **Ranking**: Confira sua posição no ranking de voluntários

## 🌐 Deploy Gratuito

O sistema pode ser facilmente implantado em plataformas gratuitas:

### Heroku
1. Crie uma conta no [Heroku](https://heroku.com)
2. Instale o Heroku CLI
3. Execute os comandos:
```bash
heroku create nome-do-app
git push heroku main
```

### Railway
1. Conecte seu repositório GitHub ao [Railway](https://railway.app)
2. O deploy será automático

### Render
1. Conecte seu repositório ao [Render](https://render.com)
2. Configure como Web Service
3. Use o comando: `python src/main.py`

## 🔧 Configurações de Produção

Para produção, altere as seguintes configurações em `src/main.py`:

```python
# Altere a SECRET_KEY para uma chave segura
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'

# Para produção, use debug=False
app.run(host='0.0.0.0', port=5000, debug=False)
```

## 📊 API Endpoints

### Autenticação
- `POST /api/auth/register` - Cadastro de usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Dados do usuário logado

### Ninhos
- `POST /api/ninhos` - Criar ninho
- `GET /api/ninhos` - Listar ninhos
- `GET /api/ninhos/<id>` - Obter ninho específico
- `PUT /api/ninhos/<id>` - Atualizar ninho
- `DELETE /api/ninhos/<id>` - Deletar ninho
- `GET /api/estatisticas` - Estatísticas gerais

### Ranking
- `GET /api/ranking` - Ranking de usuários
- `GET /api/ranking/estatisticas` - Estatísticas do ranking

### Upload
- `POST /api/upload` - Upload de arquivo
- `GET /api/uploads/<filename>` - Servir arquivo

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🌟 Agradecimentos

- Inspirado nos projetos de conservação da Amazônia
- Comunidades ribeirinhas que protegem os quelônios
- Projeto Pé-de-Pincha e iniciativas similares

## 📞 Suporte

Para dúvidas ou suporte, abra uma issue no repositório do GitHub.

---

**Desenvolvido com 💚 para a preservação das tartarugas amazônicas**


# Gerenciamento de Estoque

Sistema de gerenciamento de estoque e PDV (ponto de venda) com controle de usuários, clientes, produtos, vendas e log de atividades.

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Auth | Flask-Login |
| Banco local | SQLite (padrão) |
| Banco produção | PostgreSQL (via `DATABASE_URL`) |
| Servidor | Gunicorn |

## Rodando localmente

```bash
# Cria e ativa o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

# Instala dependências
pip install -e .
# ou com uv:
uv sync

# Inicia o servidor
gunicorn main:app
# Aplicação disponível em http://localhost:8000
```

Ou diretamente com o Flask em modo desenvolvimento:

```bash
flask --app main run --debug
```

## Variáveis de ambiente

Crie um arquivo `.env` na raiz (opcional para desenvolvimento local):

```env
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=postgresql://user:pass@localhost:5432/estoque
```

Sem `DATABASE_URL` o sistema usa SQLite (`instance/estoque.db`).

## Credenciais padrão

Na primeira execução o sistema cria automaticamente um admin:

- **Email:** `admin@sistema.com`
- **Senha:** `admin123`

## Estrutura

```
gerenciamento-estoque/
├── main.py              # Entry point + factory
├── config.py            # Configuração
├── models/              # Modelos SQLAlchemy
├── endpoints/           # Blueprints Flask
├── services/
│   └── logger.py        # Logger funcional de ações
├── templates/           # Templates Jinja2
└── public/              # Assets estáticos
```

## Logger de atividades

Toda ação de usuário é registrada em `logs` com diff do que mudou:

- **Criação** — registra os campos do novo objeto
- **Edição** — registra apenas os campos alterados (`de` → `para`)
- **Exclusão** — registra o estado antes da remoção
- **Login/Logout/Venda** — registra ação com contexto

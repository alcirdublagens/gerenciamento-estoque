# Gerenciamento de Estoque

Aplicação web da All Import Store para controle de estoque, clientes, usuários,
vendas no PDV, pagamentos e logs de atividade.

## Funcionalidades

- Autenticação com perfis de administrador e vendedor.
- Cadastro e desativação de usuários e clientes.
- Cadastro de produtos, preços, custo e estoque mínimo.
- PDV com baixa automática de estoque.
- Vendas à vista, a prazo ou parceladas.
- Acompanhamento de pagamentos pendentes e vencidos.
- Dashboard de vendas, lucro, estoque e desempenho de vendedores.
- Log de criação, edição, exclusão, login, logout e vendas.

## Stack

| Camada | Tecnologia |
|---|---|
| Aplicação web | Flask 3.x |
| Persistência | Flask-SQLAlchemy |
| Autenticação | Flask-Login |
| Banco local | SQLite |
| Banco de produção | PostgreSQL com psycopg2 |
| Templates | Jinja2 e Bootstrap |
| Servidor WSGI | Gunicorn |

## Instalação com Docker

Essa é a forma recomendada para executar o sistema no computador do cliente.
O Compose inicia a aplicação e um banco PostgreSQL, mantendo os dados em pastas
locais dentro do projeto.

### Requisitos

- Docker Engine com o plugin Docker Compose, ou Docker Desktop.

### Passo 1: criar o arquivo de configuração

Crie o arquivo de configuração a partir do exemplo:

```bash
cp .env.example .env
```

O Docker Compose lê automaticamente o arquivo `.env` localizado na mesma pasta
do `compose.yaml`.

Edite o `.env` antes de iniciar o sistema:

```env
APP_PORT=8000
SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria

POSTGRES_DB=estoque
POSTGRES_USER=estoque
POSTGRES_PASSWORD=troque-por-uma-senha-forte
POSTGRES_PORT=5432

DATABASE_URL=
```

Troque, no mínimo, `SECRET_KEY` e `POSTGRES_PASSWORD`. Uma `SECRET_KEY` pode ser
gerada com:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Variáveis disponíveis:

| Variável | Obrigatória | Exemplo | Descrição |
|---|---|---|---|
| `APP_PORT` | Não | `8000` | Porta usada para acessar o sistema |
| `SECRET_KEY` | Sim | valor aleatório | Chave de assinatura das sessões |
| `POSTGRES_DB` | Sim | `estoque` | Nome do banco PostgreSQL |
| `POSTGRES_USER` | Sim | `estoque` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | Sim | senha forte | Senha do PostgreSQL |
| `POSTGRES_PORT` | Não | `5432` | Porta local do PostgreSQL |
| `DATABASE_URL` | Não | vazio | Alternativa para execução sem Docker |

No uso com Docker, mantenha `DATABASE_URL` vazia. Ela não é necessária para a
comunicação entre os containers.

Se a porta `8000` já estiver ocupada, altere `APP_PORT`. Se a porta `5432`
estiver ocupada, altere `POSTGRES_PORT`. Essas mudanças afetam apenas as portas
do computador; não alteram as portas internas dos containers.

Defina `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` antes da primeira
inicialização. A imagem do PostgreSQL usa esses valores apenas para criar um
banco novo. Alterá-los depois que `data/postgres/` já possui dados não renomeia
o banco nem troca automaticamente as credenciais existentes.

### Como a conexão com o banco é definida

O arquivo `config.py` escolhe a conexão nesta ordem:

1. Se `DATABASE_URL` estiver preenchida, usa essa URL diretamente.
2. Se `DATABASE_URL` estiver vazia e `DB_HOST` existir, monta uma conexão
   PostgreSQL usando as variáveis `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e
   `DB_PASSWORD`.
3. Se nenhuma dessas configurações existir, usa SQLite em
   `instance/estoque.db`.

No Docker, o `compose.yaml` fornece automaticamente ao container da aplicação:

```text
DB_HOST=db
DB_PORT=5432
DB_NAME=<valor de POSTGRES_DB>
DB_USER=<valor de POSTGRES_USER>
DB_PASSWORD=<valor de POSTGRES_PASSWORD>
```

O nome `db` é o nome do serviço PostgreSQL no Compose. A rede interna criada
pelo Docker possui resolução de nomes própria, portanto o container da
aplicação encontra o PostgreSQL usando `db:5432`.

A conexão interna equivale conceitualmente a:

```text
postgresql+psycopg2://POSTGRES_USER:POSTGRES_PASSWORD@db:5432/POSTGRES_DB
```

Ela é construída pela API do SQLAlchemy, e não por concatenação de texto. Isso
evita problemas de codificação quando a senha contém caracteres especiais.

`POSTGRES_PORT` não é usado pela aplicação. Ele publica a porta do PostgreSQL
no computador para acesso opcional por ferramentas como DBeaver ou pgAdmin:

```text
Host: localhost
Porta: valor de POSTGRES_PORT
Banco: valor de POSTGRES_DB
Usuário: valor de POSTGRES_USER
Senha: valor de POSTGRES_PASSWORD
```

As portas da aplicação e do PostgreSQL são publicadas somente em `127.0.0.1`.
Por padrão, o sistema e o banco não ficam disponíveis para outros computadores
da rede local.

### Quando usar `DATABASE_URL`

Use `DATABASE_URL` quando executar a aplicação fora do Docker e quiser conectá-la
a um PostgreSQL já existente:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/estoque
```

Também pode ser usada em uma hospedagem que forneça a conexão completa em uma
única variável. Quando `DATABASE_URL` estiver preenchida, ela tem prioridade
sobre todas as variáveis `DB_*`. Caracteres reservados presentes no usuário ou
na senha precisam estar codificados para URL quando essa forma for utilizada.

Para a instalação padrão com `docker compose`, deixe-a vazia:

```env
DATABASE_URL=
```

### Passo 2: iniciar os serviços

Construa as imagens e inicie os serviços:

```bash
docker compose up -d --build
```

Confira o estado dos containers:

```bash
docker compose ps
```

O Compose aguarda o healthcheck do PostgreSQL antes de iniciar a aplicação. Na
primeira execução, também cria automaticamente as tabelas e o usuário
administrador.

### Passo 3: acessar a aplicação

Com `APP_PORT=8000`, acesse:

```text
http://localhost:8000
```

Use as credenciais iniciais:

```text
Email: admin@sistema.com
Senha: admin123
```

Troque a senha após o primeiro acesso.

### Passo 4: verificar ou diagnosticar

Para acompanhar os logs:

```bash
docker compose logs -f app
```

Para visualizar também os logs do PostgreSQL:

```bash
docker compose logs -f db
```

Se algum serviço não aparecer como iniciado ou saudável, execute:

```bash
docker compose ps
docker compose logs app
docker compose logs db
```

### Passo 5: parar e reiniciar

Para parar os serviços sem remover os dados:

```bash
docker compose down
```

Para iniciar novamente:

```bash
docker compose up -d
```

### Persistência

O Compose usa bind mounts para manter os dados fora dos containers:

| Pasta local | Conteúdo |
|---|---|
| `data/postgres/` | Arquivos do banco PostgreSQL |
| `data/app/` | Arquivos persistentes da aplicação |
| `data/backups/` | Local recomendado para backups manuais |

Essas pastas são ignoradas pelo Git. Recriar ou atualizar os containers não
remove seu conteúdo. Para migrar a instalação, copie o projeto com a pasta
`data/` e o arquivo `.env`, mantendo-os protegidos.

### Backup e restauração

Crie a pasta e gere um backup:

```bash
mkdir -p data/backups
docker compose exec -T db sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > data/backups/estoque.dump
```

Para restaurar um backup, pare a aplicação durante a operação:

```bash
docker compose stop app
docker compose exec -T db sh -c \
  'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < data/backups/estoque.dump
docker compose start app
```

A restauração substitui os objetos existentes no banco selecionado.

## Execução sem Docker

Requisitos:

- Python 3.9 ou superior.

Crie o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, a ativação é:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -e .
```

Alternativamente, com `uv`:

```bash
uv sync
```

Para desenvolvimento:

```bash
flask --app main run --debug
```

A aplicação estará disponível em `http://127.0.0.1:5000`.

Para executar com Gunicorn:

```bash
gunicorn main:app
```

Nesse caso, o endereço padrão é `http://127.0.0.1:8000`.

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `SECRET_KEY` | Em produção | `dev-secret-key-mude-em-producao` | Assina a sessão do Flask |
| `DATABASE_URL` | Não | SQLite local | URL de conexão do SQLAlchemy |

O `python-dotenv` carrega automaticamente as variáveis de um arquivo `.env`.
Sem `DATABASE_URL`, a execução fora do Docker usa SQLite em
`instance/estoque.db`.

## Primeiro acesso

Na primeira inicialização é criado automaticamente:

- Email: `admin@sistema.com`
- Senha: `admin123`

Troque essa senha antes de disponibilizar o sistema. O valor padrão da
`SECRET_KEY` também é apenas para desenvolvimento.

## Estrutura

```text
gerenciamento-estoque/
├── main.py              # Factory, rotas principais e inicialização do banco
├── config.py            # Variáveis de ambiente e URL do banco
├── models/              # Modelos SQLAlchemy
├── endpoints/           # Blueprints e regras das telas
├── services/
│   └── logger.py        # Geração dos registros de auditoria
├── templates/           # Templates Jinja2
├── public/              # Arquivos estáticos
├── Dockerfile           # Imagem da aplicação
├── compose.yaml         # Aplicação e PostgreSQL
├── .env.example         # Exemplo de configuração
├── pyproject.toml       # Metadados e dependências
└── Procfile             # Comando de execução em produção
```

## Pontos de atenção

- Não há testes automatizados no repositório.
- O administrador e a chave de sessão possuem valores padrão conhecidos e
  precisam ser alterados em qualquer implantação real.

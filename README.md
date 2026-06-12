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
- Acesso à internet na primeira construção para baixar as imagens e dependências.

Depois que as imagens forem construídas, a interface não depende de CDN:
Bootstrap e Bootstrap Icons estão incluídos no projeto.

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

ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=troque-por-uma-senha-temporaria-com-12-caracteres

POSTGRES_DB=estoque
POSTGRES_USER=estoque
POSTGRES_PASSWORD=troque-por-uma-senha-forte
POSTGRES_PORT=5432

BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=30

DATABASE_URL=
```

Troque obrigatoriamente `SECRET_KEY`, `ADMIN_PASSWORD` e `POSTGRES_PASSWORD`.
Gere valores aleatórios, diferentes entre si:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Execute o comando novamente para cada segredo. Uma saída hexadecimal longa é
adequada e evita problemas de interpretação no arquivo `.env`.

Variáveis disponíveis:

| Variável | Obrigatória | Exemplo | Descrição |
|---|---|---|---|
| `APP_PORT` | Não | `8000` | Porta usada para acessar o sistema |
| `SECRET_KEY` | Sim | 64 caracteres aleatórios | Chave de assinatura das sessões |
| `ADMIN_EMAIL` | Sim | `admin@sistema.com` | Login do primeiro administrador |
| `ADMIN_PASSWORD` | Sim | senha temporária | Senha inicial com no mínimo 12 caracteres |
| `POSTGRES_DB` | Sim | `estoque` | Nome do banco PostgreSQL |
| `POSTGRES_USER` | Sim | `estoque` | Usuário do PostgreSQL |
| `POSTGRES_PASSWORD` | Sim | senha forte | Senha do PostgreSQL |
| `POSTGRES_PORT` | Não | `5432` | Porta local do PostgreSQL |
| `BACKUP_INTERVAL_HOURS` | Não | `24` | Intervalo entre backups automáticos |
| `BACKUP_RETENTION_DAYS` | Não | `30` | Retenção dos backups automáticos |
| `DATABASE_URL` | Não | vazio | Alternativa para execução sem Docker |

No uso com Docker, mantenha `DATABASE_URL` vazia. Ela não é necessária para a
comunicação entre os containers.

Se a porta `8000` já estiver ocupada, altere `APP_PORT`. Se a porta `5432`
estiver ocupada, altere `POSTGRES_PORT`. Essas mudanças afetam apenas as portas
do computador; não alteram as portas internas dos containers.

Defina as credenciais antes da primeira inicialização:

- O PostgreSQL usa `POSTGRES_DB`, `POSTGRES_USER` e `POSTGRES_PASSWORD` somente
  quando cria `data/postgres/` pela primeira vez.
- A aplicação usa `ADMIN_EMAIL` e `ADMIN_PASSWORD` somente para criar o primeiro
  administrador. Reiniciar o container não redefine sua senha.
- Mantenha o `.env` protegido e fora de compartilhamentos públicos. Ele não é
  versionado pelo Git.

Alterar essas variáveis depois que os dados existem não renomeia o banco, não
troca automaticamente suas credenciais e não redefine o administrador.

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

O Compose aguarda o healthcheck do PostgreSQL. Antes de iniciar o Gunicorn, o
container da aplicação:

1. Executa `flask --app main db upgrade`.
2. Aplica todas as migrations pendentes.
3. Cria o administrador inicial somente se o email ainda não existir.
4. Inicia a aplicação.

O Compose rejeita os textos de exemplo, `SECRET_KEY` com menos de 32 caracteres
e senhas com menos de 12 caracteres.

### Passo 3: acessar a aplicação

Com `APP_PORT=8000`, acesse:

```text
http://localhost:8000
```

Use os valores configurados no `.env`:

```text
Email: valor de ADMIN_EMAIL
Senha: valor de ADMIN_PASSWORD
```

O primeiro administrador e todos os usuários criados com senha temporária são
obrigados a definir uma nova senha no primeiro acesso. A nova senha deve possuir
ao menos 12 caracteres.

### Proteções aplicadas

- Aplicação e PostgreSQL publicados somente em `127.0.0.1`.
- Senhas iniciais definidas pelo instalador, sem credencial fixa no código.
- Troca obrigatória das senhas temporárias.
- Proteção CSRF em formulários e requisições JSON.
- Cookies de sessão `HttpOnly` e `SameSite=Lax`.
- Logout apenas por requisição POST.
- Redirecionamentos externos após login são rejeitados.
- Valores monetários armazenados como decimal.
- Restrições de banco impedem valores e estoques negativos.
- A baixa de estoque bloqueia o produto durante a transação da venda.
- Migrations aplicadas automaticamente antes da inicialização.
- Backup automático com retenção configurável.

### Passo 4: verificar ou diagnosticar

Para acompanhar os logs:

```bash
docker compose logs -f app
```

Para visualizar também os logs do PostgreSQL:

```bash
docker compose logs -f db
```

Para verificar o serviço de backup:

```bash
docker compose logs -f backup
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
| `data/backups/` | Backups automáticos e manuais |

Essas pastas são ignoradas pelo Git. Recriar ou atualizar os containers não
remove seu conteúdo. Para migrar a instalação, copie o projeto com a pasta
`data/` e o arquivo `.env`, mantendo-os protegidos.

### Backup automático

O serviço `backup` cria um arquivo no formato customizado do PostgreSQL assim
que a aplicação fica saudável e repete a operação conforme
`BACKUP_INTERVAL_HOURS`. Arquivos com mais de `BACKUP_RETENTION_DAYS` são
removidos automaticamente.

Confirme periodicamente que `data/backups/` contém arquivos `.dump` recentes.
Um backup só é confiável depois que sua restauração foi testada.

### Backup manual e restauração

Para gerar um backup adicional:

```bash
mkdir -p data/backups
docker compose exec -T db sh -c \
  'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > data/backups/estoque.dump
```

Para restaurar um backup, pare a aplicação durante a operação:

```bash
docker compose stop app backup
docker compose exec -T db sh -c \
  'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < data/backups/estoque.dump
docker compose start app backup
```

A restauração substitui os objetos existentes no banco selecionado.

### Atualização da aplicação

Antes de atualizar:

1. Confirme a existência de um backup recente.
2. Pare os serviços com `docker compose down`.
3. Atualize os arquivos do projeto.
4. Execute `docker compose up -d --build`.
5. Confira `docker compose ps` e `docker compose logs app`.

As migrations são aplicadas automaticamente. Não apague `data/postgres/` para
atualizar o sistema.

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

Configure ao menos as variáveis necessárias para criar o administrador:

```env
SECRET_KEY=uma-chave-local
ADMIN_EMAIL=admin@sistema.com
ADMIN_PASSWORD=uma-senha-temporaria-com-12-caracteres
DATABASE_URL=
```

Prepare o banco e crie o administrador:

```bash
flask --app main db upgrade
flask --app main seed-admin
```

Depois, para desenvolvimento:

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
| `ADMIN_EMAIL` | Para o primeiro acesso | `admin@sistema.com` | Email do administrador inicial |
| `ADMIN_PASSWORD` | Para o primeiro acesso | vazio | Senha temporária do administrador |
| `DATABASE_URL` | Não | SQLite local | URL de conexão do SQLAlchemy |

O `python-dotenv` carrega automaticamente as variáveis de um arquivo `.env`.
Sem `DATABASE_URL`, a execução fora do Docker usa SQLite em
`instance/estoque.db`.

## Primeiro acesso

O primeiro administrador é criado com `ADMIN_EMAIL` e `ADMIN_PASSWORD`. A senha
é temporária e deve ser trocada no primeiro login.

## Estrutura

```text
gerenciamento-estoque/
├── main.py              # Factory, rotas principais e inicialização do banco
├── config.py            # Variáveis de ambiente e URL do banco
├── models/              # Modelos SQLAlchemy
├── endpoints/           # Blueprints e regras das telas
├── services/
│   └── logger.py        # Geração dos registros de auditoria
├── migrations/          # Evolução versionada do banco de dados
├── templates/           # Templates Jinja2
├── public/              # Arquivos estáticos
├── Dockerfile           # Imagem da aplicação
├── docker-entrypoint.sh # Migrations e inicialização
├── compose.yaml         # Aplicação e PostgreSQL
├── .env.example         # Exemplo de configuração
├── pyproject.toml       # Metadados e dependências
└── Procfile             # Comando de execução em produção
```

## Pontos de atenção

- Não há testes automatizados no repositório.
- Não compartilhe `.env`, `data/postgres/` ou `data/backups/` publicamente.
- Não use `docker compose down -v` nem apague a pasta `data/` durante uma
  atualização.
- Verifique os backups e faça um teste de restauração antes de depender do
  sistema para operação diária.

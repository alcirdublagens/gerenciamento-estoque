"""schema inicial

Revision ID: 0001
Revises:
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("senha_hash", sa.String(length=256), nullable=False),
        sa.Column("papel", sa.String(length=20), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("deve_trocar_senha", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("identificacao", sa.String(length=50), nullable=True),
        sa.Column("telefone", sa.String(length=30), nullable=True),
        sa.Column("endereco", sa.String(length=300), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "produtos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("codigo", sa.String(length=50), nullable=True),
        sa.Column("tag", sa.String(length=100), nullable=True),
        sa.Column("preco", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("preco_custo", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("estoque_minimo", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.CheckConstraint("preco >= 0", name="ck_produtos_preco_nao_negativo"),
        sa.CheckConstraint(
            "preco_custo >= 0",
            name="ck_produtos_preco_custo_nao_negativo",
        ),
        sa.CheckConstraint(
            "quantidade >= 0",
            name="ck_produtos_quantidade_nao_negativa",
        ),
        sa.CheckConstraint(
            "estoque_minimo >= 0",
            name="ck_produtos_estoque_minimo_nao_negativo",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )
    op.create_table(
        "vendas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendedor_id", sa.Integer(), nullable=False),
        sa.Column("cliente_id", sa.Integer(), nullable=True),
        sa.Column("total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("tipo_pagamento", sa.String(length=20), nullable=False),
        sa.Column("num_parcelas", sa.Integer(), nullable=True),
        sa.Column("data_vencimento", sa.Date(), nullable=True),
        sa.Column("status_pagamento", sa.String(length=20), nullable=False),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.CheckConstraint("total >= 0", name="ck_vendas_total_nao_negativo"),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.ForeignKeyConstraint(["vendedor_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("acao", sa.String(length=100), nullable=False),
        sa.Column("detalhes", sa.Text(), nullable=True),
        sa.Column("ip", sa.String(length=45), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "itens_venda",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("venda_id", sa.Integer(), nullable=False),
        sa.Column("produto_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False),
        sa.Column("preco_unitario", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "preco_custo_unitario",
            sa.Numeric(precision=12, scale=2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantidade > 0",
            name="ck_itens_venda_quantidade_positiva",
        ),
        sa.CheckConstraint(
            "preco_unitario >= 0",
            name="ck_itens_venda_preco_nao_negativo",
        ),
        sa.CheckConstraint(
            "preco_custo_unitario >= 0",
            name="ck_itens_venda_custo_nao_negativo",
        ),
        sa.ForeignKeyConstraint(["produto_id"], ["produtos.id"]),
        sa.ForeignKeyConstraint(["venda_id"], ["vendas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("itens_venda")
    op.drop_table("logs")
    op.drop_table("vendas")
    op.drop_table("produtos")
    op.drop_table("clientes")
    op.drop_table("usuarios")

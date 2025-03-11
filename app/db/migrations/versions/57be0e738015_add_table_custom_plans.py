"""add_table_custom_plans

Revision ID: 57be0e738015
Revises: c7515f4247d0
Create Date: 2023-09-05 00:54:06.661379

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '57be0e738015'
down_revision = 'c7515f4247d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "custom_plans",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('claimed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=False, index=True, unique=True),
        sa.Column("external_id", sa.String(), nullable=False, index=True, unique=True),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("is_yearly", sa.Boolean(), nullable=False, default=False),

        sa.Column("storage_limit", sa.BigInteger(), nullable=False),
        sa.Column("token_limit", sa.BigInteger(), nullable=False),
        sa.Column("chats_limit", sa.BigInteger(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table("custom_plans")
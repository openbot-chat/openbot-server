"""add_table_accounts

Revision ID: df21b94892e1
Revises: e06b74c3a8d8
Create Date: 2023-06-16 13:14:11.192103

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'df21b94892e1'
down_revision = 'e06b74c3a8d8'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),

        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("providerAccountId", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.Integer(), nullable=True),
        sa.Column("token_type", sa.String(), nullable=True),
        sa.Column("scope", sa.String(), nullable=True),
        sa.Column("id_token", sa.Text(), nullable=True),
        sa.Column("session_state", sa.String(), nullable=True),
        sa.Column("oauth_token_secret", sa.String(), nullable=True),
        sa.Column("oauth_token", sa.String(), nullable=True),
        sa.Column("refresh_token_expires_in", sa.Integer(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete ="CASCADE"),

        sa.UniqueConstraint('provider', 'providerAccountId'),

        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table("datastores")
"""add_agent_table

Revision ID: 16ae213fa590
Revises: cacaadb0965e
Create Date: 2023-05-10 14:20:00.747637

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '16ae213fa590'
down_revision = 'cacaadb0965e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("avatar", sa.JSON(), nullable=True),
        sa.Column("voice", sa.JSON(), nullable=True),
        sa.Column("cognition", sa.JSON(), nullable=True),
        sa.Column("identifier", sa.String(), nullable=True, index=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True, server_default='{}'),
        sa.Column("metadata", sa.JSON(), server_default='{}'),
        sa.Column("org_id", sa.String(), nullable=True, index=True),
        sa.Column("creator_id", sa.String(), nullable=True, index=True),

        sa.PrimaryKeyConstraint('id'),
        # sa.UniqueConstraint("org_id"),
    )


def downgrade() -> None:
    op.drop_table("agents")
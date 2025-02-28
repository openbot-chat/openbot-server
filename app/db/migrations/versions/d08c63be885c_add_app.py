"""add_app

Revision ID: d08c63be885c
Revises: 22f7d071c085
Create Date: 2023-12-12 10:18:30.585790

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd08c63be885c'
down_revision = '22f7d071c085'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "apps",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("identifier", sa.String(), nullable=True, index=True),
        sa.Column("theme", sa.String(), nullable=True, index=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=True, index=True),
        sa.Column("creator_id", sa.String(), nullable=True, index=True),
        sa.PrimaryKeyConstraint('id'),
    )    


def downgrade() -> None:
    op.drop_table("apps")
"""add_agent_orgid_required

Revision ID: 8d3a564d33e1
Revises: 7e7da99e988d
Create Date: 2023-05-10 17:40:15.657458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8d3a564d33e1'
down_revision = '7e7da99e988d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("agents", "org_id", existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    op.alter_column("agents", "org_id", existing_type=sa.String(), nullable=True)

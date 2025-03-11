"""add_column_visibility_for_agent

Revision ID: 5b39af1bc7b3
Revises: 8d3a564d33e1
Create Date: 2023-05-15 00:22:47.069931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b39af1bc7b3'
down_revision = '8d3a564d33e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column(
    'agents', 
    sa.Column("visibility", sa.String(), nullable=True, default="private")
  )

def downgrade() -> None:
    op.drop_column("agents", "visibility")
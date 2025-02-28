"""add_description_to_integrations

Revision ID: 8c8eb7dc5545
Revises: 957184537c0e
Create Date: 2023-06-19 15:16:01.290258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c8eb7dc5545'
down_revision = '957184537c0e'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column(
    'integrations',
    sa.Column("description", sa.Text(), nullable=True)
  )

def downgrade() -> None:
  op.drop_column("integrations", "description")
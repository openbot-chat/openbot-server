"""drop_column_type_for_agent

Revision ID: 9c91842d836a
Revises: 5b39af1bc7b3
Create Date: 2023-05-15 01:44:37.561242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c91842d836a'
down_revision = '5b39af1bc7b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('agents', 'type')


def downgrade() -> None:
    op.add_column(
      'agents', 
      sa.Column("type", sa.String(), nullable=True),
    )
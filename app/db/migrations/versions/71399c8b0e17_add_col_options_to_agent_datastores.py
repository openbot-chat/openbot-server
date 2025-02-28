"""add_col_options_to_agent_datastores

Revision ID: 71399c8b0e17
Revises: affde8b3e53e
Create Date: 2023-05-26 06:05:06.659672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71399c8b0e17'
down_revision = 'affde8b3e53e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'agent_datastores', 
        sa.Column("options", sa.JSON(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column('agent_datastores', 'options')
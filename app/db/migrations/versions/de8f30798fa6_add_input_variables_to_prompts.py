"""add_input_variables_to_prompts

Revision ID: de8f30798fa6
Revises: fd8b4ded3421
Create Date: 2023-06-28 14:47:31.350371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de8f30798fa6'
down_revision = 'fd8b4ded3421'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'prompts', 
        sa.Column("input_variables", sa.ARRAY(sa.String), nullable=True)
    )

def downgrade() -> None:
    op.drop_column("prompts", "input_variables")
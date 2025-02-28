"""add_rls_to_prompts

Revision ID: fdaae9962587
Revises: de8f30798fa6
Create Date: 2023-06-28 14:53:38.892047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fdaae9962587'
down_revision = 'de8f30798fa6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "prompts",
        sa.Column("org_id", sa.String(), nullable=True, index=True)
    )

def downgrade() -> None:
    op.drop_column("prompts", "org_id")
"""plugin_add_schema_version

Revision ID: 90f2173d5add
Revises: b979b5828cba
Create Date: 2023-05-09 04:43:34.053607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90f2173d5add'
down_revision = 'b979b5828cba'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column(
    'ai_plugins', 
    sa.Column("schema_version", sa.String(), nullable=True, default="v1")
  )

def downgrade() -> None:
    op.drop_column("ai_plugins", "schema_version")
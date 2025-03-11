"""add_column_template_id_to_agent

Revision ID: 34cf26677df1
Revises: 2365be62aa32
Create Date: 2023-06-15 23:27:44.421709

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '34cf26677df1'
down_revision = '2365be62aa32'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.add_column(
    'agents', 
    sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True)
  )

def downgrade() -> None:
    op.drop_column("agents", "template_id")
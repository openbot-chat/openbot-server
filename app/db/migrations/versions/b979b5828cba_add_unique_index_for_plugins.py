"""add unique index for plugins

Revision ID: b979b5828cba
Revises: abd7e531a5f4
Create Date: 2023-04-08 08:40:41.498296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b979b5828cba'
down_revision = 'abd7e531a5f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_index(op.f('ix_ai_plugins_manifest_url'), 'ai_plugins', ['manifest_url'], unique=True)



def downgrade() -> None:
  op.drop_index(op.f('ix_ai_plugins_manifest_url'), table_name = 'ai_plugins')

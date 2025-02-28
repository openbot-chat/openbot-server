"""add_table_agent_knowleges

Revision ID: affde8b3e53e
Revises: 65409fe210c6
Create Date: 2023-05-26 00:41:03.575837

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'affde8b3e53e'
down_revision = '65409fe210c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
      "agent_datastores",
      sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
      sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column("agent_id", postgresql.UUID, nullable=False),
      sa.Column("datastore_id", postgresql.UUID, nullable=False),

      sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete="CASCADE"),
      sa.ForeignKeyConstraint(['datastore_id'], ['datastores.id'], ondelete="CASCADE"),
      sa.UniqueConstraint('agent_id', 'datastore_id'),
  )


def downgrade() -> None:
    op.drop_table("agent_datastores")
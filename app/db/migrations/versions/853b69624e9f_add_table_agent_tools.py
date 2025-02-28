"""add_table_agent_tools

Revision ID: 0ecb31c48416
Revises: 853b69624e9f
Create Date: 2023-07-21 18:45:00.941829

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0ecb31c48416'
down_revision = '853b69624e9f'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
      "agent_tools",
      sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
      sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column("agent_id", postgresql.UUID, nullable=False),
      sa.Column("tool_id", postgresql.UUID, nullable=False),
      sa.Column("options", sa.JSON(), nullable=True),
      sa.Column("name", sa.String(), nullable=True),
      sa.Column("description", sa.Text(), nullable=True),
 
      sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete="CASCADE"),
      sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ondelete="CASCADE"),
      sa.UniqueConstraint('agent_id', 'tool_id'),
  )


def downgrade() -> None:
    op.drop_table("agent_tools")
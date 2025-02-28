"""add_action

Revision ID: c537dd95c338
Revises: d08c63be885c
Create Date: 2023-12-12 11:02:35.094288

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c537dd95c338'
down_revision = 'd08c63be885c'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
      "actions",
      sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
      sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
      sa.Column("app_id", postgresql.UUID, nullable=False),
      sa.Column("identifier", sa.String(), nullable=False, index=True),
      sa.Column("options", sa.JSON(), nullable=True),
      sa.Column("name", sa.String(), nullable=True),
      sa.Column("description", sa.Text(), nullable=True),

      sa.PrimaryKeyConstraint("id"), 
      sa.ForeignKeyConstraint(['app_id'], ['apps.id'], ondelete="CASCADE"),
  )


def downgrade() -> None:
    op.drop_table("actions")
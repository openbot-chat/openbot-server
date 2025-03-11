"""add_action_connection

Revision ID: 5a47ba5a546d
Revises: c537dd95c338
Create Date: 2023-12-12 11:13:45.437714

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a47ba5a546d'
down_revision = 'c537dd95c338'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "action_connection_providers",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("action_id", postgresql.UUID, nullable=False),
        sa.Column("connection_provider_id", postgresql.UUID, nullable=False),

        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id'], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(['connection_provider_id'], ['credentials_types.id'], ondelete="CASCADE"),
        sa.UniqueConstraint('action_id', 'connection_provider_id'),
  )


def downgrade() -> None:
    op.drop_table("action_connection_providers")
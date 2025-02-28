"""add_table_messages

Revision ID: 709899e7cffb
Revises: 57be0e738015
Create Date: 2023-09-08 03:48:59.743255

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '709899e7cffb'
down_revision = '57be0e738015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "messages",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("text", sa.Text(), nullable=False, index=False),
        sa.Column("conversation_id", sa.String(), nullable=True, index=True),
        sa.Column("agent_id", sa.String(), nullable=True, index=True),

        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("messages")
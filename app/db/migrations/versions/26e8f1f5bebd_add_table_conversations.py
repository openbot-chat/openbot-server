"""add_table_conversations

Revision ID: 26e8f1f5bebd
Revises: fdaae9962587
Create Date: 2023-07-05 17:23:42.212943

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '26e8f1f5bebd'
down_revision = 'fdaae9962587'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("provider", sa.String(), nullable=False, index=True),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("user_id", sa.String(), nullable=True, index=True),
        sa.Column("visitor_id", sa.String(), nullable=True, index=True),
        sa.Column("options", sa.JSON(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("conversations")
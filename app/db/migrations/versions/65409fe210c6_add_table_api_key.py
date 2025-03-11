"""add_table_api_key

Revision ID: 65409fe210c6
Revises: ffab40803d0b
Create Date: 2023-05-24 17:50:28.272633

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '65409fe210c6'
down_revision = 'ffab40803d0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("token", sa.String(255), nullable=False, index=True, unique=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),

        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("api_keys")
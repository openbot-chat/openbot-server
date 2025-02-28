"""add_table_connection_providers

Revision ID: fd8b4ded3421
Revises: 8c8eb7dc5545
Create Date: 2023-06-25 22:27:31.747116

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fd8b4ded3421'
down_revision = '8c8eb7dc5545'
branch_labels = None
depends_on = None



def upgrade() -> None:
   op.create_table(
        "credentials_types",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("identifier", sa.String(), nullable=False, index=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("doc_url", sa.String(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),

        sa.UniqueConstraint('identifier'),
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("credentials_types")
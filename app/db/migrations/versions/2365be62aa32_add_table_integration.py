"""add_table_integration

Revision ID: 2365be62aa32
Revises: 0b8bd89c5a44
Create Date: 2023-06-13 00:56:52.766062

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2365be62aa32'
down_revision = '0b8bd89c5a44'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "integrations",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("identifier", sa.String(), nullable=False),
        sa.Column("catalog", sa.String(), nullable=False),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=True, index=True),
        sa.Column("is_public", sa.BOOLEAN, nullable=True, index=True, default=False),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
    )

def downgrade() -> None:
    op.drop_table("integrations")
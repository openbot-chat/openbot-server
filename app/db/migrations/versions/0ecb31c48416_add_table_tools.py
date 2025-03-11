"""add_table_tools

Revision ID: 853b69624e9f
Revises: 26e8f1f5bebd
Create Date: 2023-07-15 13:26:39.782617

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '853b69624e9f'
down_revision = '26e8f1f5bebd'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "tools",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("return_direct", sa.Boolean(), default=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=True, index=True),
        
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("tools")
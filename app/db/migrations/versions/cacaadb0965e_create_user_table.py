"""create_user_table

Revision ID: cacaadb0965e
Revises: 90f2173d5add
Create Date: 2023-05-10 14:07:17.059586

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'cacaadb0965e'
down_revision = '90f2173d5add'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("avatar", sa.String(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table("users")
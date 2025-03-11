"""add_table_credentials

Revision ID: 6464be1140da
Revises: 71399c8b0e17
Create Date: 2023-05-28 19:11:55.261754

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '6464be1140da'
down_revision = '71399c8b0e17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "credentials",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("data", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=False, index=True),

        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("credentials")
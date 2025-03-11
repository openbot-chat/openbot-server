"""add_table_datastore

Revision ID: 5d0fbb6e47dc
Revises: 9c91842d836a
Create Date: 2023-05-21 23:07:02.475633

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5d0fbb6e47dc'
down_revision = '9c91842d836a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datastores",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name_for_model", sa.String(), nullable=False),
        sa.Column("description_for_model", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=False, index=True),
        sa.Column("creator_id", postgresql.UUID, nullable=True, index=True),

        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table("datastores")
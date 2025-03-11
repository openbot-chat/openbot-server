"""add_table_datasource

Revision ID: 297c99539242
Revises: 6464be1140da
Create Date: 2023-05-30 16:18:40.883357

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '297c99539242'
down_revision = '6464be1140da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "datasources",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default="unsynced"),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("size", sa.Integer(), nullable=True, index=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("datastore_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False, index=True),
        sa.Column('creator_id', sa.String(), nullable=True),

        sa.PrimaryKeyConstraint('id'),

        sa.ForeignKeyConstraint(
          ['datastore_id'],
          ['datastores.id'],
          ondelete ="CASCADE",
        ),
    )

def downgrade() -> None:
    op.drop_table("datasources")
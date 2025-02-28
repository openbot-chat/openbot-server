"""add_table_documents

Revision ID: 0b8bd89c5a44
Revises: 297c99539242
Create Date: 2023-06-03 04:53:19.789981

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0b8bd89c5a44'
down_revision = '297c99539242'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=False, index=True),
        sa.Column("datasource_id", postgresql.UUID(as_uuid=True), nullable=False),

        sa.PrimaryKeyConstraint('id'),

        sa.ForeignKeyConstraint(
          ['datasource_id'],
          ['datasources.id'],
          ondelete ="CASCADE",
        ),
    )
 
def downgrade() -> None:
    op.drop_table("documents")
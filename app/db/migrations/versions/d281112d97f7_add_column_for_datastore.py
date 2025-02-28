"""add_column_for_datastore

Revision ID: d281112d97f7
Revises: 5d0fbb6e47dc
Create Date: 2023-05-21 23:12:01.917919

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd281112d97f7'
down_revision = '5d0fbb6e47dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('datastores', sa.Column("collection_name", sa.String(), nullable=False))

def downgrade() -> None:
    op.drop('datastores', 'collection_name')
"""add_columns_to_user

Revision ID: e06b74c3a8d8
Revises: 34cf26677df1
Create Date: 2023-06-16 13:10:20.095866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e06b74c3a8d8'
down_revision = '34cf26677df1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users', 
        sa.Column("email", sa.String(), nullable=True)
    )

def downgrade() -> None:
    op.drop_column("users", "email")
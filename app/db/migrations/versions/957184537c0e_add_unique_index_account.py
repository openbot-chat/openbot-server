"""add_unique_index_account

Revision ID: 957184537c0e
Revises: e3423c3b9038
Create Date: 2023-06-16 22:19:18.338829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '957184537c0e'
down_revision = 'e3423c3b9038'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        'uniq_provider_accountid',
        "accounts",
        ["provider", "providerAccountId"]
    )


def downgrade() -> None:
    op.drop_constraint("uniq_provider_accountid", 'accounts')

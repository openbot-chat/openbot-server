"""add_unique_org_payment_customer_id

Revision ID: 4487c7d15e18
Revises: 6a8d7b7349e1
Create Date: 2023-11-29 13:42:01.639649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4487c7d15e18"
down_revision = "6a8d7b7349e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uniq_org_payment_customer", "orgs", ["payment_customer_id"])


def downgrade() -> None:
    op.drop_constraint("uniq_org_payment_customer", "orgs")

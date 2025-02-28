"""org_add_payment_customer_id

Revision ID: 6a8d7b7349e1
Revises: 684ebdd3fc6e
Create Date: 2023-11-22 15:33:23.536639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6a8d7b7349e1"
down_revision = "684ebdd3fc6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orgs", sa.Column("payment_customer_id", sa.String(), nullable=True, default=None)
    )


def downgrade() -> None:
    op.drop_column("orgs", "payment_customer_id")

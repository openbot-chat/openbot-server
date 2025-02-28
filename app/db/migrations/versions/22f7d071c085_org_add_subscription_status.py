"""org_add_subscription_status

Revision ID: 22f7d071c085
Revises: 4487c7d15e18
Create Date: 2023-12-06 02:05:47.535994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "22f7d071c085"
down_revision = "4487c7d15e18"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orgs", sa.Column("subscription_status", sa.String(), nullable=True, default="active")
    )
    pass


def downgrade() -> None:
    op.drop_column("orgs", "subscription_status")
    pass

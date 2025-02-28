"""add_column_for_connection_provider

Revision ID: e270f6f5a971
Revises: 5a47ba5a546d
Create Date: 2023-12-13 20:38:50.384167

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e270f6f5a971'
down_revision = '5a47ba5a546d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "credentials_types", 
        sa.Column("app_id", postgresql.UUID(as_uuid=True), nullable=True)
    )

    op.create_foreign_key(
        None,
        "credentials_types",
        "apps",
        ["app_id"],
        ["id"],
        ondelete="SET NULL",
    )

def downgrade() -> None:
    op.drop_constraint(None, "credentials_types", type_="foreignkey")
    op.drop_column("credentials_types", "app_id")
"""add_table_org

Revision ID: 59718eaa1202
Revises: df21b94892e1
Create Date: 2023-06-16 15:58:31.209770

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from models.plan import Plan


# revision identifiers, used by Alembic.
revision = '59718eaa1202'
down_revision = 'df21b94892e1'
branch_labels = None
depends_on = None



def upgrade() -> None:
    plan_type = postgresql.ENUM(Plan)
    op.create_table(
        "orgs",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False, index=True),
        sa.Column("plan", plan_type, nullable=False, index=True, default=Plan.FREE),
        sa.Column("icon", sa.String(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
    )

def downgrade() -> None:
    op.drop_table("orgs")
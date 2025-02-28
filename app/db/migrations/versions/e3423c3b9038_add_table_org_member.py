"""add_table_org_member

Revision ID: e3423c3b9038
Revises: 59718eaa1202
Create Date: 2023-06-16 16:04:58.308963

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e3423c3b9038'
down_revision = '59718eaa1202'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "org_members",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("role", sa.String(), nullable=False, index=True, default="member"),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
          ['org_id'],
          ['orgs.id'],
          ondelete ="CASCADE",
        ),
        sa.ForeignKeyConstraint(
          ['user_id'],
          ['users.id'],
          ondelete ="CASCADE",
        ),
        sa.UniqueConstraint('user_id', 'org_id'),
    )

def downgrade() -> None:
    op.drop_table("org_members")
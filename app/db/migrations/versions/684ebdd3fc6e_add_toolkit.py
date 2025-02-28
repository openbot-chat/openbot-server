"""add_toolkit

Revision ID: 684ebdd3fc6e
Revises: 709899e7cffb
Create Date: 2023-11-04 02:51:06.859031

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision = '684ebdd3fc6e'
down_revision = '709899e7cffb'
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "toolkits",
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False, index=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("org_id", sa.String(), nullable=True, index=True),

        sa.PrimaryKeyConstraint('id'),
    )

    op.add_column(
      'tools', 
      sa.Column("toolkit_id", postgresql.UUID, nullable=True),
    )

    op.create_foreign_key('fk_tools_toolkit_id', 'tools', 'toolkits', ['toolkit_id'], ['id'], ondelete="CASCADE"),



def downgrade() -> None:
    op.drop_table("toolkits")
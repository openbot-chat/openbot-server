"""add ai-plugin

Revision ID: abd7e531a5f4
Revises: b0025bde4a29
Create Date: 2023-04-08 08:02:04.933110

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'abd7e531a5f4'
down_revision = 'b0025bde4a29'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'ai_plugins',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('contact_email', sa.String(), nullable=True),
    sa.Column('logo_url', sa.String(), nullable=True),
    sa.Column('manifest_url', sa.String(), nullable=False),
    sa.Column('name_for_model', sa.String(), nullable=False),
    sa.Column('name_for_human', sa.String(), nullable=False),
    sa.Column('description_for_model', sa.Text(), nullable=False),
    sa.Column('description_for_human', sa.Text(), nullable=True),
    sa.Column('auth', sa.JSON(), nullable=True),
    sa.Column('api', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
  )

def downgrade() -> None:
  op.drop_table('ai_plugins')
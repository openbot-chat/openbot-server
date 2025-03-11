"""init

Revision ID: b0025bde4a29
Revises: 
Create Date: 2023-04-08 04:58:06.752514

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from models.plan import Plan

# revision identifiers, used by Alembic.
revision = 'b0025bde4a29'
down_revision = None
branch_labels = None
depends_on = None



def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        plan_type = postgresql.ENUM(Plan)
        plan_type.create(bind, checkfirst=True)
        #plan_type = sa.Enum(Plan)
        #plan_type.create(bind, checkfirst=True)

    op.create_table(
        'prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    op.drop_table('prompts')

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        plan_type = postgresql.ENUM(Plan)
        plan_type.drop(op.get_bind())

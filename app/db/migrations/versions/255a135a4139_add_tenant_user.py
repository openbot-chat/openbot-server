"""add_tenant_user

Revision ID: 255a135a4139
Revises: d281112d97f7
Create Date: 2023-05-22 14:10:56.074502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '255a135a4139'
down_revision = 'd281112d97f7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
        IF NOT EXISTS(SELECT * FROM pg_roles WHERE rolname = 'tenant_user') THEN
            CREATE ROLE tenant_user;
            GRANT tenant_user TO postgres;
            GRANT USAGE ON SCHEMA public TO tenant_user;
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO tenant_user;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO tenant_user;
            GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO tenant_user;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO tenant_user;
        END IF;
        END
        $$
        """
    )


def downgrade() -> None:
    pass
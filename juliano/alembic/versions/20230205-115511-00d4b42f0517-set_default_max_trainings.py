"""set default max_trainings

Revision ID: 00d4b42f0517
Revises: 8507e230a469
Create Date: 2023-02-05 11:55:11.765339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "00d4b42f0517"
down_revision = "8507e230a469"
branch_labels = None
depends_on = None

metadata = sa.MetaData()

settings_table = sa.Table(
    "settings",
    metadata,
    sa.Column("max_trainings", sa.Integer),
)


def upgrade():
    stmt = settings_table.update().values(max_trainings=4)
    op.execute(stmt)


def downgrade():
    pass

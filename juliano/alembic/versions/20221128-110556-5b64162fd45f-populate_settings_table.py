"""populate settings table

Revision ID: 5b64162fd45f
Revises: 1fa1de2a4b45
Create Date: 2022-11-28 11:05:56.835762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b64162fd45f"
down_revision = "1fa1de2a4b45"
branch_labels = None
depends_on = None

metadata = sa.MetaData()

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
)

settings_table = sa.Table(
    "settings",
    metadata,
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), unique=True),
    sa.Column("max_todo", sa.Integer, default=10),
)


def upgrade():
    stmt = settings_table.insert().from_select(["user_id"], user_table.select())
    op.execute(stmt)


def downgrade():
    pass

"""add onupdate and ondelete

Revision ID: 5f2627e447c8
Revises: 5b64162fd45f
Create Date: 2022-12-05 00:57:34.665581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5f2627e447c8"
down_revision = "5b64162fd45f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(
            None,
            "items",
            ["item_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(
            None,
            "users",
            ["user_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )

    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(
            None,
            "users",
            ["user_id"],
            ["id"],
            onupdate="CASCADE",
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(None, "users", ["user_id"], ["id"])

    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(None, "users", ["user_id"], ["id"])

    with op.batch_alter_table("events", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.create_foreign_key(None, "items", ["item_id"], ["id"])

    # ### end Alembic commands ###

"""fields for spaced repitition

Revision ID: 7844a7ef9ea4
Revises: e9e82170c359
Create Date: 2020-11-22 09:54:53.593612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7844a7ef9ea4"
down_revision = "e9e82170c359"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("easiness_factor", sa.Float(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "inter_repitition_interval", sa.Interval(), nullable=True
            )
        )
        batch_op.add_column(
            sa.Column("repitition_number", sa.Integer(), nullable=True)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("items", schema=None) as batch_op:
        batch_op.drop_column("repitition_number")
        batch_op.drop_column("inter_repitition_interval")
        batch_op.drop_column("easiness_factor")

    # ### end Alembic commands ###
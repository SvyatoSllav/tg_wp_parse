"""added device_id field

Revision ID: 22850cecb1e2
Revises: c71d6c153520
Create Date: 2023-02-05 17:13:28.773671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22850cecb1e2'
down_revision = 'c71d6c153520'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('device', sa.Column('device_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('device', 'device_id')
    # ### end Alembic commands ###

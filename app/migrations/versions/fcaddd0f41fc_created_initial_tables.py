"""created initial tables

Revision ID: fcaddd0f41fc
Revises: 
Create Date: 2023-02-01 20:02:53.490972

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fcaddd0f41fc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('messenger',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('api_token', sa.String(), nullable=True),
    sa.Column('api_id', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('phone_hash', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('type', sa.Enum('telegram', 'whats_app', name='messengertype'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messenger_id'), 'messenger', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messenger_id'), table_name='messenger')
    op.drop_table('messenger')
    # ### end Alembic commands ###

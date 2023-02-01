"""added chat message device tables

Revision ID: 432a225137a1
Revises: fcaddd0f41fc
Create Date: 2023-02-01 20:04:15.196228

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '432a225137a1'
down_revision = 'fcaddd0f41fc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_device_id'), 'device', ['id'], unique=False)
    op.create_table('chat',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('chat_id', sa.String(), nullable=True),
    sa.Column('chat_name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('chat_avatars_img_paths', sa.PickleType(), nullable=True),
    sa.Column('messenger_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['messenger_id'], ['messenger.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_id'), 'chat', ['id'], unique=False)
    op.create_table('message',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('message_id', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('author_id', sa.String(), nullable=True),
    sa.Column('author_name', sa.String(), nullable=True),
    sa.Column('auhtor_phone', sa.String(), nullable=True),
    sa.Column('sent_at', sa.DateTime(), nullable=True),
    sa.Column('message_media_paths', sa.PickleType(), nullable=True),
    sa.Column('last_message_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('chat_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_id'), 'message', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_message_id'), table_name='message')
    op.drop_table('message')
    op.drop_index(op.f('ix_chat_id'), table_name='chat')
    op.drop_table('chat')
    op.drop_index(op.f('ix_device_id'), table_name='device')
    op.drop_table('device')
    # ### end Alembic commands ###
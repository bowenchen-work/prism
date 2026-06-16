from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table('users',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('tier', sa.String(), nullable=False, server_default='free'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('usage_logs',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('query_hash', sa.String(), nullable=False),
        sa.Column('tokens_used', sa.Integer()),
        sa.Column('model', sa.String()),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table('data_chunks',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('disease', sa.String()),
        sa.Column('region', sa.String()),
        sa.Column('date_range', sa.String()),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('metadata', sa.JSON()),
    )

    op.create_table('embeddings',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('chunk_id', sa.UUID(), sa.ForeignKey('data_chunks.id'), nullable=False),
        sa.Column('vector', Vector(1536), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

def downgrade():
    op.drop_table('embeddings')
    op.drop_table('data_chunks')
    op.drop_table('usage_logs')
    op.drop_table('users')
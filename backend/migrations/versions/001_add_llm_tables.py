"""Add LLM provider tables

Revision ID: 001_llm_tables
Revises: 4a3a48417bdb
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_llm_tables'
down_revision = '4a3a48417bdb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create llm_providers table
    op.create_table('llm_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_name', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('requests_per_minute', sa.Integer(), nullable=True),
        sa.Column('tokens_per_minute', sa.Integer(), nullable=True),
        sa.Column('failure_threshold', sa.Integer(), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider_name')
    )
    
    # Create llm_api_keys table
    op.create_table('llm_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('key_name', sa.String(length=100), nullable=False),
        sa.Column('api_key_encrypted', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('request_count', sa.BigInteger(), nullable=True),
        sa.Column('failure_count', sa.Integer(), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['provider_id'], ['llm_providers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_provider_active', 'llm_api_keys', ['provider_id', 'is_active'], unique=False)
    
    # Create llm_usage_logs table
    op.create_table('llm_usage_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=True),
        sa.Column('api_key_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('request_tokens', sa.Integer(), nullable=True),
        sa.Column('response_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['api_key_id'], ['llm_api_keys.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['provider_id'], ['llm_providers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_provider_success', 'llm_usage_logs', ['provider_id', 'success', 'created_at'], unique=False)
    op.create_index('idx_session_created', 'llm_usage_logs', ['session_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_llm_usage_logs_created_at'), 'llm_usage_logs', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_llm_usage_logs_created_at'), table_name='llm_usage_logs')
    op.drop_index('idx_session_created', table_name='llm_usage_logs')
    op.drop_index('idx_provider_success', table_name='llm_usage_logs')
    op.drop_table('llm_usage_logs')
    op.drop_index('idx_provider_active', table_name='llm_api_keys')
    op.drop_table('llm_api_keys')
    op.drop_table('llm_providers')

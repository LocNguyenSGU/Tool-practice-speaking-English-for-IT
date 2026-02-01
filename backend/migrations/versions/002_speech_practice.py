"""Add speech practice tables

Revision ID: 002_speech_practice
Revises: 001_llm_tables
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_speech_practice'
down_revision = '001_llm_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create speech_practice_sessions table
    op.create_table('speech_practice_sessions',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('mode', sa.String(length=50), nullable=False),
        sa.Column('audio_url', sa.String(length=512), nullable=True),
        sa.Column('audio_duration_ms', sa.Integer(), nullable=True),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('reference_text', sa.Text(), nullable=True),
        sa.Column('prosody_features', sa.JSON(), nullable=True),
        sa.Column('provider_used', sa.String(length=50), nullable=True),
        sa.Column('llm_response', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('pronunciation_score', sa.Float(), nullable=True),
        sa.Column('prosody_score', sa.Float(), nullable=True),
        sa.Column('emotion_score', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('fluency_score', sa.Float(), nullable=True),
        sa.Column('conversational_feedback', sa.Text(), nullable=True),
        sa.Column('detailed_feedback', sa.JSON(), nullable=True),
        sa.Column('total_latency_ms', sa.Integer(), nullable=True),
        sa.Column('stt_latency_ms', sa.Integer(), nullable=True),
        sa.Column('prosody_latency_ms', sa.Integer(), nullable=True),
        sa.Column('llm_latency_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_mode_created', 'speech_practice_sessions', ['mode', 'created_at'], unique=False)
    op.create_index('idx_user_status_created', 'speech_practice_sessions', ['user_id', 'status', 'created_at'], unique=False)
    op.create_index(op.f('ix_speech_practice_sessions_created_at'), 'speech_practice_sessions', ['created_at'], unique=False)
    op.create_index(op.f('ix_speech_practice_sessions_user_id'), 'speech_practice_sessions', ['user_id'], unique=False)
    
    # Create user_progress_llm table
    op.create_table('user_progress_llm',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('total_sessions', sa.Integer(), nullable=True),
        sa.Column('conversation_sessions', sa.Integer(), nullable=True),
        sa.Column('sentence_practice_sessions', sa.Integer(), nullable=True),
        sa.Column('average_score', sa.Float(), nullable=True),
        sa.Column('average_pronunciation', sa.Float(), nullable=True),
        sa.Column('average_prosody', sa.Float(), nullable=True),
        sa.Column('average_emotion', sa.Float(), nullable=True),
        sa.Column('average_confidence', sa.Float(), nullable=True),
        sa.Column('average_fluency', sa.Float(), nullable=True),
        sa.Column('total_audio_duration_ms', sa.BigInteger(), nullable=True),
        sa.Column('total_tokens_used', sa.BigInteger(), nullable=True),
        sa.Column('current_streak_days', sa.Integer(), nullable=True),
        sa.Column('longest_streak_days', sa.Integer(), nullable=True),
        sa.Column('last_practice_at', sa.DateTime(), nullable=True),
        sa.Column('recent_scores', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_progress_llm_user_id'), 'user_progress_llm', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_progress_llm_user_id'), table_name='user_progress_llm')
    op.drop_table('user_progress_llm')
    op.drop_index(op.f('ix_speech_practice_sessions_user_id'), table_name='speech_practice_sessions')
    op.drop_index(op.f('ix_speech_practice_sessions_created_at'), table_name='speech_practice_sessions')
    op.drop_index('idx_user_status_created', table_name='speech_practice_sessions')
    op.drop_index('idx_mode_created', table_name='speech_practice_sessions')
    op.drop_table('speech_practice_sessions')

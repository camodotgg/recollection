"""Add activity tracking to lesson progress

Revision ID: 004
Revises: 003
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add activity tracking columns to lesson_progress table
    op.add_column('lesson_progress', sa.Column('activities_completed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('lesson_progress', sa.Column('total_activities', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove activity tracking columns
    op.drop_column('lesson_progress', 'total_activities')
    op.drop_column('lesson_progress', 'activities_completed')

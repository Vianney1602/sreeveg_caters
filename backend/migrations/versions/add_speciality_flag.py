"""
Revision ID: add_speciality_flag
Revises: 
Create Date: 2026-01-08
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('menu_items', sa.Column('is_speciality', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column('menu_items', 'is_speciality')

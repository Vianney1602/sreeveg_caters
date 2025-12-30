"""Add uploaded_images table for persistent image storage

Revision ID: 1b2b1f4c7d21
Revises: c4bf34826151
Create Date: 2025-12-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b2b1f4c7d21'
down_revision = 'c4bf34826151'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'uploaded_images',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=64), nullable=False),
        sa.Column('data', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True)
    )


def downgrade():
    op.drop_table('uploaded_images')

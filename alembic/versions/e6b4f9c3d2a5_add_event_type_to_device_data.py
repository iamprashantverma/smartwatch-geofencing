"""add event_type to device_data

Revision ID: e6b4f9c3d2a5
Revises: d5a3e8b2f1c4
Create Date: 2026-05-21 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6b4f9c3d2a5'
down_revision: Union[str, Sequence[str], None] = 'd5a3e8b2f1c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add event_type column to device_data table
    op.add_column('device_data', sa.Column('event_type', sa.String(length=20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove event_type column from device_data table
    op.drop_column('device_data', 'event_type')

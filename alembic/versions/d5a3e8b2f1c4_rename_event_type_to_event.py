"""rename event_type to event

Revision ID: d5a3e8b2f1c4
Revises: c493d7196edc
Create Date: 2026-05-21 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5a3e8b2f1c4'
down_revision: Union[str, Sequence[str], None] = 'c493d7196edc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename column from event_type to event and increase length
    op.alter_column('event_logs', 'event_type',
                    new_column_name='event',
                    type_=sa.String(length=200),
                    existing_type=sa.String(length=50),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Rename column back from event to event_type
    op.alter_column('event_logs', 'event',
                    new_column_name='event_type',
                    type_=sa.String(length=50),
                    existing_type=sa.String(length=200),
                    existing_nullable=False)

"""create_qdrant_migrations

Revision ID: 3cef755a3cf9
Revises: 0a79b968edc0
Create Date: 2026-07-27 09:42:36.103000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3cef755a3cf9"
down_revision: Union[str, Sequence[str], None] = "0a79b968edc0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "qdrant_migrations",
        sa.Column("version", sa.String(), primary_key=True),
        sa.Column("applied_at", sa.DateTime(), server_default=sa.func.now()),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("qdrant_migrations")
    # ### end Alembic commands ###

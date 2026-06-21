"""enable pgvector extension

Revision ID: d1593a6d2444
Revises: 300ecb825fc9
Create Date: 2026-06-21 18:30:36.063155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1593a6d2444'
down_revision: Union[str, Sequence[str], None] = '300ecb825fc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")

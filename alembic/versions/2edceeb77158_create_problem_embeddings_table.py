"""create problem embeddings table

Revision ID: 2edceeb77158
Revises: d1593a6d2444
Create Date: 2026-06-21 18:34:20.871049

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2edceeb77158'
down_revision: Union[str, Sequence[str], None] = 'd1593a6d2444'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions")

    op.execute("""
        CREATE TABLE IF NOT EXISTS problem_embeddings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
            source_type VARCHAR(50) NOT NULL,
            source_id INTEGER,
            content TEXT NOT NULL,
            embedding extensions.vector(1536) NOT NULL,
            embedding_model VARCHAR(100) NOT NULL DEFAULT 'text-embedding-3-small',
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_problem_embeddings_user_id
        ON problem_embeddings(user_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_problem_embeddings_problem_id
        ON problem_embeddings(problem_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS problem_embeddings")
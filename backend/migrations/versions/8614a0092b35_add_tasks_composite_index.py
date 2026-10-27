"""add tasks composite index

Revision ID: 8614a0092b35
Revises: d8a13ef996e5
Create Date: 2026-10-27 15:24:58.537480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8614a0092b35'
down_revision: Union[str, Sequence[str], None] = 'd8a13ef996e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("idx_tasks_project_status_created", "tasks", ["project_id", "status", "created_at"])

def downgrade() -> None:
    op.drop_index("idx_tasks_project_status_created", "tasks")
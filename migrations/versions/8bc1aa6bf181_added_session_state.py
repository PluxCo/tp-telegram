"""added session state

Revision ID: 8bc1aa6bf181
Revises: c2a37f69cbd2
Create Date: 2024-05-23 18:47:50.294568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8bc1aa6bf181'
down_revision: Union[str, None] = 'c2a37f69cbd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('sessions', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.execute("UPDATE sessions SET start_time = open_time")
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.alter_column('state',
                              existing_type=sa.VARCHAR(length=5),
                              type_=sa.Enum('OPEN', 'STARTED', 'CLOSE', name='sessionstate'),
                              existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("sessions") as batch_op:
        batch_op.alter_column('sessions', 'state',
                              existing_type=sa.Enum('OPEN', 'STARTED', 'CLOSE', name='sessionstate'),
                              type_=sa.VARCHAR(length=5),
                              existing_nullable=False)
    op.drop_column('sessions', 'start_time')

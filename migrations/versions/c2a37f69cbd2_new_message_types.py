"""new message types

Revision ID: c2a37f69cbd2
Revises: 94611849b1b2
Create Date: 2024-05-03 12:36:42.472643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2a37f69cbd2'
down_revision: Union[str, None] = '94611849b1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('mood', sa.String(), nullable=True))
    op.add_column('messages', sa.Column('reply_text', sa.String(), nullable=True))
    op.add_column('messages', sa.Column('reply_to', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'reply_to')
    op.drop_column('messages', 'reply_text')
    op.drop_column('messages', 'mood')
    # ### end Alembic commands ###

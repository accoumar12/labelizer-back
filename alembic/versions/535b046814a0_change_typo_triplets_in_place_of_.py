"""Change typo triplets in place of validation_triplets

Revision ID: 535b046814a0
Revises: 4546be8bf419
Create Date: 2024-06-18 10:29:46.346879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '535b046814a0'
down_revision: Union[str, None] = '4546be8bf419'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

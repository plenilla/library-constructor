"""Add enum role for user on database

Revision ID: 7341b68d0412
Revises: 
Create Date: 2025-03-18 17:28:47.627509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '7341b68d0412'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               type_=sa.Enum('READER', 'LIBRARIAN', 'GUEST', 'ADMIN', name='userrole'),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role',
               existing_type=sa.Enum('READER', 'LIBRARIAN', 'GUEST', 'ADMIN', name='userrole'),
               type_=mysql.VARCHAR(collation='utf8mb4_general_ci', length=50),
               existing_nullable=False)
    # ### end Alembic commands ###

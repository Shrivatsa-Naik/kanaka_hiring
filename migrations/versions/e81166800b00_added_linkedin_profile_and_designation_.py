"""Added linkedin profile and designation fields to users.py

Revision ID: e81166800b00
Revises: a1edbd5176a5
Create Date: 2025-05-29 09:46:28.480770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e81166800b00'
down_revision = 'a1edbd5176a5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('linkedin_profile', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('designation', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('designation')
        batch_op.drop_column('linkedin_profile')

    # ### end Alembic commands ###

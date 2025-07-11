"""Added new columns to job_requirements.py

Revision ID: 9f34db85efcb
Revises: c3677b760bb6
Create Date: 2025-06-09 10:35:39.311349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f34db85efcb'
down_revision = 'c3677b760bb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('jobrequirement',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('skillset', sa.String(length=100), nullable=False),
    sa.Column('experience', sa.Text(), nullable=True),
    sa.Column('clients', sa.Text(), nullable=False),
    sa.Column('budget', sa.String(length=50), nullable=False),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('applicants', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'jobrequirement', ['job_id'], ['id'])

    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'jobrequirement', ['job_id'], ['id'])

    with op.batch_alter_table('referrals', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'jobrequirement', ['job_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('referrals', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('interviews', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('applicants', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    op.drop_table('jobrequirement')
    # ### end Alembic commands ###

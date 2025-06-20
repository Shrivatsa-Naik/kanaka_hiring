"""testresult table added

Revision ID: 5822df0a9ba7
Revises: 01885a7f172f
Create Date: 2025-06-17 17:17:02.975358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5822df0a9ba7'
down_revision = '01885a7f172f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('testresult',
    sa.Column('testlink_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('total_score', sa.Integer(), nullable=False),
    sa.Column('time_taken', sa.Integer(), nullable=False),
    sa.Column('test_time', sa.Integer(), nullable=False),
    sa.Column('test_name', sa.String(length=100), nullable=False),
    sa.Column('pdf_link', sa.String(length=200), nullable=False),
    sa.Column('sections', sa.Text(), nullable=False),
    sa.Column('applicant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
    sa.PrimaryKeyConstraint('testlink_id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('testresult')
    # ### end Alembic commands ###

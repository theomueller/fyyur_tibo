"""empty message

Revision ID: 6087904fe9ef
Revises: df93884c21cb
Create Date: 2021-06-29 11:25:55.806882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6087904fe9ef'
down_revision = 'df93884c21cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=false))
    # ### end Alembic commands ###

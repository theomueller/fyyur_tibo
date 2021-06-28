"""empty message

Revision ID: 2a279bb0729a
Revises: cc5d9dec77c4
Create Date: 2021-06-27 20:06:13.903992

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a279bb0729a'
down_revision = 'cc5d9dec77c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###
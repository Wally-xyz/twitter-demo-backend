"""media address col

Revision ID: de6e1cf02056
Revises: c5282ad829b3
Create Date: 2022-03-29 09:54:08.487212

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de6e1cf02056'
down_revision = 'c5282ad829b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('address', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('media', 'address')
    # ### end Alembic commands ###
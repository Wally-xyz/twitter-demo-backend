"""more media cols

Revision ID: c5282ad829b3
Revises: ce5be026aad5
Create Date: 2022-03-28 18:00:18.704559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5282ad829b3'
down_revision = 'ce5be026aad5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('nonce', sa.String(), nullable=True))
    op.add_column('media', sa.Column('token_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('media', 'token_id')
    op.drop_column('media', 'nonce')
    # ### end Alembic commands ###

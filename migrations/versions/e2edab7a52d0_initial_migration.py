"""Initial Migration

Revision ID: e2edab7a52d0
Revises: 
Create Date: 2023-04-20 03:08:35.181485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2edab7a52d0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['author_id'], ['id'])
        batch_op.drop_column('author')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.VARCHAR(length=250), nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('author_id')

    # ### end Alembic commands ###
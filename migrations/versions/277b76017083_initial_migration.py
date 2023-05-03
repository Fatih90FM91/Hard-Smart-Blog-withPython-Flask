"""Initial migration.

Revision ID: 277b76017083
Revises: e2edab7a52d0
Create Date: 2023-04-29 16:59:35.859227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '277b76017083'
down_revision = 'e2edab7a52d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_blog_posts_title'), ['title'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    with op.batch_alter_table('blog_posts', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_blog_posts_title'), type_='unique')

    # ### end Alembic commands ###

"""Added Contact and Review models

Revision ID: 9e7336be1040
Revises: 712d86bf6dbb
Create Date: 2024-08-12 08:34:45.248991

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e7336be1040'
down_revision = '712d86bf6dbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_constraint('admins_email_key', type_='unique')
        batch_op.create_index(batch_op.f('ix_admins_email'), ['email'], unique=True)

    with op.batch_alter_table('delivery_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_delivery_history_parcel_id'), ['parcel_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_delivery_history_status'), ['status'], unique=False)

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_notifications_parcel_id'), ['parcel_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_notifications_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('parcels', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_parcels_driver_id'), ['driver_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parcels_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_parcels_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reviews_parcel_id'), ['parcel_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_reviews_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_email_key', type_='unique')
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.create_unique_constraint('users_email_key', ['email'])

    with op.batch_alter_table('reviews', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reviews_user_id'))
        batch_op.drop_index(batch_op.f('ix_reviews_parcel_id'))

    with op.batch_alter_table('parcels', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_parcels_user_id'))
        batch_op.drop_index(batch_op.f('ix_parcels_status'))
        batch_op.drop_index(batch_op.f('ix_parcels_driver_id'))

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_notifications_user_id'))
        batch_op.drop_index(batch_op.f('ix_notifications_parcel_id'))

    with op.batch_alter_table('delivery_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_delivery_history_status'))
        batch_op.drop_index(batch_op.f('ix_delivery_history_parcel_id'))

    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_admins_email'))
        batch_op.create_unique_constraint('admins_email_key', ['email'])

    # ### end Alembic commands ###

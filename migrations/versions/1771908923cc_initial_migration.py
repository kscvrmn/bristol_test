"""Initial migration

Revision ID: 1771908923cc
Revises: 
Create Date: 2025-06-05 20:32:57.913632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1771908923cc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movements',
    sa.Column('movement_id', sa.String(), nullable=False),
    sa.Column('source_warehouse', sa.String(), nullable=True),
    sa.Column('destination_warehouse', sa.String(), nullable=True),
    sa.Column('product_id', sa.String(), nullable=True),
    sa.Column('departure_time', sa.DateTime(), nullable=True),
    sa.Column('arrival_time', sa.DateTime(), nullable=True),
    sa.Column('time_difference_seconds', sa.Float(), nullable=True),
    sa.Column('departure_quantity', sa.Integer(), nullable=True),
    sa.Column('arrival_quantity', sa.Integer(), nullable=True),
    sa.Column('quantity_difference', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('movement_id')
    )
    op.create_index(op.f('ix_movements_product_id'), 'movements', ['product_id'], unique=False)
    op.create_table('warehouse_states',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('warehouse_id', sa.String(), nullable=True),
    sa.Column('product_id', sa.String(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_states_product_id'), 'warehouse_states', ['product_id'], unique=False)
    op.create_index(op.f('ix_warehouse_states_warehouse_id'), 'warehouse_states', ['warehouse_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_warehouse_states_warehouse_id'), table_name='warehouse_states')
    op.drop_index(op.f('ix_warehouse_states_product_id'), table_name='warehouse_states')
    op.drop_table('warehouse_states')
    op.drop_index(op.f('ix_movements_product_id'), table_name='movements')
    op.drop_table('movements')
    # ### end Alembic commands ###

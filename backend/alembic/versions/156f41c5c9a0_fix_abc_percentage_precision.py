"""fix abc_percentage precision

Revision ID: 156f41c5c9a0
Revises: 
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa

revision = '156f41c5c9a0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('rol', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

    # Tabla products
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('supplier', sa.String(length=150), nullable=True),
        sa.Column('width_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('height_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('depth_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('weight_kg', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('abc_zone', sa.String(length=1), nullable=True),
        sa.Column('abc_percentage', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'], unique=False)
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)

    # Tabla warehouse_positions
    op.create_table('warehouse_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rack', sa.Integer(), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('column', sa.Integer(), nullable=False),
        sa.Column('position_code', sa.String(length=20), nullable=False),
        sa.Column('max_width_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('max_height_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('max_depth_cm', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('max_weight_kg', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('suggested_abc_zone', sa.String(length=1), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('is_occupied', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_warehouse_positions_id', 'warehouse_positions', ['id'], unique=False)
    op.create_index('ix_warehouse_positions_position_code', 'warehouse_positions', ['position_code'], unique=True)

    # Tabla sales_uploads
    op.create_table('sales_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('total_skus', sa.Integer(), nullable=True),
        sa.Column('skus_zone_a', sa.Integer(), nullable=True),
        sa.Column('skus_zone_b', sa.Integer(), nullable=True),
        sa.Column('skus_zone_c', sa.Integer(), nullable=True),
        sa.Column('skus_with_errors', sa.Integer(), nullable=True),
        sa.Column('cleansing_report', sa.JSON(), nullable=True),
        sa.Column('relocation_suggestions', sa.JSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sales_uploads_id', 'sales_uploads', ['id'], unique=False)
    op.create_index('ix_sales_uploads_status', 'sales_uploads', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('sales_uploads')
    op.drop_table('warehouse_positions')
    op.drop_table('products')
    op.drop_table('users')
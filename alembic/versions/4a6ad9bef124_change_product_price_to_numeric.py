"""change product price to numeric

Revision ID: 4a6ad9bef124
Revises: c2d578c09fa7
Create Date: 2026-09-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4a6ad9bef124"
down_revision: Union[str, Sequence[str], None] = "c2d578c09fa7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "products",
        "price",
        existing_type=sa.Float(),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
        postgresql_using="price::numeric(10,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "products",
        "price",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Float(),
        existing_nullable=False,
    )
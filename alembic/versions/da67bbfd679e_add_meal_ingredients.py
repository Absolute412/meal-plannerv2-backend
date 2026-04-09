"""add meal ingredients

Revision ID: da67bbfd679e
Revises: 61a429e01a31
Create Date: 2026-04-04 01:07:55.353136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da67bbfd679e'
down_revision: Union[str, Sequence[str], None] = '61a429e01a31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # create the new table we want
    op.create_table(
        "meal_ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("meal_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("measure", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["meal_id"], ["meals.id"]),
    )
    op.create_index(op.f("ix_meal_ingredients_id"), "meal_ingredients", ["id"], unique=False)

    # optional: drop legacy tables if you don't need them anymore
    # op.drop_index(op.f("ix_mealingredient_id"), table_name="mealingredient")
    # op.drop_table("mealingredient")
    # op.drop_index(op.f("ix_meal_ingredient_id"), table_name="meal_ingredient")
    # op.drop_table("meal_ingredient")


def downgrade() -> None:
    # undo new table
    op.drop_index(op.f("ix_meal_ingredients_id"), table_name="meal_ingredients")
    op.drop_table("meal_ingredients")

    # optional: recreate old legacy tables if you dropped them
    # op.create_table("meal_ingredient",
    #     sa.Column("id", sa.Integer(), primary_key=True),
    #     sa.Column("meal_id", sa.Integer(), nullable=False),
    #     sa.Column("name", sa.String(), nullable=False),
    #     sa.Column("measure", sa.String(), nullable=True),
    #     sa.ForeignKeyConstraint(["meal_id"], ["meals.id"]),
    # )
    # op.create_index(op.f("ix_meal_ingredient_id"), "meal_ingredient", ["id"], unique=False)

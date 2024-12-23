"""Change labeled_triplets to triplets only

Revision ID: 4546be8bf419
Revises:
Create Date: 2024-06-18 10:25:07.020367

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4546be8bf419"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_labeled_triplets_encoder_id", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_id", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_label", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_left_id", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_reference_id", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_retrieved_at", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_right_id", table_name="labeled_triplets")
    op.drop_index("ix_labeled_triplets_user_id", table_name="labeled_triplets")
    op.drop_table("labeled_triplets")
    op.drop_index("ix_validation_triplets_id", table_name="validation_triplets")
    op.drop_index("ix_validation_triplets_label", table_name="validation_triplets")
    op.drop_index(
        "ix_validation_triplets_left_encoder_id", table_name="validation_triplets"
    )
    op.drop_index("ix_validation_triplets_left_id", table_name="validation_triplets")
    op.drop_index(
        "ix_validation_triplets_reference_id", table_name="validation_triplets"
    )
    op.drop_index(
        "ix_validation_triplets_retrieved_at", table_name="validation_triplets"
    )
    op.drop_index(
        "ix_validation_triplets_right_encoder_id", table_name="validation_triplets"
    )
    op.drop_index("ix_validation_triplets_right_id", table_name="validation_triplets")
    op.drop_index("ix_validation_triplets_user_id", table_name="validation_triplets")
    op.drop_table("validation_triplets")
    op.drop_index("ix_items_id", table_name="items")
    op.drop_index("ix_items_length", table_name="items")
    op.drop_table("items")
    op.drop_index("ix_triplets_upload_status_id", table_name="triplets_upload_status")
    op.drop_index(
        "ix_triplets_upload_status_to_upload_triplets_count",
        table_name="triplets_upload_status",
    )
    op.drop_index(
        "ix_triplets_upload_status_uploaded_triplets_count",
        table_name="triplets_upload_status",
    )
    op.drop_table("triplets_upload_status")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "triplets_upload_status",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "to_upload_triplets_count", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "uploaded_triplets_count", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="triplets_upload_status_pkey"),
    )
    op.create_index(
        "ix_triplets_upload_status_uploaded_triplets_count",
        "triplets_upload_status",
        ["uploaded_triplets_count"],
        unique=False,
    )
    op.create_index(
        "ix_triplets_upload_status_to_upload_triplets_count",
        "triplets_upload_status",
        ["to_upload_triplets_count"],
        unique=False,
    )
    op.create_index(
        "ix_triplets_upload_status_id", "triplets_upload_status", ["id"], unique=False
    )
    op.create_table(
        "items",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "length",
            sa.DOUBLE_PRECISION(precision=53),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("vector", sa.NullType(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="items_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_index("ix_items_length", "items", ["length"], unique=False)
    op.create_index("ix_items_id", "items", ["id"], unique=False)
    op.create_table(
        "validation_triplets",
        sa.Column("left_encoder_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("right_encoder_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("reference_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("left_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("right_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "label",
            postgresql.ENUM("LEFT", "RIGHT", "DONT_KNOW", name="selecteditemtype"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("user_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "retrieved_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["left_id"], ["items.id"], name="validation_triplets_left_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["reference_id"], ["items.id"], name="validation_triplets_reference_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["right_id"], ["items.id"], name="validation_triplets_right_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="validation_triplets_pkey"),
    )
    op.create_index(
        "ix_validation_triplets_user_id",
        "validation_triplets",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_right_id",
        "validation_triplets",
        ["right_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_right_encoder_id",
        "validation_triplets",
        ["right_encoder_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_retrieved_at",
        "validation_triplets",
        ["retrieved_at"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_reference_id",
        "validation_triplets",
        ["reference_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_left_id",
        "validation_triplets",
        ["left_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_left_encoder_id",
        "validation_triplets",
        ["left_encoder_id"],
        unique=False,
    )
    op.create_index(
        "ix_validation_triplets_label", "validation_triplets", ["label"], unique=False
    )
    op.create_index(
        "ix_validation_triplets_id", "validation_triplets", ["id"], unique=False
    )
    op.create_table(
        "labeled_triplets",
        sa.Column("encoder_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("reference_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("left_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("right_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "label",
            postgresql.ENUM("LEFT", "RIGHT", "DONT_KNOW", name="selecteditemtype"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("user_id", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "retrieved_at",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["left_id"], ["items.id"], name="labeled_triplets_left_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["reference_id"], ["items.id"], name="labeled_triplets_reference_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["right_id"], ["items.id"], name="labeled_triplets_right_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="labeled_triplets_pkey"),
    )
    op.create_index(
        "ix_labeled_triplets_user_id", "labeled_triplets", ["user_id"], unique=False
    )
    op.create_index(
        "ix_labeled_triplets_right_id", "labeled_triplets", ["right_id"], unique=False
    )
    op.create_index(
        "ix_labeled_triplets_retrieved_at",
        "labeled_triplets",
        ["retrieved_at"],
        unique=False,
    )
    op.create_index(
        "ix_labeled_triplets_reference_id",
        "labeled_triplets",
        ["reference_id"],
        unique=False,
    )
    op.create_index(
        "ix_labeled_triplets_left_id", "labeled_triplets", ["left_id"], unique=False
    )
    op.create_index(
        "ix_labeled_triplets_label", "labeled_triplets", ["label"], unique=False
    )
    op.create_index("ix_labeled_triplets_id", "labeled_triplets", ["id"], unique=False)
    op.create_index(
        "ix_labeled_triplets_encoder_id",
        "labeled_triplets",
        ["encoder_id"],
        unique=False,
    )
    # ### end Alembic commands ###

"""change podcastindex_id to big integer

Revision ID: 6e3922af94d3
Revises: 4d76cdf2e019
Create Date: 2025-03-31 17:33:44.838498

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6e3922af94d3"
down_revision = "4d76cdf2e019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "episodes",
        "podcastindex_id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "episodes",
        "podcastindex_id",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=True,
    )

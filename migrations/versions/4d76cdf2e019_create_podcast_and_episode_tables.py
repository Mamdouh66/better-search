"""Create podcast and episode tables

Revision ID: 4d76cdf2e019
Revises:
Create Date: 2025-03-09 09:25:33.364157

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4d76cdf2e019"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "podcasts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=True),
        sa.Column("itunesId", sa.Integer(), nullable=True),
        sa.Column("podcastGuid", sa.String(length=255), nullable=True),
        sa.Column("podcastindex_id", sa.Integer(), nullable=True),
        sa.Column("categories", sa.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_podcasts_id"), "podcasts", ["id"], unique=False)
    op.create_index(
        op.f("ix_podcasts_podcastindex_id"),
        "podcasts",
        ["podcastindex_id"],
        unique=False,
    )
    op.create_index(op.f("ix_podcasts_url"), "podcasts", ["url"], unique=True)

    op.create_table(
        "episodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("guid", sa.String(length=512), nullable=False),
        sa.Column("date_published", sa.DateTime(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("feedItunesId", sa.Integer(), nullable=True),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("podcastindex_id", sa.Integer(), nullable=True),
        sa.Column("podcast_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["podcast_id"],
            ["podcasts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("guid"),
    )
    op.create_index(op.f("ix_episodes_id"), "episodes", ["id"], unique=False)
    op.create_index(
        op.f("ix_episodes_podcastindex_id"),
        "episodes",
        ["podcastindex_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_episodes_podcastindex_id"), table_name="episodes")
    op.drop_index(op.f("ix_episodes_id"), table_name="episodes")
    op.drop_table("episodes")

    op.drop_index(op.f("ix_podcasts_url"), table_name="podcasts")
    op.drop_index(op.f("ix_podcasts_podcastindex_id"), table_name="podcasts")
    op.drop_index(op.f("ix_podcasts_id"), table_name="podcasts")
    op.drop_table("podcasts")

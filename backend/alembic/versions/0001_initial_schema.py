"""Initial schema for GitFolio."""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("github_id", sa.String(), nullable=False, unique=True),
        sa.Column("github_username", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "analysis_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("repo_url", sa.String(), nullable=False),
        sa.Column("github_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("analysis_requests.id")),
        sa.Column("content_json", sa.Text()),
        sa.Column("pdf_path", sa.String()),
        sa.Column("docx_path", sa.String()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        "github_data_cache",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("repo_url", sa.String(), nullable=False, unique=True),
        sa.Column("raw_data_json", sa.Text()),
        sa.Column("fetched_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("github_data_cache")
    op.drop_table("reports")
    op.drop_table("analysis_requests")
    op.drop_table("users")

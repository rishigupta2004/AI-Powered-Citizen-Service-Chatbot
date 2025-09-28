"""Create staging_documents and relax documents columns"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "create_staging_and_relax_documents"
down_revision = "884c1befb291"  # <--- This is the value
branch_labels = None
depends_on = None

def upgrade():
    # 1) Create staging_documents table
    op.create_table(
        "staging_documents",
        sa.Column("staging_id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("file_name", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=True),
        sa.Column("doc_type", sa.String(length=50), server_default="pdf", nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
    )

    # optional indexes for faster lookups
    op.create_index("ix_staging_documents_source", "staging_documents", ["source"])
    op.create_index("ix_staging_documents_file_name", "staging_documents", ["file_name"])

    # 2) Relax constraints on documents so ingestion minimal inserts succeed
    # Make service_id, name, description nullable (if they currently are NOT NULL)
    with op.batch_alter_table("documents", schema=None) as batch_op:
        batch_op.alter_column("service_id", existing_type=sa.INTEGER(), nullable=True)
        batch_op.alter_column("name", existing_type=sa.VARCHAR(length=150), nullable=True)
        batch_op.alter_column("description", existing_type=sa.TEXT(), nullable=True)
        # keep mandatory boolean and created_at as-is

def downgrade():
    # Revert documents columns to NOT NULL (danger: only safe if no NULLs exist)
    with op.batch_alter_table("documents", schema=None) as batch_op:
        batch_op.alter_column("description", existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column("name", existing_type=sa.VARCHAR(length=150), nullable=False)
        batch_op.alter_column("service_id", existing_type=sa.INTEGER(), nullable=False)

    # Drop staging indexes and table
    op.drop_index("ix_staging_documents_file_name", table_name="staging_documents")
    op.drop_index("ix_staging_documents_source", table_name="staging_documents")
    op.drop_table("staging_documents")

"""Add ingestion fields to documents table"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = "add_documents_ingestion_fields"
down_revision = "4c7a4017b7c5"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("documents", sa.Column("source", sa.String(length=100), nullable=True))
    op.add_column("documents", sa.Column("file_name", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("language", sa.String(length=10), server_default="en"))
    op.add_column("documents", sa.Column("doc_type", sa.String(length=50), server_default="pdf"))
    op.add_column("documents", sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")))

def downgrade():
    op.drop_column("documents", "updated_at")
    op.drop_column("documents", "doc_type")
    op.drop_column("documents", "language")
    op.drop_column("documents", "file_name")
    op.drop_column("documents", "source")

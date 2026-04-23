ARTIFACTS := artifacts

.PHONY: process_pending verify_warehouse ingest_live extract_pdfs build_embeddings_all api_graphql_smoke rag_demo catalog_apis

$(ARTIFACTS):
	mkdir -p $(ARTIFACTS)

process_pending: $(ARTIFACTS)
	python scripts/process_pending_raw_content.py --resume=1 | tee $(ARTIFACTS)/process_pending.log

verify_warehouse: $(ARTIFACTS)
	python scripts/verify_warehouse.py --export-dir $(ARTIFACTS)

ingest_live: $(ARTIFACTS)
	python scripts/crawl_live.py | tee $(ARTIFACTS)/ingest.log

extract_pdfs: $(ARTIFACTS)
	python scripts/extract_pdfs_ocr.py | tee $(ARTIFACTS)/extract.log

build_embeddings_all: $(ARTIFACTS)
	python scripts/backfill_embeddings.py | tee $(ARTIFACTS)/embeddings.log

catalog_apis: $(ARTIFACTS)
	python scripts/catalog_apis.py > $(ARTIFACTS)/api_catalog.json

remove_placeholders: $(ARTIFACTS)
	python scripts/remove_placeholders.py | tee $(ARTIFACTS)/cleanup.log



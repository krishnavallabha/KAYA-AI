# FlowSense RAG Assistant

## Included
- Hybrid dense + keyword retrieval with reciprocal-rank fusion.
- PDF/text/Markdown/CSV/XML/JSON/log upload endpoint.
- RAG Assistant page in the existing React dashboard.
- Project indexing endpoint for supported files under `docs/` and `data/`, plus current material, signal, and schedule records.
- Automatic best-effort indexing after vendor-email, delivery-image, and schedule ingestion.
- Source listing and source deletion (FAISS is rebuilt from saved embeddings).
- Retrieval benchmark harness reporting Recall@5, MRR, and nDCG@5.

## Configuration
Set `OPENAI_API_KEY` in the backend process environment. PDF parsing requires `pypdf` (added to `requirements.txt`).
Optional `RAG_API_TOKEN` protects RAG routes with a shared bearer token. This is a basic deployment guard, not multi-user identity or per-document authorization. For production, integrate your identity provider and enforce tenant/project permissions before exposing data.

`RAG_STORAGE_DIR` can set a persistent storage path. Keep that directory private and back it up; it contains source text and embeddings.

## Run
Backend:
```bash
uvicorn backend.main:app --reload
```
Frontend (from project root, with dependencies installed):
```bash
node node_modules/vite/bin/vite.js
```
Open the local Vite URL and select **RAG Assistant**.

## Index and test
- Use **Index project data** in the RAG Assistant to index supported project files and database snapshots.
- Use **Upload document** to index a document manually.
- Query the indexed evidence and inspect source snippets/citations.
- Delete a source from the source list to remove its chunks and rebuild FAISS.
- Run the retrieval benchmark after setting up relevant test documents:
```bash
python -m backend.rag.evaluation.run_benchmark
```
Results are saved to `rag_evaluation_results.json`. Benchmark labels in `backend/rag/evaluation/benchmark.json` are illustrative and must be adjusted to the actual source names in your evaluation corpus.

## Important limitations
- Automatic RAG indexing is best-effort: ingestion endpoints report indexing failures without rolling back the primary email/image/schedule ingestion.
- RAG storage is currently a local JSON + FAISS index and is not multi-process safe. Use a database-backed vector store or locking/transactional storage before horizontal scaling.
- The current token option is a shared bearer token; it does not provide per-user or per-document access control. Do not treat it as a complete production identity system.
- `index-project` reads project files under `docs/` and `data/`; review those folders before indexing to avoid embedding irrelevant or sensitive material.
- The system uses OpenAI embeddings and chat completions; live query/ingestion tests require a valid API key and network access.

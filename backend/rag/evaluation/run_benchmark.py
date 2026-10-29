"""Offline retrieval benchmark. Uses the live RAG retriever and computes Recall@k, MRR and nDCG@k.
Set OPENAI_API_KEY and ingest benchmark fixtures/data before running:
  python -m backend.rag.evaluation.run_benchmark
"""
import json
import math
from pathlib import Path
from backend.rag.service import retrieve

DATA = Path(__file__).with_name("benchmark.json")
TOP_K = 5

def metrics(ranked_sources, relevant):
    relevant = set(relevant)
    if not relevant:
        return {"recall_at_k": 0.0, "mrr": 0.0, "ndcg_at_k": 0.0}
    hits = [1 if source in relevant else 0 for source in ranked_sources]
    recall = sum(hits) / len(relevant)
    rr = next((1 / (i + 1) for i, hit in enumerate(hits) if hit), 0.0)
    dcg = sum(hit / math.log2(i + 2) for i, hit in enumerate(hits))
    ideal = sum(1 / math.log2(i + 2) for i in range(min(len(relevant), len(hits))))
    return {"recall_at_k": recall, "mrr": rr, "ndcg_at_k": dcg / ideal if ideal else 0.0}

def main():
    cases = json.loads(DATA.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        results = retrieve(case["question"], TOP_K)
        # A relevant-source label can match the returned filename or a source category substring.
        names = [r["filename"] for r in results]
        rel = case["relevant_sources"]
        ranked = [next((r for r in rel if name == r or r in name), name) for name in names]
        scores = metrics(ranked, rel)
        rows.append({"question": case["question"], "retrieved": names, **scores})
    summary = {key: sum(row[key] for row in rows) / len(rows) if rows else 0
               for key in ("recall_at_k", "mrr", "ndcg_at_k")}
    output = {"top_k": TOP_K, "cases": rows, "mean": summary}
    out = Path("rag_evaluation_results.json")
    out.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    print(f"Saved {out.resolve()}")

if __name__ == "__main__":
    main()

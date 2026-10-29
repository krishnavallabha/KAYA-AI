from pydantic import BaseModel, Field

class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=12)

class RAGQueryResponse(BaseModel):
    answer: str
    citations: list[dict]
    retrieval_method: str = "hybrid_dense_keyword_rrf"

class RAGIngestResponse(BaseModel):
    filename: str
    chunks_added: int
    total_chunks: int
    message: str

class ScheduleDraftRequest(BaseModel):
    brief: str = Field(min_length=10, max_length=5000)
    target_start: str | None = None

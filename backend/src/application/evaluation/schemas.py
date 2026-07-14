from pydantic import BaseModel


class EvaluationPair(BaseModel):
    query_text: str
    expected_answer: str
    expected_citations: list[str]


class BenchmarkDataset(BaseModel):
    id: str
    name: str
    description: str | None = None
    pairs: list[EvaluationPair]
    created_at: str


class EvaluationReport(BaseModel):
    id: str
    dataset_id: str
    faithfulness_score: float
    answer_relevance_score: float
    context_recall_score: float
    latency_ms: int
    raw_details: dict[str, float]
    created_at: str

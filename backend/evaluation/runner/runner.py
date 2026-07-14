import time

from pydantic import BaseModel

from evaluation.datasets.loader import BenchmarkEntry
from evaluation.fixtures.mock_pipeline import create_mock_query_service
from evaluation.metrics.calculator import EvaluationMetrics, MetricsCalculator
from src.domain.entities.query import Query
from src.domain.value_objects.identifiers import QueryId


class EvaluationResult(BaseModel):
    entry: BenchmarkEntry
    metrics: EvaluationMetrics
    generated_answer: str
    status: str  # "success" or "failed"
    error_message: str | None = None


class EvaluationRunner:
    def __init__(self, mock_mode: bool = True) -> None:
        self.mock_mode = mock_mode

    def run_entry(self, entry: BenchmarkEntry) -> EvaluationResult:
        start_pipeline = time.perf_counter()

        try:
            # 1. Setup Service
            if self.mock_mode:
                query_service = create_mock_query_service(
                    expected_pages=entry.expected_pages,
                    expected_chunks=entry.expected_chunks,
                    expected_answer=entry.expected_answer,
                    book_title=entry.book,
                )
            else:
                # Real production service from container (fallback or integrated evaluation)
                from src.application.container import container

                query_service = container.query_service

            # 2. Extract internal engines for granular stage measurement
            retrieval_engine = query_service._retrieval_engine
            grounding_engine = query_service._grounding_engine
            generation_engine = query_service._generation_engine
            citation_engine = query_service._citation_engine

            # 3. Construct Query entity
            query_id = QueryId("eval-query-id")
            query = Query(
                id=query_id,
                original_question=entry.question,
                query_timestamp=time.time(),  # type: ignore
            )

            # 4. Measure Ingestion Stages (simulated/fixture parser, chunker,
            # embedder, indexer for pipeline reporting)
            # Since query evaluation is query-time, we populate nominal baseline
            # times for ingestion stages, or run mock parsing if a test textbook is present.

            # 5. Measure Query Stages
            # Stage: Retrieval
            start_retrieval = time.perf_counter()
            retrieval_context = retrieval_engine.retrieve_context(
                query=query,
                similarity_threshold=0.1,  # low threshold to get all candidates
                limit=5,
            )
            retrieval_latency = time.perf_counter() - start_retrieval

            # Stage: Grounding (Prompt compile)
            start_grounding = time.perf_counter()
            prompt = grounding_engine.compile_prompt(query, retrieval_context)
            _grounding_latency = time.perf_counter() - start_grounding

            # Stage: Generation
            start_generation = time.perf_counter()
            generated_response = generation_engine.generate_response(prompt)
            generation_latency = time.perf_counter() - start_generation

            # Stage: Citation Verification
            start_citations = time.perf_counter()
            verified_response = citation_engine.verify_citations(
                generated_response, retrieval_context
            )
            _citations_latency = time.perf_counter() - start_citations

            total_latency = time.perf_counter() - start_pipeline

            # 6. Extract prompt text
            prompt_text = prompt.to_string() if hasattr(prompt, "to_string") else str(prompt)

            # 7. Calculate Metrics
            metrics = MetricsCalculator.calculate(
                expected_pages=entry.expected_pages,
                expected_chunks=entry.expected_chunks,
                expected_citations=entry.expected_citations,
                retrieved_chunks=retrieval_context.items,
                citations=verified_response.supporting_citations,
                generated_answer=verified_response.generated_answer,
                prompt_text=prompt_text,
                retrieval_latency=retrieval_latency,
                generation_latency=generation_latency,
                total_latency=total_latency,
            )

            return EvaluationResult(
                entry=entry,
                metrics=metrics,
                generated_answer=verified_response.generated_answer,
                status="success",
            )

        except Exception as e:
            # Handle and record pipeline failure metrics gracefully
            metrics = EvaluationMetrics(
                recall_at_k=0.0,
                precision_at_k=0.0,
                mrr=0.0,
                citation_accuracy=0.0,
                citation_coverage=0.0,
                evidence_coverage_ratio=0.0,
                prompt_size=0,
                generation_latency=0.0,
                retrieval_latency=0.0,
                total_pipeline_latency=time.perf_counter() - start_pipeline,
                response_length=0,
                chunk_count=0,
                average_similarity=0.0,
            )
            return EvaluationResult(
                entry=entry,
                metrics=metrics,
                generated_answer="",
                status="failed",
                error_message=str(e),
            )

    def run_suite(self, entries: list[BenchmarkEntry]) -> list[EvaluationResult]:
        results = []
        for entry in entries:
            res = self.run_entry(entry)
            results.append(res)
        return results

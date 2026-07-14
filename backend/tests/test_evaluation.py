import json
from typing import Any

import pytest

from evaluation.datasets.loader import BenchmarkEntry, DatasetLoader
from evaluation.metrics.calculator import EvaluationMetrics, MetricsCalculator
from evaluation.regression.comparator import RegressionComparator
from evaluation.reports.generator import ReportGenerator
from evaluation.runner.runner import EvaluationResult, EvaluationRunner


def test_benchmark_loading_success(tmp_path: Any) -> None:
    data = [
        {
            "question": "What is CRC?",
            "expected_answer": "Cyclic Redundancy Check...",
            "expected_pages": [45, 46],
            "expected_chunks": ["chunk_1"],
            "expected_keywords": ["cyclic", "redundancy"],
            "expected_citations": ["Citation 1"],
            "difficulty": "medium",
            "category": "Error Detection",
            "book": "Computer Networks",
        }
    ]
    filepath = tmp_path / "valid_benchmark.json"
    filepath.write_text(json.dumps(data), encoding="utf-8")

    entries = DatasetLoader.load_json(str(filepath))
    assert len(entries) == 1
    assert entries[0].question == "What is CRC?"
    assert entries[0].expected_pages == [45, 46]
    assert entries[0].expected_chunks == ["chunk_1"]
    assert entries[0].expected_keywords == ["cyclic", "redundancy"]
    assert entries[0].expected_citations == ["Citation 1"]


def test_benchmark_loading_empty(tmp_path: Any) -> None:
    filepath = tmp_path / "empty_benchmark.json"
    filepath.write_text(json.dumps([]), encoding="utf-8")

    entries = DatasetLoader.load_json(str(filepath))
    assert len(entries) == 0


def test_benchmark_loading_malformed(tmp_path: Any) -> None:
    # 1. Invalid JSON syntax
    filepath = tmp_path / "malformed_json.json"
    filepath.write_text("{invalid json", encoding="utf-8")
    with pytest.raises(ValueError):
        DatasetLoader.load_json(str(filepath))

    # 2. Missing required fields (question/expected_answer)
    filepath_missing = tmp_path / "missing_fields.json"
    filepath_missing.write_text(json.dumps([{"difficulty": "easy"}]), encoding="utf-8")
    with pytest.raises(ValueError):
        DatasetLoader.load_json(str(filepath_missing))


class DummyChunk:
    def __init__(self, chunk_id_val: str, page_num: int, text: str, score: float = 0.8) -> None:
        class DummyId:
            value = chunk_id_val

        self.chunk_id = DummyId()
        self.page_number = page_num
        self.chunk_text = text
        self.similarity_score = score


class DummyCitation:
    def __init__(self, page_num: int) -> None:
        self.page_number = page_num


def test_metrics_calculation() -> None:
    expected_pages = [10, 11]
    expected_chunks = ["c_1"]
    expected_citations = ["cit_1"]

    retrieved_chunks = [
        DummyChunk("c_1", 10, "Text containing CRC"),
        DummyChunk("c_2", 12, "Text not containing CRC", 0.6),
    ]
    citations = [DummyCitation(10)]

    metrics = MetricsCalculator.calculate(
        expected_pages=expected_pages,
        expected_chunks=expected_chunks,
        expected_citations=expected_citations,
        retrieved_chunks=retrieved_chunks,
        citations=citations,
        generated_answer="Cyclic redundancy check is used for error detection.",
        prompt_text="Grounding prompt content",
        retrieval_latency=0.1,
        generation_latency=1.5,
        total_latency=1.6,
    )

    # Matched expected: expected_pages [10, 11] matches retrieved page 10.
    # expected_chunks ["c_1"] matches retrieved chunk c_1.
    # Total expected items = 3 (10, 11, c_1). Matched expected items = 2 (10, c_1).
    # Recall = 2/3 = 0.6667
    assert round(metrics.recall_at_k, 2) == 0.67

    # Retrieval precision: out of 2 chunks, c_1 is relevant (matches ID and page 10).
    # c_2 is not relevant.
    # Precision = 1/2 = 0.5
    assert metrics.precision_at_k == 0.5

    # MRR: first relevant chunk is c_1 (index 0). MRR = 1.0
    assert metrics.mrr == 1.0

    # Citation accuracy: citations count = 1. Citation page 10 is in expected_pages. Accuracy = 1.0
    assert metrics.citation_accuracy == 1.0

    # Citation coverage: expected_pages [10, 11] -> cited page 10. Coverage = 1/2 = 0.5
    assert metrics.citation_coverage == 0.5

    # Evidence coverage ratio: unique retrieved pages cited = 1 (page 10) /
    # unique retrieved pages = 2 (10, 12). Ratio = 0.5
    assert metrics.evidence_coverage_ratio == 0.5


def test_report_generation() -> None:
    entry = BenchmarkEntry(
        question="What is GBN?",
        expected_answer="Go Back N sliding window...",
        expected_pages=[80],
        expected_chunks=["gbn_1"],
        expected_keywords=["sliding", "window"],
        expected_citations=["Citation GBN"],
        difficulty="hard",
        category="Transport",
        book="Computer Networks",
    )
    metrics = EvaluationMetrics(
        recall_at_k=1.0,
        precision_at_k=1.0,
        mrr=1.0,
        citation_accuracy=1.0,
        citation_coverage=1.0,
        evidence_coverage_ratio=1.0,
        prompt_size=500,
        generation_latency=1.0,
        retrieval_latency=0.2,
        total_pipeline_latency=1.2,
        response_length=200,
        chunk_count=1,
        average_similarity=0.85,
    )
    result = EvaluationResult(
        entry=entry, metrics=metrics, generated_answer="Go Back N sliding window", status="success"
    )

    summary = ReportGenerator.generate_summary_dict([result], 1.2)
    assert summary["overall_score"] == 100.0
    assert summary["total_cases"] == 1
    assert summary["success_count"] == 1

    md = ReportGenerator.to_markdown(summary)
    assert "Retrieval Recall@K" in md
    assert "Overall System Score" in md

    js = ReportGenerator.to_json(summary)
    assert '"overall_score": 100.0' in js


def test_regression_detection() -> None:
    baseline = {
        "overall_score": 80.0,
        "metrics_summary": {
            "recall_at_k": 0.8,
            "precision_at_k": 0.7,
            "mrr": 0.75,
            "citation_accuracy": 0.85,
            "citation_coverage": 0.8,
            "total_pipeline_latency_seconds": 1.5,
        },
    }
    current = {
        "overall_score": 90.0,
        "metrics_summary": {
            "recall_at_k": 0.9,
            "precision_at_k": 0.8,
            "mrr": 0.85,
            "citation_accuracy": 0.95,
            "citation_coverage": 0.9,
            "total_pipeline_latency_seconds": 1.0,
        },
    }

    comparison = RegressionComparator.compare(current, baseline)
    assert comparison["baseline_score"] == 80.0
    assert comparison["current_score"] == 90.0
    assert comparison["score_delta"] == 10.0
    assert comparison["status"] == "improved"

    # check recall_at_k is improved
    assert comparison["metrics_deltas"]["recall_at_k"]["status"] == "improved"
    # check latency is improved (since it decreased from 1.5s to 1.0s)
    assert comparison["metrics_deltas"]["total_pipeline_latency_seconds"]["status"] == "improved"

    md = RegressionComparator.to_markdown(comparison)
    assert "🟢 Improved" in md
    assert "total_pipeline_latency_seconds" in md


def test_deterministic_execution() -> None:
    entry = BenchmarkEntry(
        question="What is CRC?",
        expected_answer="Cyclic Redundancy Check is an error-detecting code...",
        expected_pages=[45, 46],
        expected_chunks=["chunk_1"],
        expected_keywords=["cyclic", "redundancy"],
        expected_citations=["Citation CRC"],
        difficulty="medium",
        category="Error Detection",
        book="Computer Networks",
    )

    runner = EvaluationRunner(mock_mode=True)
    res_1 = runner.run_entry(entry)
    res_2 = runner.run_entry(entry)

    assert res_1.status == "success"
    assert res_2.status == "success"
    assert res_1.generated_answer == res_2.generated_answer
    assert res_1.metrics.recall_at_k == res_2.metrics.recall_at_k
    assert res_1.metrics.precision_at_k == res_2.metrics.precision_at_k
    assert res_1.metrics.mrr == res_2.metrics.mrr
    assert res_1.metrics.citation_accuracy == res_2.metrics.citation_accuracy


def test_missing_citations() -> None:
    # Test pipeline runs and metrics when citations are missing / empty
    entry = BenchmarkEntry(
        question="What is CRC?",
        expected_answer="Answer without citations",
        expected_pages=[45],
        expected_chunks=["chunk_1"],
        difficulty="medium",
        category="Error Detection",
        book="Computer Networks",
    )

    # We pass empty expected citations
    runner = EvaluationRunner(mock_mode=True)
    res = runner.run_entry(entry)
    assert res.status == "success"
    # Even if generated_answer doesn't have citations, citation_accuracy should default to 1.0
    assert res.metrics.citation_accuracy == 1.0
    assert res.metrics.citation_coverage == 1.0  # citation was automatically resolved and cited


def test_pipeline_failures() -> None:
    # If the entry has a malformed question or we force a failure,
    # runner should catch it and return failed status
    entry = BenchmarkEntry(
        question="",  # Empty query text triggers ValidationException
        expected_answer="Error expected",
        expected_pages=[45],
        expected_chunks=["chunk_1"],
        difficulty="medium",
        category="Error Detection",
        book="Computer Networks",
    )

    runner = EvaluationRunner(mock_mode=True)
    res = runner.run_entry(entry)
    assert res.status == "failed"
    assert res.error_message is not None
    assert "Query text cannot be empty or blank" in res.error_message
    # Check metrics are set to 0
    assert res.metrics.recall_at_k == 0.0
    assert res.metrics.precision_at_k == 0.0

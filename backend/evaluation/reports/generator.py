import json
from typing import Any

from evaluation.runner.runner import EvaluationResult


class ReportGenerator:
    @staticmethod
    def generate_summary_dict(
        results: list[EvaluationResult], total_duration: float
    ) -> dict[str, Any]:
        if not results:
            return {
                "overall_score": 0.0,
                "metrics_summary": {},
                "failures": [],
                "warnings": ["No test results evaluated."],
                "recommendations": ["Ensure benchmark dataset has valid entries."],
                "execution_time_seconds": total_duration,
                "total_cases": 0,
                "success_count": 0,
            }

        total_cases = len(results)
        successes = [r for r in results if r.status == "success"]
        success_count = len(successes)

        # Average metrics across successes
        if success_count:
            avg_recall = sum(r.metrics.recall_at_k for r in successes) / success_count
            avg_precision = sum(r.metrics.precision_at_k for r in successes) / success_count
            avg_mrr = sum(r.metrics.mrr for r in successes) / success_count
            avg_citation_acc = sum(r.metrics.citation_accuracy for r in successes) / success_count
            avg_citation_cov = sum(r.metrics.citation_coverage for r in successes) / success_count
            avg_evidence_ratio = (
                sum(r.metrics.evidence_coverage_ratio for r in successes) / success_count
            )
            avg_prompt_size = sum(r.metrics.prompt_size for r in successes) / success_count
            avg_retrieval_lat = sum(r.metrics.retrieval_latency for r in successes) / success_count
            avg_generation_lat = (
                sum(r.metrics.generation_latency for r in successes) / success_count
            )
            avg_total_lat = sum(r.metrics.total_pipeline_latency for r in successes) / success_count
            avg_resp_len = sum(r.metrics.response_length for r in successes) / success_count
            avg_chunk_count = sum(r.metrics.chunk_count for r in successes) / success_count
            avg_similarity = sum(r.metrics.average_similarity for r in successes) / success_count
        else:
            avg_recall = 0.0
            avg_precision = 0.0
            avg_mrr = 0.0
            avg_citation_acc = 0.0
            avg_citation_cov = 0.0
            avg_evidence_ratio = 0.0
            avg_prompt_size = 0.0
            avg_retrieval_lat = 0.0
            avg_generation_lat = 0.0
            avg_total_lat = 0.0
            avg_resp_len = 0.0
            avg_chunk_count = 0.0
            avg_similarity = 0.0

        # Calculate Overall Score: Weighted average of recall, precision, mrr,
        # citation accuracy and coverage
        overall_score = (
            avg_recall * 0.3
            + avg_precision * 0.1
            + avg_mrr * 0.2
            + avg_citation_acc * 0.2
            + avg_citation_cov * 0.2
        ) * 100.0

        # Compile warnings and recommendations
        warnings = []
        recommendations = []
        failures = []

        for r in results:
            if r.status != "success":
                failures.append({"question": r.entry.question, "error": r.error_message})

        if avg_recall < 0.8:
            warnings.append(
                f"Retrieval Recall is low ({avg_recall:.2%}). "
                "Some expected textbook passages were not retrieved."
            )
            recommendations.append(
                "Increase chunk overlap size or lower the similarity "
                "cutoff threshold to retrieve more candidates."
            )

        if avg_precision < 0.6:
            warnings.append(
                f"Retrieval Precision is low ({avg_precision:.2%}). "
                "Prompt context contains high noise level."
            )
            recommendations.append(
                "Increase similarity cutoff threshold or decrease "
                "the retrieval limit (K) to reduce context noise."
            )

        if avg_citation_acc < 0.9:
            warnings.append(
                f"Citation Accuracy is low ({avg_citation_acc:.2%}). "
                "Some citations point to incorrect page numbers."
            )
            recommendations.append(
                "Audit DefaultCitationEngine offset matching algorithm "
                "or prompt constraints to enforce page alignment."
            )

        if avg_total_lat > 3.0:
            warnings.append(f"Average Pipeline Latency is high ({avg_total_lat:.2f}s).")
            recommendations.append(
                "Examine model provider latency. Consider caching "
                "queries or using smaller embeddings."
            )

        if not warnings:
            warnings.append("No critical metric warnings.")
        if not recommendations:
            recommendations.append(
                "Pipeline is performing optimally according to benchmark criteria."
            )

        return {
            "overall_score": round(overall_score, 2),
            "total_cases": total_cases,
            "success_count": success_count,
            "execution_time_seconds": round(total_duration, 4),
            "metrics_summary": {
                "recall_at_k": round(avg_recall, 4),
                "precision_at_k": round(avg_precision, 4),
                "mrr": round(avg_mrr, 4),
                "citation_accuracy": round(avg_citation_acc, 4),
                "citation_coverage": round(avg_citation_cov, 4),
                "evidence_coverage_ratio": round(avg_evidence_ratio, 4),
                "prompt_size_chars": int(avg_prompt_size),
                "retrieval_latency_seconds": round(avg_retrieval_lat, 4),
                "generation_latency_seconds": round(avg_generation_lat, 4),
                "total_pipeline_latency_seconds": round(avg_total_lat, 4),
                "response_length_chars": int(avg_resp_len),
                "chunk_count": int(avg_chunk_count),
                "average_similarity": round(avg_similarity, 4),
            },
            "failures": failures,
            "warnings": warnings,
            "recommendations": recommendations,
        }

    @staticmethod
    def to_json(summary: dict[str, Any]) -> str:
        return json.dumps(summary, indent=2)

    @staticmethod
    def to_markdown(summary: dict[str, Any]) -> str:
        metrics = summary["metrics_summary"]

        md = []
        md.append("# Knowledge Retrieval Platform Evaluation Report")
        md.append("")
        cases_passed = summary["success_count"]
        cases_total = summary["total_cases"]
        exec_time = summary["execution_time_seconds"]
        md.append(f"**Overall System Score:** `{summary['overall_score']}%`  ")
        md.append(f"**Benchmark Test Cases:** {cases_passed} / {cases_total} Passed  ")
        md.append(f"**Execution Time:** {exec_time} seconds")
        md.append("")
        md.append("## Metric Breakdown")
        md.append("")
        md.append("| Metric | Value | Target / Description |")
        md.append("|---|---|---|")

        recall_at_k = metrics.get("recall_at_k", 0.0)
        precision_at_k = metrics.get("precision_at_k", 0.0)
        mrr = metrics.get("mrr", 0.0)
        citation_acc = metrics.get("citation_accuracy", 0.0)
        citation_cov = metrics.get("citation_coverage", 0.0)
        evidence_cov = metrics.get("evidence_coverage_ratio", 0.0)
        prompt_size = metrics.get("prompt_size_chars", 0)
        resp_len = metrics.get("response_length_chars", 0)
        chunk_count = metrics.get("chunk_count", 0)
        avg_sim = metrics.get("average_similarity", 0.0)

        md.append(
            f"| **Retrieval Recall@K** | {recall_at_k:.2%} | "
            "Proportion of expected context retrieved |"
        )
        md.append(
            f"| **Retrieval Precision@K** | {precision_at_k:.2%} | "
            "Proportion of retrieved context that is relevant |"
        )
        md.append(
            f"| **Mean Reciprocal Rank (MRR)** | {mrr:.4f} | "
            "Position rank of the first relevant chunk |"
        )
        md.append(
            f"| **Citation Accuracy** | {citation_acc:.2%} | "
            "Citations that resolve to valid source pages |"
        )
        md.append(
            f"| **Citation Coverage** | {citation_cov:.2%} | Proportion of expected pages cited |"
        )
        md.append(
            f"| **Evidence Coverage Ratio** | {evidence_cov:.2%} | "
            "Retrieved evidence utilized in response |"
        )
        md.append(
            f"| **Average Prompt Size** | {prompt_size:,} chars | "
            "Length of compiled grounding context |"
        )
        md.append(f"| **Response Length** | {resp_len:,} chars | Average answer length |")
        md.append(f"| **Chunk Count** | {chunk_count} chunks | Chunks retrieved per query |")
        md.append(
            f"| **Average Similarity** | {avg_sim:.4f} | Cosine similarity of retrieved vectors |"
        )
        md.append("")

        ret_lat = metrics.get("retrieval_latency_seconds", 0.0)
        gen_lat = metrics.get("generation_latency_seconds", 0.0)
        tot_lat = metrics.get("total_pipeline_latency_seconds", 0.0)

        md.append("## Stage Latency Breakdown")
        md.append("")
        md.append(f"- **Retrieval Latency:** `{ret_lat:.4f}s`  ")
        md.append(f"- **Generation Latency:** `{gen_lat:.4f}s`  ")
        md.append(f"- **Total Pipeline Latency:** `{tot_lat:.4f}s`  ")
        md.append("")

        md.append("## Warnings")
        for warning in summary.get("warnings", []):
            md.append(f"- ⚠️ {warning}")
        md.append("")

        md.append("## Recommendations")
        for rec in summary.get("recommendations", []):
            md.append(f"- 💡 {rec}")
        md.append("")

        if summary.get("failures"):
            md.append("## Failures")
            for failure in summary["failures"]:
                md.append(f"- **Query:** `{failure['question']}`")
                md.append(f"  - **Error:** {failure['error']}")
            md.append("")

        return "\n".join(md)

    @staticmethod
    def print_console_summary(summary: dict[str, Any]) -> None:
        metrics = summary["metrics_summary"]
        print("=" * 60)
        print("        KNOWLEDGE RETRIEVAL PLATFORM EVALUATION")
        print("=" * 60)
        print(f"Overall Score:            {summary['overall_score']}%")
        print(f"Test cases:               {summary['success_count']}/{summary['total_cases']}")
        print(f"Execution time:           {summary['execution_time_seconds']} s")
        print("-" * 60)
        recall = metrics.get("recall_at_k", 0.0)
        precision = metrics.get("precision_at_k", 0.0)
        mrr_val = metrics.get("mrr", 0.0)
        cit_acc = metrics.get("citation_accuracy", 0.0)
        cit_cov = metrics.get("citation_coverage", 0.0)
        ev_cov = metrics.get("evidence_coverage_ratio", 0.0)
        resp_len_chars = metrics.get("response_length_chars", 0)
        tot_pipe_lat = metrics.get("total_pipeline_latency_seconds", 0.0)

        print(f"Recall@K:                 {recall:.2%}")
        print(f"Precision@K:              {precision:.2%}")
        print(f"MRR:                      {mrr_val:.4f}")
        print(f"Citation Accuracy:        {cit_acc:.2%}")
        print(f"Citation Coverage:        {cit_cov:.2%}")
        print(f"Evidence Coverage Ratio:  {ev_cov:.2%}")
        print(f"Avg Response Length:      {resp_len_chars} chars")
        print(f"Avg Total Pipeline Time:  {tot_pipe_lat:.4f} s")
        print("=" * 60)

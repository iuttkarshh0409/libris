from typing import Any

from pydantic import BaseModel


class EvaluationMetrics(BaseModel):
    recall_at_k: float
    precision_at_k: float
    mrr: float
    citation_accuracy: float
    citation_coverage: float
    evidence_coverage_ratio: float
    prompt_size: int
    generation_latency: float
    retrieval_latency: float
    total_pipeline_latency: float
    response_length: int
    chunk_count: int
    average_similarity: float


class MetricsCalculator:
    @staticmethod
    def calculate(
        expected_pages: list[int],
        expected_chunks: list[str],
        expected_citations: list[str],
        retrieved_chunks: list[Any],
        citations: list[Any],
        generated_answer: str,
        prompt_text: str,
        retrieval_latency: float,
        generation_latency: float,
        total_latency: float,
    ) -> EvaluationMetrics:
        k = len(retrieved_chunks)

        # 1. Recall@K
        # If expected_pages is provided, we check matching page numbers
        # If expected_chunks is provided, we check chunk text or ID matches
        matched_expected_pages = set()
        matched_expected_chunks = set()

        for chunk in retrieved_chunks:
            # Check page match
            page_num = getattr(chunk, "page_number", None)
            if page_num is not None and page_num in expected_pages:
                matched_expected_pages.add(page_num)

            # Check chunk match
            chunk_text = getattr(chunk, "chunk_text", "")
            chunk_id = getattr(chunk, "chunk_id", None)
            chunk_id_str = getattr(chunk_id, "value", "") if chunk_id else ""
            for ec in expected_chunks:
                if ec == chunk_id_str or ec in chunk_text:
                    matched_expected_chunks.add(ec)

        total_expected_items = len(expected_pages) + len(expected_chunks)
        total_matched_items = len(matched_expected_pages) + len(matched_expected_chunks)

        recall = total_matched_items / total_expected_items if total_expected_items > 0 else 1.0

        # 2. Precision@K
        relevant_retrieved = 0
        for chunk in retrieved_chunks:
            is_relevant = False
            page_num = getattr(chunk, "page_number", None)
            if page_num is not None and page_num in expected_pages:
                is_relevant = True

            chunk_text = getattr(chunk, "chunk_text", "")
            chunk_id = getattr(chunk, "chunk_id", None)
            chunk_id_str = getattr(chunk_id, "value", "") if chunk_id else ""
            for ec in expected_chunks:
                if ec == chunk_id_str or ec in chunk_text:
                    is_relevant = True
                    break

            if is_relevant:
                relevant_retrieved += 1

        precision = relevant_retrieved / k if k > 0 else 1.0

        # 3. MRR
        mrr = 0.0
        for idx, chunk in enumerate(retrieved_chunks):
            is_relevant = False
            page_num = getattr(chunk, "page_number", None)
            if page_num is not None and page_num in expected_pages:
                is_relevant = True

            chunk_text = getattr(chunk, "chunk_text", "")
            chunk_id = getattr(chunk, "chunk_id", None)
            chunk_id_str = getattr(chunk_id, "value", "") if chunk_id else ""
            for ec in expected_chunks:
                if ec == chunk_id_str or ec in chunk_text:
                    is_relevant = True
                    break

            if is_relevant:
                mrr = 1.0 / (idx + 1)
                break

        # 4. Citation Accuracy
        # A citation is accurate if its page number is in the expected pages
        accurate_citations = 0
        for citation in citations:
            p_num = getattr(citation, "page_number", None)
            if p_num is not None and p_num in expected_pages:
                accurate_citations += 1
            elif not expected_pages:
                # If no expected pages, count as accurate to avoid punishing empty settings
                accurate_citations += 1

        citation_accuracy = accurate_citations / len(citations) if citations else 1.0

        # 5. Citation Coverage
        # Proportion of expected pages/citations actually cited
        cited_pages = {getattr(c, "page_number", None) for c in citations}
        cited_pages.discard(None)

        matched_citations = len(cited_pages.intersection(expected_pages))
        citation_coverage = matched_citations / len(expected_pages) if expected_pages else 1.0

        # 6. Evidence Coverage Ratio
        # Ratio of unique chunks/pages cited in response to total retrieved chunks/pages
        unique_retrieved_pages = {getattr(c, "page_number", None) for c in retrieved_chunks}
        unique_retrieved_pages.discard(None)

        evidence_coverage_ratio = (
            len(cited_pages.intersection(unique_retrieved_pages)) / len(unique_retrieved_pages)
            if unique_retrieved_pages
            else 0.0
        )

        # 7. Prompt Size
        prompt_size = len(prompt_text)

        # 8. Generation Latency, Retrieval Latency, Total Pipeline Latency
        # Passed directly from runner

        # 9. Response Length
        response_length = len(generated_answer)

        # 10. Chunk Count
        chunk_count = k

        # 11. Average Similarity
        total_sim = sum(float(getattr(c, "similarity_score", 0.0)) for c in retrieved_chunks)
        average_similarity = total_sim / k if k > 0 else 0.0

        return EvaluationMetrics(
            recall_at_k=recall,
            precision_at_k=precision,
            mrr=mrr,
            citation_accuracy=citation_accuracy,
            citation_coverage=citation_coverage,
            evidence_coverage_ratio=evidence_coverage_ratio,
            prompt_size=prompt_size,
            generation_latency=generation_latency,
            retrieval_latency=retrieval_latency,
            total_pipeline_latency=total_latency,
            response_length=response_length,
            chunk_count=chunk_count,
            average_similarity=average_similarity,
        )

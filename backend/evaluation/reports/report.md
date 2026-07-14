# Knowledge Retrieval Platform Evaluation Report

**Overall System Score:** `100.0%`  
**Benchmark Test Cases:** 2 / 2 Passed  
**Execution Time:** 0.0019 seconds

## Metric Breakdown

| Metric | Value | Target / Description |
|---|---|---|
| **Retrieval Recall@K** | 100.00% | Proportion of expected context retrieved |
| **Retrieval Precision@K** | 100.00% | Proportion of retrieved context that is relevant |
| **Mean Reciprocal Rank (MRR)** | 1.0000 | Position rank of the first relevant chunk |
| **Citation Accuracy** | 100.00% | Citations that resolve to valid source pages |
| **Citation Coverage** | 100.00% | Proportion of expected pages cited |
| **Evidence Coverage Ratio** | 100.00% | Retrieved evidence utilized in response |
| **Average Prompt Size** | 1,633 chars | Length of compiled grounding context |
| **Response Length** | 116 chars | Average answer length |
| **Chunk Count** | 2 chunks | Chunks retrieved per query |
| **Average Similarity** | 0.8125 | Cosine similarity of retrieved vectors |

## Stage Latency Breakdown

- **Retrieval Latency:** `0.0003s`  
- **Generation Latency:** `0.0002s`  
- **Total Pipeline Latency:** `0.0009s`  

## Warnings
- ⚠️ No critical metric warnings.

## Recommendations
- 💡 Pipeline is performing optimally according to benchmark criteria.

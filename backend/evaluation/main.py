import argparse
import json
import os
import time

from loguru import logger

from evaluation.datasets.loader import DatasetLoader
from evaluation.regression.comparator import RegressionComparator
from evaluation.reports.generator import ReportGenerator
from evaluation.runner.runner import EvaluationRunner


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Knowledge Retrieval Platform Evaluation & Benchmark Harness"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "datasets", "benchmark.json"),
        help="Path to the benchmark dataset JSON file",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "golden", "baseline.json"),
        help="Path to the baseline golden JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(os.path.dirname(__file__), "reports"),
        help="Directory to write reports to",
    )
    parser.add_argument(
        "--real-pipeline",
        action="store_true",
        help="Run against real production model/database providers "
        "instead of deterministic mock mode",
    )

    args = parser.parse_args()

    logger.info("Initializing Evaluation Framework Run...")

    # 1. Load benchmark dataset
    if not os.path.exists(args.dataset):
        logger.error(f"Dataset path does not exist: {args.dataset}")
        return

    try:
        entries = DatasetLoader.load_json(args.dataset)
        logger.info(f"Loaded {len(entries)} benchmark test cases from {args.dataset}")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return

    # 2. Run evaluation
    runner = EvaluationRunner(mock_mode=not args.real_pipeline)

    start_time = time.perf_counter()
    results = runner.run_suite(entries)
    total_duration = time.perf_counter() - start_time

    # 3. Generate summary report
    summary = ReportGenerator.generate_summary_dict(results, total_duration)

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Write JSON report
    json_report = ReportGenerator.to_json(summary)
    json_path = os.path.join(args.output_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_report)

    # Write Markdown report
    md_report = ReportGenerator.to_markdown(summary)
    md_path = os.path.join(args.output_dir, "report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    logger.info(f"Evaluation reports written to {args.output_dir}")

    # 4. Print console summary
    ReportGenerator.print_console_summary(summary)

    # 5. Regression detection
    if os.path.exists(args.baseline):
        try:
            with open(args.baseline, encoding="utf-8") as f:
                baseline_data = json.load(f)

            regression_report = RegressionComparator.compare(summary, baseline_data)

            # Write regression report to markdown
            reg_md = RegressionComparator.to_markdown(regression_report)
            reg_md_path = os.path.join(args.output_dir, "regression_report.md")
            with open(reg_md_path, "w", encoding="utf-8") as f:
                f.write(reg_md)

            # Log status
            status = regression_report["status"]
            delta = regression_report["score_delta"]
            if status == "improved":
                logger.info(f"🎉 System has IMPROVED! Overall score increased by {delta:+}%.")
            elif status == "regressed":
                logger.warning(f"⚠️ Regression detected! Overall score decreased by {delta}%.")
            else:
                logger.info("System performance is stable and matches the baseline.")

            print("\n" + "=" * 60)
            print("                REGRESSION ANALYSIS")
            print("=" * 60)
            print(f"Status:          {status.upper()}")
            print(f"Baseline Score:  {regression_report['baseline_score']}%")
            print(f"Current Score:   {regression_report['current_score']}%")
            print(f"Score Delta:     {delta:+}%")
            print("=" * 60)
        except Exception as e:
            logger.error(f"Failed to load baseline or run regression analysis: {e}")
    else:
        logger.warning(f"Baseline file not found at {args.baseline}. Skipping regression check.")


if __name__ == "__main__":
    main()

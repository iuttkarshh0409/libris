from typing import Any


class RegressionComparator:
    @staticmethod
    def compare(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
        """Compares current evaluation metrics summary with a baseline summary.

        Detects improvements, regressions, and unchanged metrics.
        """
        current_score = current.get("overall_score", 0.0)
        baseline_score = baseline.get("overall_score", 0.0)
        score_delta = round(current_score - baseline_score, 2)

        if score_delta > 0:
            status = "improved"
        elif score_delta < 0:
            status = "regressed"
        else:
            status = "unchanged"

        current_metrics = current.get("metrics_summary", {})
        baseline_metrics = baseline.get("metrics_summary", {})

        metrics_deltas = {}
        for key, val in current_metrics.items():
            base_val = baseline_metrics.get(key, 0.0)
            delta = val - base_val

            # Latency: lower is better
            if "latency" in key:
                # Use a small tolerance of 50ms (or 5%) to filter noise
                tolerance = max(0.05, base_val * 0.05) if base_val else 0.05
                if delta < -tolerance:
                    metric_status = "improved"
                elif delta > tolerance:
                    metric_status = "regressed"
                else:
                    metric_status = "unchanged"
            else:
                if delta > 0.0001:
                    metric_status = "improved"
                elif delta < -0.0001:
                    metric_status = "regressed"
                else:
                    metric_status = "unchanged"

            metrics_deltas[key] = {
                "baseline": base_val,
                "current": val,
                "delta": round(delta, 4),
                "status": metric_status,
            }

        return {
            "baseline_score": baseline_score,
            "current_score": current_score,
            "score_delta": score_delta,
            "status": status,
            "metrics_deltas": metrics_deltas,
        }

    @staticmethod
    def to_markdown(report: dict[str, Any]) -> str:
        md = []
        md.append("# Regression Detection Report")
        md.append("")

        status_emoji = {
            "improved": "🟢 Improved",
            "regressed": "🔴 Regressed",
            "unchanged": "⚪ Unchanged",
        }

        md.append(f"**Status:** {status_emoji[report['status']]}  ")
        md.append(f"**Baseline Score:** `{report['baseline_score']}%`  ")
        md.append(f"**Current Score:** `{report['current_score']}%`  ")
        md.append(f"**Score Delta:** `{report['score_delta']:+}%`  ")
        md.append("")
        md.append("## Metric Comparisons")
        md.append("")
        md.append("| Metric | Baseline | Current | Delta | Status |")
        md.append("|---|---|---|---|---|")

        for name, comp in report["metrics_deltas"].items():
            status = comp["status"]
            emoji = "✅" if status == "improved" else ("❌" if status == "regressed" else "⚪")

            # Format nicely
            pct_metrics = {
                "recall_at_k",
                "precision_at_k",
                "citation_accuracy",
                "citation_coverage",
                "evidence_coverage_ratio",
            }
            if name in pct_metrics:
                base_str = f"{comp['baseline']:.2%}"
                curr_str = f"{comp['current']:.2%}"
                delta_str = f"{comp['delta']:+.2%}"
            elif "latency" in name:
                base_str = f"{comp['baseline']:.4f}s"
                curr_str = f"{comp['current']:.4f}s"
                delta_str = f"{comp['delta']:+.4f}s"
            else:
                base_str = str(comp["baseline"])
                curr_str = str(comp["current"])
                delta_str = f"{comp['delta']:+}"

            row = f"| {name} | {base_str} | {curr_str} | {delta_str} | {emoji} {status} |"
            md.append(row)

        md.append("")
        return "\n".join(md)

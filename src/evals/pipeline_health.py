from src.evals.schemas import PipelineHealthResult, CheckResult
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

def get_freshness_hours(timestamp_str: str) -> float:
    try:
        dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        return diff.total_seconds() / 3600
    except Exception:
        return 999.0

def evaluate_pipeline_health(
    analytics_manifest: Optional[Dict[str, Any]],
    trend_manifest: Optional[Dict[str, Any]],
    logs_summary: List[Dict[str, Any]],
    required_files: List[Path]
) -> PipelineHealthResult:
    checks = []
    
    # Check Required Files
    missing_files = [f.name for f in required_files if not f.exists()]
    required_files_exist = len(missing_files) == 0
    
    checks.append(CheckResult(
        name="Required Files",
        status="PASS" if required_files_exist else "FAIL",
        message="All required files exist." if required_files_exist else f"Missing files: {', '.join(missing_files)}"
    ))
    
    # Check Freshness
    analytics_freshness_hours = None
    ingestion_freshness_hours = None
    
    if analytics_manifest and "created_at" in analytics_manifest:
        analytics_freshness_hours = get_freshness_hours(analytics_manifest["created_at"])
    
    if trend_manifest and "created_at" in trend_manifest:
        trend_freshness_hours = get_freshness_hours(trend_manifest["created_at"])
        if analytics_freshness_hours is None:
            analytics_freshness_hours = trend_freshness_hours
            
    # Try finding ingestion freshness from logs
    ingestion_logs = [log for log in logs_summary if log.get("step") == "ingestion" or "records_collected" in log]
    if ingestion_logs:
        latest_ingestion = ingestion_logs[-1]
        if "timestamp" in latest_ingestion:
             ingestion_freshness_hours = get_freshness_hours(latest_ingestion["timestamp"])

    max_freshness = max(
        analytics_freshness_hours if analytics_freshness_hours is not None else 999,
        ingestion_freshness_hours if ingestion_freshness_hours is not None else 999
    )
    
    checks.append(CheckResult(
        name="Data Freshness",
        status="PASS" if max_freshness < 24 else ("WARN" if max_freshness < 72 else "FAIL"),
        score=max_freshness,
        message=f"Data freshness: {max_freshness:.1f} hours old." if max_freshness != 999 else "Freshness could not be determined."
    ))

    # Check Pipeline Success Rate from logs
    total_runs = len(logs_summary)
    success_runs = len([log for log in logs_summary if log.get("status") == "success" or "error" in log and log["error"] is None or log.get("error_message") is None])
    
    pipeline_success_rate = (success_runs / total_runs) if total_runs > 0 else 1.0
    
    checks.append(CheckResult(
        name="Pipeline Success Rate",
        status="PASS" if pipeline_success_rate >= 0.8 else "WARN",
        score=pipeline_success_rate,
        message=f"Pipeline success rate: {pipeline_success_rate*100:.1f}% based on {total_runs} logs."
    ))
    
    return PipelineHealthResult(
        required_files_exist=required_files_exist,
        ingestion_freshness_hours=ingestion_freshness_hours,
        analytics_freshness_hours=analytics_freshness_hours,
        pipeline_success_rate=pipeline_success_rate,
        checks=checks
    )

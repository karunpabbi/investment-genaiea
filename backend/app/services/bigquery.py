from __future__ import annotations

from typing import Dict, List

from google.cloud import bigquery

from ..config import get_settings


class BigQuerySignals:
    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: bigquery.Client | None = None
        if self._settings.enable_google_services and self._settings.google_project_id:
            try:
                self._client = bigquery.Client(project=self._settings.google_project_id)
            except Exception:
                self._client = None

    def fetch_sector_benchmarks(self, sector: str | None) -> Dict[str, float]:
        if not sector:
            return {}
        if self._client is None or not self._settings.bigquery_dataset:
            # Provide heuristic defaults
            return {
                "revenue_growth_pct": 65.0,
                "gross_margin_pct": 48.0,
                "team_size": 35.0,
                "customer_retention_pct": 72.0,
            }
        query = f"""
        SELECT
            AVG(revenue_growth) as revenue_growth_pct,
            AVG(gross_margin) as gross_margin_pct,
            AVG(team_size) as team_size,
            AVG(customer_retention) as customer_retention_pct
        FROM `{self._settings.bigquery_dataset}.sector_benchmarks`
        WHERE LOWER(sector) = LOWER(@sector)
        """
        job = self._client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("sector", "STRING", sector)]
        ))
        result = job.result()
        row = next(iter(result), None)
        if row is None:
            return {}
        return {k: float(v) for k, v in dict(row).items() if v is not None}

    def fetch_market_signals(self, startup_name: str) -> List[Dict[str, str]]:
        if self._client is None or not self._settings.bigquery_dataset:
            return [
                {
                    "source": "Crunchbase",
                    "title": f"{startup_name} raises seed round",
                    "summary": "Simulated funding activity. Connect BigQuery for live data.",
                }
            ]
        query = f"""
        SELECT source, title, summary
        FROM `{self._settings.bigquery_dataset}.public_signals`
        WHERE LOWER(company_name) = LOWER(@name)
        ORDER BY published_at DESC
        LIMIT 10
        """
        job = self._client.query(query, job_config=bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("name", "STRING", startup_name)]
        ))
        return [dict(row) for row in job.result()]


_bigquery_client: BigQuerySignals | None = None


def get_bigquery_client() -> BigQuerySignals:
    global _bigquery_client
    if _bigquery_client is None:
        _bigquery_client = BigQuerySignals()
    return _bigquery_client

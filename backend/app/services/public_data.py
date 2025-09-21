from __future__ import annotations

from typing import List

from ..models import PublicSignal
from .bigquery import get_bigquery_client


class PublicDataAggregator:
    def __init__(self) -> None:
        self._bigquery = get_bigquery_client()

    def gather_signals(self, startup_name: str) -> List[PublicSignal]:
        rows = self._bigquery.fetch_market_signals(startup_name)
        return [
            PublicSignal(source=row["source"], title=row["title"], summary=row["summary"], metadata=row)
            for row in rows
        ]


_public_data_aggregator: PublicDataAggregator | None = None


def get_public_data_aggregator() -> PublicDataAggregator:
    global _public_data_aggregator
    if _public_data_aggregator is None:
        _public_data_aggregator = PublicDataAggregator()
    return _public_data_aggregator

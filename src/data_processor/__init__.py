"""
Data Processor Component

This module handles all data collection, processing, and analysis operations
for the federal clean energy funding analysis project.
"""

from .core_processor import DataProcessor
from .api_client import USASpendingAPIClient
from .data_transformer import DataTransformer
from .analytics_engine import AnalyticsEngine

__all__ = [
    "DataProcessor",
    "USASpendingAPIClient",
    "DataTransformer",
    "AnalyticsEngine",
]

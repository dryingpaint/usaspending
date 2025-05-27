#!/usr/bin/env python3
"""
Data Connector

Bridges the data processor and visualizer components, providing
a clean interface for the dashboard to access processed data.
"""

from typing import Dict, List, Optional, Any

# Add src to path for imports


from src.data_processor.core_processor import DataProcessor


class DataConnector:
    """
    Connects the visualization layer to the data processing layer.

    This class provides a clean interface for the dashboard to access
    processed data without needing to know about the underlying
    data processing implementation.
    """

    def __init__(self):
        self.data_processor = DataProcessor()
        self._current_data = None
        self._current_analysis = None

    def load_data(
        self,
        time_period: str = "ira_chips_period",
        max_pages: int = 5,
        force_refresh: bool = False,
    ) -> bool:
        """
        Load data for the specified time period.

        Args:
            time_period: Time period to load
            max_pages: Maximum pages to collect
            force_refresh: Force refresh even if data is cached

        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            self._current_data = self.data_processor.collect_clean_energy_data(
                time_period=time_period,
                max_pages=max_pages,
                use_cache=not force_refresh,
            )
            return not self._current_data.empty
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Get high-level summary metrics for dashboard header."""
        if self._current_data is None or self._current_data.empty:
            return {
                "total_funding": 0,
                "total_awards": 0,
                "unique_states": 0,
                "top_technology": "N/A",
            }

        df = self._current_data

        # Calculate metrics
        total_funding = df["award_amount"].sum() if "award_amount" in df.columns else 0
        total_awards = len(df)
        unique_states = df["state_code"].nunique() if "state_code" in df.columns else 0

        # Top technology
        top_tech = "N/A"
        if "technology_category" in df.columns:
            tech_summary = df.groupby("technology_category")["award_amount"].sum()
            if not tech_summary.empty:
                top_tech = tech_summary.idxmax()

        return {
            "total_funding": total_funding,
            "total_awards": total_awards,
            "unique_states": unique_states,
            "top_technology": top_tech,
        }

    def get_geographic_data(self) -> Dict[str, Any]:
        """Get data for geographic visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        return self.data_processor.get_geographic_analysis(self._current_data)

    def get_timeline_data(self) -> Dict[str, Any]:
        """Get data for timeline visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        return self.data_processor.get_timeline_analysis(self._current_data)

    def get_technology_data(self) -> Dict[str, Any]:
        """Get data for technology visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        return self.data_processor.get_technology_analysis(self._current_data)

    def get_recipient_data(self, top_n: int = 50) -> Dict[str, Any]:
        """Get data for recipient visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        return self.data_processor.get_recipient_analysis(
            self._current_data, top_n=top_n
        )

    def get_comparative_data(self) -> Dict[str, Any]:
        """Get data for comparative analysis visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        # Get comprehensive analysis if not already cached
        if self._current_analysis is None:
            self._current_analysis = self.data_processor.get_comprehensive_analysis()

        return self._current_analysis

    def get_insights(self) -> List[Dict[str, Any]]:
        """Get automated insights for the dashboard."""
        if self._current_data is None or self._current_data.empty:
            return []

        return self.data_processor.analytics.generate_insights(self._current_data)

    def export_current_data(
        self, filename: str = "dashboard_data.csv", format: str = "csv"
    ) -> Optional[str]:
        """Export current data to file."""
        if self._current_data is None or self._current_data.empty:
            return None

        try:
            return self.data_processor.export_data(
                self._current_data, filename=filename, format=format
            )
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None

    def get_data_info(self) -> Dict[str, Any]:
        """Get information about the current dataset."""
        if self._current_data is None:
            return {"status": "no_data_loaded"}

        if self._current_data.empty:
            return {"status": "empty_dataset"}

        df = self._current_data

        return {
            "status": "data_loaded",
            "total_records": len(df),
            "columns": list(df.columns),
            "date_range": {
                "start": df["start_date"].min().strftime("%Y-%m-%d")
                if "start_date" in df.columns
                else None,
                "end": df["start_date"].max().strftime("%Y-%m-%d")
                if "start_date" in df.columns
                else None,
            },
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
        }

    def refresh_data(
        self, time_period: str = "ira_chips_period", max_pages: int = 5
    ) -> bool:
        """Refresh data and clear analysis cache."""
        self._current_analysis = None
        self.data_processor.clear_cache()
        return self.load_data(time_period, max_pages, force_refresh=True)

    def get_available_time_periods(self) -> List[str]:
        """Get list of available time periods."""
        # This would typically come from the config
        return ["ira_chips_period", "pre_ira_period", "iija_period", "arra_period"]

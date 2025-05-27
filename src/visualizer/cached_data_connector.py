#!/usr/bin/env python3
"""
Cached Data Connector

Provides a clean interface for the dashboard to access consolidated clean energy data.
This replaces the original data connector that made live API calls with a fast,
cached version that uses pre-collected data.

Benefits:
- No API rate limits or 422 errors
- Instant loading (vs 30+ second API calls)
- Consistent data across all users
- Offline capability
- Better performance and reliability
"""

from typing import Dict, List, Optional, Any
import pandas as pd
from src.visualizer.cached_data_loader import CachedDataLoader


class CachedDataConnector:
    """
    Connects the visualization layer to cached clean energy data.

    This class provides the same interface as DataConnector but uses
    pre-collected and consolidated data for much faster performance.
    """

    def __init__(self):
        self.cached_loader = CachedDataLoader()
        self._current_data = None
        self._current_time_period = None

        print("🚀 Cached Data Connector initialized")
        print("📊 Using consolidated data - no API calls needed!")

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
            max_pages: Maximum pages to collect (ignored - using cached data)
            force_refresh: Force refresh (ignored - using cached data)

        Returns:
            True if data loaded successfully, False otherwise
        """
        try:
            print(f"📊 Loading cached data for time period: {time_period}")

            # Load the full dataset
            self._current_data = self.cached_loader.get_awards_data(sample=False)
            self._current_time_period = time_period
            print(f"🔧 Set _current_time_period to: {self._current_time_period}")

            # Filter by time period if specified and not full period
            if (
                time_period != "full_period"
                and "time_period_category" in self._current_data.columns
            ):
                print(
                    f"🔍 Available time periods in data: {self._current_data['time_period_category'].unique()}"
                )
                filtered_data = self._current_data[
                    self._current_data["time_period_category"] == time_period
                ]
                if not filtered_data.empty:
                    self._current_data = filtered_data
                    print(
                        f"✅ Filtered to {len(self._current_data):,} records for {time_period}"
                    )
                else:
                    print(
                        f"⚠️  No data found for time period {time_period}, using full dataset"
                    )

            print(f"✅ Loaded {len(self._current_data):,} total records")
            print(f"🔧 Final _current_time_period: {self._current_time_period}")
            return not self._current_data.empty

        except Exception as e:
            print(f"❌ Error loading cached data: {e}")
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

        # Calculate metrics using standardized column names
        total_funding = df["award_amount"].sum() if "award_amount" in df.columns else 0
        total_awards = len(df)
        unique_states = (
            df["performance_state_code"].nunique()
            if "performance_state_code" in df.columns
            else 0
        )

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

        try:
            df = self._current_data

            # Create state summary from current filtered data
            state_summary = pd.DataFrame()
            if "performance_state_code" in df.columns and "award_amount" in df.columns:
                state_summary = (
                    df.groupby("performance_state_code")
                    .agg(
                        {
                            "award_amount": ["sum", "count", "mean"],
                            "recipient_name": "nunique",
                        }
                    )
                    .round(2)
                )

                # Flatten column names
                state_summary.columns = [
                    "total_funding",
                    "award_count",
                    "avg_award_size",
                    "unique_recipients",
                ]
                state_summary = state_summary.reset_index()
                state_summary = state_summary.sort_values(
                    "total_funding", ascending=False
                )

            return {
                "state_summary": state_summary.to_dict("records")
                if not state_summary.empty
                else [],
                "county_summary": [],  # Could add county analysis if needed
                "geographic_data": state_summary.to_dict("records")
                if not state_summary.empty
                else [],
                "insights": [
                    {
                        "type": "geographic",
                        "description": f"Top state by funding: {state_summary.iloc[0]['performance_state_code'] if not state_summary.empty else 'N/A'}",
                    }
                ],
            }
        except Exception as e:
            print(f"Error getting geographic data: {e}")
            return {}

    def get_timeline_data(self) -> Dict[str, Any]:
        """Get data for timeline visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        try:
            df = self._current_data

            # Create time series data from current filtered data
            monthly_data = pd.DataFrame()
            quarterly_data = pd.DataFrame()
            yearly_trends = pd.DataFrame()

            # Monthly series
            if "start_date" in df.columns and "award_amount" in df.columns:
                df_copy = df.copy()
                df_copy["start_date"] = pd.to_datetime(df_copy["start_date"])
                df_copy["year_month"] = df_copy["start_date"].dt.to_period("M")

                monthly_data = (
                    df_copy.groupby("year_month")
                    .agg(
                        {
                            "award_amount": ["sum", "count"],
                        }
                    )
                    .round(2)
                )
                monthly_data.columns = ["total_funding", "award_count"]
                monthly_data = monthly_data.reset_index()
                monthly_data["year_month"] = monthly_data["year_month"].astype(str)

            # Yearly trends
            if "fiscal_year" in df.columns and "award_amount" in df.columns:
                yearly_trends = (
                    df.groupby("fiscal_year")
                    .agg(
                        {
                            "award_amount": ["sum", "count", "mean"],
                        }
                    )
                    .round(2)
                )
                yearly_trends.columns = ["total_funding", "award_count", "avg_award"]
                yearly_trends = yearly_trends.reset_index()
                yearly_trends = yearly_trends.sort_values("fiscal_year")

            # Create period comparison
            period_comparison = {}
            if "time_period_category" in df.columns and "award_amount" in df.columns:
                period_stats = (
                    df.groupby("time_period_category")["award_amount"]
                    .agg(["count", "sum", "mean"])
                    .to_dict()
                )
                period_comparison = {
                    "period_stats": period_stats,
                    "changes": {},  # Could calculate changes between periods
                }

            return {
                "monthly_series": monthly_data.to_dict("records")
                if not monthly_data.empty
                else [],
                "quarterly_series": quarterly_data.to_dict("records")
                if not quarterly_data.empty
                else [],
                "yearly_trends": yearly_trends.to_dict("records")
                if not yearly_trends.empty
                else [],
                "period_comparison": period_comparison,
                "insights": [
                    {
                        "type": "timeline",
                        "description": f"Peak funding year: {yearly_trends.loc[yearly_trends['total_funding'].idxmax(), 'fiscal_year'] if not yearly_trends.empty else 'N/A'}",
                    }
                ],
            }
        except Exception as e:
            print(f"Error getting timeline data: {e}")
            return {}

    def get_technology_data(self) -> Dict[str, Any]:
        """Get data for technology visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        try:
            df = self._current_data

            # Create technology summary from current filtered data
            tech_summary = pd.DataFrame()
            if "technology_category" in df.columns and "award_amount" in df.columns:
                tech_summary = (
                    df.groupby("technology_category")
                    .agg(
                        {
                            "award_amount": ["sum", "count", "mean"],
                            "recipient_name": "nunique",
                        }
                    )
                    .round(2)
                )

                # Flatten column names
                tech_summary.columns = [
                    "total_funding",
                    "award_count",
                    "avg_award_size",
                    "unique_recipients",
                ]
                tech_summary = tech_summary.reset_index()
                tech_summary = tech_summary.sort_values(
                    "total_funding", ascending=False
                )

            return {
                "technology_summary": tech_summary.to_dict("records")
                if not tech_summary.empty
                else [],
                "insights": [
                    {
                        "type": "technology",
                        "description": f"Top technology: {tech_summary.iloc[0]['technology_category'] if not tech_summary.empty else 'N/A'}",
                    }
                ],
            }
        except Exception as e:
            print(f"Error getting technology data: {e}")
            return {}

    def get_recipient_data(self, top_n: int = 50) -> Dict[str, Any]:
        """Get data for recipient visualizations."""
        if self._current_data is None or self._current_data.empty:
            return {}

        try:
            df = self._current_data

            # Create recipient analysis from current filtered data
            recipient_analysis = pd.DataFrame()
            if "recipient_name" in df.columns and "award_amount" in df.columns:
                recipient_analysis = (
                    df.groupby("recipient_name")
                    .agg(
                        {
                            "award_amount": ["sum", "count", "mean"],
                            "performance_state_code": "first",  # Get state for each recipient
                        }
                    )
                    .round(2)
                )

                # Flatten column names
                recipient_analysis.columns = [
                    "total_funding",
                    "award_count",
                    "avg_award_size",
                    "state",
                ]
                recipient_analysis = recipient_analysis.reset_index()
                recipient_analysis = recipient_analysis.sort_values(
                    "total_funding", ascending=False
                )

                # Limit to top N
                recipient_analysis = recipient_analysis.head(top_n)

            return {
                "recipient_summary": recipient_analysis.to_dict("records")
                if not recipient_analysis.empty
                else [],
                "clustering": {},  # Could add clustering analysis if needed
                "insights": [
                    {
                        "type": "recipient",
                        "description": f"Top recipient: {recipient_analysis.iloc[0]['recipient_name'] if not recipient_analysis.empty else 'N/A'}",
                    }
                ],
            }
        except Exception as e:
            print(f"Error getting recipient data: {e}")
            return {}

    def get_comparative_data(self) -> Dict[str, Any]:
        """Get data for comparative analysis visualizations."""
        try:
            # Get all the different data types for comparison
            geographic_data = self.get_geographic_data()
            technology_data = self.get_technology_data()
            timeline_data = self.get_timeline_data()

            return {
                "geographic": geographic_data,
                "technology": technology_data,
                "timeline": timeline_data,
                "summary": self.cached_loader.get_summary_statistics(),
            }
        except Exception as e:
            print(f"Error getting comparative data: {e}")
            return {}

    def get_insights(self) -> List[Dict[str, Any]]:
        """Get automated insights for the dashboard."""
        if self._current_data is None or self._current_data.empty:
            return []

        insights = []

        try:
            df = self._current_data

            # Funding insights
            if "award_amount" in df.columns:
                total_funding = df["award_amount"].sum()
                avg_award = df["award_amount"].mean()
                insights.append(
                    {
                        "type": "funding",
                        "description": f"Total funding: ${total_funding:,.0f} across {len(df):,} awards (avg: ${avg_award:,.0f})",
                    }
                )

            # Technology insights
            if "technology_category" in df.columns:
                top_tech = (
                    df.groupby("technology_category")["award_amount"].sum().idxmax()
                )
                insights.append(
                    {
                        "type": "technology",
                        "description": f"Leading technology category: {top_tech}",
                    }
                )

            # Geographic insights
            if "performance_state_code" in df.columns:
                top_state = (
                    df.groupby("performance_state_code")["award_amount"].sum().idxmax()
                )
                insights.append(
                    {
                        "type": "geographic",
                        "description": f"Top state by funding: {top_state}",
                    }
                )

            # Temporal insights
            if "fiscal_year" in df.columns:
                peak_year = df.groupby("fiscal_year")["award_amount"].sum().idxmax()
                insights.append(
                    {
                        "type": "temporal",
                        "description": f"Peak funding year: {peak_year}",
                    }
                )

        except Exception as e:
            print(f"Error generating insights: {e}")

        return insights

    def export_current_data(
        self, filename: str = "dashboard_data.csv", format: str = "csv"
    ) -> Optional[str]:
        """Export current data to file."""
        if self._current_data is None or self._current_data.empty:
            return None

        try:
            if format.lower() == "csv":
                filepath = f"data/exports/{filename}"
                self._current_data.to_csv(filepath, index=False)
                return filepath
            elif format.lower() == "parquet":
                filepath = f"data/exports/{filename.replace('.csv', '.parquet')}"
                self._current_data.to_parquet(filepath, index=False)
                return filepath
            else:
                print(f"Unsupported format: {format}")
                return None
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

        # Get additional info from cached loader
        cached_info = self.cached_loader.get_data_info()

        return {
            "status": "cached_data_loaded",
            "data_source": "consolidated_cache",
            "current_time_period": self._current_time_period,
            "total_records": len(df),
            "columns": list(df.columns),
            "date_range": {
                "start": df["start_date"].min().strftime("%Y-%m-%d")
                if "start_date" in df.columns and not df["start_date"].isna().all()
                else None,
                "end": df["start_date"].max().strftime("%Y-%m-%d")
                if "start_date" in df.columns and not df["start_date"].isna().all()
                else None,
            },
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            "cache_info": cached_info,
        }

    def refresh_data(
        self, time_period: str = "ira_chips_period", max_pages: int = 5
    ) -> bool:
        """Refresh data (for cached data, this just reloads)."""
        print("🔄 Refreshing cached data...")
        self.cached_loader.clear_cache()
        return self.load_data(time_period, max_pages, force_refresh=True)

    def get_available_time_periods(self) -> List[str]:
        """Get list of available time periods from cached data."""
        try:
            df = self.cached_loader.get_awards_data(
                sample=True
            )  # Use sample for quick check
            if "time_period_category" in df.columns:
                return df["time_period_category"].unique().tolist()
            else:
                return [
                    "full_period",
                    "ira_chips_period",
                    "post_arra_pre_ira",
                    "arra_period",
                    "pre_arra",
                ]
        except Exception as e:
            print(f"Error getting time periods: {e}")
            return [
                "full_period",
                "ira_chips_period",
                "post_arra_pre_ira",
                "arra_period",
                "pre_arra",
            ]

    def preload_all_data(self):
        """Preload all cached data for faster dashboard performance."""
        print("🚀 Preloading all cached data...")
        self.cached_loader.preload_all_data()
        print("✅ All data preloaded for maximum dashboard performance!")


# Backward compatibility alias
DataConnector = CachedDataConnector

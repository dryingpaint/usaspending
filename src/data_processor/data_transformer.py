#!/usr/bin/env python3
"""
Data Transformer

Handles data cleaning, transformation, and categorization operations
for federal clean energy funding analysis.
"""

import pandas as pd
from typing import Dict, Any

# Import constants from the new constants file
from src.config.data_constants import (
    TECHNOLOGY_CATEGORIES,
    RECIPIENT_TYPES,
    COLUMN_MAPPING,
    DATE_COLUMNS,
    TEXT_COLUMNS,
    DEFAULT_TECHNOLOGY_CATEGORY,
    DEFAULT_RECIPIENT_TYPE,
)


class DataTransformer:
    """
    Transforms raw USASpending data into analysis-ready formats.

    This class handles data cleaning, categorization, aggregation,
    and preparation for visualization and analysis.
    """

    def __init__(self):
        self.technology_categories = TECHNOLOGY_CATEGORIES
        self.recipient_types = RECIPIENT_TYPES

    def clean_award_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize award data.

        Args:
            df: Raw award data DataFrame

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df

        df_clean = df.copy()

        # Rename columns that exist using constants
        for old_name, new_name in COLUMN_MAPPING.items():
            if old_name in df_clean.columns:
                df_clean = df_clean.rename(columns={old_name: new_name})

        # Clean award amounts
        if "award_amount" in df_clean.columns:
            df_clean["award_amount"] = pd.to_numeric(
                df_clean["award_amount"], errors="coerce"
            ).fillna(0)

        # Clean dates using constants
        for col in DATE_COLUMNS:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors="coerce")

        # Clean text fields using constants
        for col in TEXT_COLUMNS:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

        # Remove rows with zero or negative amounts
        if "award_amount" in df_clean.columns:
            df_clean = df_clean[df_clean["award_amount"] > 0]

        return df_clean

    def categorize_by_technology(
        self, df: pd.DataFrame, text_column: str = "description"
    ) -> pd.DataFrame:
        """
        Categorize awards by clean energy technology.

        Args:
            df: DataFrame with award data
            text_column: Column containing text to categorize

        Returns:
            DataFrame with technology category column added
        """
        if df.empty or text_column not in df.columns:
            return df

        df_cat = df.copy()
        df_cat["technology_category"] = DEFAULT_TECHNOLOGY_CATEGORY

        for tech, keywords in self.technology_categories.items():
            # Create boolean mask for this technology
            mask = (
                df_cat[text_column]
                .str.lower()
                .str.contains("|".join(keywords), na=False, regex=True)
            )
            df_cat.loc[mask, "technology_category"] = tech

        return df_cat

    def categorize_recipients(
        self, df: pd.DataFrame, recipient_column: str = "recipient_name"
    ) -> pd.DataFrame:
        """
        Categorize recipients by organization type.

        Args:
            df: DataFrame with recipient data
            recipient_column: Column containing recipient names

        Returns:
            DataFrame with recipient type column added
        """
        if df.empty or recipient_column not in df.columns:
            return df

        df_cat = df.copy()
        df_cat["recipient_type"] = DEFAULT_RECIPIENT_TYPE

        for org_type, keywords in self.recipient_types.items():
            # Create boolean mask for this organization type
            mask = (
                df_cat[recipient_column]
                .str.lower()
                .str.contains("|".join(keywords), na=False, regex=True)
            )
            df_cat.loc[mask, "recipient_type"] = org_type

        return df_cat

    def aggregate_by_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate funding data by state.

        Args:
            df: DataFrame with award data

        Returns:
            DataFrame aggregated by state
        """
        if df.empty or "state_code" not in df.columns:
            return pd.DataFrame()

        # Group by state and aggregate
        state_agg = (
            df.groupby("state_code")
            .agg(
                {"award_amount": ["sum", "count", "mean"], "recipient_name": "nunique"}
            )
            .round(2)
        )

        # Flatten column names
        state_agg.columns = [
            "total_funding",
            "award_count",
            "avg_award_size",
            "unique_recipients",
        ]

        state_agg = state_agg.reset_index()

        # Add state names if available
        if "state_name" in df.columns:
            state_names = df.groupby("state_code")["state_name"].first()
            state_agg = state_agg.merge(
                state_names.reset_index(), on="state_code", how="left"
            )

        return state_agg.sort_values("total_funding", ascending=False)

    def aggregate_by_technology(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate funding data by technology category.

        Args:
            df: DataFrame with categorized award data

        Returns:
            DataFrame aggregated by technology
        """
        if df.empty or "technology_category" not in df.columns:
            return pd.DataFrame()

        tech_agg = (
            df.groupby("technology_category")
            .agg(
                {"award_amount": ["sum", "count", "mean"], "recipient_name": "nunique"}
            )
            .round(2)
        )

        # Flatten column names
        tech_agg.columns = [
            "total_funding",
            "award_count",
            "avg_award_size",
            "unique_recipients",
        ]

        tech_agg = tech_agg.reset_index()

        # Calculate percentages
        total_funding = tech_agg["total_funding"].sum()
        tech_agg["funding_percentage"] = (
            tech_agg["total_funding"] / total_funding * 100
        ).round(1)

        return tech_agg.sort_values("total_funding", ascending=False)

    def aggregate_by_recipient(self, df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
        """
        Aggregate funding data by recipient.

        Args:
            df: DataFrame with award data
            top_n: Number of top recipients to return

        Returns:
            DataFrame aggregated by recipient
        """
        if df.empty or "recipient_name" not in df.columns:
            return pd.DataFrame()

        recipient_agg = (
            df.groupby("recipient_name")
            .agg(
                {
                    "award_amount": ["sum", "count", "mean"],
                    "state_code": "first",
                    "technology_category": lambda x: x.mode().iloc[0]
                    if not x.empty
                    else "Other",
                }
            )
            .round(2)
        )

        # Flatten column names
        recipient_agg.columns = [
            "total_funding",
            "award_count",
            "avg_award_size",
            "primary_state",
            "primary_technology",
        ]

        recipient_agg = recipient_agg.reset_index()

        # Add recipient type if available
        if "recipient_type" in df.columns:
            recipient_types = df.groupby("recipient_name")["recipient_type"].first()
            recipient_agg = recipient_agg.merge(
                recipient_types.reset_index(), on="recipient_name", how="left"
            )

        return recipient_agg.sort_values("total_funding", ascending=False).head(top_n)

    def create_time_series(
        self, df: pd.DataFrame, date_column: str = "start_date", freq: str = "M"
    ) -> pd.DataFrame:
        """
        Create time series data for trend analysis.

        Args:
            df: DataFrame with award data
            date_column: Column containing dates
            freq: Frequency for grouping (M=monthly, Q=quarterly, Y=yearly)

        Returns:
            DataFrame with time series data
        """
        if df.empty or date_column not in df.columns:
            return pd.DataFrame()

        df_ts = df.copy()
        df_ts = df_ts.dropna(subset=[date_column])

        # Set date as index and resample
        df_ts = df_ts.set_index(date_column)

        time_series = (
            df_ts.resample(freq)
            .agg({"award_amount": ["sum", "count"], "recipient_name": "nunique"})
            .round(2)
        )

        # Flatten column names
        time_series.columns = ["total_funding", "award_count", "unique_recipients"]

        # Add cumulative funding
        time_series["cumulative_funding"] = time_series["total_funding"].cumsum()

        return time_series.reset_index()

    def calculate_growth_rates(
        self, df: pd.DataFrame, value_column: str = "total_funding", periods: int = 1
    ) -> pd.DataFrame:
        """
        Calculate growth rates for time series data.

        Args:
            df: DataFrame with time series data
            value_column: Column to calculate growth for
            periods: Number of periods for growth calculation

        Returns:
            DataFrame with growth rates added
        """
        if df.empty or value_column not in df.columns:
            return df

        df_growth = df.copy()

        # Calculate period-over-period growth
        df_growth[f"{value_column}_growth"] = (
            df_growth[value_column].pct_change(periods=periods) * 100
        )

        # Calculate year-over-year growth if possible
        if len(df_growth) >= 12:
            df_growth[f"{value_column}_yoy_growth"] = (
                df_growth[value_column].pct_change(periods=12) * 100
            )

        return df_growth

    def prepare_for_visualization(
        self, df: pd.DataFrame, viz_type: str = "geographic"
    ) -> Dict[str, Any]:
        """
        Prepare data specifically for visualization components.

        Args:
            df: Processed DataFrame
            viz_type: Type of visualization (geographic, timeline, technology, etc.)

        Returns:
            Dictionary with data formatted for specific visualization
        """
        if df.empty:
            return {}

        if viz_type == "geographic":
            return self._prepare_geographic_viz(df)
        elif viz_type == "timeline":
            return self._prepare_timeline_viz(df)
        elif viz_type == "technology":
            return self._prepare_technology_viz(df)
        elif viz_type == "recipient":
            return self._prepare_recipient_viz(df)
        else:
            return {"data": df.to_dict("records")}

    def _prepare_geographic_viz(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for geographic visualizations."""
        if "state_code" not in df.columns:
            return {}

        state_data = self.aggregate_by_state(df)

        return {
            "state_summary": state_data.to_dict("records"),
            "total_states": len(state_data),
            "top_state": state_data.iloc[0].to_dict() if not state_data.empty else {},
            "geographic_distribution": state_data[
                ["state_code", "total_funding"]
            ].to_dict("records"),
        }

    def _prepare_timeline_viz(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for timeline visualizations."""
        if "start_date" not in df.columns:
            return {}

        monthly_data = self.create_time_series(df, freq="M")
        monthly_data = self.calculate_growth_rates(monthly_data)

        return {
            "monthly_series": monthly_data.to_dict("records"),
            "total_periods": len(monthly_data),
            "peak_month": monthly_data.loc[
                monthly_data["total_funding"].idxmax()
            ].to_dict()
            if not monthly_data.empty
            else {},
            "growth_trend": monthly_data["total_funding_growth"].mean()
            if "total_funding_growth" in monthly_data.columns
            else 0,
        }

    def _prepare_technology_viz(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for technology visualizations."""
        if "technology_category" not in df.columns:
            df = self.categorize_by_technology(df)

        tech_data = self.aggregate_by_technology(df)

        return {
            "technology_breakdown": tech_data.to_dict("records"),
            "total_technologies": len(tech_data),
            "top_technology": tech_data.iloc[0].to_dict()
            if not tech_data.empty
            else {},
            "diversity_index": len(tech_data[tech_data["total_funding"] > 0]),
        }

    def _prepare_recipient_viz(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare data for recipient visualizations."""
        if "recipient_name" not in df.columns:
            return {}

        recipient_data = self.aggregate_by_recipient(df)

        return {
            "top_recipients": recipient_data.to_dict("records"),
            "total_recipients": df["recipient_name"].nunique(),
            "top_recipient": recipient_data.iloc[0].to_dict()
            if not recipient_data.empty
            else {},
            "concentration_ratio": recipient_data.head(10)["total_funding"].sum()
            / df["award_amount"].sum()
            * 100,
        }

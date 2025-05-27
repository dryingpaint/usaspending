#!/usr/bin/env python3
"""
Analytics Engine

Handles advanced analytics operations including statistical analysis,
trend detection, correlation analysis, and insight generation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings("ignore")


class AnalyticsEngine:
    """
    Advanced analytics engine for federal clean energy funding analysis.

    Provides statistical analysis, trend detection, correlation analysis,
    and automated insight generation capabilities.
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def calculate_summary_statistics(
        self, df: pd.DataFrame, value_column: str = "award_amount"
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive summary statistics.

        Args:
            df: DataFrame with data
            value_column: Column to analyze

        Returns:
            Dictionary with summary statistics
        """
        if df.empty or value_column not in df.columns:
            return {}

        values = df[value_column].dropna()

        if len(values) == 0:
            return {}

        stats_dict = {
            "count": len(values),
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "q25": float(values.quantile(0.25)),
            "q75": float(values.quantile(0.75)),
            "skewness": float(values.skew()),
            "kurtosis": float(values.kurtosis()),
            "total": float(values.sum()),
        }

        # Add coefficient of variation
        if stats_dict["mean"] != 0:
            stats_dict["cv"] = stats_dict["std"] / stats_dict["mean"]
        else:
            stats_dict["cv"] = 0

        return stats_dict

    def detect_trends(
        self,
        df: pd.DataFrame,
        date_column: str = "start_date",
        value_column: str = "award_amount",
    ) -> Dict[str, Any]:
        """
        Detect trends in time series data.

        Args:
            df: DataFrame with time series data
            date_column: Column containing dates
            value_column: Column containing values

        Returns:
            Dictionary with trend analysis results
        """
        if df.empty or date_column not in df.columns or value_column not in df.columns:
            return {}

        # Prepare time series data
        df_ts = df.copy()
        df_ts = df_ts.dropna(subset=[date_column, value_column])
        df_ts = df_ts.sort_values(date_column)

        if len(df_ts) < 3:
            return {"trend": "insufficient_data"}

        # Create time index for regression
        df_ts["time_index"] = range(len(df_ts))

        # Linear regression for trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            df_ts["time_index"], df_ts[value_column]
        )

        # Determine trend direction
        if p_value < 0.05:  # Statistically significant
            if slope > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # Calculate trend strength
        trend_strength = abs(r_value)

        # Seasonal analysis (if enough data)
        seasonal_pattern = None
        if len(df_ts) >= 12:
            df_ts["month"] = pd.to_datetime(df_ts[date_column]).dt.month
            monthly_avg = df_ts.groupby("month")[value_column].mean()
            seasonal_pattern = monthly_avg.to_dict()

        return {
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "seasonal_pattern": seasonal_pattern,
            "data_points": len(df_ts),
        }

    def analyze_correlations(
        self,
        df: pd.DataFrame,
        target_column: str = "award_amount",
        feature_columns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze correlations between variables.

        Args:
            df: DataFrame with data
            target_column: Target variable for correlation analysis
            feature_columns: List of feature columns to correlate with target

        Returns:
            Dictionary with correlation analysis results
        """
        if df.empty or target_column not in df.columns:
            return {}

        if feature_columns is None:
            # Auto-select numeric columns
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in numeric_columns if col != target_column]

        correlations = {}

        for col in feature_columns:
            if col in df.columns:
                # Calculate Pearson correlation
                corr_coef, p_value = stats.pearsonr(
                    df[target_column].dropna(), df[col].dropna()
                )

                correlations[col] = {
                    "correlation": float(corr_coef),
                    "p_value": float(p_value),
                    "significance": "significant"
                    if p_value < 0.05
                    else "not_significant",
                }

        # Sort by absolute correlation strength
        sorted_correlations = dict(
            sorted(
                correlations.items(),
                key=lambda x: abs(x[1]["correlation"]),
                reverse=True,
            )
        )

        return {
            "correlations": sorted_correlations,
            "strongest_positive": max(
                correlations.items(), key=lambda x: x[1]["correlation"]
            )[0]
            if correlations
            else None,
            "strongest_negative": min(
                correlations.items(), key=lambda x: x[1]["correlation"]
            )[0]
            if correlations
            else None,
        }

    def compare_periods(
        self,
        df: pd.DataFrame,
        date_column: str = "start_date",
        value_column: str = "award_amount",
        split_date: str = "2022-08-16",
    ) -> Dict[str, Any]:
        """
        Compare metrics between two time periods (e.g., pre/post policy).

        Args:
            df: DataFrame with time series data
            date_column: Column containing dates
            value_column: Column containing values
            split_date: Date to split periods

        Returns:
            Dictionary with period comparison results
        """
        if df.empty or date_column not in df.columns or value_column not in df.columns:
            return {}

        df_comp = df.copy()
        df_comp[date_column] = pd.to_datetime(df_comp[date_column])
        split_date = pd.to_datetime(split_date)

        # Split data into periods
        before = df_comp[df_comp[date_column] < split_date]
        after = df_comp[df_comp[date_column] >= split_date]

        if len(before) == 0 or len(after) == 0:
            return {"error": "insufficient_data_for_comparison"}

        # Calculate statistics for each period
        before_stats = self.calculate_summary_statistics(before, value_column)
        after_stats = self.calculate_summary_statistics(after, value_column)

        # Calculate changes
        changes = {}
        for metric in ["mean", "median", "total", "count"]:
            if metric in before_stats and metric in after_stats:
                if before_stats[metric] != 0:
                    pct_change = (
                        (after_stats[metric] - before_stats[metric])
                        / before_stats[metric]
                    ) * 100
                else:
                    pct_change = 0
                changes[f"{metric}_change_pct"] = float(pct_change)
                changes[f"{metric}_change_abs"] = float(
                    after_stats[metric] - before_stats[metric]
                )

        # Statistical test for difference in means
        if (
            len(before[value_column].dropna()) > 1
            and len(after[value_column].dropna()) > 1
        ):
            t_stat, p_value = stats.ttest_ind(
                before[value_column].dropna(), after[value_column].dropna()
            )
            statistical_test = {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant_difference": p_value < 0.05,
            }
        else:
            statistical_test = None

        return {
            "before_period": before_stats,
            "after_period": after_stats,
            "changes": changes,
            "statistical_test": statistical_test,
            "split_date": split_date.strftime("%Y-%m-%d"),
        }

    def analyze_geographic_patterns(
        self,
        df: pd.DataFrame,
        state_column: str = "state_code",
        value_column: str = "award_amount",
    ) -> Dict[str, Any]:
        """
        Analyze geographic distribution patterns.

        Args:
            df: DataFrame with geographic data
            state_column: Column containing state codes
            value_column: Column containing values

        Returns:
            Dictionary with geographic analysis results
        """
        if df.empty or state_column not in df.columns or value_column not in df.columns:
            return {}

        # Aggregate by state
        state_agg = (
            df.groupby(state_column)[value_column]
            .agg(["sum", "count", "mean"])
            .reset_index()
        )
        state_agg.columns = [
            state_column,
            "total_funding",
            "award_count",
            "avg_award_size",
        ]

        # Calculate concentration metrics
        total_funding = state_agg["total_funding"].sum()
        state_agg["funding_share"] = state_agg["total_funding"] / total_funding * 100

        # Gini coefficient for inequality
        gini_coef = self._calculate_gini_coefficient(state_agg["total_funding"])

        # Top states analysis
        top_5_states = state_agg.nlargest(5, "total_funding")
        top_5_share = top_5_states["total_funding"].sum() / total_funding * 100

        # Geographic diversity
        states_with_funding = len(state_agg[state_agg["total_funding"] > 0])

        return {
            "total_states": len(state_agg),
            "states_with_funding": states_with_funding,
            "gini_coefficient": float(gini_coef),
            "top_5_concentration": float(top_5_share),
            "geographic_distribution": state_agg.to_dict("records"),
            "top_states": top_5_states.to_dict("records"),
        }

    def cluster_recipients(
        self, df: pd.DataFrame, features: List[str] = None, n_clusters: int = 5
    ) -> Dict[str, Any]:
        """
        Perform clustering analysis on recipients.

        Args:
            df: DataFrame with recipient data
            features: List of features for clustering
            n_clusters: Number of clusters

        Returns:
            Dictionary with clustering results
        """
        if df.empty:
            return {}

        if features is None:
            # Default features for clustering
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            features = [col for col in numeric_cols if col in df.columns]

        if not features:
            return {"error": "no_numeric_features_available"}

        # Prepare data for clustering
        cluster_data = df[features].dropna()

        if len(cluster_data) < n_clusters:
            return {"error": "insufficient_data_for_clustering"}

        # Standardize features
        scaled_data = self.scaler.fit_transform(cluster_data)

        # Perform K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(scaled_data)

        # Add cluster labels to original data
        cluster_df = cluster_data.copy()
        cluster_df["cluster"] = cluster_labels

        # Analyze clusters
        cluster_summary = cluster_df.groupby("cluster")[features].mean().round(2)
        cluster_sizes = cluster_df["cluster"].value_counts().sort_index()

        return {
            "n_clusters": n_clusters,
            "cluster_summary": cluster_summary.to_dict("index"),
            "cluster_sizes": cluster_sizes.to_dict(),
            "features_used": features,
            "total_records_clustered": len(cluster_data),
        }

    def generate_insights(
        self, df: pd.DataFrame, analysis_type: str = "comprehensive"
    ) -> List[Dict[str, Any]]:
        """
        Generate automated insights from the data.

        Args:
            df: DataFrame with data
            analysis_type: Type of analysis (comprehensive, trends, geographic, etc.)

        Returns:
            List of insight dictionaries
        """
        insights = []

        if df.empty:
            return insights

        # Basic statistics insights
        if "award_amount" in df.columns:
            stats = self.calculate_summary_statistics(df, "award_amount")

            if stats:
                insights.append(
                    {
                        "type": "summary",
                        "title": "Funding Overview",
                        "description": f"Total funding of ${stats['total']:,.0f} across {stats['count']} awards",
                        "value": stats["total"],
                        "metric": "total_funding",
                    }
                )

                insights.append(
                    {
                        "type": "summary",
                        "title": "Average Award Size",
                        "description": f"Average award size is ${stats['mean']:,.0f}",
                        "value": stats["mean"],
                        "metric": "avg_award_size",
                    }
                )

        # Geographic insights
        if "state_code" in df.columns:
            geo_analysis = self.analyze_geographic_patterns(df)

            if geo_analysis and "top_states" in geo_analysis:
                top_state = (
                    geo_analysis["top_states"][0]
                    if geo_analysis["top_states"]
                    else None
                )
                if top_state:
                    insights.append(
                        {
                            "type": "geographic",
                            "title": "Top State for Funding",
                            "description": f"{top_state['state_code']} leads with ${top_state['total_funding']:,.0f}",
                            "value": top_state["total_funding"],
                            "metric": "state_funding",
                        }
                    )

        # Technology insights
        if "technology_category" in df.columns:
            tech_summary = (
                df.groupby("technology_category")["award_amount"]
                .sum()
                .sort_values(ascending=False)
            )
            if not tech_summary.empty:
                top_tech = tech_summary.index[0]
                top_tech_value = tech_summary.iloc[0]

                insights.append(
                    {
                        "type": "technology",
                        "title": "Leading Technology",
                        "description": f"{top_tech} receives the most funding with ${top_tech_value:,.0f}",
                        "value": top_tech_value,
                        "metric": "technology_funding",
                    }
                )

        # Trend insights
        if "start_date" in df.columns:
            trend_analysis = self.detect_trends(df)

            if trend_analysis and "trend_direction" in trend_analysis:
                insights.append(
                    {
                        "type": "trend",
                        "title": "Funding Trend",
                        "description": f"Funding is {trend_analysis['trend_direction']} over time",
                        "value": trend_analysis["trend_strength"],
                        "metric": "trend_strength",
                    }
                )

        return insights

    def _calculate_gini_coefficient(self, values: pd.Series) -> float:
        """Calculate Gini coefficient for inequality measurement."""
        values = values.sort_values()
        n = len(values)
        cumsum = values.cumsum()
        return (n + 1 - 2 * cumsum.sum() / values.sum()) / n

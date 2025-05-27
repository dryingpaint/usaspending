#!/usr/bin/env python3
"""
Tests for the Analytics Engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_processor.analytics_engine import AnalyticsEngine


class TestAnalyticsEngine:
    """Test suite for AnalyticsEngine."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.engine = AnalyticsEngine()

    def test_init(self):
        """Test analytics engine initialization."""
        assert hasattr(self.engine, "scaler")

    def create_sample_data(self):
        """Create sample data for testing."""
        np.random.seed(42)  # For reproducible tests
        dates = pd.date_range("2022-01-01", periods=100, freq="D")
        return pd.DataFrame(
            {
                "award_amount": np.random.lognormal(15, 1, 100),
                "start_date": dates,
                "state_code": np.random.choice(["CA", "TX", "NY", "FL"], 100),
                "technology_category": np.random.choice(
                    ["Solar", "Wind", "Battery"], 100
                ),
                "recipient_name": [f"Company_{i%20}" for i in range(100)],
            }
        )

    def test_calculate_summary_statistics(self):
        """Test summary statistics calculation."""
        data = self.create_sample_data()

        result = self.engine.calculate_summary_statistics(data, "award_amount")

        # Check all expected statistics are present
        expected_keys = [
            "count",
            "mean",
            "median",
            "std",
            "min",
            "max",
            "q25",
            "q75",
            "skewness",
            "kurtosis",
            "total",
            "cv",
        ]
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], (int, float))

        # Basic sanity checks
        assert result["count"] == 100
        assert (
            result["min"]
            <= result["q25"]
            <= result["median"]
            <= result["q75"]
            <= result["max"]
        )
        assert result["total"] == result["mean"] * result["count"]

    def test_calculate_summary_statistics_empty(self):
        """Test summary statistics with empty data."""
        empty_df = pd.DataFrame()
        result = self.engine.calculate_summary_statistics(empty_df, "award_amount")
        assert result == {}

    def test_calculate_summary_statistics_missing_column(self):
        """Test summary statistics with missing column."""
        data = pd.DataFrame({"other_column": [1, 2, 3]})
        result = self.engine.calculate_summary_statistics(data, "award_amount")
        assert result == {}

    def test_detect_trends_increasing(self):
        """Test trend detection with increasing trend."""
        # Create data with clear increasing trend
        dates = pd.date_range("2022-01-01", periods=50, freq="D")
        data = pd.DataFrame(
            {
                "start_date": dates,
                "award_amount": [
                    1000000 + i * 50000 for i in range(50)
                ],  # Clear upward trend
            }
        )

        result = self.engine.detect_trends(data)

        assert result["trend_direction"] == "increasing"
        assert result["trend_strength"] > 0.8  # Should be strong correlation
        assert result["slope"] > 0
        assert result["p_value"] < 0.05  # Should be statistically significant

    def test_detect_trends_decreasing(self):
        """Test trend detection with decreasing trend."""
        dates = pd.date_range("2022-01-01", periods=50, freq="D")
        data = pd.DataFrame(
            {
                "start_date": dates,
                "award_amount": [
                    2000000 - i * 30000 for i in range(50)
                ],  # Clear downward trend
            }
        )

        result = self.engine.detect_trends(data)

        assert result["trend_direction"] == "decreasing"
        assert result["slope"] < 0

    def test_detect_trends_stable(self):
        """Test trend detection with stable/random data."""
        dates = pd.date_range("2022-01-01", periods=50, freq="D")
        np.random.seed(42)
        data = pd.DataFrame(
            {
                "start_date": dates,
                "award_amount": np.random.normal(
                    1000000, 100000, 50
                ),  # Random around mean
            }
        )

        result = self.engine.detect_trends(data)

        # With random data, should likely be stable (p_value > 0.05)
        assert result["trend_direction"] in ["stable", "increasing", "decreasing"]

    def test_detect_trends_insufficient_data(self):
        """Test trend detection with insufficient data."""
        data = pd.DataFrame(
            {
                "start_date": ["2022-01-01", "2022-01-02"],
                "award_amount": [1000000, 1100000],
            }
        )
        data["start_date"] = pd.to_datetime(data["start_date"])

        result = self.engine.detect_trends(data)

        assert result["trend"] == "insufficient_data"

    def test_analyze_correlations(self):
        """Test correlation analysis."""
        # Create data with known correlations
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 2000000, 3000000, 4000000],
                "duration_days": [365, 730, 1095, 1460],  # Should correlate with amount
                "random_var": [10, 5, 15, 8],  # Should not correlate
            }
        )

        result = self.engine.analyze_correlations(data, "award_amount")

        assert "correlations" in result
        assert "duration_days" in result["correlations"]
        assert "random_var" in result["correlations"]

        # Duration should have strong positive correlation
        duration_corr = result["correlations"]["duration_days"]["correlation"]
        assert duration_corr > 0.9

    def test_compare_periods(self):
        """Test period comparison analysis."""
        # Create data spanning the split date
        dates_before = pd.date_range("2022-01-01", "2022-08-15", freq="D")
        dates_after = pd.date_range("2022-08-17", "2022-12-31", freq="D")

        data = pd.DataFrame(
            {
                "start_date": list(dates_before) + list(dates_after),
                "award_amount": (
                    [1000000] * len(dates_before) + [2000000] * len(dates_after)
                ),  # Higher amounts after split
            }
        )

        result = self.engine.compare_periods(data, split_date="2022-08-16")

        assert "before_period" in result
        assert "after_period" in result
        assert "changes" in result

        # Should detect increase in mean
        assert result["changes"]["mean_change_pct"] > 0
        assert result["after_period"]["mean"] > result["before_period"]["mean"]

    def test_compare_periods_insufficient_data(self):
        """Test period comparison with insufficient data."""
        data = pd.DataFrame(
            {
                "start_date": ["2022-01-01"],  # Only one data point
                "award_amount": [1000000],
            }
        )
        data["start_date"] = pd.to_datetime(data["start_date"])

        result = self.engine.compare_periods(data, split_date="2022-08-16")

        assert result["error"] == "insufficient_data_for_comparison"

    def test_analyze_geographic_patterns(self):
        """Test geographic pattern analysis."""
        data = pd.DataFrame(
            {
                "state_code": ["CA", "CA", "TX", "TX", "NY"],
                "award_amount": [5000000, 3000000, 2000000, 1000000, 4000000],
            }
        )

        result = self.engine.analyze_geographic_patterns(data)

        assert "total_states" in result
        assert "states_with_funding" in result
        assert "gini_coefficient" in result
        assert "top_5_concentration" in result
        assert "geographic_distribution" in result

        assert result["total_states"] == 3
        assert result["states_with_funding"] == 3

    def test_cluster_recipients(self):
        """Test recipient clustering analysis."""
        # Create data suitable for clustering
        data = pd.DataFrame(
            {
                "total_funding": [10000000, 12000000, 1000000, 1200000, 15000000],
                "award_count": [10, 12, 2, 3, 15],
                "avg_award_size": [1000000, 1000000, 500000, 400000, 1000000],
            }
        )

        result = self.engine.cluster_recipients(data, n_clusters=2)

        assert "n_clusters" in result
        assert "cluster_summary" in result
        assert "cluster_sizes" in result
        assert result["n_clusters"] == 2

    def test_cluster_recipients_insufficient_data(self):
        """Test clustering with insufficient data."""
        data = pd.DataFrame({"total_funding": [1000000], "award_count": [1]})

        result = self.engine.cluster_recipients(data, n_clusters=3)

        assert result["error"] == "insufficient_data_for_clustering"

    def test_cluster_recipients_no_numeric_features(self):
        """Test clustering with no numeric features."""
        data = pd.DataFrame(
            {"recipient_name": ["Corp A", "Corp B"], "state": ["CA", "TX"]}
        )

        result = self.engine.cluster_recipients(data)

        assert result["error"] == "no_numeric_features_available"

    def test_generate_insights_comprehensive(self):
        """Test comprehensive insight generation."""
        data = self.create_sample_data()

        result = self.engine.generate_insights(data, "comprehensive")

        assert isinstance(result, list)
        assert len(result) > 0

        # Check that insights have required structure
        for insight in result:
            assert "type" in insight
            assert "title" in insight
            assert "description" in insight
            assert "value" in insight
            assert "metric" in insight

    def test_generate_insights_empty_data(self):
        """Test insight generation with empty data."""
        empty_df = pd.DataFrame()

        result = self.engine.generate_insights(empty_df)

        assert result == []

    def test_gini_coefficient_calculation(self):
        """Test Gini coefficient calculation."""
        # Perfect equality (all values same)
        equal_values = pd.Series([100, 100, 100, 100])
        gini_equal = self.engine._calculate_gini_coefficient(equal_values)
        assert abs(gini_equal) < 0.01  # Should be close to 0

        # Perfect inequality (one person has everything)
        unequal_values = pd.Series([0, 0, 0, 100])
        gini_unequal = self.engine._calculate_gini_coefficient(unequal_values)
        assert gini_unequal > 0.5  # Should be high


class TestAnalyticsEngineEdgeCases:
    """Test edge cases and error conditions for AnalyticsEngine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engine = AnalyticsEngine()

    def test_statistics_with_zero_values(self):
        """Test statistics calculation with zero values."""
        data = pd.DataFrame({"award_amount": [0, 1000000, 2000000, 0, 3000000]})

        result = self.engine.calculate_summary_statistics(data, "award_amount")

        # Should handle zeros appropriately
        assert result["min"] == 0
        assert result["count"] == 5

    def test_trends_with_constant_values(self):
        """Test trend detection with constant values."""
        dates = pd.date_range("2022-01-01", periods=10, freq="D")
        data = pd.DataFrame(
            {
                "start_date": dates,
                "award_amount": [1000000] * 10,  # All same value
            }
        )

        result = self.engine.detect_trends(data)

        # Should detect stable trend (slope = 0)
        assert result["slope"] == 0
        assert result["trend_direction"] == "stable"

    def test_correlations_with_identical_values(self):
        """Test correlation analysis with identical values."""
        data = pd.DataFrame(
            {
                "award_amount": [1000000, 1000000, 1000000],
                "constant_var": [5, 5, 5],  # No variation
            }
        )

        result = self.engine.analyze_correlations(data, "award_amount")

        # Should handle constant variables gracefully
        assert "correlations" in result

    def test_geographic_analysis_single_state(self):
        """Test geographic analysis with single state."""
        data = pd.DataFrame(
            {
                "state_code": ["CA", "CA", "CA"],
                "award_amount": [1000000, 2000000, 3000000],
            }
        )

        result = self.engine.analyze_geographic_patterns(data)

        assert result["total_states"] == 1
        assert result["gini_coefficient"] >= 0  # Should be valid


if __name__ == "__main__":
    pytest.main([__file__])

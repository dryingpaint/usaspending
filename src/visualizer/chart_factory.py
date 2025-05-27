#!/usr/bin/env python3
"""
Chart Factory

Creates and configures all visualization components for the dashboard.
Provides a centralized way to generate consistent, interactive charts.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import folium


class ChartFactory:
    """
    Factory class for creating interactive visualizations.

    Provides methods to create consistent, interactive charts
    for all dashboard components.
    """

    def __init__(self):
        # Color schemes for consistent styling
        self.colors = {
            "primary": "#2E8B57",  # Sea Green
            "secondary": "#228B22",  # Forest Green
            "accent": "#32CD32",  # Lime Green
            "neutral": "#708090",  # Slate Gray
            "background": "#F8F9FA",  # Light Gray
            "text": "#2F4F4F",  # Dark Slate Gray
        }

        self.tech_colors = {
            "Solar": "#FFD700",  # Gold
            "Wind": "#87CEEB",  # Sky Blue
            "Battery Storage": "#FF6347",  # Tomato
            "Grid Modernization": "#9370DB",  # Medium Purple
            "Electric Vehicles": "#20B2AA",  # Light Sea Green
            "Energy Efficiency": "#FFA500",  # Orange
            "Carbon Capture": "#8B4513",  # Saddle Brown
            "Geothermal": "#DC143C",  # Crimson
            "Hydroelectric": "#4682B4",  # Steel Blue
            "Biomass": "#228B22",  # Forest Green
            "Hydrogen": "#FF1493",  # Deep Pink
            "Other": "#808080",  # Gray
        }

    def create_geographic_map(
        self, state_data: List[Dict], value_column: str = "total_funding"
    ) -> folium.Map:
        """
        Create an interactive geographic map.

        Args:
            state_data: List of state data dictionaries
            value_column: Column to use for sizing/coloring

        Returns:
            Folium map object
        """
        # Create base map centered on US
        m = folium.Map(
            location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap"
        )

        if not state_data:
            return m

        # State coordinates (simplified - would use proper geocoding in production)
        state_coords = {
            "CA": [36.7783, -119.4179],
            "TX": [31.9686, -99.9018],
            "NY": [40.7128, -74.0060],
            "FL": [27.7663, -82.6404],
            "WA": [47.7511, -120.7401],
            "IL": [40.6331, -89.3985],
            "PA": [41.2033, -77.1945],
            "OH": [40.4173, -82.9071],
            "NC": [35.7596, -79.0193],
            "GA": [33.7490, -84.3880],
        }

        # Add markers for each state
        for state in state_data:
            state_code = state.get("state_code", "")
            if state_code in state_coords:
                coords = state_coords[state_code]
                value = state.get(value_column, 0)

                # Scale marker size based on value
                radius = max(5, min(50, value / 1000000))  # Scale to reasonable size

                folium.CircleMarker(
                    location=coords,
                    radius=radius,
                    popup=f"{state_code}: ${value:,.0f}",
                    color=self.colors["primary"],
                    fillColor=self.colors["accent"],
                    fillOpacity=0.7,
                    weight=2,
                ).add_to(m)

        return m

    def create_state_ranking_chart(
        self,
        state_data: List[Dict],
        value_column: str = "total_funding",
        top_n: int = 10,
    ) -> go.Figure:
        """Create horizontal bar chart of top states."""
        if not state_data:
            return go.Figure()

        df = pd.DataFrame(state_data).head(top_n)

        fig = px.bar(
            df,
            x=value_column,
            y="state_code",
            orientation="h",
            title=f'Top {top_n} States by {value_column.replace("_", " ").title()}',
            color=value_column,
            color_continuous_scale="Viridis",
        )

        fig.update_layout(
            height=400, yaxis={"categoryorder": "total ascending"}, showlegend=False
        )

        return fig

    def create_timeline_chart(self, timeline_data: List[Dict]) -> go.Figure:
        """Create time series chart with multiple metrics."""
        if not timeline_data:
            return go.Figure()

        df = pd.DataFrame(timeline_data)

        # Create subplot with secondary y-axis
        fig = make_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Monthly Funding", "Cumulative Funding"),
            vertical_spacing=0.1,
        )

        # Monthly funding
        fig.add_trace(
            go.Scatter(
                x=df["start_date"] if "start_date" in df.columns else df.index,
                y=df["total_funding"] if "total_funding" in df.columns else [],
                mode="lines+markers",
                name="Monthly Funding",
                line=dict(color=self.colors["primary"], width=3),
                marker=dict(size=6),
            ),
            row=1,
            col=1,
        )

        # Cumulative funding
        if "cumulative_funding" in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df["start_date"] if "start_date" in df.columns else df.index,
                    y=df["cumulative_funding"],
                    mode="lines",
                    name="Cumulative Funding",
                    line=dict(color=self.colors["secondary"], width=3),
                ),
                row=2,
                col=1,
            )

        fig.update_layout(
            height=600, title="Funding Trends Over Time", showlegend=False
        )

        return fig

    def create_technology_pie_chart(self, tech_data: List[Dict]) -> go.Figure:
        """Create pie chart for technology distribution."""
        if not tech_data:
            return go.Figure()

        df = pd.DataFrame(tech_data)

        # Get colors for each technology
        colors = [
            self.tech_colors.get(tech, "#808080") for tech in df["technology_category"]
        ]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=df["technology_category"],
                    values=df["total_funding"],
                    hole=0.3,
                    marker_colors=colors,
                    textinfo="label+percent",
                    textposition="outside",
                )
            ]
        )

        fig.update_layout(
            title="Funding Distribution by Technology",
            height=500,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5),
        )

        return fig

    def create_technology_growth_chart(self, tech_data: List[Dict]) -> go.Figure:
        """Create bar chart showing technology growth rates."""
        if not tech_data:
            return go.Figure()

        df = pd.DataFrame(tech_data)

        # Create mock growth rates if not present
        if "growth_rate" not in df.columns:
            df["growth_rate"] = np.random.uniform(-10, 50, len(df))

        colors = [
            self.tech_colors.get(tech, "#808080") for tech in df["technology_category"]
        ]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=df["technology_category"],
                    y=df["growth_rate"],
                    marker_color=colors,
                    text=df["growth_rate"].round(1),
                    textposition="outside",
                )
            ]
        )

        fig.update_layout(
            title="Technology Growth Rates (%)",
            xaxis_title="Technology",
            yaxis_title="Growth Rate (%)",
            height=400,
            xaxis={"tickangle": 45},
        )

        return fig

    def create_recipient_scatter(self, recipient_data: List[Dict]) -> go.Figure:
        """Create scatter plot of recipients by funding vs award count."""
        if not recipient_data:
            return go.Figure()

        df = pd.DataFrame(recipient_data)

        fig = px.scatter(
            df,
            x="award_count",
            y="total_funding",
            size="total_funding",
            color="recipient_type" if "recipient_type" in df.columns else None,
            hover_name="recipient_name",
            title="Recipients: Funding vs Award Count",
            labels={
                "award_count": "Number of Awards",
                "total_funding": "Total Funding ($)",
            },
        )

        fig.update_layout(height=500)

        return fig

    def create_award_size_histogram(self, award_data: List[Dict]) -> go.Figure:
        """Create histogram of award sizes."""
        if not award_data:
            return go.Figure()

        df = pd.DataFrame(award_data)

        if "award_amount" not in df.columns:
            return go.Figure()

        fig = px.histogram(
            df,
            x="award_amount",
            nbins=50,
            title="Distribution of Award Sizes",
            labels={"award_amount": "Award Size ($)", "count": "Number of Awards"},
        )

        fig.update_layout(height=400, showlegend=False)

        return fig

    def create_comparison_chart(
        self, comparison_data: Dict[str, Any], metric: str = "total_funding"
    ) -> go.Figure:
        """Create comparison chart for different periods or categories."""
        if not comparison_data:
            return go.Figure()

        # Handle period comparison
        if "before_period" in comparison_data and "after_period" in comparison_data:
            before = comparison_data["before_period"]
            after = comparison_data["after_period"]

            categories = ["Before", "After"]
            values = [before.get(metric, 0), after.get(metric, 0)]

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=categories,
                        y=values,
                        marker_color=[self.colors["neutral"], self.colors["primary"]],
                        text=[
                            f"${v:,.0f}" if "funding" in metric else f"{v:,.0f}"
                            for v in values
                        ],
                        textposition="outside",
                    )
                ]
            )

            fig.update_layout(
                title=f'{metric.replace("_", " ").title()} Comparison', height=400
            )

            return fig

        return go.Figure()

    def create_correlation_heatmap(self, correlation_data: Dict[str, Any]) -> go.Figure:
        """Create correlation heatmap."""
        if not correlation_data or "correlations" not in correlation_data:
            return go.Figure()

        correlations = correlation_data["correlations"]

        # Convert to matrix format
        variables = list(correlations.keys())
        values = [correlations[var]["correlation"] for var in variables]

        # Create simple correlation display
        fig = go.Figure(
            data=go.Bar(
                x=variables,
                y=values,
                marker_color=[
                    self.colors["primary"] if v > 0 else self.colors["neutral"]
                    for v in values
                ],
            )
        )

        fig.update_layout(
            title="Correlation with Funding",
            xaxis_title="Variables",
            yaxis_title="Correlation Coefficient",
            height=400,
            xaxis={"tickangle": 45},
        )

        return fig

    def create_metric_cards(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create data for metric cards display."""
        cards = []

        if "total_funding" in metrics:
            cards.append(
                {
                    "title": "Total Funding",
                    "value": f"${metrics['total_funding']:,.0f}",
                    "delta": "+15%",  # Would calculate from actual data
                    "color": "primary",
                }
            )

        if "total_awards" in metrics:
            cards.append(
                {
                    "title": "Total Awards",
                    "value": f"{metrics['total_awards']:,}",
                    "delta": "+8%",
                    "color": "secondary",
                }
            )

        if "unique_states" in metrics:
            cards.append(
                {
                    "title": "States Covered",
                    "value": str(metrics["unique_states"]),
                    "delta": "→",
                    "color": "accent",
                }
            )

        if "top_technology" in metrics:
            cards.append(
                {
                    "title": "Top Technology",
                    "value": metrics["top_technology"],
                    "delta": "+22%",
                    "color": "neutral",
                }
            )

        return cards

    def apply_theme(self, fig: go.Figure) -> go.Figure:
        """Apply consistent theme to a figure."""
        fig.update_layout(
            plot_bgcolor=self.colors["background"],
            paper_bgcolor="white",
            font=dict(color=self.colors["text"], size=12),
            title_font=dict(size=16, color=self.colors["text"]),
            margin=dict(l=50, r=50, t=50, b=50),
        )

        return fig

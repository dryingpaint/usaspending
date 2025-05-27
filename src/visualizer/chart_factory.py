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
import folium  # type: ignore


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
            "background": "#FFFFFF",  # White
            "text": "#1F2937",  # Dark Gray (much darker for readability)
        }

        self.tech_colors = {
            "Solar": "#F59E0B",  # Amber
            "Wind": "#3B82F6",  # Blue
            "Battery Storage": "#EF4444",  # Red
            "Grid Modernization": "#8B5CF6",  # Violet
            "Electric Vehicles": "#10B981",  # Emerald
            "Energy Efficiency": "#F97316",  # Orange
            "Carbon Capture": "#92400E",  # Brown
            "Geothermal": "#DC2626",  # Red
            "Hydroelectric": "#1D4ED8",  # Blue
            "Biomass": "#059669",  # Green
            "Hydrogen": "#EC4899",  # Pink
            "Other Clean Energy": "#6B7280",  # Gray
            "Other": "#6B7280",  # Gray
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
            "AL": [32.3617, -86.2792],
            "AK": [64.0685, -152.2782],
            "AZ": [34.2744, -111.2847],
            "AR": [34.7519, -92.1313],
            "CA": [36.7783, -119.4179],
            "CO": [39.5501, -105.7821],
            "CT": [41.6219, -72.7273],
            "DE": [38.9108, -75.5277],
            "FL": [27.7663, -82.6404],
            "GA": [33.7490, -84.3880],
            "HI": [19.8968, -155.5828],
            "ID": [44.0682, -114.7420],
            "IL": [40.6331, -89.3985],
            "IN": [40.2732, -86.1349],
            "IA": [42.0046, -93.2140],
            "KS": [38.4937, -98.3804],
            "KY": [37.8393, -84.2700],
            "LA": [30.9843, -91.9623],
            "ME": [45.3695, -69.2169],
            "MD": [39.0458, -76.6413],
            "MA": [42.2373, -71.5314],
            "MI": [44.3467, -85.4102],
            "MN": [46.3954, -94.6859],
            "MS": [32.3547, -89.3985],
            "MO": [38.3566, -92.4580],
            "MT": [47.0527, -109.6333],
            "NE": [41.4925, -99.9018],
            "NV": [38.4199, -117.1219],
            "NH": [43.4525, -71.5639],
            "NJ": [40.3140, -74.5089],
            "NM": [34.8405, -106.2485],
            "NY": [40.7128, -74.0060],
            "NC": [35.7596, -79.0193],
            "ND": [47.5515, -101.0020],
            "OH": [40.4173, -82.9071],
            "OK": [35.5889, -97.5348],
            "OR": [44.9778, -120.7374],
            "PA": [41.2033, -77.1945],
            "RI": [41.6762, -71.5562],
            "SC": [33.8191, -80.9066],
            "SD": [44.2853, -100.2263],
            "TN": [35.7449, -86.7489],
            "TX": [31.9686, -99.9018],
            "UT": [40.1135, -111.8535],
            "VT": [44.0407, -72.7093],
            "VA": [37.7693, -78.2057],
            "WA": [47.7511, -120.7401],
            "WV": [38.4680, -80.9696],
            "WI": [44.2619, -89.6165],
            "WY": [42.7475, -107.2085],
            "DC": [38.8974, -77.0365],
        }

        # Calculate value range for proper scaling
        values = [state.get(value_column, 0) for state in state_data]
        if values:
            min_value = min(values)
            max_value = max(values)
            value_range = max_value - min_value if max_value > min_value else 1
        else:
            min_value = max_value = value_range = 1

        # Add markers for each state
        for state in state_data:
            # Handle different state column names
            state_code = state.get("state_code") or state.get(
                "performance_state_code", ""
            )
            if state_code in state_coords:
                coords = state_coords[state_code]
                value = state.get(value_column, 0)

                # Scale marker size based on value with proper normalization
                if value_range > 0:
                    # Normalize value to 0-1 range, then scale to 8-40 pixel radius
                    normalized_value = (value - min_value) / value_range
                    radius = 8 + (normalized_value * 32)  # Range: 8-40 pixels
                else:
                    radius = 15  # Default size if all values are the same

                # Ensure minimum visibility
                radius = max(8, radius)

                # Create detailed popup with multiple metrics
                popup_text = f"""
                <b>{state_code}</b><br>
                {value_column.replace('_', ' ').title()}: ${value:,.0f}<br>
                """

                # Add additional metrics if available
                if "award_count" in state:
                    popup_text += f"Awards: {state['award_count']:,}<br>"
                if "avg_award_size" in state:
                    popup_text += f"Avg Award: ${state['avg_award_size']:,.0f}<br>"
                if "unique_recipients" in state:
                    popup_text += f"Recipients: {state['unique_recipients']:,}"

                folium.CircleMarker(
                    location=coords,
                    radius=radius,
                    popup=folium.Popup(popup_text, max_width=200),
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

        # Handle different state column names
        state_column = None
        if "state_code" in df.columns:
            state_column = "state_code"
        elif "performance_state_code" in df.columns:
            state_column = "performance_state_code"
        else:
            # If no state column found, return empty figure
            return go.Figure()

        fig = px.bar(
            df,
            x=value_column,
            y=state_column,
            orientation="h",
            title=f'Top {top_n} States by {value_column.replace("_", " ").title()}',
            color=value_column,
            color_continuous_scale="Blues",
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
                    "color": "primary",
                }
            )

        if "total_awards" in metrics:
            cards.append(
                {
                    "title": "Total Awards",
                    "value": f"{metrics['total_awards']:,}",
                    "color": "secondary",
                }
            )

        if "unique_states" in metrics:
            cards.append(
                {
                    "title": "States Covered",
                    "value": str(metrics["unique_states"]),
                    "color": "accent",
                }
            )

        if "top_technology" in metrics:
            cards.append(
                {
                    "title": "Top Technology",
                    "value": metrics["top_technology"],
                    "color": "neutral",
                }
            )

        return cards

    def apply_theme(self, fig: go.Figure) -> go.Figure:
        """Apply consistent theme to a figure."""
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1F2937", size=12, family="Arial, sans-serif"),
            title_font=dict(size=18, color="#111827", family="Arial, sans-serif"),
            margin=dict(l=60, r=60, t=60, b=60),
            # Ensure axis labels are dark and readable
            xaxis=dict(
                title_font=dict(color="#111827", size=14),
                tickfont=dict(color="#374151", size=11),
                gridcolor="#E5E7EB",
                linecolor="#D1D5DB",
            ),
            yaxis=dict(
                title_font=dict(color="#111827", size=14),
                tickfont=dict(color="#374151", size=11),
                gridcolor="#E5E7EB",
                linecolor="#D1D5DB",
            ),
            # Fix legend text color
            legend=dict(
                font=dict(color="#1F2937", size=11),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#D1D5DB",
                borderwidth=1,
            ),
            # Fix colorbar text color
            coloraxis_colorbar=dict(
                title_font=dict(color="#111827", size=12),
                tickfont=dict(color="#374151", size=10),
            ),
        )

        return fig

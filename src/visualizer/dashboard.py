#!/usr/bin/env python3
"""
Federal Clean Energy Funding Dashboard

An intuitive interface for exploring and visualizing federal clean energy funding data
from the USASpending API. This dashboard provides multiple interconnected views for
comprehensive analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.visualizer.cached_data_connector import CachedDataConnector as DataConnector
from src.visualizer.chart_factory import ChartFactory
from streamlit_folium import st_folium  # type: ignore


class CleanEnergyDashboard:
    """Main dashboard class for federal clean energy funding visualization."""

    def __init__(self):
        # Store data connector in session state to persist across reruns
        if "data_connector" not in st.session_state:
            st.session_state.data_connector = DataConnector()

        self.data_connector = st.session_state.data_connector
        self.chart_factory = ChartFactory()
        self.setup_page_config()

        # Auto-load data on initialization if not already loaded
        if not self._has_data_loaded():
            # Use the current time period from session state if available
            initial_period = st.session_state.get(
                "current_time_period", "ira_chips_period"
            )
            self._auto_load_data(initial_period)

    def setup_page_config(self):
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="Federal Clean Energy Funding Dashboard",
            page_icon="🌱",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def _has_data_loaded(self) -> bool:
        """Check if data is already loaded."""
        data_info = self.data_connector.get_data_info()
        return data_info.get("status") in ["data_loaded", "cached_data_loaded"]

    def _auto_load_data(self, time_period: str = "ira_chips_period"):
        """Automatically load default data on startup."""
        try:
            success = self.data_connector.load_data(
                time_period=time_period,
                max_pages=5,
                force_refresh=False,
            )
            if success:
                print(f"✅ Auto-loaded data successfully for period: {time_period}")
            else:
                print(f"⚠️ Failed to auto-load data for period: {time_period}")
        except Exception as e:
            print(f"❌ Error auto-loading data: {e}")

    def run(self):
        """Main dashboard execution."""
        self.render_header()
        self.render_sidebar()
        self.render_main_content()

    def render_header(self):
        """Render dashboard header with title and key metrics."""
        st.title("🌱 Federal Clean Energy Funding Dashboard")
        st.markdown("""
        Explore federal investments in clean energy across states, time periods, and technologies.
        Data sourced from USASpending.gov API covering major legislation including IRA, CHIPS Act, and IIJA.
        """)

        # Get summary metrics
        metrics = self.data_connector.get_summary_metrics()

        # Create metric cards
        metric_cards = self.chart_factory.create_metric_cards(metrics)

        # Display metrics in columns
        cols = st.columns(len(metric_cards))
        for i, card in enumerate(metric_cards):
            with cols[i]:
                st.metric(card["title"], card["value"], card.get("delta", ""))

    def render_sidebar(self):
        """Render sidebar with filters and controls."""
        st.sidebar.header("🔍 Filters & Controls")

        # Time period selection
        st.sidebar.subheader("Time Period")
        time_options = {
            "IRA/CHIPS Era (2022-2024)": "ira_chips_period",
            "Post-ARRA Pre-IRA (2010-2022)": "post_arra_pre_ira",
            "ARRA Period (2009-2010)": "arra_period",
            "Pre-ARRA (2008 and earlier)": "pre_arra",
            "Full Period (All Years)": "full_period",
            "Custom Range": "custom",
        }

        selected_period = st.sidebar.selectbox(
            "Select Time Period", options=list(time_options.keys()), index=0
        )

        if selected_period == "Custom Range":
            start_date = st.sidebar.date_input("Start Date", datetime(2020, 1, 1))
            end_date = st.sidebar.date_input("End Date", datetime.now())

        # Auto-reload data when time period changes
        current_time_period = (
            time_options[selected_period]
            if selected_period != "Custom Range"
            else "custom"
        )

        # Simple time period management - just load data when period changes
        if "current_time_period" not in st.session_state:
            st.session_state.current_time_period = current_time_period
        elif st.session_state.current_time_period != current_time_period:
            st.session_state.current_time_period = current_time_period
            # Load data for the new time period
            self.data_connector.load_data(
                time_period=current_time_period,
                max_pages=5,
                force_refresh=False,
            )

        # Data loading controls
        st.sidebar.subheader("Data Management")

        # Data info
        data_info = self.data_connector.get_data_info()
        if data_info.get("status") in ["data_loaded", "cached_data_loaded"]:
            st.sidebar.success(
                f"✅ Data loaded: {data_info['total_records']:,} records"
            )
            st.sidebar.info(f"💾 Memory: {data_info['memory_usage']}")
            st.sidebar.info(
                f"📅 Current period: {data_info.get('current_time_period', 'Unknown')}"
            )
            if data_info.get("data_source") == "consolidated_cache":
                st.sidebar.info("🚀 Using cached data (fast mode)")
        elif data_info.get("status") == "no_data_loaded":
            st.sidebar.warning("⚠️ Loading data automatically...")
        elif data_info.get("status") == "empty_dataset":
            st.sidebar.error("❌ Dataset is empty")

        # Export options
        st.sidebar.subheader("Export")
        if st.sidebar.button("📊 Export Data"):
            export_path = self.data_connector.export_current_data()
            if export_path:
                st.sidebar.success(f"Data exported to {export_path}")
            else:
                st.sidebar.error("No data to export")

    def render_main_content(self):
        """Render main dashboard content with multiple tabs."""
        tab1, tab3, tab4, tab5 = st.tabs(
            [
                "🗺️ Geographic Overview",
                # "📈 Trends & Timeline",
                "🏢 Recipients & Awards",
                "🔬 Technology Analysis",
                "📊 Comparative Analysis",
            ]
        )

        with tab1:
            self.render_geographic_view()

        # with tab2:
        #     self.render_trends_view()

        with tab3:
            self.render_recipients_view()

        with tab4:
            self.render_technology_view()

        with tab5:
            self.render_comparative_view()

    def render_geographic_view(self):
        """Render geographic visualization tab."""
        st.header("🗺️ Geographic Distribution of Clean Energy Funding")

        # Get geographic data
        geo_data = self.data_connector.get_geographic_data()

        if not geo_data:
            st.warning("No geographic data available. Please load data first.")
            return

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Interactive Map")

            if "state_summary" in geo_data:
                # Create map using chart factory
                map_obj = self.chart_factory.create_geographic_map(
                    geo_data["state_summary"]  # type: ignore
                )
                map_data = st_folium(map_obj, width=700, height=500)
            else:
                st.info(
                    "Map visualization requires folium. Showing data table instead."
                )
                if "state_summary" in geo_data:
                    st.dataframe(pd.DataFrame(geo_data["state_summary"]))

        with col2:
            st.subheader("State Rankings")

            if "state_summary" in geo_data:
                # Create state ranking chart
                ranking_chart = self.chart_factory.create_state_ranking_chart(
                    geo_data["state_summary"]
                )
                ranking_chart = self.chart_factory.apply_theme(ranking_chart)
                st.plotly_chart(ranking_chart, use_container_width=True)

        # Geographic insights
        if "insights" in geo_data:
            st.subheader("Geographic Insights")
            for insight in geo_data["insights"]:
                if insight.get("type") == "geographic":
                    st.info(f"💡 {insight['description']}")

    def render_trends_view(self):
        """Render trends and timeline visualization."""
        st.header("📈 Funding Trends & Timeline Analysis")

        # Get timeline data
        timeline_data = self.data_connector.get_timeline_data()

        if not timeline_data:
            st.warning("No timeline data available. Please load data first.")
            return

        # Time series chart
        st.subheader("Funding Over Time")

        if "monthly_series" in timeline_data:
            timeline_chart = self.chart_factory.create_timeline_chart(
                timeline_data["monthly_series"]
            )
            timeline_chart = self.chart_factory.apply_theme(timeline_chart)
            st.plotly_chart(timeline_chart, use_container_width=True)

        # Policy impact analysis
        st.subheader("Policy Impact Analysis")

        if "period_comparison" in timeline_data:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Pre-IRA vs Post-IRA Comparison**")
                comparison_chart = self.chart_factory.create_comparison_chart(
                    timeline_data["period_comparison"], "mean"
                )
                comparison_chart = self.chart_factory.apply_theme(comparison_chart)
                st.plotly_chart(comparison_chart, use_container_width=True)

            with col2:
                st.markdown("**Period Statistics**")
                if "changes" in timeline_data["period_comparison"]:
                    changes = timeline_data["period_comparison"]["changes"]
                    for metric, change in changes.items():
                        if "pct" in metric:
                            st.metric(
                                metric.replace("_", " ").title(), f"{change:.1f}%"
                            )

    def render_recipients_view(self):
        """Render recipients and awards analysis."""
        st.header("🏢 Recipients & Awards Analysis")

        # Get recipient data
        recipient_data = self.data_connector.get_recipient_data()

        if not recipient_data:
            st.warning("No recipient data available. Please load data first.")
            return

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top Recipients")

            if "recipient_summary" in recipient_data:
                scatter_chart = self.chart_factory.create_recipient_scatter(
                    recipient_data["recipient_summary"]
                )
                scatter_chart = self.chart_factory.apply_theme(scatter_chart)
                st.plotly_chart(scatter_chart, use_container_width=True)

        with col2:
            st.subheader("Award Distribution")

            # Show recipient summary table
            if "recipient_summary" in recipient_data:
                df = pd.DataFrame(recipient_data["recipient_summary"])
                st.dataframe(df.head(10), use_container_width=True)

        # Clustering analysis
        if "clustering" in recipient_data and recipient_data["clustering"]:
            st.subheader("Recipient Clustering Analysis")
            clustering = recipient_data["clustering"]

            if "cluster_summary" in clustering:
                st.write("**Cluster Characteristics:**")
                for cluster_id, characteristics in clustering[
                    "cluster_summary"
                ].items():
                    st.write(f"Cluster {cluster_id}: {characteristics}")

    def render_technology_view(self):
        """Render technology-focused analysis."""
        st.header("🔬 Technology Analysis")

        # Get technology data
        tech_data = self.data_connector.get_technology_data()

        if not tech_data:
            st.warning("No technology data available. Please load data first.")
            return

        # Technology breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Funding by Technology")

            if "technology_summary" in tech_data:
                pie_chart = self.chart_factory.create_technology_pie_chart(
                    tech_data["technology_summary"]
                )
                pie_chart = self.chart_factory.apply_theme(pie_chart)
                st.plotly_chart(pie_chart, use_container_width=True)

        with col2:
            st.subheader("Technology Growth Rates")

            if "technology_summary" in tech_data:
                growth_chart = self.chart_factory.create_technology_growth_chart(
                    tech_data["technology_summary"]
                )
                growth_chart = self.chart_factory.apply_theme(growth_chart)
                st.plotly_chart(growth_chart, use_container_width=True)

        # Technology insights
        if "insights" in tech_data:
            st.subheader("Technology Insights")
            for insight in tech_data["insights"]:
                if insight.get("type") == "technology":
                    st.info(f"💡 {insight['description']}")

    def render_comparative_view(self):
        """Render comparative analysis across different dimensions."""
        st.header("📊 Comparative Analysis")

        # Get comparative data
        comparative_data = self.data_connector.get_comparative_data()

        if not comparative_data:
            st.warning("No comparative data available. Please load data first.")
            return

        # State comparison
        st.subheader("State-by-State Comparison")

        comparison_metric = st.selectbox(
            "Select Comparison Metric",
            ["Total Funding", "Award Count", "Average Award Size", "Unique Recipients"],
        )

        # Show state comparison based on geographic data
        if (
            "geographic" in comparative_data
            and "state_summary" in comparative_data["geographic"]
        ):
            state_data = comparative_data["geographic"]["state_summary"]

            # Map metric names to data columns
            metric_mapping = {
                "Total Funding": "total_funding",
                "Award Count": "award_count",
                "Average Award Size": "avg_award_size",
                "Unique Recipients": "unique_recipients",
            }

            value_column = metric_mapping.get(comparison_metric, "total_funding")

            comparison_chart = self.chart_factory.create_state_ranking_chart(
                state_data, value_column=value_column, top_n=15
            )
            comparison_chart = self.chart_factory.apply_theme(comparison_chart)
            st.plotly_chart(comparison_chart, use_container_width=True)

        # Overall insights
        insights = self.data_connector.get_insights()
        if insights:
            st.subheader("Key Insights")
            for insight in insights[:5]:  # Show top 5 insights
                st.info(f"💡 {insight['description']}")


def main():
    """Main function to run the dashboard."""
    dashboard = CleanEnergyDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()

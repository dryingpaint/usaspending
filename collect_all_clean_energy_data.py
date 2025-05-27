#!/usr/bin/env python3
"""
Comprehensive Federal Clean Energy Data Collection Script

This script uses the USAspending API client to collect all possible federal clean energy
spending data across multiple dimensions:
- All time periods (pre-ARRA, ARRA, post-ARRA, IRA/CHIPS)
- All award types (contracts, grants, loans, etc.)
- All geographic levels (state, county)
- All clean energy keywords and CFDA codes
- Recipient analysis and spending trends

Features:
- Parallelized data collection for faster processing
- Progress saving throughout collection
- Resume capability from interruptions
- Comprehensive error handling and logging

The script saves data in multiple formats and provides comprehensive coverage
of federal clean energy investments.
"""

import sys
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.data_processor.api_client import USASpendingAPIClient
from src.config.api_config import (
    CLEAN_ENERGY_KEYWORDS,
    ENERGY_CFDA_CODES,
    DATE_RANGES,
    AWARD_TYPE_GROUPS,
)


class ParallelDataCollector:
    """
    Parallelized comprehensive data collector for federal clean energy spending.

    This class orchestrates the collection of all possible clean energy data
    from the USAspending API across multiple dimensions with parallelization
    and progress saving capabilities.
    """

    def __init__(self, output_dir: str = "data/collected", max_workers: int = 4):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers

        # Create subdirectories for different data types
        self.subdirs = {
            "awards": self.output_dir / "awards",
            "geographic": self.output_dir / "geographic",
            "recipients": self.output_dir / "recipients",
            "time_series": self.output_dir / "time_series",
            "summary": self.output_dir / "summary",
            "progress": self.output_dir / "progress",  # For saving progress
        }

        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)

        self.collection_log = []
        self.start_time = datetime.now()
        self.lock = threading.Lock()  # For thread-safe operations

        # Progress tracking
        self.progress_file = self.subdirs["progress"] / "collection_progress.json"
        self.completed_tasks = self.load_progress()

        print("🚀 Starting parallelized clean energy data collection")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"🔧 Max workers: {max_workers}")
        print(f"⏰ Start time: {self.start_time}")

        if self.completed_tasks:
            print(
                f"📋 Resuming from previous run - {len(self.completed_tasks)} tasks already completed"
            )

    def load_progress(self) -> Dict[str, Any]:
        """Load progress from previous runs."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load progress file: {e}")
        return {}

    def save_progress(self, task_id: str, result: Any):
        """Save progress for a completed task."""
        with self.lock:
            self.completed_tasks[task_id] = {
                "completed_at": datetime.now().isoformat(),
                "result_summary": str(type(result).__name__),
                "records": len(result) if hasattr(result, "__len__") else 0,
            }

            # Save to file
            try:
                with open(self.progress_file, "w") as f:
                    json.dump(self.completed_tasks, f, indent=2)
            except Exception as e:
                print(f"⚠️  Could not save progress: {e}")

    def is_task_completed(self, task_id: str) -> bool:
        """Check if a task has already been completed."""
        return task_id in self.completed_tasks

    def log_collection(
        self, data_type: str, description: str, records: int, success: bool = True
    ):
        """Thread-safe logging of collection activity."""
        with self.lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "data_type": data_type,
                "description": description,
                "records_collected": records,
                "success": success,
            }
            self.collection_log.append(entry)

            status = "✅" if success else "❌"
            print(f"{status} {data_type}: {description} - {records:,} records")

    def save_data(
        self, data: pd.DataFrame, filename: str, subdir: str = "awards"
    ) -> bool:
        """Thread-safe data saving to multiple formats."""
        if data.empty:
            print(f"⚠️  No data to save for {filename}")
            return False

        base_path = self.subdirs[subdir] / filename

        try:
            with self.lock:  # Ensure thread-safe file operations
                # Save as CSV
                csv_path = base_path.with_suffix(".csv")
                data.to_csv(csv_path, index=False)

                # Save as JSON for complex nested data
                json_path = base_path.with_suffix(".json")
                data.to_json(json_path, orient="records", indent=2)

                # Save as Parquet for efficient storage
                parquet_path = base_path.with_suffix(".parquet")
                data.to_parquet(parquet_path, index=False)

                print(
                    f"💾 Saved {len(data):,} records to {filename} (CSV, JSON, Parquet)"
                )
                return True

        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")
            return False

    def collect_single_award_group(
        self,
        period_name: str,
        period_dates: Dict[str, str],
        award_group: str,
        award_types: List[str],
        max_pages: int,
    ) -> Optional[pd.DataFrame]:
        """Collect data for a single award group in a time period."""
        task_id = f"awards_{period_name}_{award_group}"

        if self.is_task_completed(task_id):
            print(f"⏭️  Skipping {task_id} - already completed")
            return None

        client = USASpendingAPIClient()  # Each thread gets its own client

        try:
            # Build filters for this specific combination
            date_filter = client.build_date_filter(
                period_dates["start"], period_dates["end"]
            )
            keyword_filter = client.build_keyword_filter(CLEAN_ENERGY_KEYWORDS)

            filters = {
                **date_filter,
                **keyword_filter,
                "award_type_codes": award_types,
            }

            results = client.collect_paginated_data(
                filters=filters,
                max_pages=max_pages,
                delay=0.3,  # Reduced delay for parallel processing
            )

            if results:
                df = pd.DataFrame(results)
                df["award_group"] = award_group
                df["time_period"] = period_name

                # Save individual file
                filename = f"awards_{period_name}_{award_group}"
                self.save_data(df, filename, "awards")

                self.log_collection(
                    "awards", f"{period_name} - {award_group}", len(results)
                )
                self.save_progress(task_id, df)
                return df
            else:
                self.log_collection("awards", f"{period_name} - {award_group}", 0)
                self.save_progress(task_id, [])
                return pd.DataFrame()

        except Exception as e:
            print(f"❌ Error collecting {award_group} for {period_name}: {e}")
            self.log_collection(
                "awards", f"{period_name} - {award_group}", 0, success=False
            )
            return None

    def collect_awards_by_time_period_parallel(
        self, max_pages_per_period: int = 20
    ) -> Dict[str, pd.DataFrame]:
        """Collect awards data for each time period using parallel processing."""
        print(
            f"\n📅 Collecting awards by time period (parallel, max {max_pages_per_period} pages each)"
        )

        time_period_data = {}

        # Create tasks for parallel execution
        tasks = []
        for period_name, period_dates in DATE_RANGES.items():
            for award_group, award_types in AWARD_TYPE_GROUPS.items():
                tasks.append(
                    (
                        period_name,
                        period_dates,
                        award_group,
                        award_types,
                        max_pages_per_period,
                    )
                )

        print(f"🔄 Processing {len(tasks)} award collection tasks in parallel...")

        # Execute tasks in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(
                    self.collect_single_award_group,
                    period_name,
                    period_dates,
                    award_group,
                    award_types,
                    max_pages,
                ): (period_name, award_group)
                for period_name, period_dates, award_group, award_types, max_pages in tasks
            }

            # Collect results as they complete
            period_results = {}
            for future in as_completed(future_to_task):
                period_name, award_group = future_to_task[future]
                try:
                    result = future.result()
                    if result is not None and not result.empty:
                        if period_name not in period_results:
                            period_results[period_name] = []
                        period_results[period_name].append(result)
                except Exception as e:
                    print(f"❌ Task failed for {period_name} - {award_group}: {e}")

        # Combine results by time period
        for period_name, dfs in period_results.items():
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                time_period_data[period_name] = combined_df

                # Save combined period data
                self.save_data(combined_df, f"awards_{period_name}_combined", "awards")

        return time_period_data

    def collect_single_cfda(
        self, cfda_code: str, max_pages: int
    ) -> Optional[pd.DataFrame]:
        """Collect data for a single CFDA code."""
        task_id = f"cfda_{cfda_code}"

        if self.is_task_completed(task_id):
            print(f"⏭️  Skipping CFDA {cfda_code} - already completed")
            return None

        client = USASpendingAPIClient()

        try:
            # Use full time period for CFDA analysis
            date_filter = client.build_date_filter(
                DATE_RANGES["full_period"]["start"], DATE_RANGES["full_period"]["end"]
            )

            filters = {
                **date_filter,
                "cfda_numbers": [cfda_code],
                "award_type_codes": AWARD_TYPE_GROUPS[
                    "grants"
                ],  # CFDA codes are for grants
            }

            results = client.collect_paginated_data(
                filters=filters, max_pages=max_pages, delay=0.2
            )

            if results:
                df = pd.DataFrame(results)
                df["cfda_code"] = cfda_code

                # Save individual CFDA file
                filename = f"cfda_{cfda_code.replace('.', '_')}"
                self.save_data(df, filename, "awards")

                self.log_collection("cfda", f"CFDA {cfda_code}", len(results))
                self.save_progress(task_id, df)
                return df
            else:
                self.log_collection("cfda", f"CFDA {cfda_code}", 0)
                self.save_progress(task_id, [])
                return pd.DataFrame()

        except Exception as e:
            print(f"❌ Error collecting CFDA {cfda_code}: {e}")
            self.log_collection("cfda", f"CFDA {cfda_code}", 0, success=False)
            return None

    def collect_cfda_specific_data_parallel(
        self, max_pages_per_cfda: int = 10
    ) -> pd.DataFrame:
        """Collect data specifically for energy CFDA codes using parallel processing."""
        print(
            f"\n🏛️  Collecting CFDA-specific data (parallel, max {max_pages_per_cfda} pages each)"
        )

        print(f"🔄 Processing {len(ENERGY_CFDA_CODES)} CFDA codes in parallel...")

        cfda_results = []

        # Execute CFDA collection in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_cfda = {
                executor.submit(
                    self.collect_single_cfda, cfda_code, max_pages_per_cfda
                ): cfda_code
                for cfda_code in ENERGY_CFDA_CODES
            }

            for future in as_completed(future_to_cfda):
                cfda_code = future_to_cfda[future]
                try:
                    result = future.result()
                    if result is not None and not result.empty:
                        cfda_results.append(result)
                except Exception as e:
                    print(f"❌ CFDA task failed for {cfda_code}: {e}")

        if cfda_results:
            cfda_df = pd.concat(cfda_results, ignore_index=True)
            self.save_data(cfda_df, "awards_by_cfda_combined", "awards")
            return cfda_df
        else:
            return pd.DataFrame()

    def collect_single_keyword(
        self, keyword: str, max_pages: int
    ) -> Optional[pd.DataFrame]:
        """Collect data for a single keyword."""
        task_id = f"keyword_{keyword.replace(' ', '_')}"

        if self.is_task_completed(task_id):
            print(f"⏭️  Skipping keyword '{keyword}' - already completed")
            return None

        client = USASpendingAPIClient()

        try:
            # Use IRA/CHIPS period for keyword analysis
            date_filter = client.build_date_filter(
                DATE_RANGES["ira_chips_period"]["start"],
                DATE_RANGES["ira_chips_period"]["end"],
            )

            keyword_filter = client.build_keyword_filter([keyword])
            filters = {**date_filter, **keyword_filter}

            results = client.collect_paginated_data(
                filters=filters, max_pages=max_pages, delay=0.2
            )

            if results:
                df = pd.DataFrame(results)
                df["primary_keyword"] = keyword

                # Save individual keyword file
                filename = f"keyword_{keyword.replace(' ', '_')}"
                self.save_data(df, filename, "awards")

                self.log_collection("keyword", keyword, len(results))
                self.save_progress(task_id, df)
                return df
            else:
                self.log_collection("keyword", keyword, 0)
                self.save_progress(task_id, [])
                return pd.DataFrame()

        except Exception as e:
            print(f"❌ Error collecting data for '{keyword}': {e}")
            self.log_collection("keyword", keyword, 0, success=False)
            return None

    def collect_keyword_specific_data_parallel(
        self, max_pages_per_keyword: int = 5
    ) -> Dict[str, pd.DataFrame]:
        """Collect data for specific high-value keywords using parallel processing."""
        print("\n🔍 Collecting keyword-specific data (parallel)")

        # Focus on high-impact keywords
        priority_keywords = [
            "solar",
            "wind",
            "battery",
            "electric vehicle",
            "renewable energy",
            "clean energy",
            "energy storage",
            "smart grid",
            "carbon capture",
            "clean hydrogen",
            "geothermal",
            "biomass",
        ]

        print(f"🔄 Processing {len(priority_keywords)} keywords in parallel...")

        keyword_data = {}

        # Execute keyword collection in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_keyword = {
                executor.submit(
                    self.collect_single_keyword, keyword, max_pages_per_keyword
                ): keyword
                for keyword in priority_keywords
            }

            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    result = future.result()
                    if result is not None and not result.empty:
                        keyword_data[keyword] = result
                except Exception as e:
                    print(f"❌ Keyword task failed for '{keyword}': {e}")

        return keyword_data

    def collect_geographic_data(self) -> Dict[str, pd.DataFrame]:
        """Collect geographic spending data (not parallelized as it's already fast)."""
        print("\n🗺️  Collecting geographic spending data")

        geographic_data = {}
        client = USASpendingAPIClient()

        # Build filters for recent period (most relevant for geographic analysis)
        date_filter = client.build_date_filter(
            DATE_RANGES["ira_chips_period"]["start"],
            DATE_RANGES["ira_chips_period"]["end"],
        )
        keyword_filter = client.build_keyword_filter(CLEAN_ENERGY_KEYWORDS)

        base_filters = {**date_filter, **keyword_filter}

        # Collect state-level data
        for geo_layer in ["state", "county"]:
            task_id = f"geographic_{geo_layer}"

            if self.is_task_completed(task_id):
                print(f"⏭️  Skipping geographic {geo_layer} - already completed")
                continue

            print(f"  📍 Collecting {geo_layer}-level data...")

            try:
                response = client.get_geographic_spending(
                    filters=base_filters,
                    geo_layer=geo_layer,
                    scope="place_of_performance",
                )

                if response.get("results"):
                    df = pd.DataFrame(response["results"])
                    df["geographic_scope"] = geo_layer
                    geographic_data[geo_layer] = df

                    self.save_data(df, f"geographic_{geo_layer}", "geographic")
                    self.log_collection("geographic", f"{geo_layer} level", len(df))
                    self.save_progress(task_id, df)
                else:
                    self.log_collection("geographic", f"{geo_layer} level", 0)
                    self.save_progress(task_id, [])

            except Exception as e:
                print(f"❌ Error collecting {geo_layer} data: {e}")
                self.log_collection(
                    "geographic", f"{geo_layer} level", 0, success=False
                )

            time.sleep(1)

        return geographic_data

    def collect_recipient_data(self) -> pd.DataFrame:
        """Collect recipient analysis data."""
        task_id = "recipients_analysis"

        if self.is_task_completed(task_id):
            print("⏭️  Skipping recipient analysis - already completed")
            return pd.DataFrame()

        print("\n🏢 Collecting recipient data")

        client = USASpendingAPIClient()

        # Use IRA/CHIPS period for recipient analysis
        date_filter = client.build_date_filter(
            DATE_RANGES["ira_chips_period"]["start"],
            DATE_RANGES["ira_chips_period"]["end"],
        )
        keyword_filter = client.build_keyword_filter(CLEAN_ENERGY_KEYWORDS)

        filters = {**date_filter, **keyword_filter}

        try:
            response = client.get_recipient_data(filters=filters, limit=100)

            if response.get("results"):
                df = pd.DataFrame(response["results"])
                self.save_data(df, "recipients_analysis", "recipients")
                self.log_collection("recipients", "Top recipients", len(df))
                self.save_progress(task_id, df)
                return df
            else:
                self.log_collection("recipients", "Top recipients", 0)
                self.save_progress(task_id, [])
                return pd.DataFrame()

        except Exception as e:
            print(f"❌ Error collecting recipient data: {e}")
            self.log_collection("recipients", "Top recipients", 0, success=False)
            return pd.DataFrame()

    def collect_time_series_data(self) -> Dict[str, pd.DataFrame]:
        """Collect spending over time data."""
        print("\n📈 Collecting time series data")

        time_series_data = {}
        client = USASpendingAPIClient()

        # Build filters for full period
        date_filter = client.build_date_filter(
            DATE_RANGES["full_period"]["start"], DATE_RANGES["full_period"]["end"]
        )
        keyword_filter = client.build_keyword_filter(CLEAN_ENERGY_KEYWORDS)

        base_filters = {**date_filter, **keyword_filter}

        # Collect data at different time granularities
        for grouping in ["month", "quarter", "fiscal_year"]:
            task_id = f"time_series_{grouping}"

            if self.is_task_completed(task_id):
                print(f"⏭️  Skipping time series {grouping} - already completed")
                continue

            print(f"  📊 Collecting {grouping} time series...")

            try:
                response = client.get_spending_over_time(
                    filters=base_filters, group=grouping
                )

                if response.get("results"):
                    df = pd.DataFrame(response["results"])
                    df["time_grouping"] = grouping
                    time_series_data[grouping] = df

                    self.save_data(df, f"time_series_{grouping}", "time_series")
                    self.log_collection("time_series", f"{grouping} grouping", len(df))
                    self.save_progress(task_id, df)
                else:
                    self.log_collection("time_series", f"{grouping} grouping", 0)
                    self.save_progress(task_id, [])

            except Exception as e:
                print(f"❌ Error collecting {grouping} time series: {e}")
                self.log_collection(
                    "time_series", f"{grouping} grouping", 0, success=False
                )

            time.sleep(1)

        return time_series_data

    def generate_collection_summary(self) -> Dict[str, Any]:
        """Generate a summary of the data collection process."""
        print("\n📋 Generating collection summary")

        end_time = datetime.now()
        duration = end_time - self.start_time

        # Calculate summary statistics
        total_records = sum(entry["records_collected"] for entry in self.collection_log)
        successful_collections = sum(
            1 for entry in self.collection_log if entry["success"]
        )
        total_collections = len(self.collection_log)

        summary = {
            "collection_metadata": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "duration_formatted": str(duration),
                "max_workers": self.max_workers,
                "parallelized": True,
            },
            "collection_stats": {
                "total_records_collected": total_records,
                "successful_collections": successful_collections,
                "total_collection_attempts": total_collections,
                "success_rate": successful_collections / total_collections
                if total_collections > 0
                else 0,
                "completed_tasks": len(self.completed_tasks),
            },
            "data_types_collected": list(
                set(entry["data_type"] for entry in self.collection_log)
            ),
            "collection_log": self.collection_log,
            "completed_tasks": self.completed_tasks,
        }

        # Save summary
        summary_path = self.subdirs["summary"] / "collection_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        # Save collection log as CSV
        log_df = pd.DataFrame(self.collection_log)
        log_path = self.subdirs["summary"] / "collection_log.csv"
        log_df.to_csv(log_path, index=False)

        print("📊 Collection Summary:")
        print(f"   ⏱️  Duration: {summary['collection_metadata']['duration_formatted']}")
        print(f"   📈 Total records: {total_records:,}")
        print(f"   ✅ Success rate: {summary['collection_stats']['success_rate']:.1%}")
        print(f"   🔄 Completed tasks: {len(self.completed_tasks)}")
        print(f"   📁 Data saved to: {self.output_dir}")

        return summary

    def run_comprehensive_collection(
        self,
        max_pages_per_period: int = 20,
        max_pages_per_cfda: int = 10,
        max_pages_per_keyword: int = 5,
    ) -> Dict[str, Any]:
        """
        Run the complete comprehensive data collection process with parallelization.

        Args:
            max_pages_per_period: Maximum pages to collect per time period
            max_pages_per_cfda: Maximum pages to collect per CFDA code
            max_pages_per_keyword: Maximum pages to collect per keyword

        Returns:
            Dictionary containing collection summary and metadata
        """
        print(
            "🎯 Starting comprehensive federal clean energy data collection (PARALLELIZED)"
        )
        print("📊 Collection parameters:")
        print(f"   📅 Max pages per time period: {max_pages_per_period}")
        print(f"   🏛️  Max pages per CFDA code: {max_pages_per_cfda}")
        print(f"   🏷️  Max pages per keyword: {max_pages_per_keyword}")
        print(f"   🔧 Max workers: {self.max_workers}")

        try:
            # 1. Collect awards by time period (PARALLELIZED)
            time_period_data = self.collect_awards_by_time_period_parallel(
                max_pages_per_period
            )

            # 2. Collect CFDA-specific data (PARALLELIZED)
            cfda_data = self.collect_cfda_specific_data_parallel(max_pages_per_cfda)

            # 3. Collect keyword-specific data (PARALLELIZED)
            keyword_data = self.collect_keyword_specific_data_parallel(
                max_pages_per_keyword
            )

            # 4. Collect geographic data
            geographic_data = self.collect_geographic_data()

            # 5. Collect recipient data
            recipient_data = self.collect_recipient_data()

            # 6. Collect time series data
            time_series_data = self.collect_time_series_data()

            # 7. Generate summary
            summary = self.generate_collection_summary()

            print("\n🎉 Comprehensive data collection completed successfully!")
            print(f"📁 All data saved to: {self.output_dir}")

            return {
                "summary": summary,
                "data_collected": {
                    "time_periods": list(time_period_data.keys()),
                    "cfda_records": len(cfda_data) if not cfda_data.empty else 0,
                    "geographic_scopes": list(geographic_data.keys()),
                    "recipient_records": len(recipient_data)
                    if not recipient_data.empty
                    else 0,
                    "time_series_groupings": list(time_series_data.keys()),
                    "keywords_analyzed": list(keyword_data.keys()),
                },
            }

        except Exception as e:
            print(f"❌ Error during comprehensive collection: {e}")
            summary = self.generate_collection_summary()
            return {"summary": summary, "error": str(e)}


# Backward compatibility alias
ComprehensiveDataCollector = ParallelDataCollector


def main():
    """Main function to run comprehensive data collection."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect comprehensive federal clean energy spending data (PARALLELIZED)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/collected",
        help="Output directory for collected data",
    )
    parser.add_argument(
        "--max-pages-period",
        type=int,
        default=20,
        help="Maximum pages to collect per time period",
    )
    parser.add_argument(
        "--max-pages-cfda",
        type=int,
        default=10,
        help="Maximum pages to collect per CFDA code",
    )
    parser.add_argument(
        "--max-pages-keyword",
        type=int,
        default=5,
        help="Maximum pages to collect per keyword",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers",
    )
    parser.add_argument(
        "--quick", action="store_true", help="Quick collection with reduced page limits"
    )

    args = parser.parse_args()

    # Adjust limits for quick collection
    if args.quick:
        args.max_pages_period = 5
        args.max_pages_cfda = 3
        args.max_pages_keyword = 2
        print("🚀 Running quick collection with reduced limits")

    # Initialize collector
    collector = ParallelDataCollector(
        output_dir=args.output_dir, max_workers=args.max_workers
    )

    # Run collection
    results = collector.run_comprehensive_collection(
        max_pages_per_period=args.max_pages_period,
        max_pages_per_cfda=args.max_pages_cfda,
        max_pages_per_keyword=args.max_pages_keyword,
    )

    print("\n🏁 Collection completed!")
    print(f"📊 Check {args.output_dir}/summary/ for detailed results")
    print(f"📋 Progress saved in {args.output_dir}/progress/ for resuming")


if __name__ == "__main__":
    main()

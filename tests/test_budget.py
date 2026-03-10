"""Budget Sentinel Kenya — test suite."""
from __future__ import annotations
import pandas as pd
import pytest
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "allocations"


class TestSeedData:
    def _df(self):
        return pd.read_csv(DATA / "county_budgets_fy2223.csv")

    def test_load(self):
        df = self._df()
        assert len(df) >= 40, f"Expected ≥40 counties, got {len(df)}"

    def test_required_columns(self):
        df = self._df()
        required = {
            "county", "county_code", "region", "population_2019",
            "total_allocation_kes_m", "revenue_raised_kes_m",
            "recurrent_exp_kes_m", "development_exp_kes_m",
            "absorption_pct", "development_absorption_pct",
            "health_allocation_kes_m", "education_allocation_kes_m",
            "infrastructure_allocation_kes_m",
            "fy", "source", "verified",
        }
        assert required.issubset(df.columns)

    def test_all_confirmed(self):
        df = self._df()
        bad = df[df["verified"] != "confirmed"]
        assert len(bad) == 0, f"Unverified: {bad['county'].tolist()}"

    def test_source_is_cob(self):
        df = self._df()
        assert df["source"].str.contains("COB").all(), "All records must cite COB"

    def test_no_duplicate_counties(self):
        df = self._df()
        assert df["county"].is_unique, "Duplicate county entries found"


class TestFinancialRanges:
    def _df(self): return pd.read_csv(DATA / "county_budgets_fy2223.csv")

    def test_absorption_range(self):
        df = self._df()
        assert df["absorption_pct"].between(0, 100).all(), "absorption_pct must be 0–100"

    def test_dev_absorption_range(self):
        df = self._df()
        assert df["development_absorption_pct"].between(0, 100).all()

    def test_allocations_positive(self):
        df = self._df()
        for col in ["total_allocation_kes_m", "development_exp_kes_m",
                    "health_allocation_kes_m", "infrastructure_allocation_kes_m"]:
            assert (df[col] > 0).all(), f"{col} must be positive"

    def test_sector_allocations_lt_total(self):
        df = self._df()
        sector_sum = (df["health_allocation_kes_m"]
                      + df["education_allocation_kes_m"]
                      + df["infrastructure_allocation_kes_m"])
        assert (sector_sum <= df["total_allocation_kes_m"]).all(), \
            "Sector sum cannot exceed total allocation"

    def test_dev_exp_lt_total(self):
        df = self._df()
        assert (df["development_exp_kes_m"] < df["total_allocation_kes_m"]).all()

    def test_population_positive(self):
        df = self._df()
        assert (df["population_2019"] > 0).all()


class TestDerivedMetrics:
    """Mirror the derived computations in app.py."""

    def _df(self): return pd.read_csv(DATA / "county_budgets_fy2223.csv")

    def test_dev_unspent_formula(self):
        df = self._df()
        df["dev_utilised"] = df["development_exp_kes_m"] * df["development_absorption_pct"] / 100
        df["dev_unspent"] = df["development_exp_kes_m"] - df["dev_utilised"]
        assert (df["dev_unspent"] >= 0).all(), "Unspent cannot be negative"

    def test_per_capita_formula(self):
        df = self._df()
        df["per_capita"] = (df["total_allocation_kes_m"] * 1_000_000) / df["population_2019"]
        assert (df["per_capita"] > 0).all()
        assert (df["per_capita"] < 100_000).all(), "Per capita seems too large"

    def test_low_absorption_counties_exist(self):
        """Regression: at least some counties should fall below 70% threshold."""
        df = self._df()
        low = (df["development_absorption_pct"] < 70).sum()
        assert low >= 3, f"Expected at least 3 low-absorption counties, got {low}"

    def test_nairobi_high_budget(self):
        df = self._df()
        nairobi = df[df["county"] == "Nairobi"]
        assert len(nairobi) == 1, "Nairobi should appear exactly once"
        assert nairobi["total_allocation_kes_m"].iloc[0] > 15000, \
            "Nairobi allocation should be > 15B KES"

    def test_region_coverage(self):
        df = self._df()
        regions = df["region"].nunique()
        assert regions >= 5, f"Expected ≥5 regions, got {regions}"


def test_app_compiles():
    import py_compile
    py_compile.compile(str(Path(__file__).parent.parent / "app.py"), doraise=True)

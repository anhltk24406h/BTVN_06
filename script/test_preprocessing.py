"""Kiểm tra các lỗi gán ngày và chuyển đổi có thể làm sai kết quả nghiên cứu."""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from preprocessing import DataValidationError, assign_events, load_market, parse_volume


class PreprocessingTests(unittest.TestCase):
    def market(self):
        # Loại 15/01 khỏi lịch quan sát để kiểm tra lễ, thay vì chỉ kiểm tra cuối tuần.
        dates = pd.bdate_range("2024-01-02", periods=50).difference(pd.DatetimeIndex(["2024-01-15"]))
        price = pd.Series(np.arange(len(dates), dtype=float) + 100.0)
        y = np.log(price / price.shift(1))
        return pd.DataFrame({"date": dates, "price": price, "Y": y, "Y_lag1": y.shift(1)})

    def events(self, market):
        dates = ["2024-01-06", "2024-01-15"] + [
            market.loc[i, "date"].strftime("%Y-%m-%d") for i in [19, 29, 39]
        ]
        return pd.DataFrame({
            "date": dates,
            "event": [f"Sự kiện thử {i}" for i in range(5)],
            "description": ["Dữ liệu tổng hợp chỉ dùng kiểm thử"] * 5,
            "source_url": ["https://example.org/first"] * 5,
            "source_url_2": ["https://example.net/second"] * 5,
        })

    def test_volume_units_and_missing(self):
        values = parse_volume(pd.Series(["1.5K", "2M", "1,234", "", None, "sai"]))
        np.testing.assert_allclose(values.iloc[:3], [1500, 2000000, 1234])
        self.assertTrue(values.iloc[3:].isna().all())

    def test_sort_deduplicate_and_lags(self):
        raw = pd.DataFrame({"Date": ["01/04/2024", "01/02/2024", "01/03/2024", "01/03/2024"],
                            "Price": ["1,030", "1,000", "1,010", "1,010"]})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "market.csv"
            raw.to_csv(path, index=False)
            clean, report = load_market(path)
        self.assertEqual(len(clean), 3)
        self.assertEqual(report["ban_ghi_trung_hoan_toan"], 1)
        self.assertTrue(clean.date.is_monotonic_increasing)
        np.testing.assert_allclose(clean.Y.iloc[1:], np.log([1010 / 1000, 1030 / 1010]))
        self.assertAlmostEqual(clean.Y_lag1.iloc[2], clean.Y.iloc[1])
        self.assertEqual(clean.Y_lag1.isna().sum(), 2)

    def test_conflicting_prices_and_invalid_input_stop(self):
        cases = [
            {"Date": ["01/02/2024", "01/02/2024"], "Price": ["100", "101"]},
            {"Date": ["01/02/2024", "01/03/2024"], "Price": ["100", "0"]},
            {"Date": ["01/02/2024", "01/03/2024"], "Price": ["100", None]},
            {"Date": ["31/12/2024", "01/03/2024"], "Price": ["100", "101"]},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "market.csv"
                pd.DataFrame(case).to_csv(path, index=False)
                with self.assertRaises(DataValidationError):
                    load_market(path)

    def test_weekend_holiday_and_real_date_preserved(self):
        market = self.market()
        processed, assigned = assign_events(market, self.events(market))
        self.assertEqual(assigned.loc[0, "date"], pd.Timestamp("2024-01-06"))
        self.assertEqual(assigned.loc[0, "date_assigned"], pd.Timestamp("2024-01-08"))
        self.assertEqual(assigned.loc[1, "date_assigned"], pd.Timestamp("2024-01-16"))
        self.assertEqual(processed.D.sum(), 5)

    def test_collision_spacing_count_and_horizon_stop(self):
        market = self.market()
        original = self.events(market)
        mutations = []
        collision = original.copy(); collision.loc[1, "date"] = "2024-01-07"; mutations.append(collision)
        close = original.copy(); close.loc[1, "date"] = "2024-01-09"; mutations.append(close)
        outside = original.copy(); outside.loc[4, "date"] = "2027-01-01"; mutations.append(outside)
        before = original.copy(); before.loc[0, "date"] = "2022-12-31"; mutations.append(before)
        mutations.append(original.iloc[:4])
        for events in mutations:
            with self.subTest(dates=events.date.tolist()):
                with self.assertRaises(DataValidationError):
                    assign_events(market, events)

    def test_real_dataset_invariants(self):
        root = Path(__file__).resolve().parents[1]
        market, _ = load_market(root / "data" / "sp500.csv")
        events = pd.read_csv(root / "data" / "events.csv", dtype="string")
        processed, assigned = assign_events(market, events)
        self.assertEqual(processed.D.sum(), 5)
        self.assertEqual(len(processed), len(market))
        self.assertEqual(len(processed.dropna(subset=["Y", "Y_lag1"])), len(market) - 2)
        self.assertTrue(processed.date.is_unique)
        self.assertTrue(processed.date.is_monotonic_increasing)
        positions = pd.DatetimeIndex(market.date).get_indexer(assigned.date_assigned)
        self.assertTrue((np.diff(positions) >= 5).all())


if __name__ == "__main__":
    unittest.main(verbosity=2)

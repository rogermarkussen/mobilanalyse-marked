from pathlib import Path
import unittest

import polars as pl

from scripts.preprocess_assets import market_share_omsetning


ROOT = Path(__file__).resolve().parents[1]


class MarketShareOmsetningTest(unittest.TestCase):
    def test_2025_includes_roaming_revenue(self) -> None:
        shares = (
            market_share_omsetning(pl.scan_parquet(ROOT / "data" / "mobil.parquet"))
            .filter(pl.col("ar") == 2025)
            .select("tilbyder", pl.col("markedsandel").round(1))
        )

        self.assertEqual(
            dict(shares.iter_rows()),
            {
                "Lyse Tele (Ice)": 11.8,
                "Telia": 30.8,
                "Telenor": 50.6,
                "Øvrige": 6.7,
            },
        )


if __name__ == "__main__":
    unittest.main()

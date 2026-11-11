import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from src.bike_sharing_demand_analysis.preprocessing import run as run_preprocessing


class TestPreprocessing(unittest.TestCase):
    def test_joins_weather_and_dispatch_on_trip_date(self):
        with TemporaryDirectory() as folder:
            project = Path(folder)
            raw_dir = project / "data" / "raw"
            output_dir = project / "output"
            raw_dir.mkdir(parents=True)
            output_dir.mkdir()

            inputs = {
                "trips.csv": (
                    "trip_id,start_time,end_time,start_grid,end_grid,distance_km\n"
                    "T1,2024-01-01 07:00:00,2024-01-01 07:10:00,G1,G2,1.5\n"
                ),
                "grids.csv": (
                    "grid_id,lng,lat,district\n"
                    "G1,108.9,34.2,D1\n"
                    "G2,108.8,34.2,D1\n"
                ),
                "weather.csv": (
                    "date,temp_c,rain_mm,wind_ms\n"
                    "2024-01-01,-6.59,7.32,4.12\n"
                ),
                "ops.csv": (
                    "date,grid_id,dispatch_in,dispatch_out\n"
                    "2024-01-01,G1,7,13\n"
                ),
            }
            for name, contents in inputs.items():
                (raw_dir / name).write_text(contents, encoding="utf-8")

            run_preprocessing(output_dir)

            merged = pd.read_csv(output_dir / "003merged_data.csv").set_index("grid_id")
            origin = merged.loc["G1"]
            self.assertEqual(origin["date"], "2024-01-01")
            self.assertAlmostEqual(origin["temp_c"], -6.59)
            self.assertAlmostEqual(origin["rain_mm"], 7.32)
            self.assertEqual(origin["dispatch_in"], 7)
            self.assertEqual(origin["dispatch_out"], 13)
            self.assertEqual(origin["gap_index"], 7)


if __name__ == "__main__":
    unittest.main()

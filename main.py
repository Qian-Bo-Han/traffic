import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bike_sharing_demand_analysis.pipeline import run


if __name__ == "__main__":
    print(f"Results saved to {run(PROJECT_ROOT)}")

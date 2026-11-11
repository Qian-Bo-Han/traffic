from pathlib import Path

from . import analysis, forecasting, preprocessing, visualization


def run(project_root: Path) -> Path:
    output_dir = project_root / "output"
    output_dir.mkdir(exist_ok=True)
    preprocessing.run(output_dir)
    analysis.run(output_dir)
    forecasting.run(output_dir)
    visualization.run(output_dir)
    return output_dir

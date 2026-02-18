import re
from pathlib import Path

import pandas as pd


class DatasetService:
    """Loads CSV files and store in datasets + metadata."""

    def __init__(self, data_dir: str = "data") -> None:
        self._datasets: dict[str, pd.DataFrame] = {}
        self._dataset_info: str = ""
        self._data_dir = data_dir

    @property
    def datasets(self) -> dict[str, pd.DataFrame]:
        return self._datasets

    @property
    def dataset_info(self) -> str:
        return self._dataset_info

    def load(self) -> None:
        """Load all CSV files from the data directory."""
        data_path = Path(self._data_dir)
        if not data_path.exists():
            data_path.mkdir(parents=True, exist_ok=True)
            self._dataset_info = "No datasets available."
            return

        info_lines: list[str] = []

        for csv_file in sorted(data_path.glob("*.csv")):
            name = re.sub(r"[^a-zA-Z0-9_]", "_", csv_file.stem).strip("_").lower()
            df = pd.read_csv(csv_file)
            self._datasets[name] = df

            cols = ", ".join(df.columns.tolist())
            info_lines.append(
                f"- **{name}** ({df.shape[0]} rows, {df.shape[1]} columns)\n"
                f"  Columns: {cols}"
            )

        if not info_lines:
            self._dataset_info = (
                "No datasets available. Add CSV files to the data/ directory."
            )
            return

        self._dataset_info = "\n".join(info_lines)

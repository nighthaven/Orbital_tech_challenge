import re
from pathlib import Path
from typing import List, Dict

import pandas as pd


class DatasetService:
    """Loads CSV files and store in datasets + metadata."""

    def __init__(self, data_dir: str = "data") -> None:
        self._datasets: Dict[str, pd.DataFrame] = {}
        self._dataset_info: str = ""
        self._data_dir = data_dir

    @property
    def datasets(self) -> Dict[str, pd.DataFrame]:
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

        info_lines: List[str] = []

        for csv_file in sorted(data_path.glob("*.csv")):
            name = re.sub(r"[^a-zA-Z0-9_]", "_", csv_file.stem).strip("_").lower()
            df = pd.read_csv(csv_file, sep=None, engine="python")
            df = df.loc[:, df.columns.notna() & (df.columns.str.strip() != "")]
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

    def get_dataset_summaries(self) -> List[Dict[str, pd.DataFrame]]:
        """Return a summary of each loaded dataset"""
        return [
            {
                "name": name,
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist(),
            }
            for name, df in self._datasets.items()
        ]

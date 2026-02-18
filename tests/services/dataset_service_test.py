import pandas as pd
from src.services.dataset_service import DatasetService


class TestDatasetService:
    def setup_method(self):
        self.dataset_service = DatasetService()

    def test_load_with_success(self, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        csv_file = data_dir / "test-file.csv"
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        df.to_csv(csv_file, index=False)

        service = DatasetService(data_dir=str(data_dir))
        service.load()

        assert "test_file" in service.datasets
        loaded_df = service.datasets["test_file"]
        assert loaded_df.shape == (2, 2)
        assert "col1" in loaded_df.columns
        assert "col2" in loaded_df.columns

    def test_load_with_invalid_path(self, tmp_path):
        data_dir = tmp_path / "wrong_path"
        DatasetService(data_dir=str(data_dir))
        assert not data_dir.exists()

import pandas as pd


class TestListDatasetsRoute:
    def test_list_datasets_route(self, client, tmp_path):
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        csv_file = data_dir / "my_dataset.csv"
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        df.to_csv(csv_file, index=False)

        response = client.get("/api/datasets")
        assert response.status_code == 200
        assert len(response.json()) > 0

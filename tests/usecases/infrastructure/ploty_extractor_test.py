from src.usecases.infrastructure.plotly_extractor import extract_plotly_json_from_html


def test_extract_plotly_json_from_html_success(tmp_path):
    html_content = """
    <html>
    <body>
    <script>
    Plotly.newPlot('graph',
        [{"x": [1,2,3], "y": [4,5,6]}],
        {"title": "Test Graph"}
    );
    </script>
    </body>
    </html>
    """
    html_file = tmp_path / "plot.html"
    html_file.write_text(html_content)

    result = extract_plotly_json_from_html(str(html_file))

    assert isinstance(result, dict)
    assert "data" in result
    assert "layout" in result
    assert result["data"] == [{"x": [1, 2, 3], "y": [4, 5, 6]}]
    assert result["layout"] == {"title": "Test Graph"}


def test_extract_plotly_json_from_html_missing_file(tmp_path):
    missing_file = tmp_path / "missing.html"
    result = extract_plotly_json_from_html(str(missing_file))
    assert result is None


def test_extract_plotly_json_from_html_invalid_content(tmp_path):
    html_content = "<html><body>No plotly here</body></html>"
    html_file = tmp_path / "noplot.html"
    html_file.write_text(html_content)

    result = extract_plotly_json_from_html(str(html_file))
    assert result is None

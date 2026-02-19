import json
import re


def extract_plotly_json_from_html(html_path: str) -> dict | None:
    """
    Extract Plotly data + layout from an HTML file generated.
    """
    try:
        with open(html_path) as f:
            html = f.read()
    except FileNotFoundError:
        return None

    decoder = json.JSONDecoder()

    for marker in ("Plotly.newPlot(", "Plotly.react("):
        for match in re.finditer(re.escape(marker), html):
            after_marker = html[match.end() :]

            comma_idx = after_marker.find(",")
            if comma_idx == -1:
                continue
            rest = after_marker[comma_idx + 1 :].strip()

            try:
                data, end = decoder.raw_decode(rest)
            except (json.JSONDecodeError, ValueError):
                continue

            rest = rest[end:].strip().lstrip(",").strip()
            try:
                layout, _ = decoder.raw_decode(rest)
            except (json.JSONDecodeError, ValueError):
                continue

            if isinstance(data, list) and isinstance(layout, dict):
                return {"data": data, "layout": layout}

    return None

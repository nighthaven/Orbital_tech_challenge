import json


def extract_plotly_json_from_html(html_path: str) -> dict | None:
    """Extract Plotly data + layout from an HTML file"""
    try:
        with open(html_path) as f:
            html = f.read()
    except FileNotFoundError:
        return None

    for marker in ("Plotly.newPlot(", "Plotly.react("):
        idx = html.find(marker)
        if idx == -1:
            continue

        after_marker = html[idx + len(marker) :]
        comma_idx = after_marker.find(",")
        if comma_idx == -1:
            continue
        rest = after_marker[comma_idx + 1 :].strip()

        decoder = json.JSONDecoder()
        try:
            data, end = decoder.raw_decode(rest)
        except (json.JSONDecodeError, ValueError):
            continue

        rest = rest[end:].strip().lstrip(",").strip()
        try:
            layout, _ = decoder.raw_decode(rest)
        except (json.JSONDecodeError, ValueError):
            continue
        return {"data": data, "layout": layout}
    return None

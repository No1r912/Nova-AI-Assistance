"""Private analytics and charting for local CSV, TSV, and JSON files."""

import csv
import json
import platform
import shutil
from collections import Counter
from pathlib import Path
from statistics import mean, median, pstdev


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_EXTENSIONS = {".csv", ".tsv", ".json"}
CHARTS_DIRECTORY = PROJECT_ROOT / "data" / "charts"


def _resolve_path(value):
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    path = path.resolve()
    if PROJECT_ROOT not in path.parents and path != PROJECT_ROOT:
        raise ValueError("For privacy, analytics can only read files inside the Nova folder.")
    if not path.is_file():
        raise ValueError(f"File not found: {path}")
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Use CSV, TSV, or JSON.")
    return path


def _load_rows(path):
    if path.suffix.lower() in {".csv", ".tsv"}:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
            return list(csv.DictReader(source, delimiter=delimiter))
    with path.open("r", encoding="utf-8") as source:
        data = json.load(source)
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return data
    if isinstance(data, dict):
        return [{"key": key, "value": value} for key, value in data.items()]
    raise ValueError("JSON must contain an object or a list of objects.")


def _number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _numeric_values(rows, column):
    return [number for number in (_number(row.get(column)) for row in rows) if number is not None]


def _percent(value, total):
    return f"{(value / total * 100):.0f}%" if total else "0%"


def _safe_filename(value):
    return "".join(char if char.isalnum() or char in "-_" else "_" for char in value)[:80] or "chart"


def analyze_file(value):
    """Create a compact, readable profile of a user-selected local dataset."""
    path = _resolve_path(value)
    rows = _load_rows(path)
    if not rows:
        return f"{path.name} is empty."

    columns = sorted({key for row in rows for key in row})
    lines = [f"Analysis: {path.name}", f"Rows: {len(rows)}", f"Columns: {', '.join(columns)}"]
    for column in columns:
        values = [row.get(column) for row in rows if row.get(column) not in (None, "")]
        numeric = _numeric_values(rows, column)
        missing = len(rows) - len(values)
        if numeric and len(numeric) >= max(2, len(values) * 0.7):
            sorted_values = sorted(numeric)
            lower_quartile = sorted_values[len(sorted_values) // 4]
            upper_quartile = sorted_values[(len(sorted_values) * 3) // 4]
            iqr = upper_quartile - lower_quartile
            outliers = sum(value < lower_quartile - 1.5 * iqr or value > upper_quartile + 1.5 * iqr for value in numeric)
            lines.append(
                f"{column} (numeric): {len(numeric)} valid, {missing} missing ({_percent(missing, len(rows))}); "
                f"mean {mean(numeric):.2f}, median {median(numeric):.2f}, std. dev. {pstdev(numeric):.2f}; "
                f"min {min(numeric):.2f}, max {max(numeric):.2f}, sum {sum(numeric):.2f}"
            )
            if outliers:
                lines.append(f"  Potential outliers (IQR): {outliers}")
        elif values:
            common = Counter(str(value) for value in values).most_common(3)
            lines.append(
                f"{column} (categorical): {len(values)} populated, {missing} missing ({_percent(missing, len(rows))}), "
                f"{len(set(str(value) for value in values))} distinct; common: "
                + ", ".join(f"{item} ({count})" for item, count in common)
            )
    return "\n".join(lines)


def create_chart(value, x_column=None, y_column=None):
    """Save a useful PNG chart for a user-selected local dataset and return its path."""
    path = _resolve_path(value)
    rows = _load_rows(path)
    if not rows:
        raise ValueError("Cannot chart an empty dataset.")
    columns = sorted({key for row in rows for key in row})
    if not columns:
        raise ValueError("The dataset has no columns to chart.")
    if x_column and x_column not in columns:
        raise ValueError(f"Column not found: {x_column}. Available columns: {', '.join(columns)}")
    if y_column and y_column not in columns:
        raise ValueError(f"Column not found: {y_column}. Available columns: {', '.join(columns)}")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise OSError("Charting requires matplotlib. Install the project dependencies and try again.") from error

    numeric_columns = [column for column in columns if len(_numeric_values(rows, column)) >= 2]
    x_column = x_column or (numeric_columns[0] if numeric_columns else columns[0])
    title = f"{path.stem}: {x_column}"
    figure, axis = plt.subplots(figsize=(10, 6))

    if y_column:
        points = [(str(row.get(x_column, "")), _number(row.get(y_column))) for row in rows]
        points = [(label, number) for label, number in points if label and number is not None]
        if not points:
            raise ValueError(f"No usable values found for {x_column} and {y_column}.")
        labels, values = zip(*points)
        if len(set(labels)) <= 20:
            totals, counts = {}, Counter()
            for label, number in points:
                totals[label] = totals.get(label, 0) + number
                counts[label] += 1
            labels = list(totals)
            values = [totals[label] / counts[label] for label in labels]
            axis.bar(labels, values, color="#4f7cff")
            axis.tick_params(axis="x", rotation=35)
            axis.set_ylabel(f"Average {y_column}")
        else:
            axis.plot(range(1, len(values) + 1), values, marker="o", color="#4f7cff")
            axis.set_xlabel("Row")
            axis.set_ylabel(y_column)
        title = f"{path.stem}: {y_column} by {x_column}"
    elif x_column in numeric_columns:
        values = _numeric_values(rows, x_column)
        axis.hist(values, bins=min(20, max(5, int(len(values) ** 0.5))), color="#4f7cff", edgecolor="white")
        axis.set_xlabel(x_column)
        axis.set_ylabel("Records")
        title += " distribution"
    else:
        counts = Counter(str(row.get(x_column)) for row in rows if row.get(x_column) not in (None, ""))
        labels, values = zip(*counts.most_common(12)) if counts else ([], [])
        if not labels:
            raise ValueError(f"No usable values found for {x_column}.")
        axis.bar(labels, values, color="#4f7cff")
        axis.tick_params(axis="x", rotation=35)
        axis.set_ylabel("Records")
        title += " counts"

    axis.set_title(title)
    figure.tight_layout()
    CHARTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    chart_path = CHARTS_DIRECTORY / f"{_safe_filename(path.stem)}_{_safe_filename(x_column)}.png"
    figure.savefig(chart_path, dpi=160)
    plt.close(figure)
    return chart_path


def system_status():
    total, _, free = shutil.disk_usage(PROJECT_ROOT)
    return (
        f"System: {platform.system()} {platform.release()}\n"
        f"Python: {platform.python_version()}\n"
        f"Project drive: {free / 1024 ** 3:.1f} GB free of {total / 1024 ** 3:.1f} GB"
    )

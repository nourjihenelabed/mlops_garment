import subprocess
import os
import pandas as pd


def make_small_csv(path):
    df = pd.DataFrame({
        "department": ["A", "B"],
        "quarter": ["Quarter1", "Quarter1"],
        "day": ["Mon", "Tue"],
        "date": ["2020-01-01", "2020-01-02"],
        "wip": [10, 12],
        "no_of_workers": [2, 3],
        "idle_time": [1, 0],
        "idle_men": [1, 1],
        "over_time": [5, 6],
        "actual_productivity": [7.5, 8.0]
    })
    df.to_csv(path, index=False)
    return str(path)


def test_cli_prepare_and_cleanup(tmp_path, monkeypatch):
    csv = tmp_path / "small.csv"
    make_small_csv(csv)
    # run the CLI prepare step pointing to our small csv
    r = subprocess.run(
        ["python", "main.py", "--prepare", "--data_path", str(csv)],
        capture_output=True,
        text=True,
    )
    # main.py should exit 0
    assert r.returncode == 0

    # prepared_data.joblib should have been created in working dir
    assert os.path.exists("prepared_data.joblib")

    # Cleanup artifacts (safe for CI)
    try:
        os.remove("prepared_data.joblib")
    except FileNotFoundError:
        pass

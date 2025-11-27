import os
import pandas as pd
import model_pipeline as mp


def make_small_csv(path):
    # minimal dataset matching expected columns used by pipeline
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
    return path


def test_load_and_backup(tmp_path):
    csv = tmp_path / "small.csv"
    make_small_csv(csv)
    df = mp.load_data(str(csv))
    assert isinstance(df, pd.DataFrame)
    # backup should create a file; cleanup afterwards
    backup = mp.backup_dataset(str(csv))
    assert os.path.exists(backup)
    os.remove(backup)

import model_pipeline as mp
import pandas as pd


def make_small_df():
    return pd.DataFrame({
        "department": ["A", "B", "A", "B"],
        "quarter": ["Quarter1", "Quarter1", "Quarter2", "Quarter2"],
        "day": ["Mon", "Tue", "Wed", "Thu"],
        "date": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04"],
        "wip": [10, 12, 11, 9],
        "no_of_workers": [2, 3, 2, 1],
        "idle_time": [1, 0, 2, 0],
        "idle_men": [1, 1, 1, 1],
        "over_time": [5, 6, 4, 3],
        "actual_productivity": [7.5, 8.0, 7.0, 6.5]
    })


def test_prepare_train_pipeline(tmp_path):
    df = make_small_df()
    df = mp.clean_data(df)
    df = mp.engineer_features(df)
    X_train, X_test, y_train, y_test, pre = mp.prepare_data(df)

    model = mp.train_model(X_train, y_train, pre)
    assert model is not None
    assert hasattr(model, "predict")

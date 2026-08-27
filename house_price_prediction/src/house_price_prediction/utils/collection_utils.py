def check_equal(first, second):
    missing_columns = sorted(set(first) - set(second))
    if missing_columns:
        raise ValueError(f"House dataset is missing feature columns: {missing_columns}")

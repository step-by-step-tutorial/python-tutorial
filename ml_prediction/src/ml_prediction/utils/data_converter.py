def boolean_to_numeric(features, boolean_columns: tuple[str, ...]):
    for column in boolean_columns:
        features[column] = features[column].map({True: 1, False: 0, "True": 1, "False": 0})

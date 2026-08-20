class CsvGeneratorError(Exception):
    pass


class ConfigurationError(CsvGeneratorError):
    pass


class DependencyError(ConfigurationError):
    pass


class SourceDataError(CsvGeneratorError):
    pass


class DatasetNotFoundError(CsvGeneratorError):
    pass


class OutputNotFoundError(CsvGeneratorError):
    pass

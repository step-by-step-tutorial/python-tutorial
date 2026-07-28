"""Exception hierarchy for the CSV data generator.

Every error raised on purpose by this package derives from :class:`CsvGeneratorError`,
so callers — the CLI and the REST API — can map failures to exit codes or HTTP
statuses without catching bare ``Exception``.
"""

from __future__ import annotations


class CsvGeneratorError(Exception):
    """Base class for every error raised by this package."""


class ConfigurationError(CsvGeneratorError):
    """A config file is missing a key, or holds a value that cannot be used."""


class DependencyError(ConfigurationError):
    """Columns reference each other in a way that cannot be resolved."""


class SourceDataError(CsvGeneratorError):
    """A source text file or mapping CSV is missing, empty, or malformed."""


class DatasetNotFoundError(CsvGeneratorError):
    """No dataset config matches the requested name."""


class OutputNotFoundError(CsvGeneratorError):
    """The dataset exists but has not been generated yet."""

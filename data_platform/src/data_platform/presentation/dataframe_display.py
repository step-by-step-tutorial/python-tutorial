import logging
from collections.abc import Mapping

from pandas import DataFrame

try:
    from itables import show
except ImportError:
    def show(dataframe: DataFrame) -> None:
        print(dataframe)

logger = logging.getLogger(__name__)


def show_map_of_dataframe(map_of_dataframe: Mapping[str, DataFrame]) -> None:
    for key, value in map_of_dataframe.items():
        logger.info("%s", key)
        show(value)

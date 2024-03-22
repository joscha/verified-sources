from functools import reduce
from operator import getitem
from typing import Any, Sequence, Union, Tuple

from dlt.common import logger
from dlt.extract.source import DltSource


def join_url(base_url: str, path: str) -> str:
    if not base_url.endswith("/"):
        base_url += "/"
    return base_url + path.lstrip("/")


def create_nested_accessor(path: Union[str, Sequence[str]]) -> Any:
    if isinstance(path, (list, tuple)):
        return lambda d: reduce(getitem, path, d)
    return lambda d: d.get(path)


def check_connection(
    source: DltSource,
    *resource_names: str,
) -> Tuple[bool, str]:
    try:
        list(source.with_resources(*resource_names).add_limit(1))
        return (True, "")
    except Exception as e:
        logger.error(f"Error checking connection: {e}")
        return (False, str(e))

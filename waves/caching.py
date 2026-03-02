import logging

from flask_caching import Cache

from waves.config import CACHE_DEFAULT_TIMEOUT, DISABLE_CACHE

cache = Cache()
_logger = logging.getLogger(__name__)


def get_cache_config():
    if DISABLE_CACHE:
        _logger.warning(
            "Caching is disabled. This behaviour is not recommended for a production deployment."
        )
        return {
            "CACHE_TYPE": "NullCache",
        }
    _logger.info(
        f"Caching is enabled with a default timeout of {CACHE_DEFAULT_TIMEOUT} seconds."
    )
    return {
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    }

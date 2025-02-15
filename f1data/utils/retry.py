import logging
import time
from typing import Callable, TypeVar


T = TypeVar("T")

class Retry:

    def __init__(
        self,
        polling_interval_seconds: float,
        attempt_count: int,
        ignored_exceptions: tuple,
    ) -> None:
        self._polling_interval_seconds = polling_interval_seconds 
        self._attempt_count = attempt_count
        self._ignored_exceptions = ignored_exceptions

    def __call__(self, cb: Callable[..., T], *args, **kwargs) -> T:
        for i in range(self._attempt_count):
            try:
                return cb(*args, **kwargs)

            except self._ignored_exceptions as e:
                logging.warning(
                    f"Ignoring exception {e}, waiting for {self._polling_interval_seconds} ms"
                )
                time.sleep(self._polling_interval_seconds)

        raise RuntimeError("Max attempts exceeded")
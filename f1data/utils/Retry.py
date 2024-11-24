import logging
import time
from typing import Callable, Type, TypeVar
from asyncio import sleep


T = TypeVar("T")


class Retry:

    def __init__(
        self,
        polling_interval_seconds: float,
        timeout_seconds: float,
        ignored_exceptions: tuple[Type[Exception]],
    ) -> None:
        self._polling_interval_seconds = polling_interval_seconds 
        self._timeout = timeout_seconds
        self._ignored_exceptions = ignored_exceptions

    async def call(self, cb: Callable[..., T], *args, **kwargs) -> T:
        t_start = time.time()
        while time.time() - t_start < self._timeout:
            try:
                return cb(*args, **kwargs)

            except self._ignored_exceptions as e:
                logging.warning(
                    f"Ignoring exception {e}, waiting for {self._polling_interval_seconds} ms"
                )
                await sleep(self._polling_interval_seconds)

        raise RuntimeError("Max attempts exceeded")

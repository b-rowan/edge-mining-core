"""Collection of utility functions for adapters."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar("T")


def run_async_func(func: Callable[[], Coroutine[Any, Any, T]]) -> T:
    """
    Executes an asynchronous function (coroutine) from a synchronous context,
    handling the presence of an already running event loop.

    If no event loop is running, the coroutine is executed directly using asyncio.run().
    If an event loop is already running (e.g., in environments like FastAPI),
    the coroutine is executed in a separate thread to avoid conflicts with the main event loop.

    Args:
        func: A zero-argument function that returns a coroutine (e.g., lambda: my_async_func()).

    Returns:
        The result returned by the coroutine.

    Raises:
        Propagates any exceptions raised by the coroutine.
    """

    try:
        asyncio.get_running_loop()  # Triggers RuntimeError if no running event loop
        with ThreadPoolExecutor(1) as pool:
            return pool.submit(lambda: asyncio.run(func())).result()

    except RuntimeError:
        return asyncio.run(func())

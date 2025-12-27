"""Retry logic for message delivery."""

import asyncio
from typing import Callable, Optional, TypeVar
from functools import wraps
import httpx
from datetime import datetime, timezone

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (httpx.RequestError, httpx.HTTPStatusError),
) -> T:
    """Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 10.0)
        backoff_factor: Multiplier for delay on each retry (default: 2.0)
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Result of the function call
        
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                raise
    
    # Should never reach here, but for type checking
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry failed without exception")


async def send_message_with_retry(
    client: httpx.AsyncClient,
    endpoint: str,
    message: dict,
    max_retries: int = 3,
    timeout: float = 10.0,
) -> Optional[httpx.Response]:
    """Send HTTP message with retry logic.
    
    Args:
        client: HTTP client instance
        endpoint: Target endpoint URL
        message: Message payload as dictionary
        max_retries: Maximum retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 10.0)
        
    Returns:
        HTTP response if successful, None if all retries fail
    """
    async def _send():
        response = await client.post(endpoint, json=message, timeout=timeout)
        response.raise_for_status()
        return response
    
    try:
        return await retry_with_backoff(
            _send,
            max_retries=max_retries,
            initial_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0,
        )
    except Exception:
        return None


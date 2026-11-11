import time
import random
import psycopg2.errors
from functools import wraps
from fastapi import HTTPException, status


from typing import Optional


def with_psycopg2_retry(max_retries: int = 3, base_backoff_ms: int = 25, base_delay: Optional[float] = None):
    """
    Safely retries synchronous psycopg2 operations when PostgreSQL raises:
    - SerializationFailure (SQLSTATE 40001)
    - DeadlockDetected (SQLSTATE 40P01)
    Ensures connection is rolled back prior to retry.
    """
    if base_delay is not None:
        base_backoff_ms = max(1, int(base_delay * 1000))

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    pgcode = getattr(e, "pgcode", None)
                    is_conflict = (
                        isinstance(e, (psycopg2.errors.SerializationFailure, psycopg2.errors.DeadlockDetected)) or
                        pgcode in ("40001", "40P01")
                    )
                    if not is_conflict:
                        raise e

                    retries += 1
                    # Extract connection from kwargs or args if available
                    conn = kwargs.get("conn")
                    if conn and hasattr(conn, "rollback"):
                        try:
                            conn.rollback()
                        except Exception:
                            pass
                    elif len(args) > 1 and hasattr(args[1], "rollback"):
                        try:
                            args[1].rollback()
                        except Exception:
                            pass

                    if retries >= max_retries:
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Database transaction conflict under heavy concurrency. Please retry."
                        )
                    # Exponential backoff with random jitter
                    delay = (base_backoff_ms * (2 ** (retries - 1)) + random.uniform(5, 20)) / 1000.0
                    time.sleep(delay)
        return wrapper
    return decorator

import time
import threading
from collections import defaultdict
from fastapi import HTTPException, status
from typing import Dict, List

_LOCK = threading.Lock()
# In-memory sliding window rate limiter: key -> list of timestamps
_ATTEMPTS: Dict[str, List[float]] = defaultdict(list)
_BLOCKS: Dict[str, float] = {}
_LAST_CLEANUP: float = 0.0


def _cleanup_expired(now: float, window_seconds: int = 300):
    """Prunes expired attempts and blocks to prevent unbounded memory growth."""
    global _LAST_CLEANUP
    if now - _LAST_CLEANUP < 60:
        return
    _LAST_CLEANUP = now

    # Remove expired blocks
    expired_blocks = [k for k, unblock in list(_BLOCKS.items()) if now >= unblock]
    for k in expired_blocks:
        _BLOCKS.pop(k, None)

    # Remove empty or fully expired attempt lists
    cutoff = now - window_seconds
    expired_keys = []
    for k, timestamps in list(_ATTEMPTS.items()):
        valid = [t for t in timestamps if t > cutoff]
        if not valid:
            expired_keys.append(k)
        else:
            _ATTEMPTS[k] = valid
    for k in expired_keys:
        _ATTEMPTS.pop(k, None)


def check_rate_limit(
    key: str,
    max_requests: int = 5,
    window_seconds: int = 60,
    block_duration_seconds: int = 300,
):
    """
    Thread-safe sliding window rate limiter with temporary lockouts.
    Used to protect authentication and sensitive endpoints from brute-force attacks.
    """
    now = time.time()

    with _LOCK:
        _cleanup_expired(now, max(window_seconds, block_duration_seconds))

        # 1. Check if key is currently blocked
        if key in _BLOCKS:
            unblock_time = _BLOCKS[key]
            if now < unblock_time:
                remaining = int(unblock_time - now)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed attempts. Temporary lockout active for {remaining} seconds.",
                    headers={"Retry-After": str(remaining)},
                )
            else:
                del _BLOCKS[key]

        # 2. Filter out timestamps older than the window
        window_start = now - window_seconds
        valid_attempts = [t for t in _ATTEMPTS[key] if t > window_start]
        _ATTEMPTS[key] = valid_attempts

        # 3. Check threshold
        if len(valid_attempts) >= max_requests:
            _BLOCKS[key] = now + block_duration_seconds
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Locked out for {block_duration_seconds} seconds.",
                headers={"Retry-After": str(block_duration_seconds)},
            )

        # 4. Record new attempt
        _ATTEMPTS[key].append(now)


def record_failed_login(identifier: str):
    """Record a failed login attempt for an IP or username."""
    check_rate_limit(f"login_fail:{identifier}", max_requests=5, window_seconds=60, block_duration_seconds=300)


def check_account_lockout(identifier: str):
    """Checks whether an identifier is currently in lockout state without incrementing attempt count."""
    key = f"login_fail:{identifier}"
    now = time.time()
    with _LOCK:
        if key in _BLOCKS:
            unblock_time = _BLOCKS[key]
            if now < unblock_time:
                remaining = int(unblock_time - now)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many failed login attempts. Account temporarily locked for {remaining} seconds.",
                    headers={"Retry-After": str(remaining)},
                )
            else:
                del _BLOCKS[key]


def clear_rate_limit(identifier: str):
    """Reset rate limit counter on successful login."""
    with _LOCK:
        _ATTEMPTS.pop(f"login_fail:{identifier}", None)
        _BLOCKS.pop(f"login_fail:{identifier}", None)


def reset_all_rate_limits():
    """Testing helper to clear rate limiter state."""
    with _LOCK:
        _ATTEMPTS.clear()
        _BLOCKS.clear()

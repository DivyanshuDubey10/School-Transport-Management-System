import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from typing import Dict, List, Tuple

# In-memory sliding window rate limiter: key -> list of timestamps
_ATTEMPTS: Dict[str, List[float]] = defaultdict(list)
_BLOCKS: Dict[str, float] = {}


def check_rate_limit(
    key: str,
    max_requests: int = 5,
    window_seconds: int = 60,
    block_duration_seconds: int = 300,
):
    """
    Sliding window rate limiter with temporary lockouts.
    Used to protect authentication and sensitive endpoints from brute-force attacks.
    """
    now = time.time()

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
    _ATTEMPTS[key] = [t for t in _ATTEMPTS[key] if t > window_start]

    # 3. Check threshold
    if len(_ATTEMPTS[key]) >= max_requests:
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
    _ATTEMPTS.pop(f"login_fail:{identifier}", None)
    _BLOCKS.pop(f"login_fail:{identifier}", None)


def reset_all_rate_limits():
    """Testing helper to clear rate limiter state."""
    _ATTEMPTS.clear()
    _BLOCKS.clear()

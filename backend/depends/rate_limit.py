from fastapi import HTTPException
from util.rate_limiter import check_rate_limit

def enforce_rate_limit(
    user_id: int
):
    allowed = check_rate_limit(
        user_id=user_id
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )
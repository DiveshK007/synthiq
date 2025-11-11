"""
Middleware for rate limiting and request size validation
"""
import time
from collections import defaultdict
from typing import Callable
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-process token bucket rate limiter"""
    
    def __init__(self, app, requests_per_minute: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = requests_per_minute
        self.buckets: dict[str, dict] = defaultdict(lambda: {
            'tokens': requests_per_minute,
            'last_refill': time.time()
        })
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only rate limit POST /jobs
        if request.method == "POST" and request.url.path == "/jobs":
            client_ip = request.client.host if request.client else "unknown"
            bucket = self.buckets[client_ip]
            
            # Refill tokens
            now = time.time()
            elapsed = now - bucket['last_refill']
            tokens_to_add = (elapsed / 60.0) * self.tokens_per_minute
            bucket['tokens'] = min(
                self.tokens_per_minute,
                bucket['tokens'] + tokens_to_add
            )
            bucket['last_refill'] = now
            
            # Check if we have tokens
            if bucket['tokens'] < 1:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
                )
            
            # Consume token
            bucket['tokens'] -= 1
        
        response = await call_next(request)
        return response


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to reject requests larger than 2MB"""
    
    def __init__(self, app, max_size: int = 2 * 1024 * 1024):  # 2MB
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request body too large: {size} bytes (max {self.max_size} bytes)"
                    )
            except ValueError:
                pass  # Invalid content-length, let it through
        
        response = await call_next(request)
        return response


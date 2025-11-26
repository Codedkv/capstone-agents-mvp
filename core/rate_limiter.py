import asyncio
import time
from collections import deque

class RateLimiter:
    """Simple token bucket rate limiter for API calls."""
    
    def __init__(self, max_tokens_per_minute=900000, max_requests_per_minute=15):
        self.max_tokens = max_tokens_per_minute
        self.max_requests = max_requests_per_minute
        self.token_usage = deque(maxlen=60)  # Track last 60 seconds
        self.request_times = deque(maxlen=60)
    
    async def wait_if_needed(self, estimated_tokens=5000):
        """Wait if quota would be exceeded."""
        now = time.time()
        
        # Remove old entries (>60 seconds)
        while self.token_usage and self.token_usage[0][0] < now - 60:
            self.token_usage.popleft()
        
        while self.request_times and self.request_times[0] < now - 60:
            self.request_times.popleft()
        
        # Check if adding this request would exceed limits
        current_tokens = sum(t[1] for t in self.token_usage)
        current_requests = len(self.request_times)
        
        if current_tokens + estimated_tokens > self.max_tokens:
            wait_time = 60 - (now - self.token_usage[0][0])
            print(f"[RateLimiter] Token quota near limit, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time + 1)
        
        if current_requests >= self.max_requests:
            wait_time = 60 - (now - self.request_times[0])
            print(f"[RateLimiter] Request quota near limit, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time + 1)
        
        # Record this request
        self.token_usage.append((now, estimated_tokens))
        self.request_times.append(now)

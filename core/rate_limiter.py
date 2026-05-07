import asyncio
import os
import time
from collections import deque


# Free tier of gemini-2.5-flash is 5 RPM (as of 2026-05). Override with
# GEMINI_RPM in the environment when running on a paid quota.
DEFAULT_RPM = int(os.getenv("GEMINI_RPM", "5"))
DEFAULT_TPM = int(os.getenv("GEMINI_TPM", "250000"))


class RateLimiter:
    """Simple token bucket rate limiter for API calls."""

    def __init__(self, max_tokens_per_minute=DEFAULT_TPM, max_requests_per_minute=DEFAULT_RPM):
        self.max_tokens = max_tokens_per_minute
        self.max_requests = max_requests_per_minute
        self.token_usage = deque(maxlen=60)
        self.request_times = deque(maxlen=60)
        self._lock = asyncio.Lock()

    async def wait_if_needed(self, estimated_tokens=5000):
        """Wait if quota would be exceeded. Lock-protected so concurrent
        callers from different LLMAgents see a consistent counter — without
        the lock two coroutines can both pass the threshold check before
        either records its request."""
        async with self._lock:
            now = time.time()

            while self.token_usage and self.token_usage[0][0] < now - 60:
                self.token_usage.popleft()

            while self.request_times and self.request_times[0] < now - 60:
                self.request_times.popleft()

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

            self.token_usage.append((now, estimated_tokens))
            self.request_times.append(now)


# Process-wide singleton: Gemini quota is enforced per API key, not per
# client instance, so all GeminiClients in the same process must share
# one limiter to avoid 429s. Re-created lazily so that an explicit
# get_shared_limiter() call after env mutation picks up the new RPM.
_shared_limiter: RateLimiter | None = None


def get_shared_limiter() -> RateLimiter:
    global _shared_limiter
    if _shared_limiter is None:
        _shared_limiter = RateLimiter()
    return _shared_limiter

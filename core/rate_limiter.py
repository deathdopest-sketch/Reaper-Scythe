# Token-bucket rate limiter

from __future__ import annotations
import time
from dataclasses import dataclass

@dataclass
class RateLimitConfig:
	rate_per_second: float
	burst: int = 1

class TokenBucket:
	def __init__(self, rate_per_second: float, burst: int = 1) -> None:
		if rate_per_second <= 0:
			raise ValueError("rate_per_second must be > 0")
		if burst <= 0:
			raise ValueError("burst must be > 0")
		self.rate = rate_per_second
		self.capacity = float(burst)
		self.tokens = float(burst)
		self.last = time.monotonic()

	def try_acquire(self, tokens: float = 1.0) -> bool:
		"""Attempt to take tokens; return True if allowed, False if rate-limited."""
		if tokens <= 0:
			return True
		now = time.monotonic()
		elapsed = now - self.last
		self.last = now
		# Refill
		self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
		if self.tokens >= tokens:
			self.tokens -= tokens
			return True
		return False

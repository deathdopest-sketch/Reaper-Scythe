# SecureString for sensitive data handling
# Stores contents in a mutable bytearray and supports zeroization

from __future__ import annotations
from typing import Optional
import hmac

class SecureString:
	"""A memory-conscious secure string wrapper.
	
	- Stores data in a bytearray to allow in-place zeroization
	- Optional zeroize on deletion
	- Constant-time equality comparison
	- Bounded length checks to mitigate accidental large allocations
	"""

	__slots__ = ("_buf", "_zeroize_on_del")

	def __init__(self, data: bytes, zeroize_on_del: bool = True, max_length: int = 1_000_000) -> None:
		if not isinstance(data, (bytes, bytearray)):
			raise TypeError("SecureString data must be bytes or bytearray")
		if len(data) > max_length:
			raise ValueError(f"SecureString length {len(data)} exceeds maximum {max_length}")
		self._buf = bytearray(data)
		self._zeroize_on_del = zeroize_on_del

	@classmethod
	def from_plain(cls, text: str, encoding: str = "utf-8", zeroize_on_del: bool = True, max_length: int = 1_000_000) -> "SecureString":
		if not isinstance(text, str):
			raise TypeError("text must be str")
		return cls(text.encode(encoding), zeroize_on_del=zeroize_on_del, max_length=max_length)

	def to_plain(self, encoding: str = "utf-8") -> str:
		"""Convert to a Python str. Note: resulting str cannot be zeroized."""
		return self._buf.decode(encoding)

	def to_bytes(self) -> bytes:
		return bytes(self._buf)

	def clear(self) -> None:
		"""Zeroize the underlying buffer in place."""
		for i in range(len(self._buf)):
			self._buf[i] = 0

	def __len__(self) -> int:
		return len(self._buf)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, SecureString):
			return False
		return hmac.compare_digest(self._buf, other._buf)

	def __repr__(self) -> str:
		return f"SecureString(len={len(self._buf)})"

	def __del__(self) -> None:
		if getattr(self, "_zeroize_on_del", False):
			try:
				self.clear()
			except Exception:
				# Never raise from __del__
				pass

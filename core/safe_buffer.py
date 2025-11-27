# SafeBuffer for memory-safe operations

from __future__ import annotations
from typing import Iterable

class SafeBuffer:
	"""A bounds-checked byte buffer with zeroization support."""

	__slots__ = ("_buf",)

	def __init__(self, size: int = 0, data: Iterable[int] | bytes | bytearray | None = None):
		if size < 0:
			raise ValueError("size must be >= 0")
		if data is not None:
			if isinstance(data, (bytes, bytearray)):
				self._buf = bytearray(data)
			else:
				self._buf = bytearray(int(b) & 0xFF for b in data)
		else:
			self._buf = bytearray(size)

	def __len__(self) -> int:
		return len(self._buf)

	def read(self, offset: int, length: int) -> bytes:
		self._check_bounds(offset, length)
		return bytes(self._buf[offset:offset+length])

	def write(self, offset: int, data: bytes | bytearray) -> None:
		if not isinstance(data, (bytes, bytearray)):
			raise TypeError("data must be bytes-like")
		self._check_bounds(offset, len(data))
		self._buf[offset:offset+len(data)] = data

	def append(self, data: bytes | bytearray) -> None:
		if not isinstance(data, (bytes, bytearray)):
			raise TypeError("data must be bytes-like")
		self._buf.extend(data)

	def clear(self) -> None:
		for i in range(len(self._buf)):
			self._buf[i] = 0

	def to_bytes(self) -> bytes:
		return bytes(self._buf)

	def _check_bounds(self, offset: int, length: int) -> None:
		if offset < 0 or length < 0:
			raise IndexError("negative offset/length")
		end = offset + length
		if end > len(self._buf):
			raise IndexError("buffer access out of bounds")

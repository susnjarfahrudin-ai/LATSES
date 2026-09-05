"""Best-effort explicit clearing of mutable sensitive buffers."""
from __future__ import annotations

import ctypes


def secure_zero(buffer: bytearray) -> None:
    """Overwrite a mutable byte buffer in-place with zero bytes."""
    if not isinstance(buffer, bytearray):
        raise TypeError("secure_zero requires bytearray so the caller retains a mutable buffer")
    if not buffer:
        return
    view = (ctypes.c_char * len(buffer)).from_buffer(buffer)
    ctypes.memset(view, 0, len(buffer))


__all__ = ["secure_zero"]

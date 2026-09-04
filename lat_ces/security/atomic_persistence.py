"""Crash-resistant file replacement primitives."""
from __future__ import annotations

import os
from pathlib import Path


def atomic_write_bytes(path: str | os.PathLike[str], data: bytes) -> None:
    """Write bytes to a temp file, fsync it, then atomically replace the target.

    On POSIX, the containing directory is fsynced after ``os.replace`` so the
    rename itself is durable across a sudden restart as far as the filesystem
    contract permits. Windows does not expose the same directory-fsync API.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.tmp-{os.getpid()}-{os.urandom(6).hex()}")
    try:
        with open(temp, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, target)
        if os.name == "posix":
            directory_fd = os.open(target.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
        raise IOError(f"atomic persistence failed for {target}") from exc


__all__ = ["atomic_write_bytes"]

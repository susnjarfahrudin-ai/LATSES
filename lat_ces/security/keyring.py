"""OS-backed secret storage and versioned HKDF key derivation."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Protocol

from .secure_memory import secure_zero


class SecretStore(Protocol):
    """Minimal backend contract; production uses an OS keyring implementation."""

    def get_password(self, service: str, account: str) -> str | None: ...
    def set_password(self, service: str, account: str, password: str) -> None: ...


def _os_keyring() -> SecretStore:
    try:
        import keyring
    except ImportError as exc:
        raise RuntimeError("OS keyring backend unavailable; install the keyring package") from exc
    return keyring


def hkdf_sha256(ikm: bytes | bytearray, *, salt: bytes = b"", info: bytes = b"", length: int = 32) -> bytearray:
    """RFC 5869 HKDF-SHA256 without retaining a mutable copy in the result owner."""
    if length <= 0 or length > 255 * hashlib.sha256().digest_size:
        raise ValueError("invalid HKDF output length")
    if not salt:
        salt = bytes(hashlib.sha256().digest_size)
    prk = hmac.new(salt, bytes(ikm), hashlib.sha256).digest()
    output = bytearray()
    previous = b""
    try:
        for counter in range(1, (length + 31) // 32 + 1):
            previous = hmac.new(prk, previous + info + bytes([counter]), hashlib.sha256).digest()
            output.extend(previous)
        return output[:length]
    finally:
        previous = b""
        prk = bytes(len(prk))


@dataclass(frozen=True)
class KeyVersion:
    version: int
    account: str


class KeyRing:
    """Versioned root secrets stored only through an OS keyring backend."""

    def __init__(self, service: str = "LAT-CES", *, store: SecretStore | None = None) -> None:
        if not service:
            raise ValueError("service must be non-empty")
        self._service = service
        self._store = store if store is not None else _os_keyring()
        self._current_account = "root/current-version"

    def initialize(self) -> int:
        """Create v1 when absent; never overwrite an existing root secret."""
        current = self._store.get_password(self._service, self._current_account)
        if current is not None:
            return int(current)
        version = 1
        self._store_root(version, bytearray(os.urandom(32)))
        self._store.set_password(self._service, self._current_account, str(version))
        return version

    def rotate(self) -> int:
        current = self.current_version()
        next_version = current + 1
        self._store_root(next_version, bytearray(os.urandom(32)))
        self._store.set_password(self._service, self._current_account, str(next_version))
        return next_version

    def current_version(self) -> int:
        current = self._store.get_password(self._service, self._current_account)
        if current is None:
            return self.initialize()
        try:
            version = int(current)
        except ValueError as exc:
            raise RuntimeError("keyring current-version record is corrupt") from exc
        if version < 1:
            raise RuntimeError("invalid keyring version")
        return version

    def _account(self, version: int) -> str:
        if version < 1:
            raise ValueError("version must be >= 1")
        return f"root/v{version}"

    def _store_root(self, version: int, root: bytearray) -> None:
        try:
            encoded = base64.b64encode(root).decode("ascii")
            self._store.set_password(self._service, self._account(version), encoded)
        finally:
            secure_zero(root)

    @contextmanager
    def borrow_root_key(self, version: int | None = None) -> Iterator[bytearray]:
        selected = self.current_version() if version is None else version
        encoded = self._store.get_password(self._service, self._account(selected))
        if encoded is None:
            raise KeyError(f"root key version v{selected} not found")
        try:
            root = bytearray(base64.b64decode(encoded, validate=True))
        except Exception as exc:
            raise RuntimeError("keyring secret is not valid base64") from exc
        if len(root) != 32:
            secure_zero(root)
            raise RuntimeError("root key must be 256 bits")
        try:
            yield root
        finally:
            secure_zero(root)

    @contextmanager
    def borrow_derived_key(self, *, purpose: bytes, version: int | None = None, length: int = 32) -> Iterator[bytearray]:
        with self.borrow_root_key(version) as root:
            derived = hkdf_sha256(root, info=purpose, length=length)
        try:
            yield derived
        finally:
            secure_zero(derived)


__all__ = ["KeyRing", "KeyVersion", "SecretStore", "hkdf_sha256"]

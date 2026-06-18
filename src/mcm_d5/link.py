"""CAN link abstraction (read side only).

A :class:`Link` is anything that can yield received J1939 frames. The package
deliberately models only the receive direction — there is no ``send`` — so it
can be used for passive monitoring, logging, and decoding without any ability
to transmit, request security access, or write to a control module.

Implementations:
- :class:`ReplayLink` — feed frames from a list or a recorded log (offline,
  used by the tests; no hardware needed).
- :class:`PythonCanLink` — thin adapter over the optional ``python-can``
  package for live capture from a real adapter (J2534/RP1210/SocketCAN).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Optional, Protocol, runtime_checkable

from mcm_d5.frame import J1939Frame


@runtime_checkable
class Link(Protocol):
    """Read-only source of J1939 frames."""

    def recv(self, timeout: float = 1.0) -> Optional[J1939Frame]:
        """Return the next frame, or ``None`` if none arrived before timeout."""
        ...

    def close(self) -> None:
        ...


class ReplayLink:
    """In-memory / log-backed link for offline decoding and tests."""

    def __init__(self, frames: Iterable[J1939Frame]) -> None:
        self._frames: Iterator[J1939Frame] = iter(list(frames))

    def recv(self, timeout: float = 1.0) -> Optional[J1939Frame]:
        return next(self._frames, None)

    def close(self) -> None:  # nothing to release
        pass


class PythonCanLink:
    """Live capture adapter over the optional ``python-can`` library.

    Receive-only by construction: it reads from a ``can.BusABC`` and never
    calls ``bus.send``. Install the extra with ``pip install mcm-d5[can]``.
    """

    def __init__(self, bus) -> None:  # type: ignore[no-untyped-def]
        self._bus = bus

    @classmethod
    def open(cls, channel: str, interface: str = "socketcan", **kwargs) -> PythonCanLink:
        try:
            import can  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on optional dep
            raise ImportError(
                "PythonCanLink requires the 'can' package; install with "
                "pip install 'mcm-d5[can]'"
            ) from exc
        bus = can.Bus(channel=channel, interface=interface, **kwargs)
        return cls(bus)

    def recv(self, timeout: float = 1.0) -> Optional[J1939Frame]:
        msg = self._bus.recv(timeout=timeout)
        if msg is None:
            return None
        return J1939Frame.from_can_id(msg.arbitration_id, bytes(msg.data))

    def close(self) -> None:  # pragma: no cover - depends on optional dep
        self._bus.shutdown()

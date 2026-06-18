"""Command-line entry point: ``mcm-d5``.

Subcommands:
  monitor      connect to a CAN adapter and print live data + DTCs (read-only)
  decode-log   decode a capture file (candump/CSV/asc/blf) offline

Both are strictly read-only: there is no command that transmits control
requests, unlocks, clears codes, or writes to a module.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from mcm_d5.frame import J1939Frame
from mcm_d5.logreader import open_log
from mcm_d5.monitor import J1939Monitor


def _attach_printers(monitor: J1939Monitor) -> None:
    monitor.on_signal(lambda name, value, frame: print(f"{name:46s} {value:12.3f}"))

    def show_dtcs(diag, frame: J1939Frame) -> None:
        lamps = "MIL" if diag.malfunction_indicator_lamp else "---"
        print(f"[DTC] src=0x{frame.source:02X} lamps={lamps} count={len(diag.dtcs)}")
        for dtc in diag.dtcs:
            print(f"      SPN {dtc.spn} FMI {dtc.fmi} (x{dtc.occurrence_count})")

    monitor.on_diagnostic(show_dtcs)
    monitor.on_readiness(
        lambda r, frame: print(
            f"[DM5] active={r.active_trouble_codes} "
            f"prev={r.previously_active_trouble_codes} obd=0x{r.obd_compliance:02X}"
        )
    )


def _cmd_decode_log(args: argparse.Namespace) -> int:
    monitor = J1939Monitor(open_log(args.path))
    _attach_printers(monitor)
    processed = monitor.pump()
    print(f"\nProcessed {processed} frames.", file=sys.stderr)
    return 0


def _cmd_monitor(args: argparse.Namespace) -> int:
    from mcm_d5.link import PythonCanLink

    link = PythonCanLink.open(args.channel, interface=args.interface, bitrate=args.bitrate)
    monitor = J1939Monitor(link)
    _attach_printers(monitor)
    print(
        f"Listening on {args.interface}:{args.channel} @ {args.bitrate} "
        "(Ctrl-C to stop)...",
        file=sys.stderr,
    )
    try:
        monitor.pump(timeout=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        link.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcm-d5", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_mon = sub.add_parser("monitor", help="live read from a CAN adapter")
    p_mon.add_argument("--interface", default="socketcan")
    p_mon.add_argument("--channel", default="can0")
    p_mon.add_argument("--bitrate", type=int, default=250000)
    p_mon.set_defaults(func=_cmd_monitor)

    p_log = sub.add_parser("decode-log", help="decode a capture file offline")
    p_log.add_argument("path", help="candump/.csv/.asc/.blf capture file")
    p_log.set_defaults(func=_cmd_decode_log)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

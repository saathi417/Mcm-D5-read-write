"""Connect to a CAN adapter and print live J1939 data + fault codes.

Read-only: opens the bus for receive, decodes broadcast signals, and prints
DM1/DM2 fault codes. It never transmits.

Usage:
    pip install 'mcm-d5[can]'
    python examples/live_monitor.py --interface socketcan --channel can0

For a NEXIQ / RP1210 or J2534 adapter, use the matching python-can interface
(see the python-can docs); the decoding is identical regardless of adapter.
"""

import argparse

from mcm_d5 import J1939Monitor, PythonCanLink


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="socketcan", help="python-can interface")
    parser.add_argument("--channel", default="can0", help="adapter channel")
    parser.add_argument("--bitrate", type=int, default=250000, help="J1939 bitrate")
    args = parser.parse_args()

    link = PythonCanLink.open(args.channel, interface=args.interface, bitrate=args.bitrate)
    monitor = J1939Monitor(link)

    monitor.on_signal(lambda name, value, frame: print(f"{name:42s} {value:10.3f}"))

    def show_dtcs(diag, frame):
        lamps = "MIL" if diag.malfunction_indicator_lamp else "---"
        print(f"[DTC] lamps={lamps} count={len(diag.dtcs)}")
        for dtc in diag.dtcs:
            print(f"      SPN {dtc.spn} FMI {dtc.fmi} (x{dtc.occurrence_count})")

    monitor.on_diagnostic(show_dtcs)

    print(f"Listening on {args.interface}:{args.channel} @ {args.bitrate} (Ctrl-C to stop)...")
    try:
        monitor.pump(timeout=1.0)  # runs until the bus goes idle / interrupted
    except KeyboardInterrupt:
        pass
    finally:
        link.close()


if __name__ == "__main__":
    main()

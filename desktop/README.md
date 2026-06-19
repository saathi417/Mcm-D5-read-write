# MCM D5 Viewer — read-only WPF + C++ desktop GUI

A Windows desktop viewer that decodes J1939 live data and DM1/DM2 fault codes
through a native C++ core. It is **read-only**: it replays/decodes CAN data and
displays it. There is no transmit, security access, code clearing, derate
reset, or flash read/write — by design, the native core exports no such
function.

```
desktop/
  core/                  C++ native decode library (mcmcore.dll)
    include/mcm_core.h   C ABI (decode-only)
    src/mcm_core.cpp     J1939 PGN/SPN decode + DM1 parsing
    test/                self-test (parity with the Python lib)
    CMakeLists.txt
  app/                   C# WPF front-end (P/Invokes mcmcore)
    *.csproj, *.xaml, *.cs
```

This mirrors the Python library in `../src/mcm_d5`; keep the SPN tables in
`core/src/mcm_core.cpp` and `signals.py` in sync.

```
desktop/
  core/include/iecu_plugin.h   read-only OEM plugin contract
  plugins/detroit/             DetroitPlugin (read-only identify + decode)
  plugins/cummins/             CumminsPlugin (read-only)
  plugins/paccar/              PaccarPlugin  (read-only)
```

The core also exposes `mcm_fmi_text()` — standard SAE J1939-73 Failure Mode
Identifier descriptions — so fault codes show human-readable failure modes.
Plugins add OEM-specific SPN text on top via `DtcText()`.

## Scope (read-only)

The native core exposes decode helpers plus exactly one transmit helper —
`mcm_build_request_pgn`, which builds a J1939 *Request PGN* frame (it solicits
a broadcast; it carries no payload and cannot write). The supported feature set
is: connect/receive, vehicle discovery, read VIN / ECU IDs, read DTCs (DM1/DM2),
live data, and log saving.

Out of scope by design — not implemented here: **Clear DTCs** (UDS 0x14 / DM11),
SecurityAccess unlock (0x27), RequestDownload/Upload/TransferData (0x34–0x37),
WriteMemoryByAddress/WriteDataByIdentifier, any flash program/erase, and any
"Programming" UI. The `IEcuPlugin` contract has no programming entry point;
keep it that way.

## Build

**Native core** (produces `mcmcore.dll`):

```bash
cd desktop/core
cmake -B build -DMCM_BUILD_TESTS=ON
cmake --build build --config Release
ctest --test-dir build         # runs the decode self-test
```

**WPF app** (Windows, .NET 8 SDK):

```bash
cd desktop/app
dotnet build -c Release
# copy the built mcmcore.dll next to McmD5Viewer.exe (same folder)
```

> The C++ core is portable and is verified on Linux/macOS via its self-test.
> The WPF app requires Windows (`net8.0-windows`, `UseWPF`) and is built there;
> it was not compiled in the authoring environment.

## Use

Launch `McmD5Viewer.exe`, click **Open Log…**, choose a `candump` capture, and
press **Play**. Live signals update in the left grid; DM1/DM2 fault codes and
lamp status appear on the right. A live RP1210/J2534 capture source can be
added later behind the same read-only decode path.

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

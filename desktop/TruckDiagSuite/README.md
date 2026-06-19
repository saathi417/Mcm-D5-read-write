# TruckDiagSuite — read-only multi-OEM truck diagnostics

A layered Windows diagnostic application. **Read-only by design**: it connects,
discovers vehicles/modules, reads VIN, ECU IDs, DTCs, and live data, and saves
logs. It contains no Clear-DTC, SecurityAccess unlock, download/transfer, flash
program/erase, or "Programming" UI — and the interfaces have no entry point for
any of those.

```
TruckDiagSuite/
  TruckDiagSuite.sln
  TruckDiag.Core/        C# business logic — NativeEngine P/Invoke,
                         DiagnosticSession, models, IEcuPlugin, PluginLoader, Fmi
  TruckDiag.Database/    C# SQLite — repository + DefinitionSeeder
                         (Vehicles/Modules/FaultCodes/Definitions/Logs)
  TruckDiag.Plugins.Detroit/  managed read-only plugin (loaded by PluginLoader)
  TruckDiag.UI/          C# WPF — Dashboard, Vehicle Discovery, Fault Codes,
                         Live Data, Logs, Settings (no Programming tab)
  NativeEngine/          C++ DLL — ITransport (receive + Request-PGN only),
                         decode via mcm_core, C ABI for Core
```

Plugins (`../plugins/detroit`, …) implement the read-only `IEcuPlugin` contract
for OEM identify/decode. The native decode core is shared with `../core`.

## Read-only boundary

| Layer | What it does | What it does not do |
|-------|--------------|---------------------|
| NativeEngine / ITransport | connect, receive, J1939 Request-PGN | arbitrary send, write, program |
| J1939 / UDS | RequestPGN, TP reassembly, UDS reads (0x22/0x19/0x3E) | 0x27 unlock, 0x34–0x37, writes |
| UI | 6 read tabs | no Programming tab |
| Actions | Read VIN/IDs/DTCs, Live Data, Save Logs | no Clear DTCs |

## Build

**NativeEngine** (C++ → `NativeEngine.dll`):

```bash
cd NativeEngine
cmake -B build -DMCM_BUILD_TESTS=ON
cmake --build build --config Release
ctest --test-dir build          # read-only engine self-test
```

**Managed solution** (Windows, .NET 8 SDK):

```bash
cd TruckDiagSuite
dotnet build TruckDiagSuite.sln -c Release
# copy NativeEngine.dll next to TruckDiag.exe; run as 64-bit to match the DLL.
```

> The C++ NativeEngine + core are verified via their self-tests on any
> platform. `TruckDiag.UI` is WPF (`net8.0-windows`) and builds on Windows; it
> was not compiled in the authoring environment.

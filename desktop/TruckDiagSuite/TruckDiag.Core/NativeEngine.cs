using System.Runtime.InteropServices;

namespace TruckDiag.Core;

/// <summary>
/// P/Invoke bindings to NativeEngine.dll. Read-only: connect, poll decoded
/// events, and emit J1939 Request-PGN solicitations. No clear/unlock/program.
/// </summary>
public static class NativeEngine
{
    private const string Dll = "NativeEngine";

    public const int EventNone = 0;
    public const int EventSignals = 1;
    public const int EventDtcs = 2;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
    public struct SignalValue
    {
        public int Spn;
        public double Value;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string Name;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 16)]
        public string Unit;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct Dtc
    {
        public int Spn;
        public int Fmi;
        public int OccurrenceCount;
        public int Pad;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct Lamps
    {
        public int Mil;
        public int RedStop;
        public int AmberWarning;
        public int Protect;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct FrameEvent
    {
        public int Kind;
        public int Pgn;
        public int Source;
        public int SignalCount;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)]
        public SignalValue[] Signals;

        public int DtcCount;

        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 32)]
        public Dtc[] Dtcs;

        public Lamps Lamps;
    }

    [DllImport(Dll, CharSet = CharSet.Ansi, CallingConvention = CallingConvention.Cdecl)]
    public static extern IntPtr mcm_engine_open_replay(string candumpPath);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_engine_connect(IntPtr engine);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_engine_poll(IntPtr engine, ref FrameEvent ev);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_engine_request_pgn(IntPtr engine, int pgn, byte dest, byte src);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern void mcm_engine_close(IntPtr engine);
}

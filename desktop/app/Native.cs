using System.Runtime.InteropServices;

namespace McmD5Viewer;

/// <summary>
/// P/Invoke bindings into the read-only native core (mcmcore.dll).
/// Mirrors desktop/core/include/mcm_core.h. Decode-only — no transmit/write.
/// </summary>
internal static class Native
{
    private const string Dll = "mcmcore";

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
    public struct McmSignalValue
    {
        public int spn;
        public double value;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 64)]
        public string name;

        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 16)]
        public string unit;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct McmDtc
    {
        public int spn;
        public int fmi;
        public int occurrence_count;
        public int _pad;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct McmLamps
    {
        public int mil;
        public int red_stop;
        public int amber_warning;
        public int protect;
    }

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_pgn_from_can_id(uint canId);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_source_from_can_id(uint canId);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_decode_pgn(
        int pgn, byte[] data, int len, [Out] McmSignalValue[] outValues, int max);

    [DllImport(Dll, CallingConvention = CallingConvention.Cdecl)]
    public static extern int mcm_parse_dm1(
        byte[] data, int len, ref McmLamps lamps, [Out] McmDtc[] outDtcs, int max);
}

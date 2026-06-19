namespace TruckDiag.Core;

/// <summary>
/// Standard SAE J1939-73 Failure Mode Identifier (FMI) text. Mirrors the
/// native mcm_fmi_text() so managed code can describe faults offline.
/// </summary>
public static class Fmi
{
    /// <summary>FMI values with standardized text (0-21 and 31).</summary>
    public static readonly IReadOnlyList<int> Standard =
        new[] { 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 31 };

    public static string Text(int fmi) => fmi switch
    {
        0 => "Data valid but above normal operational range (most severe)",
        1 => "Data valid but below normal operational range (most severe)",
        2 => "Data erratic, intermittent or incorrect",
        3 => "Voltage above normal or shorted high",
        4 => "Voltage below normal or shorted low",
        5 => "Current below normal or open circuit",
        6 => "Current above normal or grounded circuit",
        7 => "Mechanical system not responding properly",
        8 => "Abnormal frequency, pulse width or period",
        9 => "Abnormal update rate",
        10 => "Abnormal rate of change",
        11 => "Root cause not known",
        12 => "Bad intelligent device or component",
        13 => "Out of calibration",
        14 => "Special instructions",
        15 => "Data valid but above normal operating range (least severe)",
        16 => "Data valid but above normal operating range (moderately severe)",
        17 => "Data valid but below normal operating range (least severe)",
        18 => "Data valid but below normal operating range (moderately severe)",
        19 => "Received network data in error",
        20 => "Data drifted high",
        21 => "Data drifted low",
        31 => "Condition exists",
        _ => "Unknown FMI",
    };
}

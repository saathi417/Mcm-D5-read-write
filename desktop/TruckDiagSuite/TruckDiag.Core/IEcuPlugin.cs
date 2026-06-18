namespace TruckDiag.Core;

/// <summary>
/// Managed read-only OEM plugin contract (Detroit/Cummins/Paccar). Mirrors the
/// native IEcuPlugin: identify a module and supply decode/DTC text. There is no
/// programming or DTC-clear method — keep it read-only.
/// </summary>
public interface IEcuPlugin
{
    string Name { get; }

    bool Identify(EcuModule module);

    /// <summary>OEM-specific text for an SPN/FMI, or null to use the default.</summary>
    string? DtcText(int spn, int fmi);
}

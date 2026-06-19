using TruckDiag.Core;

namespace TruckDiag.Plugins.Detroit;

/// <summary>
/// Managed read-only Detroit Diesel plugin, loadable via PluginLoader. Provides
/// identification and OEM fault text only — no programming/clear/unlock.
/// </summary>
public sealed class DetroitPlugin : IEcuPlugin
{
    public string Name => "Detroit Diesel";

    public bool Identify(EcuModule module)
        => module.ComponentId.Contains("DDEC", StringComparison.OrdinalIgnoreCase)
           || module.ComponentId.Contains("DD", StringComparison.OrdinalIgnoreCase);

    public string? DtcText(int spn, int fmi) => (spn, fmi) switch
    {
        (1761, 1) => "Aftertreatment 1 DEF Tank Level Low",
        (3226, _) => "Aftertreatment 1 Outlet NOx sensor",
        _ => null,
    };
}

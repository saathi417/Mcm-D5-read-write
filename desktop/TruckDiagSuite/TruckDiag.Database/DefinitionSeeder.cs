using TruckDiag.Core;

namespace TruckDiag.Database;

/// <summary>
/// Seeds the read-only Definitions table with offline fault descriptions,
/// composed from an SPN-name map and the standard FMI text. Lets the UI show
/// "&lt;SPN name&gt;: &lt;failure mode&gt;" without a network lookup.
/// </summary>
public static class DefinitionSeeder
{
    /// <summary>
    /// Insert (spn, fmi) -&gt; "name: fmi text" rows for every supplied SPN
    /// across the standard FMIs. Returns the number of rows written.
    /// </summary>
    public static int Seed(DiagRepository repository, IReadOnlyDictionary<int, string> spnNames)
    {
        int written = 0;
        foreach (KeyValuePair<int, string> entry in spnNames)
        {
            foreach (int fmi in Fmi.Standard)
            {
                repository.UpsertDefinition(entry.Key, fmi, $"{entry.Value}: {Fmi.Text(fmi)}");
                written++;
            }
        }

        return written;
    }
}

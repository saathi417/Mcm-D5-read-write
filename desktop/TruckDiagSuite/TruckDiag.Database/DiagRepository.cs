using Microsoft.Data.Sqlite;
using TruckDiag.Core;

namespace TruckDiag.Database;

/// <summary>
/// SQLite persistence for vehicles, modules, fault codes, definitions, and
/// logs. Stores diagnostic results only — no programming artifacts.
/// </summary>
public sealed class DiagRepository : IDisposable
{
    private readonly SqliteConnection _conn;

    public DiagRepository(string databasePath)
    {
        _conn = new SqliteConnection($"Data Source={databasePath}");
        _conn.Open();
    }

    /// <summary>Apply schema.sql (idempotent).</summary>
    public void Initialize(string schemaSqlPath)
    {
        string sql = File.ReadAllText(schemaSqlPath);
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText = sql;
        cmd.ExecuteNonQuery();
    }

    public long UpsertVehicle(Vehicle vehicle)
    {
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText =
            "INSERT INTO Vehicles (Vin, Make, Model) VALUES ($vin, $make, $model) " +
            "ON CONFLICT(Vin) DO UPDATE SET Make=$make, Model=$model; " +
            "SELECT Id FROM Vehicles WHERE Vin=$vin;";
        cmd.Parameters.AddWithValue("$vin", vehicle.Vin);
        cmd.Parameters.AddWithValue("$make", vehicle.Make);
        cmd.Parameters.AddWithValue("$model", vehicle.Model);
        return (long)(cmd.ExecuteScalar() ?? 0L);
    }

    public void InsertFaultCode(long moduleId, FaultCode fault)
    {
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText =
            "INSERT INTO FaultCodes (ModuleId, Spn, Fmi, OccurrenceCount, CapturedAt) " +
            "VALUES ($m, $spn, $fmi, $oc, $ts);";
        cmd.Parameters.AddWithValue("$m", moduleId);
        cmd.Parameters.AddWithValue("$spn", fault.Spn);
        cmd.Parameters.AddWithValue("$fmi", fault.Fmi);
        cmd.Parameters.AddWithValue("$oc", fault.OccurrenceCount);
        cmd.Parameters.AddWithValue("$ts", DateTime.UtcNow.ToString("o"));
        cmd.ExecuteNonQuery();
    }

    public string? LookupDefinition(int spn, int fmi)
    {
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText = "SELECT Description FROM Definitions WHERE Spn=$spn AND Fmi=$fmi;";
        cmd.Parameters.AddWithValue("$spn", spn);
        cmd.Parameters.AddWithValue("$fmi", fmi);
        return cmd.ExecuteScalar() as string;
    }

    public void UpsertDefinition(int spn, int fmi, string description)
    {
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText =
            "INSERT INTO Definitions (Spn, Fmi, Description) VALUES ($spn, $fmi, $desc) " +
            "ON CONFLICT(Spn, Fmi) DO UPDATE SET Description=$desc;";
        cmd.Parameters.AddWithValue("$spn", spn);
        cmd.Parameters.AddWithValue("$fmi", fmi);
        cmd.Parameters.AddWithValue("$desc", description);
        cmd.ExecuteNonQuery();
    }

    public void Log(string source, string message)
    {
        using SqliteCommand cmd = _conn.CreateCommand();
        cmd.CommandText = "INSERT INTO Logs (CreatedAt, Source, Message) VALUES ($ts, $src, $msg);";
        cmd.Parameters.AddWithValue("$ts", DateTime.UtcNow.ToString("o"));
        cmd.Parameters.AddWithValue("$src", source);
        cmd.Parameters.AddWithValue("$msg", message);
        cmd.ExecuteNonQuery();
    }

    public void Dispose() => _conn.Dispose();
}

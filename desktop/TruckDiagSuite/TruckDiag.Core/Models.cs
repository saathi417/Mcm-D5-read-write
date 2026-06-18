namespace TruckDiag.Core;

/// <summary>An identified vehicle (read from VIN / address claim).</summary>
public sealed record Vehicle(string Vin, string Make, string Model);

/// <summary>An ECU/module on the bus.</summary>
public sealed record EcuModule(int SourceAddress, string Name, string SoftwareId, string ComponentId);

/// <summary>A decoded diagnostic trouble code.</summary>
public sealed record FaultCode(int Spn, int Fmi, int OccurrenceCount, int Source, string? Description);

/// <summary>A single live-data sample.</summary>
public sealed record SignalSample(int Spn, string Name, double Value, string Unit, DateTime Timestamp);

/// <summary>Lamp status from a DM1/DM2 message.</summary>
public sealed record LampStatus(bool Mil, bool RedStop, bool AmberWarning, bool Protect);

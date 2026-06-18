namespace TruckDiag.Core;

/// <summary>
/// Orchestrates a read-only diagnostic session over the NativeEngine: connect,
/// poll decoded events, and surface live signals + fault codes. It exposes no
/// clear-DTC, unlock, or programming operation — there is no such code path.
/// </summary>
public sealed class DiagnosticSession : IDisposable
{
    private IntPtr _engine;

    public event Action<SignalSample>? SignalReceived;
    public event Action<IReadOnlyList<FaultCode>, LampStatus>? FaultsReceived;

    public bool IsConnected { get; private set; }

    /// <summary>Open an offline candump replay session.</summary>
    public void OpenReplay(string candumpPath)
    {
        _engine = NativeEngine.mcm_engine_open_replay(candumpPath);
        if (_engine == IntPtr.Zero)
        {
            throw new InvalidOperationException($"failed to open replay: {candumpPath}");
        }

        IsConnected = NativeEngine.mcm_engine_connect(_engine) == 1;
    }

    /// <summary>
    /// Actively solicit a broadcast of <paramref name="pgn"/> (read-only J1939
    /// Request PGN). Used by "Identify Vehicle" / "Read Faults".
    /// </summary>
    public bool RequestPgn(int pgn, byte dest = 0xFF, byte src = 0xF9)
        => _engine != IntPtr.Zero && NativeEngine.mcm_engine_request_pgn(_engine, pgn, dest, src) == 1;

    /// <summary>Pump all available events, raising callbacks. Returns the count.</summary>
    public int Pump(Func<int, int, string?>? dtcText = null)
    {
        int processed = 0;
        var ev = new NativeEngine.FrameEvent();
        while (_engine != IntPtr.Zero && NativeEngine.mcm_engine_poll(_engine, ref ev) == 1)
        {
            processed++;
            if (ev.Kind == NativeEngine.EventSignals)
            {
                for (int i = 0; i < ev.SignalCount; i++)
                {
                    NativeEngine.SignalValue s = ev.Signals[i];
                    SignalReceived?.Invoke(new SignalSample(s.Spn, s.Name, s.Value, s.Unit, DateTime.UtcNow));
                }
            }
            else if (ev.Kind == NativeEngine.EventDtcs)
            {
                var faults = new List<FaultCode>(ev.DtcCount);
                for (int i = 0; i < ev.DtcCount; i++)
                {
                    NativeEngine.Dtc d = ev.Dtcs[i];
                    faults.Add(new FaultCode(d.Spn, d.Fmi, d.OccurrenceCount, ev.Source,
                        dtcText?.Invoke(d.Spn, d.Fmi)));
                }

                var lamps = new LampStatus(ev.Lamps.Mil == 1, ev.Lamps.RedStop == 1,
                    ev.Lamps.AmberWarning == 1, ev.Lamps.Protect == 1);
                FaultsReceived?.Invoke(faults, lamps);
            }
        }

        return processed;
    }

    public void Dispose()
    {
        if (_engine != IntPtr.Zero)
        {
            NativeEngine.mcm_engine_close(_engine);
            _engine = IntPtr.Zero;
        }

        IsConnected = false;
    }
}

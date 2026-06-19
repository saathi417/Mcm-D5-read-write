using System.Collections.ObjectModel;
using System.Windows;
using Microsoft.Win32;
using TruckDiag.Core;

namespace TruckDiag.UI;

/// <summary>
/// Read-only diagnostics shell. Loads a capture, decodes it through the
/// NativeEngine, and shows modules, fault codes, and live data. There is no
/// Programming tab and no clear/unlock/write action.
/// </summary>
public partial class MainWindow : Window
{
    private readonly ObservableCollection<EcuModule> _modules = new();
    private readonly ObservableCollection<FaultCode> _faults = new();
    private readonly ObservableCollection<SignalSample> _live = new();
    private readonly Dictionary<int, int> _liveIndexBySpn = new();

    private DiagnosticSession? _session;
    private readonly IReadOnlyList<IEcuPlugin> _plugins;

    public MainWindow()
    {
        InitializeComponent();
        ModulesGrid.ItemsSource = _modules;
        FaultsGrid.ItemsSource = _faults;
        LiveGrid.ItemsSource = _live;

        // Load read-only OEM plugins shipped next to the app.
        string pluginDir = Path.Combine(AppContext.BaseDirectory, "plugins");
        _plugins = PluginLoader.LoadFrom(pluginDir);
    }

    /// <summary>OEM-specific fault text from the first plugin that has it.</summary>
    private string? ResolveDtcText(int spn, int fmi)
    {
        foreach (IEcuPlugin plugin in _plugins)
        {
            string? text = plugin.DtcText(spn, fmi);
            if (!string.IsNullOrEmpty(text))
            {
                return text;
            }
        }

        return Fmi.Text(fmi);
    }

    private void OnOpenCapture(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog { Filter = "candump logs (*.log;*.txt)|*.log;*.txt|All files (*.*)|*.*" };
        if (dialog.ShowDialog() != true)
        {
            return;
        }

        _session?.Dispose();
        _session = new DiagnosticSession();
        _session.SignalReceived += OnSignal;
        _session.FaultsReceived += OnFaults;

        _modules.Clear();
        _faults.Clear();
        _live.Clear();
        _liveIndexBySpn.Clear();

        _session.OpenReplay(dialog.FileName);
        StatusText.Text = _session.IsConnected ? $"Connected: {dialog.FileName}" : "Connect failed.";
        AppendLog($"Opened capture {dialog.FileName}");
    }

    private void OnIdentify(object sender, RoutedEventArgs e)
    {
        // Read-only: solicit VIN (PGN 65260) and component id (PGN 65259).
        if (_session is null)
        {
            return;
        }

        _session.RequestPgn(65260);
        _session.RequestPgn(65259);
        int n = _session.Pump();
        DashboardText.Text = $"Processed {n} frames. Modules seen: {_modules.Count}.";
        AppendLog("Identify Vehicle (read-only request).");
    }

    private void OnReadFaults(object sender, RoutedEventArgs e)
    {
        if (_session is null)
        {
            return;
        }

        _session.RequestPgn(65226); // DM1
        int n = _session.Pump(ResolveDtcText);
        StatusText.Text = $"Read {_faults.Count} fault codes from {n} frames.";
        AppendLog("Read Faults (read-only request).");
    }

    private void OnSignal(SignalSample sample)
    {
        if (_liveIndexBySpn.TryGetValue(sample.Spn, out int index))
        {
            _live[index] = sample;
        }
        else
        {
            _liveIndexBySpn[sample.Spn] = _live.Count;
            _live.Add(sample);
        }
    }

    private void OnFaults(IReadOnlyList<FaultCode> faults, LampStatus lamps)
    {
        _faults.Clear();
        foreach (FaultCode fault in faults)
        {
            _faults.Add(fault);
        }

        DashboardText.Text = $"MIL: {(lamps.Mil ? "ON" : "off")}   Active faults: {faults.Count}";
    }

    private void AppendLog(string message) => LogBox.AppendText($"{DateTime.Now:T}  {message}{Environment.NewLine}");
}

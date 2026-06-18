using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Windows;
using System.Windows.Threading;
using Microsoft.Win32;

namespace McmD5Viewer;

/// <summary>
/// Read-only viewer: replays a candump capture, decodes each frame through the
/// native core, and shows live signals + DM1/DM2 fault codes. It never
/// transmits, unlocks, clears codes, or writes to a module.
/// </summary>
public partial class MainWindow : Window
{
    private const int Dm1Pgn = 65226;
    private const int Dm2Pgn = 65227;

    private readonly ObservableCollection<SignalRow> _signals = new();
    private readonly ObservableCollection<DtcRow> _dtcs = new();
    private readonly Dictionary<int, SignalRow> _signalBySpn = new();
    private readonly DispatcherTimer _timer = new() { Interval = System.TimeSpan.FromMilliseconds(20) };

    private List<CanFrame> _frames = new();
    private int _cursor;

    public MainWindow()
    {
        InitializeComponent();
        SignalsGrid.ItemsSource = _signals;
        DtcGrid.ItemsSource = _dtcs;
        _timer.Tick += (_, _) => Step();
    }

    private void OnOpenLog(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog
        {
            Filter = "candump logs (*.log;*.txt)|*.log;*.txt|All files (*.*)|*.*",
        };
        if (dialog.ShowDialog() != true)
        {
            return;
        }

        _frames = LogReader.ReadCandump(dialog.FileName).ToList();
        _cursor = 0;
        _signals.Clear();
        _dtcs.Clear();
        _signalBySpn.Clear();
        StatusText.Text = $"Loaded {_frames.Count} frames from {dialog.FileName}.";
    }

    private void OnPlayPause(object sender, RoutedEventArgs e)
    {
        if (_timer.IsEnabled)
        {
            _timer.Stop();
            PlayButton.Content = "Play";
        }
        else
        {
            _timer.Start();
            PlayButton.Content = "Pause";
        }
    }

    private void OnStop(object sender, RoutedEventArgs e)
    {
        _timer.Stop();
        PlayButton.Content = "Play";
        _cursor = 0;
        StatusText.Text = "Stopped.";
    }

    private void Step()
    {
        // Process a small batch per tick for smooth playback.
        for (int i = 0; i < 25 && _cursor < _frames.Count; i++, _cursor++)
        {
            Handle(_frames[_cursor]);
        }

        if (_cursor >= _frames.Count)
        {
            _timer.Stop();
            PlayButton.Content = "Play";
            StatusText.Text = $"Replay complete ({_frames.Count} frames).";
        }
    }

    private void Handle(CanFrame frame)
    {
        int pgn = Native.mcm_pgn_from_can_id(frame.CanId);

        if (pgn is Dm1Pgn or Dm2Pgn)
        {
            var lamps = default(Native.McmLamps);
            var outDtcs = new Native.McmDtc[32];
            int count = Native.mcm_parse_dm1(frame.Data, frame.Data.Length, ref lamps, outDtcs, outDtcs.Length);
            if (count < 0)
            {
                return;
            }

            int source = Native.mcm_source_from_can_id(frame.CanId);
            _dtcs.Clear();
            for (int i = 0; i < count; i++)
            {
                _dtcs.Add(new DtcRow(outDtcs[i].spn, outDtcs[i].fmi, outDtcs[i].occurrence_count, source));
            }

            LampMil.Opacity = lamps.mil == 1 ? 1.0 : 0.3;
            LampRed.Opacity = lamps.red_stop == 1 ? 1.0 : 0.3;
            LampAmber.Opacity = lamps.amber_warning == 1 ? 1.0 : 0.3;
            return;
        }

        var values = new Native.McmSignalValue[16];
        int n = Native.mcm_decode_pgn(pgn, frame.Data, frame.Data.Length, values, values.Length);
        for (int i = 0; i < n; i++)
        {
            if (!_signalBySpn.TryGetValue(values[i].spn, out SignalRow? row))
            {
                row = new SignalRow(values[i].spn, values[i].name, values[i].unit);
                _signalBySpn[values[i].spn] = row;
                _signals.Add(row);
            }

            row.Value = values[i].value;
        }
    }
}

using System.ComponentModel;

namespace McmD5Viewer;

/// <summary>A live signal row shown in the data grid (value updates in place).</summary>
public sealed class SignalRow : INotifyPropertyChanged
{
    private double _value;

    public SignalRow(int spn, string name, string unit)
    {
        Spn = spn;
        Name = name;
        Unit = unit;
    }

    public int Spn { get; }
    public string Name { get; }
    public string Unit { get; }

    public double Value
    {
        get => _value;
        set
        {
            if (_value.Equals(value))
            {
                return;
            }

            _value = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Value)));
        }
    }

    public event PropertyChangedEventHandler? PropertyChanged;
}

/// <summary>A diagnostic trouble code row.</summary>
public sealed class DtcRow
{
    public DtcRow(int spn, int fmi, int occurrenceCount, int source)
    {
        Spn = spn;
        Fmi = fmi;
        OccurrenceCount = occurrenceCount;
        Source = source;
    }

    public int Spn { get; }
    public int Fmi { get; }
    public int OccurrenceCount { get; }
    public int Source { get; }
}

/// <summary>A single received CAN frame.</summary>
public readonly record struct CanFrame(uint CanId, byte[] Data);

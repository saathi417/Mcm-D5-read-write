using System.Collections.Generic;
using System.Globalization;
using System.IO;

namespace McmD5Viewer;

/// <summary>
/// Reads a candump capture file into CAN frames for offline replay.
/// Line format: <c>(timestamp) iface  CANID#HEXDATA</c>.
/// Read-only — parses existing captures, never transmits.
/// </summary>
public static class LogReader
{
    public static IEnumerable<CanFrame> ReadCandump(string path)
    {
        foreach (string line in File.ReadLines(path))
        {
            string? token = null;
            foreach (string part in line.Split(' ', '\t'))
            {
                if (part.Contains('#'))
                {
                    token = part;
                    break;
                }
            }

            if (token is null)
            {
                continue;
            }

            int hash = token.IndexOf('#');
            string idStr = token[..hash];
            string dataStr = token[(hash + 1)..].Replace("#", string.Empty);
            if (dataStr.Length % 2 != 0)
            {
                continue;
            }

            if (!uint.TryParse(idStr, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out uint canId))
            {
                continue;
            }

            var data = new byte[dataStr.Length / 2];
            bool ok = true;
            for (int i = 0; i < data.Length; i++)
            {
                if (!byte.TryParse(dataStr.AsSpan(i * 2, 2), NumberStyles.HexNumber,
                        CultureInfo.InvariantCulture, out data[i]))
                {
                    ok = false;
                    break;
                }
            }

            if (ok)
            {
                yield return new CanFrame(canId, data);
            }
        }
    }
}

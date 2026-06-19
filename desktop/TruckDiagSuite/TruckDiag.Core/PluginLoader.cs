using System.Reflection;

namespace TruckDiag.Core;

/// <summary>
/// Discovers and instantiates read-only OEM plugins (types implementing
/// <see cref="IEcuPlugin"/>) from assemblies in a directory. Loading a plugin
/// grants only the read-only contract — there is no programming surface.
/// </summary>
public static class PluginLoader
{
    public static IReadOnlyList<IEcuPlugin> LoadFrom(string directory)
    {
        var plugins = new List<IEcuPlugin>();
        if (!Directory.Exists(directory))
        {
            return plugins;
        }

        foreach (string path in Directory.EnumerateFiles(directory, "*.dll"))
        {
            try
            {
                Assembly assembly = Assembly.LoadFrom(path);
                foreach (Type type in assembly.GetTypes())
                {
                    if (typeof(IEcuPlugin).IsAssignableFrom(type) && type is { IsClass: true, IsAbstract: false })
                    {
                        if (Activator.CreateInstance(type) is IEcuPlugin plugin)
                        {
                            plugins.Add(plugin);
                        }
                    }
                }
            }
            catch (Exception ex) when (ex is BadImageFormatException or ReflectionTypeLoadException)
            {
                // Not a managed plugin assembly (e.g. a native DLL) — skip it.
            }
        }

        return plugins;
    }

    /// <summary>Pick the first plugin that identifies the given module, if any.</summary>
    public static IEcuPlugin? MatchFor(IEnumerable<IEcuPlugin> plugins, EcuModule module)
        => plugins.FirstOrDefault(p => p.Identify(module));
}

/* PaccarPlugin — read-only OEM plugin (PACCAR MX).
 *
 * Identify + decode/text only. No programming, unlock, or DTC-clear path,
 * matching the read-only IEcuPlugin contract.
 */
#include "iecu_plugin.h"

#include <string>

namespace {

class PaccarPlugin : public IEcuPlugin {
public:
    std::string Name() override { return "PACCAR"; }

    bool Identify(const EcuIdentity& identity) override {
        // Read-only match on already-read identity strings reported by PACCAR
        // MX engine controllers (e.g. "PACCAR", "MX-13", "MX-11").
        return identity.component_id.find("PACCAR") != std::string::npos ||
               identity.component_id.find("MX-13") != std::string::npos ||
               identity.component_id.find("MX-11") != std::string::npos;
    }

    std::string DtcText(int32_t spn, int32_t fmi) override {
        if (spn == 1761 && fmi == 18) {
            return "Aftertreatment 1 DEF Tank Level Low (moderate)";
        }
        if (spn == 5246) {
            return "Aftertreatment SCR Operator Inducement - Severity";
        }
        return std::string();
    }
};

}  // namespace

extern "C" {

#if defined(_WIN32)
__declspec(dllexport)
#endif
IEcuPlugin* CreatePlugin() {
    return new PaccarPlugin();
}

#if defined(_WIN32)
__declspec(dllexport)
#endif
void DestroyPlugin(IEcuPlugin* plugin) {
    delete plugin;
}

}  // extern "C"

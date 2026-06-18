/* DetroitPlugin — read-only OEM plugin (Detroit Diesel MCM/ACM).
 *
 * Provides identification and decode/text knowledge only. It implements no
 * programming, unlock, or DTC-clear entry point, matching the read-only
 * IEcuPlugin contract.
 */
#include "iecu_plugin.h"

#include <string>

namespace {

class DetroitPlugin : public IEcuPlugin {
public:
    std::string Name() override { return "Detroit Diesel"; }

    bool Identify(const EcuIdentity& identity) override {
        // Read-only match on already-read identity data (e.g. component id
        // strings reported by Detroit DDEC modules).
        return identity.component_id.find("DDEC") != std::string::npos ||
               identity.component_id.find("DD") != std::string::npos;
    }

    std::string DtcText(int32_t spn, int32_t fmi) override {
        if (spn == 1761 && fmi == 1) {
            return "Aftertreatment 1 DEF Tank Level Low";
        }
        if (spn == 3226) {
            return "Aftertreatment 1 Outlet NOx sensor";
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
    return new DetroitPlugin();
}

#if defined(_WIN32)
__declspec(dllexport)
#endif
void DestroyPlugin(IEcuPlugin* plugin) {
    delete plugin;
}

}  // extern "C"

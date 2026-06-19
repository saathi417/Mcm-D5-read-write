/* CumminsPlugin — read-only OEM plugin (Cummins).
 *
 * Identify + decode/text only. No programming, unlock, or DTC-clear path,
 * matching the read-only IEcuPlugin contract.
 */
#include "iecu_plugin.h"

#include <string>

namespace {

class CumminsPlugin : public IEcuPlugin {
public:
    std::string Name() override { return "Cummins"; }

    bool Identify(const EcuIdentity& identity) override {
        // Read-only match on already-read identity strings reported by
        // Cummins engine controllers (e.g. "CM2350", "ISX", "CUMMINS").
        return identity.component_id.find("CUMMINS") != std::string::npos ||
               identity.component_id.find("CM2") != std::string::npos ||
               identity.component_id.find("ISX") != std::string::npos;
    }

    std::string DtcText(int32_t spn, int32_t fmi) override {
        if (spn == 3361 && fmi == 7) {
            return "Aftertreatment 1 DEF Dosing Unit";
        }
        if (spn == 4334) {
            return "Aftertreatment 1 DEF Dosing Absolute Pressure";
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
    return new CumminsPlugin();
}

#if defined(_WIN32)
__declspec(dllexport)
#endif
void DestroyPlugin(IEcuPlugin* plugin) {
    delete plugin;
}

}  // extern "C"

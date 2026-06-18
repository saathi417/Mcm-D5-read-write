/* IEcuPlugin — read-only OEM plugin contract for the NativeEngine.
 *
 * Plugins provide per-OEM identification and decode knowledge (SPN/PID maps,
 * DTC text) for modules such as Detroit, Cummins, and Paccar. The contract is
 * intentionally read-only: a plugin can name itself, identify a connected
 * module, and describe how to decode its data. There is deliberately NO
 * programming/flash/unlock entry point on this interface — keep it that way.
 */
#ifndef IECU_PLUGIN_H
#define IECU_PLUGIN_H

#include <cstdint>
#include <string>
#include <vector>

#include "mcm_core.h"

struct EcuIdentity {
    std::string vin;
    std::string component_id;
    std::string software_id;
    int32_t     source_address = -1;
};

class IEcuPlugin {
public:
    virtual ~IEcuPlugin() = default;

    /* Human-readable plugin name, e.g. "Detroit Diesel". */
    virtual std::string Name() = 0;

    /* True if this plugin recognizes the module described by `identity`
     * (read-only: matching is based on already-read identity data). */
    virtual bool Identify(const EcuIdentity& identity) = 0;

    /* Decode known signals for a PGN using this OEM's table. Returns the
     * number written to `out` (decode-only). Default: no OEM-specific signals
     * (the engine falls back to the generic J1939 table). */
    virtual int32_t DecodePgn(int32_t /*pgn*/, const uint8_t* /*data*/,
                              int32_t /*len*/, McmSignalValue* /*out*/,
                              int32_t /*max*/) {
        return 0;
    }

    /* Optional human-readable text for an SPN/FMI fault, if the OEM table has
     * one; empty string means "fall back to the generic description". */
    virtual std::string DtcText(int32_t /*spn*/, int32_t /*fmi*/) {
        return std::string();
    }
};

#endif /* IECU_PLUGIN_H */

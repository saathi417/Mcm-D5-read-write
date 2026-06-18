/* mcm_core implementation — decode-only J1939 (see include/mcm_core.h).
 *
 * The SPN table mirrors a representative subset of src/mcm_d5/signals.py.
 * Extend both together so the native viewer and the Python library agree.
 */
#define MCM_CORE_EXPORTS
#include "mcm_core.h"

#include <cstring>

namespace {

struct SignalDef {
    int32_t     spn;
    const char* name;
    int         start;
    int         len;
    double      scale;
    double      offset;
    const char* unit;
};

struct PgnDef {
    int32_t          pgn;
    const SignalDef* sigs;
    int              count;
};

const SignalDef EEC1[] = {
    {513, "Actual Engine - Percent Torque", 2, 1, 1.0, -125.0, "%"},
    {190, "Engine Speed", 3, 2, 0.125, 0.0, "rpm"},
};
const SignalDef ET1[] = {
    {110, "Engine Coolant Temperature", 0, 1, 1.0, -40.0, "degC"},
    {175, "Engine Oil Temperature 1", 2, 2, 0.03125, -273.0, "degC"},
};
const SignalDef IC1[] = {
    {102, "Intake Manifold #1 Pressure", 1, 1, 2.0, 0.0, "kPa"},
    {105, "Intake Manifold 1 Temperature", 2, 1, 1.0, -40.0, "degC"},
    {173, "Exhaust Gas Temperature", 5, 2, 0.03125, -273.0, "degC"},
};
const SignalDef CCVS1[] = {
    {84, "Wheel-Based Vehicle Speed", 1, 2, 1.0 / 256.0, 0.0, "km/h"},
};
const SignalDef DD[] = {
    {96, "Fuel Level 1", 1, 1, 0.4, 0.0, "%"},
};
const SignalDef AT1T1I[] = {
    {1761, "DEF Tank Volume", 0, 1, 0.4, 0.0, "%"},
    {3031, "DEF Tank Temperature", 1, 1, 1.0, -40.0, "degC"},
};
const SignalDef AT1OG1[] = {
    {3226, "Aftertreatment 1 Outlet NOx", 0, 2, 0.05, -200.0, "ppm"},
};

const PgnDef PGNS[] = {
    {61444, EEC1, 2},
    {65262, ET1, 2},
    {65270, IC1, 3},
    {65265, CCVS1, 1},
    {65276, DD, 1},
    {65110, AT1T1I, 2},
    {61455, AT1OG1, 1},
};
const int PGN_COUNT = static_cast<int>(sizeof(PGNS) / sizeof(PGNS[0]));

bool decode_signal(const SignalDef& s, const uint8_t* data, int len, double* value) {
    const int end = s.start + s.len;
    if (len < end) {
        return false;
    }
    uint32_t raw = 0;
    for (int i = 0; i < s.len; ++i) {
        raw |= static_cast<uint32_t>(data[s.start + i]) << (8 * i);
    }
    const uint32_t not_available =
        (s.len >= 4) ? 0xFFFFFFFEu : ((1u << (8 * s.len)) - 2u);
    if (raw >= not_available) {
        return false;
    }
    *value = static_cast<double>(raw) * s.scale + s.offset;
    return true;
}

void copy_fixed(char* dst, const char* src, size_t size) {
    std::strncpy(dst, src, size - 1);
    dst[size - 1] = '\0';
}

}  // namespace

int32_t mcm_pgn_from_can_id(uint32_t can_id) {
    const uint32_t cid = can_id & 0x1FFFFFFFu;
    const uint32_t ps = (cid >> 8) & 0xFF;
    const uint32_t pf = (cid >> 16) & 0xFF;
    const uint32_t dp = (cid >> 24) & 0x01;
    const uint32_t edp = (cid >> 25) & 0x01;
    if (pf < 240) {
        return static_cast<int32_t>((edp << 17) | (dp << 16) | (pf << 8));
    }
    return static_cast<int32_t>((edp << 17) | (dp << 16) | (pf << 8) | ps);
}

int32_t mcm_source_from_can_id(uint32_t can_id) {
    return static_cast<int32_t>(can_id & 0xFF);
}

int32_t mcm_decode_pgn(int32_t pgn, const uint8_t* data, int32_t len,
                       McmSignalValue* out, int32_t max) {
    if (data == nullptr || out == nullptr) {
        return 0;
    }
    int written = 0;
    for (int p = 0; p < PGN_COUNT; ++p) {
        if (PGNS[p].pgn != pgn) {
            continue;
        }
        for (int s = 0; s < PGNS[p].count && written < max; ++s) {
            double value = 0.0;
            if (decode_signal(PGNS[p].sigs[s], data, len, &value)) {
                out[written].spn = PGNS[p].sigs[s].spn;
                out[written].value = value;
                copy_fixed(out[written].name, PGNS[p].sigs[s].name, sizeof(out[written].name));
                copy_fixed(out[written].unit, PGNS[p].sigs[s].unit, sizeof(out[written].unit));
                ++written;
            }
        }
        break;
    }
    return written;
}

uint32_t mcm_build_request_pgn(int32_t requested_pgn, uint8_t dest, uint8_t src,
                               uint8_t priority, uint8_t* out_data) {
    if (out_data != nullptr) {
        out_data[0] = static_cast<uint8_t>(requested_pgn & 0xFF);
        out_data[1] = static_cast<uint8_t>((requested_pgn >> 8) & 0xFF);
        out_data[2] = static_cast<uint8_t>((requested_pgn >> 16) & 0xFF);
    }
    // Request PGN is 59904 (0xEA00), a PDU1 destination-specific message:
    // PF = 0xEA, PS = destination address.
    const uint32_t prio = static_cast<uint32_t>(priority & 0x07);
    return (prio << 26) | (0xEAu << 16) | (static_cast<uint32_t>(dest) << 8) | src;
}

int32_t mcm_parse_dm1(const uint8_t* data, int32_t len, McmLamps* lamps,
                      McmDtc* out, int32_t max) {
    if (data == nullptr || lamps == nullptr || out == nullptr || len < 2) {
        return -1;
    }
    const uint8_t lamp = data[0];
    lamps->mil = (((lamp >> 6) & 0x03) == 0x01) ? 1 : 0;
    lamps->red_stop = (((lamp >> 4) & 0x03) == 0x01) ? 1 : 0;
    lamps->amber_warning = (((lamp >> 2) & 0x03) == 0x01) ? 1 : 0;
    lamps->protect = ((lamp & 0x03) == 0x01) ? 1 : 0;

    int count = 0;
    for (int i = 2; i + 3 < len && count < max; i += 4) {
        const uint8_t b0 = data[i];
        const uint8_t b1 = data[i + 1];
        const uint8_t b2 = data[i + 2];
        const uint8_t b3 = data[i + 3];
        const int32_t spn = b0 | (b1 << 8) | ((b2 >> 5) << 16);
        const int32_t fmi = b2 & 0x1F;
        if (spn == 0 && fmi == 0) {
            continue;
        }
        out[count].spn = spn;
        out[count].fmi = fmi;
        out[count].occurrence_count = b3 & 0x7F;
        out[count]._pad = 0;
        ++count;
    }
    return count;
}

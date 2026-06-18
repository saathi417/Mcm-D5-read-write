/* Minimal self-test for mcm_core: verifies decode parity with the Python lib. */
#include "mcm_core.h"

#include <cmath>
#include <cstdio>

static int failures = 0;

static void check(bool ok, const char* what) {
    if (!ok) {
        std::printf("FAIL: %s\n", what);
        ++failures;
    }
}

int main() {
    // PGN parsing: EEC1 broadcast 0x0CF00400 -> PGN 61444, source 0.
    check(mcm_pgn_from_can_id(0x0CF00400) == 61444, "pgn eec1");
    check(mcm_source_from_can_id(0x0CF00400) == 0, "source eec1");

    // Engine speed 1500 rpm (raw 12000 = 0x2EE0) + 0% torque (raw 125).
    const uint8_t eec1[8] = {0xFF, 0xFF, 0x7D, 0xE0, 0x2E, 0xFF, 0xFF, 0xFF};
    McmSignalValue sv[8];
    int n = mcm_decode_pgn(61444, eec1, 8, sv, 8);
    check(n == 2, "eec1 count");
    bool rpm_ok = false;
    for (int i = 0; i < n; ++i) {
        if (sv[i].spn == 190) {
            rpm_ok = std::fabs(sv[i].value - 1500.0) < 1e-9;
        }
    }
    check(rpm_ok, "engine speed 1500");

    // DM1: MIL on, SPN 100 / FMI 1 / OC 5.
    const uint8_t dm1[6] = {0x40, 0x00, 0x64, 0x00, 0x01, 0x05};
    McmLamps lamps;
    McmDtc dtcs[4];
    int d = mcm_parse_dm1(dm1, 6, &lamps, dtcs, 4);
    check(d == 1, "dm1 count");
    check(lamps.mil == 1, "dm1 mil");
    check(dtcs[0].spn == 100 && dtcs[0].fmi == 1 && dtcs[0].occurrence_count == 5, "dm1 dtc");

    if (failures == 0) {
        std::printf("all core tests passed\n");
    }
    return failures == 0 ? 0 : 1;
}

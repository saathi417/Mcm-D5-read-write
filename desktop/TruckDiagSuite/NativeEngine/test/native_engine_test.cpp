/* Self-test for the NativeEngine replay path. */
#include "native_engine.h"

#include <cmath>
#include <cstdio>

static int failures = 0;
static void check(bool ok, const char* what) {
    if (!ok) { std::printf("FAIL: %s\n", what); ++failures; }
}

int main() {
    const char* path = "/tmp/te_engine.log";
    FILE* fp = std::fopen(path, "w");
    std::fprintf(fp, "(0.0) can0 0CF00400#FFFF7DE02EFFFFFF\n");   // EEC1 1500 rpm
    std::fprintf(fp, "(0.1) can0 18FECA00#4000640001050000\n");  // DM1 SPN100/FMI1
    std::fclose(fp);

    McmEngine eng = mcm_engine_open_replay(path);
    check(eng != nullptr, "engine open");
    check(mcm_engine_connect(eng) == 1, "engine connect");

    McmFrameEvent ev;
    check(mcm_engine_poll(eng, &ev) == 1, "poll 1");
    check(ev.kind == MCM_EVENT_SIGNALS && ev.pgn == 61444, "eec1 event");
    bool rpm_ok = false;
    for (int i = 0; i < ev.signal_count; ++i) {
        if (ev.signals[i].spn == 190) {
            rpm_ok = std::fabs(ev.signals[i].value - 1500.0) < 1e-9;
        }
    }
    check(rpm_ok, "engine speed 1500");

    check(mcm_engine_poll(eng, &ev) == 1, "poll 2");
    check(ev.kind == MCM_EVENT_DTCS && ev.dtc_count == 1, "dm1 event");
    check(ev.dtcs[0].spn == 100 && ev.lamps.mil == 1, "dm1 contents");

    check(mcm_engine_poll(eng, &ev) == 0, "poll end");
    // Replay cannot solicit a live node.
    check(mcm_engine_request_pgn(eng, 65226, 0xFF, 0xF9) == 0, "request on replay");

    mcm_engine_close(eng);
    if (failures == 0) { std::printf("all engine tests passed\n"); }
    return failures == 0 ? 0 : 1;
}

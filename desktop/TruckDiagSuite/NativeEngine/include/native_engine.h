/* NativeEngine C ABI — read-only diagnostics engine for TruckDiag.Core.
 *
 * Wraps a transport + the mcm_core decoders. It connects, receives frames, and
 * surfaces decoded signals and DM1/DM2 fault codes, plus J1939 Request-PGN
 * solicitation. There is no clear-DTC, unlock, download, or program function.
 */
#ifndef NATIVE_ENGINE_H
#define NATIVE_ENGINE_H

#include <stdint.h>

#include "mcm_core.h"

#if defined(_WIN32)
#  ifdef NATIVE_ENGINE_EXPORTS
#    define ENGINE_API __declspec(dllexport)
#  else
#    define ENGINE_API __declspec(dllimport)
#  endif
#else
#  define ENGINE_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void* McmEngine;

enum {
    MCM_EVENT_NONE = 0,
    MCM_EVENT_SIGNALS = 1,
    MCM_EVENT_DTCS = 2,
};

typedef struct McmFrameEvent {
    int32_t        kind;     /* one of MCM_EVENT_* */
    int32_t        pgn;
    int32_t        source;
    int32_t        signal_count;
    McmSignalValue signals[16];
    int32_t        dtc_count;
    McmDtc         dtcs[32];
    McmLamps       lamps;
} McmFrameEvent;

/* Create an engine backed by an offline candump replay. NULL on failure. */
ENGINE_API McmEngine mcm_engine_open_replay(const char* candump_path);

/* Connect the underlying transport (no-op for replay). */
ENGINE_API int32_t mcm_engine_connect(McmEngine engine);

/* Produce the next decoded event. Returns 1 if `out` was filled, 0 at end. */
ENGINE_API int32_t mcm_engine_poll(McmEngine engine, McmFrameEvent* out);

/* Emit a J1939 Request PGN solicitation (read-only). Returns 1 if sent. */
ENGINE_API int32_t mcm_engine_request_pgn(McmEngine engine, int32_t pgn,
                                          uint8_t dest, uint8_t src);

ENGINE_API void mcm_engine_close(McmEngine engine);

#ifdef __cplusplus
}
#endif

#endif /* NATIVE_ENGINE_H */

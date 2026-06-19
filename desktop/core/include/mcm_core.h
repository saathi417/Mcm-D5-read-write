/* mcm_core — read-only J1939 decoding, C ABI for the WPF viewer.
 *
 * This native core decodes J1939 broadcast signals and DM1/DM2 fault codes.
 * It is decode-only: there is no function that transmits, unlocks, clears
 * codes, or writes to a module. The C# WPF front-end calls these via P/Invoke.
 */
#ifndef MCM_CORE_H
#define MCM_CORE_H

#include <stdint.h>

#if defined(_WIN32)
#  ifdef MCM_CORE_EXPORTS
#    define MCM_API __declspec(dllexport)
#  else
#    define MCM_API __declspec(dllimport)
#  endif
#else
#  define MCM_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct McmSignalValue {
    int32_t spn;
    double  value;
    char    name[64];
    char    unit[16];
} McmSignalValue;

typedef struct McmDtc {
    int32_t spn;
    int32_t fmi;
    int32_t occurrence_count;
    int32_t _pad;
} McmDtc;

typedef struct McmLamps {
    int32_t mil;
    int32_t red_stop;
    int32_t amber_warning;
    int32_t protect;
} McmLamps;

/* Parse a 29-bit extended CAN id. */
MCM_API int32_t mcm_pgn_from_can_id(uint32_t can_id);
MCM_API int32_t mcm_source_from_can_id(uint32_t can_id);

/* Decode known SPNs for a PGN into `out` (up to `max`); returns the count. */
MCM_API int32_t mcm_decode_pgn(int32_t pgn, const uint8_t* data, int32_t len,
                               McmSignalValue* out, int32_t max);

/* Parse a DM1/DM2 payload: fills `lamps`, writes DTCs to `out` (up to `max`),
 * returns the DTC count, or -1 on a malformed (too-short) payload. */
MCM_API int32_t mcm_parse_dm1(const uint8_t* data, int32_t len,
                              McmLamps* lamps, McmDtc* out, int32_t max);

/* Build a J1939 "Request PGN" (PGN 59904) frame that solicits a broadcast of
 * `requested_pgn` from `dest` (0xFF = global request). Fills out_data[0..2]
 * and returns the 29-bit CAN id to transmit.
 *
 * This is read-only by nature: a Request PGN only asks a node to *send* its
 * data (VIN, component ID, DM1/DM2, etc.). It carries no payload and cannot
 * write, unlock, or program. This is the only "transmit helper" the core
 * provides — there is intentionally no arbitrary-send or write/program path. */
MCM_API uint32_t mcm_build_request_pgn(int32_t requested_pgn, uint8_t dest,
                                       uint8_t src, uint8_t priority,
                                       uint8_t* out_data /* >= 3 bytes */);

/* Standard SAE J1939-73 Failure Mode Identifier (FMI) text for 0..31.
 * Returns a static string (never NULL); unknown values yield "Unknown FMI". */
MCM_API const char* mcm_fmi_text(int32_t fmi);

#ifdef __cplusplus
}
#endif

#endif /* MCM_CORE_H */

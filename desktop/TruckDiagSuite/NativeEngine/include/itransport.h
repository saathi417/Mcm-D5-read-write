/* ITransport — read-only CAN transport contract for the NativeEngine.
 *
 * A transport can connect to an adapter, receive frames, and emit J1939
 * *Request PGN* solicitations (which ask a node to broadcast its data). It
 * deliberately has NO general-purpose send: there is no method that transmits
 * arbitrary payloads, so it cannot carry SecurityAccess, RequestDownload,
 * TransferData, or any program/write request. Keep this asymmetry.
 *
 * Concrete transports:
 *   - ReplayTransport  (offline candump replay; implemented, testable anywhere)
 *   - RP1210Transport  (Windows + vendor SDK; receive + RequestPgn only)
 *   - J2534Transport   (Windows + vendor SDK; receive + RequestPgn only)
 */
#ifndef ITRANSPORT_H
#define ITRANSPORT_H

#include <cstdint>

struct CanMessage {
    uint32_t can_id;
    uint8_t  data[8];
    uint8_t  len;
};

class ITransport {
public:
    virtual ~ITransport() = default;

    virtual bool Connect() = 0;
    virtual void Disconnect() = 0;

    /* Fetch the next received frame. Returns false when none is available
     * (end of replay, or timeout on a live transport). */
    virtual bool Receive(CanMessage& out) = 0;

    /* Transmit a J1939 Request PGN (read-only solicitation). This is the only
     * transmit operation a transport exposes. Returns false if unsupported
     * (e.g. an offline replay has no live node to ask). */
    virtual bool RequestPgn(int32_t requested_pgn, uint8_t dest, uint8_t src) = 0;
};

#endif /* ITRANSPORT_H */

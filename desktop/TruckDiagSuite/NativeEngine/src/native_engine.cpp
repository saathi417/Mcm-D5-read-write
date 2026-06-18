/* NativeEngine implementation — read-only (see include/native_engine.h).
 *
 * Includes an offline ReplayTransport so the engine is testable without
 * hardware. Live RP1210/J2534 transports plug in behind ITransport on Windows
 * (receive + RequestPgn only).
 */
#define NATIVE_ENGINE_EXPORTS
#include "native_engine.h"

#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <vector>

#include "itransport.h"

namespace {

const int32_t DM1_PGN = 65226;
const int32_t DM2_PGN = 65227;

bool parse_candump_line(const std::string& line, CanMessage& msg) {
    // Find the "CANID#DATA" token.
    size_t hash = std::string::npos;
    size_t start = 0;
    for (size_t i = 0; i < line.size(); ++i) {
        if (line[i] == ' ' || line[i] == '\t') {
            start = i + 1;
        } else if (line[i] == '#') {
            hash = i;
            break;
        }
    }
    if (hash == std::string::npos) {
        return false;
    }
    std::string id_str = line.substr(start, hash - start);
    size_t data_end = line.find_first_of(" \t\r\n", hash + 1);
    std::string data_str = line.substr(hash + 1, data_end - (hash + 1));
    if (id_str.empty() || (data_str.size() % 2) != 0 || data_str.size() > 16) {
        return false;
    }
    msg.can_id = static_cast<uint32_t>(std::strtoul(id_str.c_str(), nullptr, 16));
    msg.len = static_cast<uint8_t>(data_str.size() / 2);
    for (uint8_t i = 0; i < msg.len; ++i) {
        msg.data[i] = static_cast<uint8_t>(
            std::strtoul(data_str.substr(i * 2, 2).c_str(), nullptr, 16));
    }
    return true;
}

class ReplayTransport : public ITransport {
public:
    explicit ReplayTransport(const std::string& path) {
        FILE* fp = std::fopen(path.c_str(), "r");
        if (fp == nullptr) {
            return;
        }
        char buf[256];
        while (std::fgets(buf, sizeof(buf), fp) != nullptr) {
            CanMessage msg{};
            if (parse_candump_line(buf, msg)) {
                frames_.push_back(msg);
            }
        }
        std::fclose(fp);
    }

    bool Connect() override { return true; }
    void Disconnect() override {}

    bool Receive(CanMessage& out) override {
        if (cursor_ >= frames_.size()) {
            return false;
        }
        out = frames_[cursor_++];
        return true;
    }

    bool RequestPgn(int32_t, uint8_t, uint8_t) override {
        // Offline replay has no live node to solicit.
        return false;
    }

private:
    std::vector<CanMessage> frames_;
    size_t cursor_ = 0;
};

struct Engine {
    std::unique_ptr<ITransport> transport;
};

}  // namespace

McmEngine mcm_engine_open_replay(const char* candump_path) {
    if (candump_path == nullptr) {
        return nullptr;
    }
    auto* engine = new Engine();
    engine->transport = std::make_unique<ReplayTransport>(candump_path);
    return engine;
}

int32_t mcm_engine_connect(McmEngine handle) {
    auto* engine = static_cast<Engine*>(handle);
    return (engine != nullptr && engine->transport->Connect()) ? 1 : 0;
}

int32_t mcm_engine_poll(McmEngine handle, McmFrameEvent* out) {
    auto* engine = static_cast<Engine*>(handle);
    if (engine == nullptr || out == nullptr) {
        return 0;
    }
    CanMessage msg{};
    if (!engine->transport->Receive(msg)) {
        return 0;
    }

    std::memset(out, 0, sizeof(*out));
    out->pgn = mcm_pgn_from_can_id(msg.can_id);
    out->source = mcm_source_from_can_id(msg.can_id);

    if (out->pgn == DM1_PGN || out->pgn == DM2_PGN) {
        out->kind = MCM_EVENT_DTCS;
        int32_t n = mcm_parse_dm1(msg.data, msg.len, &out->lamps, out->dtcs, 32);
        out->dtc_count = (n < 0) ? 0 : n;
    } else {
        out->kind = MCM_EVENT_SIGNALS;
        out->signal_count = mcm_decode_pgn(out->pgn, msg.data, msg.len, out->signals, 16);
    }
    return 1;
}

int32_t mcm_engine_request_pgn(McmEngine handle, int32_t pgn, uint8_t dest, uint8_t src) {
    auto* engine = static_cast<Engine*>(handle);
    if (engine == nullptr) {
        return 0;
    }
    return engine->transport->RequestPgn(pgn, dest, src) ? 1 : 0;
}

void mcm_engine_close(McmEngine handle) {
    delete static_cast<Engine*>(handle);
}

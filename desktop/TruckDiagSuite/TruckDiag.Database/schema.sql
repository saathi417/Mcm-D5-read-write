-- TruckDiagSuite SQLite schema (read-only diagnostics storage).

CREATE TABLE IF NOT EXISTS Vehicles (
    Id     INTEGER PRIMARY KEY AUTOINCREMENT,
    Vin    TEXT NOT NULL UNIQUE,
    Make   TEXT,
    Model  TEXT
);

CREATE TABLE IF NOT EXISTS Modules (
    Id            INTEGER PRIMARY KEY AUTOINCREMENT,
    VehicleId     INTEGER REFERENCES Vehicles(Id),
    SourceAddress INTEGER NOT NULL,
    Name          TEXT,
    SoftwareId    TEXT,
    ComponentId   TEXT
);

CREATE TABLE IF NOT EXISTS FaultCodes (
    Id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ModuleId        INTEGER REFERENCES Modules(Id),
    Spn             INTEGER NOT NULL,
    Fmi             INTEGER NOT NULL,
    OccurrenceCount INTEGER NOT NULL,
    CapturedAt      TEXT NOT NULL
);

-- SPN/FMI reference text (read-only lookup, e.g. seeded from OEM plugins).
CREATE TABLE IF NOT EXISTS Definitions (
    Spn         INTEGER NOT NULL,
    Fmi         INTEGER NOT NULL,
    Description TEXT NOT NULL,
    PRIMARY KEY (Spn, Fmi)
);

CREATE TABLE IF NOT EXISTS Logs (
    Id        INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatedAt TEXT NOT NULL,
    Source    TEXT,
    Message   TEXT NOT NULL
);

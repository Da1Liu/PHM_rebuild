BEGIN;

CREATE SCHEMA IF NOT EXISTS phm;

CREATE TABLE phm.machine (
    machine_id       TEXT PRIMARY KEY,
    display_name     TEXT NOT NULL,
    model             TEXT,
    controller_type   TEXT,
    active_epoch      INTEGER NOT NULL DEFAULT 1 CHECK (active_epoch > 0),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE phm.signal (
    signal_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    machine_id        TEXT NOT NULL REFERENCES phm.machine(machine_id),
    code              TEXT NOT NULL,
    display_name      TEXT NOT NULL,
    unit              TEXT,
    source_protocol   TEXT NOT NULL,
    source_address    TEXT NOT NULL,
    measurement_kind  TEXT NOT NULL,
    enabled           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (machine_id, code),
    UNIQUE (machine_id, source_protocol, source_address)
);

CREATE TABLE phm.acquisition_profile (
    profile_id        UUID PRIMARY KEY,
    machine_id        TEXT NOT NULL REFERENCES phm.machine(machine_id),
    revision          INTEGER NOT NULL CHECK (revision > 0),
    protocol          TEXT NOT NULL,
    configuration     JSONB NOT NULL,
    active            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (machine_id, protocol, revision)
);

CREATE UNIQUE INDEX ux_acquisition_profile_active
    ON phm.acquisition_profile(machine_id, protocol) WHERE active;

CREATE TABLE phm.collector_instance (
    collector_id      TEXT PRIMARY KEY,
    machine_id        TEXT NOT NULL REFERENCES phm.machine(machine_id),
    protocol          TEXT NOT NULL,
    software_version  TEXT NOT NULL,
    state             TEXT NOT NULL,
    last_seen_at      TIMESTAMPTZ,
    detail            JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE phm.scalar_observation (
    message_id        TEXT PRIMARY KEY,
    machine_id        TEXT NOT NULL REFERENCES phm.machine(machine_id),
    signal_id         BIGINT NOT NULL REFERENCES phm.signal(signal_id),
    observed_at       TIMESTAMPTZ NOT NULL,
    received_at       TIMESTAMPTZ NOT NULL,
    persisted_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    value             DOUBLE PRECISION,
    quality           TEXT NOT NULL CHECK (quality IN ('good', 'uncertain', 'bad', 'missing')),
    context           JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (quality <> 'good' OR value IS NOT NULL)
);

CREATE INDEX ix_scalar_observation_signal_time
    ON phm.scalar_observation(signal_id, observed_at DESC);
CREATE INDEX ix_scalar_observation_machine_time
    ON phm.scalar_observation(machine_id, observed_at DESC);

CREATE TABLE phm.feature_window (
    window_id          TEXT PRIMARY KEY,
    machine_id         TEXT NOT NULL REFERENCES phm.machine(machine_id),
    epoch              INTEGER NOT NULL CHECK (epoch > 0),
    window_start       TIMESTAMPTZ NOT NULL,
    window_end         TIMESTAMPTZ NOT NULL,
    received_at        TIMESTAMPTZ NOT NULL,
    persisted_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_signal_ids  BIGINT[] NOT NULL,
    features           JSONB NOT NULL,
    quality            TEXT NOT NULL CHECK (quality IN ('good', 'uncertain', 'bad', 'missing')),
    context            JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (window_end > window_start),
    CHECK (cardinality(source_signal_ids) > 0)
);

CREATE INDEX ix_feature_window_machine_time
    ON phm.feature_window(machine_id, window_start DESC);

CREATE TABLE phm.waveform_block (
    block_id           TEXT PRIMARY KEY,
    machine_id         TEXT NOT NULL REFERENCES phm.machine(machine_id),
    signal_id          BIGINT NOT NULL REFERENCES phm.signal(signal_id),
    epoch              INTEGER NOT NULL CHECK (epoch > 0),
    observed_at        TIMESTAMPTZ NOT NULL,
    received_at        TIMESTAMPTZ NOT NULL,
    sample_rate_hz     DOUBLE PRECISION NOT NULL CHECK (sample_rate_hz > 0),
    sample_count       INTEGER NOT NULL CHECK (sample_count > 0),
    encoding           TEXT NOT NULL,
    payload            BYTEA NOT NULL,
    checksum_sha256    TEXT NOT NULL,
    persisted_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_waveform_block_machine_time
    ON phm.waveform_block(machine_id, observed_at DESC);

CREATE TABLE phm.baseline_model (
    baseline_id        UUID PRIMARY KEY,
    machine_id         TEXT NOT NULL REFERENCES phm.machine(machine_id),
    epoch              INTEGER NOT NULL CHECK (epoch > 0),
    context_key        TEXT NOT NULL,
    algorithm          TEXT NOT NULL,
    algorithm_version  TEXT NOT NULL,
    feature_schema     JSONB NOT NULL,
    model_payload      JSONB NOT NULL,
    sample_count       INTEGER NOT NULL CHECK (sample_count >= 0),
    trained_at         TIMESTAMPTZ NOT NULL,
    active             BOOLEAN NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX ux_baseline_model_active
    ON phm.baseline_model(machine_id, epoch, context_key) WHERE active;

CREATE TABLE phm.evaluation_result (
    evaluation_id      UUID PRIMARY KEY,
    window_id          TEXT NOT NULL REFERENCES phm.feature_window(window_id),
    baseline_id        UUID REFERENCES phm.baseline_model(baseline_id),
    baseline_identity  UUID GENERATED ALWAYS AS (
                           COALESCE(baseline_id, '00000000-0000-0000-0000-000000000000'::uuid)
                       ) STORED,
    state              TEXT NOT NULL CHECK (state IN (
                            'not_evaluable', 'insufficient_data', 'normal',
                            'deviating', 'invalid_data')),
    score              DOUBLE PRECISION,
    t2                 DOUBLE PRECISION,
    spe                DOUBLE PRECISION,
    ucl_t2             DOUBLE PRECISION,
    ucl_spe            DOUBLE PRECISION,
    evidence           JSONB NOT NULL DEFAULT '{}'::jsonb,
    reason             TEXT,
    evaluated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (window_id, baseline_identity)
);

CREATE TABLE phm.maintenance_event (
    event_id           UUID PRIMARY KEY,
    machine_id         TEXT NOT NULL REFERENCES phm.machine(machine_id),
    occurred_at        TIMESTAMPTZ NOT NULL,
    event_type         TEXT NOT NULL,
    description        TEXT NOT NULL,
    epoch_before       INTEGER,
    epoch_after        INTEGER,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE phm.ingest_checkpoint (
    consumer_name      TEXT NOT NULL,
    source_name        TEXT NOT NULL,
    checkpoint         JSONB NOT NULL,
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (consumer_name, source_name)
);

COMMIT;

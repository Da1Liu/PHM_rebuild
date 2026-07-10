import json
from pathlib import Path

import jsonschema


SCHEMAS = Path(__file__).resolve().parents[2] / "packages" / "contracts" / "schemas"


def test_scalar_observation_example_matches_schema() -> None:
    schema = json.loads((SCHEMAS / "scalar-observation.schema.json").read_text("utf-8"))
    message = {
        "schemaVersion": "1.0",
        "messageId": "edge-01:speed:1",
        "machineId": "machine-01",
        "signalCode": "spindle_speed",
        "observedAt": "2026-07-10T08:00:00Z",
        "receivedAt": "2026-07-10T08:00:00.021Z",
        "value": 150.0,
        "quality": "good",
        "context": {"collectorId": "edge-01"},
    }
    jsonschema.validate(message, schema)


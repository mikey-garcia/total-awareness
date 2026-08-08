from total_awareness.core.models import Modality, Observation, ObservationType


def test_observation_round_trip():
    obs = Observation(sensor_id="test", modality=Modality.WIFI, type=ObservationType.RF_DETECTION)
    restored = Observation.model_validate_json(obs.model_dump_json())
    assert restored == obs

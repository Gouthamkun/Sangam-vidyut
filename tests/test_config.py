import pytest
from pydantic import ValidationError
from src.config.schema import SIRConfig, NetworkConfig

def test_invalid_beta():
    with pytest.raises(ValidationError):
        SIRConfig(beta=-0.1)
    with pytest.raises(ValidationError):
        SIRConfig(beta=1.1)

def test_invalid_network_p():
    with pytest.raises(ValidationError):
        NetworkConfig(ws_p=-0.5)
    with pytest.raises(ValidationError):
        NetworkConfig(ws_p=1.5)

def test_valid_bounds():
    config = SIRConfig(beta=0.0)
    assert config.beta == 0.0
    config = SIRConfig(beta=1.0)
    assert config.beta == 1.0

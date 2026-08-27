from __future__ import annotations

import pytest

from gridlens.domain.models import ScenarioRequest


@pytest.fixture
def default_request() -> ScenarioRequest:
    return ScenarioRequest()

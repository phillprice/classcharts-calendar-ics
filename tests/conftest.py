import os
import pytest

@pytest.fixture(autouse=True)
def mock_config_env(monkeypatch):
    """Configure environment variables for testing"""
    monkeypatch.setenv("AWS_REGION", "eu-west-2")
    monkeypatch.setenv("BUCKET_NAME", "classcharts-calendar")
    monkeypatch.setenv("CALENDAR_FILENAME_TEMPLATE", "{student_id}.ics")
    monkeypatch.setenv("SECRET_NAME", "classcharts/credentials")
    
    # Set test AWS credentials
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-2")
    
    # Patch LAMBDA_TMP_DIR to use actual temp dir for tests
    import tempfile
    import config
    monkeypatch.setattr(config, "LAMBDA_TMP_DIR", tempfile.gettempdir())
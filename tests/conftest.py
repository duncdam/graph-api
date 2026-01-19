import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from app.main import app
from app.utils.auth_utils import get_current_user, require_read_medical_data


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock current user data."""
    return {
        "username": "test_user",
        "full_name": "Test User",
        "email": "test@example.com",
        "token_id": "test_token_001",
        "scopes": ["read:medical_data"],
        "token_name": "Test Token",
    }


@pytest.fixture
def mock_valid_token_data():
    """Mock valid token data with all required fields."""
    return {
        "token": "mapi-test-token",
        "token_id": "test_token_001",
        "name": "Test Token",
        "description": "Test description",
        "scopes": ["read:medical_data"],
        "created_at": datetime.now(),
        "expires_at": None,
        "is_active": True,
        "user_info": {
            "username": "test_user",
            "full_name": "Test User",
            "email": "test@example.com",
        },
        "use_count": 0,
        "last_used": None,
    }


@pytest.fixture
def sample_patient_data():
    """Sample patient medical data for testing."""
    return {
        "medications": [
            {
                "startDate": "2024-01-01",
                "endDate": "2024-12-31",
                "medication": ["aspirin", "acetylsalicylic acid"],
                "medicationCode": "1191",
                "codeSystem": "RxNorm",
                "dosage": "81 mg",
                "prescriber": "Dr. Smith",
                "route": "oral",
                "medicationStatus": "active",
                "associatedCondition": ["heart disease prevention"],
                "associatedConditionCode": "Z87.891",
                "associatedConditionSystem": "ICD-10",
                "associatedConditionStatus": "active",
            }
        ],
        "conditions": [
            {
                "onsetDate": "2023-06-15",
                "abatementDate": None,
                "condition": ["hypertension", "high blood pressure"],
                "conditionCode": "I10",
                "codeSystem": "ICD-10",
                "conditionStatus": "active",
            }
        ],
        "procedures": [
            {
                "startDate": "2024-01-15",
                "procedure": ["cardiac catheterization"],
                "procedureCode": "93458",
                "codeSystem": "CPT",
                "procedureStatus": "completed",
                "associatedCondition": ["heart disease"],
                "associatedConditionCode": "414.9",
                "associatedConditionSystem": "ICD-9",
                "associatedConditionStatus": "active",
            }
        ],
        "observations": [
            {
                "startDate": "2024-01-01",
                "endDate": "2024-01-01",
                "diagnosticReport": "Blood Pressure Reading",
                "observationType": "vital-signs",
                "observation": ["blood pressure"],
                "observationCode": "85354-9",
                "codeSystem": "LOINC",
                "valueText": "120/80 mmHg",
                "valueQuantity": "120/80",
                "category": "vital-signs",
            }
        ],
    }


@pytest.fixture
def valid_patient_id():
    """Generate a valid patient ID for testing."""
    return "1234567890"


@pytest.fixture
def valid_uuid_patient_id():
    """Generate a valid UUID patient ID for testing."""
    import uuid

    return str(uuid.uuid4())


@pytest.fixture
def sample_pdm_data():
    """Sample PDM data for testing."""
    return {
        "patientStatement": [
            {"id": "1234567890", "name": [{"given": ["John"], "family": "Doe"}]}
        ],
        "condition": [{"id": "condition-456", "code": {"coding": [{"code": "I10"}]}}],
        "observation": [{"id": "observation-789", "status": "final"}],
        "medicationEvent": [{"id": "medication-event-101", "status": "active"}],
        "procedure": [],
        "encounter": [],
        "practitioner": [],
    }


@pytest.fixture
def authenticated_client(client, mock_current_user):
    """Create an authenticated test client."""

    def mock_get_current_user():
        return mock_current_user

    def mock_require_read_medical_data():
        return mock_current_user

    # Override dependencies
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_read_medical_data] = mock_require_read_medical_data

    yield client

    # Clean up
    app.dependency_overrides.clear()

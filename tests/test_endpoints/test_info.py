import pytest
from unittest.mock import patch, AsyncMock
from fastapi import status


class TestInfoEndpoints:
    """Test medical information endpoints."""

    def test_get_medications_authenticated(
        self, authenticated_client, sample_patient_data
    ):
        """Test getting patient medications with authentication."""
        # Use a valid UUID format for patient_id
        patient_id = (
            "123456789012345678901234567890123456"  # 36 character UUID-like string
        )
        # Or use a numeric-only patient ID
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["medications"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["patient_id"] == patient_id
            assert data["data_type"] == "medications"
            assert len(data["data"]) == 1
            assert data["data"][0]["medication"] == ["aspirin", "acetylsalicylic acid"]

    def test_get_medications_unauthenticated(self, client):
        """Test getting patient medications without authentication."""
        patient_id = "1234567890"
        response = client.get(f"/api/v1/info/medications/{patient_id}")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_get_conditions_authenticated(
        self, authenticated_client, sample_patient_data
    ):
        """Test getting patient conditions with authentication."""
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["conditions"],
        ):
            response = authenticated_client.get(f"/api/v1/info/conditions/{patient_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["patient_id"] == patient_id
            assert data["data_type"] == "conditions"
            assert len(data["data"]) == 1

    def test_get_patient_data_empty_patient_id(self, authenticated_client):
        """Test getting patient data with empty patient ID."""
        response = authenticated_client.get("/api/v1/info/medications/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_patient_data_database_error(self, authenticated_client):
        """Test getting patient data when database error occurs."""
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            side_effect=Exception("Database error"),
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_get_procedures_authenticated(
        self, authenticated_client, sample_patient_data
    ):
        """Test getting patient procedures with authentication."""
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["procedures"],
        ):
            response = authenticated_client.get(f"/api/v1/info/procedures/{patient_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["data_type"] == "procedures"
            assert len(data["data"]) == 1

    def test_get_observations_authenticated(
        self, authenticated_client, sample_patient_data
    ):
        """Test getting patient observations with authentication."""
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["observations"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/observations/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["data_type"] == "observations"
            assert len(data["data"]) == 1

    def test_get_medications_with_uuid(self, authenticated_client, sample_patient_data):
        """Test getting patient medications with a valid UUID."""
        import uuid

        patient_id = str(uuid.uuid4())  # Generate a valid UUID

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["medications"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["patient_id"] == patient_id
            assert data["data_type"] == "medications"
            assert len(data["data"]) == 1

    def test_patient_id_validation_numeric_only(
        self, authenticated_client, sample_patient_data
    ):
        """Test that numeric-only patient IDs are accepted."""
        patient_id = "123456789"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["medications"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK

    def test_get_all_data_types_for_patient(
        self, authenticated_client, sample_patient_data
    ):
        """Test getting all types of medical data for a patient."""
        patient_id = "1234567890"

        # Test medications
        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["medications"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["data_type"] == "medications"

        # Test conditions
        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["conditions"],
        ):
            response = authenticated_client.get(f"/api/v1/info/conditions/{patient_id}")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["data_type"] == "conditions"

        # Test procedures
        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["procedures"],
        ):
            response = authenticated_client.get(f"/api/v1/info/procedures/{patient_id}")
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["data_type"] == "procedures"

        # Test observations
        with patch(
            "app.utils.app_utils.execute_cypher_query",
            return_value=sample_patient_data["observations"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/observations/{patient_id}"
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["data_type"] == "observations"

    def test_empty_data_response(self, authenticated_client):
        """Test endpoint behavior when no data is found for patient."""
        patient_id = "9999999999"

        with patch("app.utils.app_utils.execute_cypher_query", return_value=[]):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["patient_id"] == patient_id
            assert data["data_type"] == "medications"
            assert len(data["data"]) == 0

    def test_async_cypher_query(self, authenticated_client, sample_patient_data):
        """Test with AsyncMock if execute_cypher_query is async."""
        patient_id = "1234567890"

        with patch(
            "app.utils.app_utils.execute_cypher_query",
            new_callable=AsyncMock,
            return_value=sample_patient_data["medications"],
        ):
            response = authenticated_client.get(
                f"/api/v1/info/medications/{patient_id}"
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["patient_id"] == patient_id

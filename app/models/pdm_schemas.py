from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict
import re
import uuid


class GoldenPDMResponse(BaseModel):
    """Response model for Golden PDM data"""

    patient_id: str = Field(..., description="The patient ID that was queried")
    data: Dict[str, List[Any]] = Field(
        ..., description="Dictionary containing all PDM data arrays"
    )
    total_records: int = Field(..., description="Total number of record types returned")
    record_counts: Dict[str, int] = Field(
        ..., description="Count of records per data type"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        # Check if it's a valid UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass

        # Check if it's a string of only numbers
        if re.match(r"^\d+$", v):
            return v

        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient123",
                "data": {
                    "patientStatement": ["statement1", "statement2"],
                    "condition": ["condition1", "condition2"],
                    "observation": ["obs1", "obs2"],
                },
                "total_records": 3,
                "record_counts": {
                    "patientStatement": 2,
                    "condition": 2,
                    "observation": 2,
                },
            }
        }


class GoldenPDMSummaryResponse(BaseModel):
    """Response model for Golden PDM summary"""

    patient_id: str = Field(..., description="The patient ID that was queried")
    data_types_available: List[str] = Field(
        ..., description="List of available data types"
    )
    record_counts: Dict[str, int] = Field(
        ..., description="Count of records per data type"
    )
    total_data_types: int = Field(
        ..., description="Total number of data types available"
    )
    total_records: int = Field(
        ..., description="Total number of records across all types"
    )
    has_data: bool = Field(
        ..., description="Whether any data was found for the patient"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        # Check if it's a valid UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass

        # Check if it's a string of only numbers
        if re.match(r"^\d+$", v):
            return v

        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )


class GoldenPDMByTypeResponse(BaseModel):
    """Response model for the specific data type endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(..., description="The specific data type requested")
    data: List[Dict[str, Any]] = Field(
        ..., description="The actual data records for the requested type"
    )
    count: int = Field(..., description="Number of records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        # Check if it's a valid UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass

        # Check if it's a string of only numbers
        if re.match(r"^\d+$", v):
            return v

        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "data_type": "condition",
                "data": [
                    {"id": "c1", "code": "diabetes", "status": "active"},
                    {"id": "c2", "code": "hypertension", "status": "active"},
                ],
                "count": 2,
            }
        }


class AvailableDataTypesResponse(BaseModel):
    """Response model for the available data types endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    available_data_types: List[str] = Field(
        ..., description="List of data types that contain data for this patient"
    )
    total_types: int = Field(..., description="Number of data types that have data")
    all_possible_types: List[str] = Field(
        ..., description="All possible data types that could be queried"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        # Check if it's a valid UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass

        # Check if it's a string of only numbers
        if re.match(r"^\d+$", v):
            return v

        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "550e8400-e29b-41d4-a716-446655440000",
                "available_data_types": [
                    "patientStatement",
                    "condition",
                    "observation",
                ],
                "total_types": 3,
                "all_possible_types": [
                    "patientStatement",
                    "condition",
                    "observation",
                    "documentReference",
                    "diagnosticReport",
                    "procedure",
                ],
            }
        }


class PDMServiceInfoResponse(BaseModel):
    """Response model for the service info endpoint"""

    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    endpoints: Dict[str, str] = Field(
        ..., description="Available endpoints and their paths"
    )
    supported_data_types: List[str] = Field(..., description="All supported data types")

    class Config:
        json_schema_extra = {
            "example": {
                "service": "PDM (Patient Data Management)",
                "version": "1.0.0",
                "description": "Service for retrieving golden PDM records from Neo4j graph database",
                "endpoints": {
                    "get_golden_pdm": "/pdm/golden/{patient_id}",
                    "get_summary": "/pdm/golden/{patient_id}/summary",
                    "get_by_type": "/pdm/golden/{patient_id}/type/{data_type}",
                    "get_types": "/pdm/golden/{patient_id}/types",
                },
                "supported_data_types": [
                    "patientStatement",
                    "condition",
                    "observation",
                    "documentReference",
                    "diagnosticReport",
                    "procedure",
                ],
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    patient_id: Optional[str] = Field(None, description="Patient ID if provided")
    status_code: int = Field(..., description="HTTP status code")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        # Check if it's a valid UUID
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass

        # Check if it's a string of only numbers
        if re.match(r"^\d+$", v):
            return v

        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

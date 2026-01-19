from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict
from datetime import datetime
import re
import uuid


class MedicationResponse(BaseModel):
    """Response model for patient medications endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="medications", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of medication records")
    count: int = Field(..., description="Number of medication records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "medications",
                "data": [
                    {
                        "startDate": "2023-01-15T10:30:00",
                        "endDate": "2023-02-15T10:30:00",
                        "medication": ["aspirin", "acetylsalicylic acid"],
                        "medicationCode": "1191",
                        "codeSystem": "RxNorm",
                        "medicationStatus": "active",
                        "route": "oral",
                        "dosage": "81 mg daily",
                        "associatedCondition": ["cardiovascular disease"],
                        "associatedConditionSystem": "SNOMED-CT",
                        "associatedConditionCode": "49601007",
                        "conditionStatus": "active",
                    }
                ],
                "count": 1,
            }
        }


class ConditionResponse(BaseModel):
    """Response model for patient conditions endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="conditions", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of condition records")
    count: int = Field(..., description="Number of condition records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "conditions",
                "data": [
                    {
                        "condition": ["diabetes mellitus", "diabetes"],
                        "conditionCode": "73211009",
                        "codeSystem": "SNOMED-CT",
                        "clinicalStatus": "active",
                        "onsetDate": "2020-03-15T00:00:00",
                        "abatementDate": None,
                    }
                ],
                "count": 1,
            }
        }


class ProcedureResponse(BaseModel):
    """Response model for patient procedures endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="procedures", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of procedure records")
    count: int = Field(..., description="Number of procedure records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "procedures",
                "data": [
                    {
                        "startDate": "2023-06-10T14:00:00",
                        "procedure": ["colonoscopy", "endoscopic examination"],
                        "procedureCode": "73761001",
                        "codeSystem": "SNOMED-CT",
                        "procedureStatus": "completed",
                        "associatedCondition": ["colorectal screening"],
                        "associatedConditionSystem": "SNOMED-CT",
                        "associatedConditionCode": "268547008",
                        "associatedConditionStatus": "active",
                    }
                ],
                "count": 1,
            }
        }


class ObservationResponse(BaseModel):
    """Response model for patient observations endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="observations", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of observation records")
    count: int = Field(..., description="Number of observation records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "observations",
                "data": [
                    {
                        "startDate": "2023-08-15T09:30:00",
                        "endDate": "2023-08-15T10:00:00",
                        "diagnosticReport": ["blood chemistry panel"],
                        "observationType": "laboratory",
                        "observation": ["glucose", "blood glucose"],
                        "observationCode": "33747000",
                        "codeSystem": "SNOMED-CT",
                        "valueText": "95 mg/dL",
                        "valueQuantity": {
                            "value": 95,
                            "unit": "mg/dL",
                            "system": "UCUM",
                        },
                        "category": "laboratory",
                    }
                ],
                "count": 1,
            }
        }


class AllergyResponse(BaseModel):
    """Response model for patient allergies endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="allergies", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of allergy records")
    count: int = Field(..., description="Number of allergy records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "allergies",
                "data": [
                    {
                        "allergyRecordedDate": "2021-05-20T00:00:00",
                        "allergy": ["penicillin", "beta-lactam antibiotic"],
                        "allergyCode": "764146007",
                        "codeSystem": "SNOMED-CT",
                        "allergyType": "medication",
                        "reactionRecordedDate": "2021-05-20T12:30:00",
                        "reactionSeverity": "moderate",
                    }
                ],
                "count": 1,
            }
        }


class ImmunizationResponse(BaseModel):
    """Response model for patient immunizations endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="immunizations", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of immunization records")
    count: int = Field(..., description="Number of immunization records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "immunizations",
                "data": [
                    {
                        "recordedDate": "2023-09-01T10:00:00",
                        "status": "completed",
                        "immunization": ["covid-19 vaccine", "mrna vaccine"],
                        "immunizationCode": "91300-6",
                        "codeSystem": "LOINC",
                    }
                ],
                "count": 1,
            }
        }


class ProviderResponse(BaseModel):
    """Response model for patient providers endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="providers", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of provider records")
    count: int = Field(..., description="Number of provider records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "providers",
                "data": [
                    {
                        "providerType": "Practitioner",
                        "name": "Dr. John Smith",
                        "telecom": [
                            {
                                "system": "phone",
                                "value": "(555) 123-4567",
                                "use": "work",
                            }
                        ],
                        "address": "123 Medical Center Dr",
                        "city": "Healthcare City",
                        "state": "CA",
                        "postalCode": "12345",
                    }
                ],
                "count": 1,
            }
        }


class ClinicalNoteResponse(BaseModel):
    """Response model for patient clinical notes endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(
        default="clinical_notes", description="Type of data returned"
    )
    data: List[Dict[str, Any]] = Field(..., description="List of clinical note records")
    count: int = Field(..., description="Number of clinical note records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "clinical_notes",
                "data": [
                    {
                        "noteType": "Condition",
                        "content": "Patient presents with well-controlled diabetes mellitus type 2. Continue current medication regimen.",
                    }
                ],
                "count": 1,
            }
        }


class EncounterResponse(BaseModel):
    """Response model for patient encounters endpoint"""

    patient_id: str = Field(..., description="The unique identifier for the patient")
    data_type: str = Field(default="encounters", description="Type of data returned")
    data: List[Dict[str, Any]] = Field(..., description="List of encounter records")
    count: int = Field(..., description="Number of encounter records found")

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "008288897179",
                "data_type": "encounters",
                "data": [
                    {
                        "startDate": "2023-08-15T09:00:00",
                        "endDate": "2023-08-15T10:30:00",
                        "encounterClassification": "outpatient",
                        "encounterType": "routine checkup",
                    }
                ],
                "count": 1,
            }
        }


class CodeServiceInfoResponse(BaseModel):
    """Response model for the code service info endpoint"""

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
                "service": "Code (Medical Code Management)",
                "version": "1.0.0",
                "description": "Service for retrieving medical codes and names from Neo4j graph database",
                "endpoints": {
                    "get_medications": "/code/medications/{patient_id}",
                    "get_conditions": "/code/conditions/{patient_id}",
                    "get_procedures": "/code/procedures/{patient_id}",
                    "get_observations": "/code/observations/{patient_id}",
                    "get_allergies": "/code/allergies/{patient_id}",
                    "get_immunizations": "/code/immunizations/{patient_id}",
                    "get_providers": "/code/providers/{patient_id}",
                    "get_clinical_notes": "/code/clinical-notes/{patient_id}",
                    "get_encounters": "/code/encounters/{patient_id}",
                },
                "supported_data_types": [
                    "medications",
                    "conditions",
                    "procedures",
                    "observations",
                    "allergies",
                    "immunizations",
                    "providers",
                    "clinical_notes",
                    "encounters",
                ],
            }
        }


# Error response schemas
class CodeErrorResponse(BaseModel):
    """Error response model for code endpoints"""

    error: str = Field(..., description="Error message")
    patient_id: Optional[str] = Field(None, description="Patient ID if provided")
    status_code: int = Field(..., description="HTTP status code")
    endpoint: Optional[str] = Field(
        None, description="Endpoint that generated the error"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            pass
        if re.match(r"^\d+$", v):
            return v
        raise ValueError(
            "patient_id must be a valid UUID or a string containing only numbers"
        )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "No medication data found for patient ID: 008288897179",
                "patient_id": "008288897179",
                "status_code": 404,
                "endpoint": "/code/medications/{patient_id}",
            }
        }

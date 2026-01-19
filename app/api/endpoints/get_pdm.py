from fastapi import APIRouter, HTTPException, Query, Depends, Path
from typing import Dict, Any

from app.models.pdm_schemas import (
    GoldenPDMResponse,
    GoldenPDMSummaryResponse,
    GoldenPDMByTypeResponse,
    AvailableDataTypesResponse,
    PDMServiceInfoResponse,
)
from app.utils import app_utils
from app.utils.app_utils import logger
from app.utils.pdm_utils import get_golden_pdm
from app.utils.auth_utils import require_read_medical_data

# Configure router
router = APIRouter()


@router.get(
    "/golden/{patient_id}",
    response_model=GoldenPDMResponse,
    responses={
        200: {"description": "Successfully retrieved golden PDM data"},
        404: {"description": "Patient not found or no data available"},
        400: {"description": "Invalid patient ID format"},
        500: {"description": "Internal server error"},
    },
    summary="Get Golden PDM for Patient",
    description="""
    Retrieve comprehensive golden PDM data for a specific patient from the Neo4j graph database.
    
    This endpoint executes multiple Cypher queries in parallel to gather comprehensive
    patient data including:
    - Patient statements
    - Conditions  
    - Observations
    - Document references
    - Diagnostic reports
    - Procedures
    - Encounters
    - Contact persons
    - Medication events
    - Practitioners
    - Allergies
    - Family member history
    - Compositions
    - Service requests
    - Care teams
    - Care plans
    - Organizations
    - Locations
    - Practitioner roles
    """,
)
async def get_golden_pdm_endpoint(
    patient_id: str = Path(
        ...,
        description="The unique identifier for the patient",
        examples="550e8400-e29b-41d4-a716-446655440000",
    ),
    include_empty: bool = Query(
        False, description="Whether to include empty result sets in response"
    ),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> GoldenPDMResponse:
    """
    Retrieve golden PDM data for a specific patient.
    """

    try:
        logger.info(f"Retrieving golden PDM data for patient: {patient_id}")

        # Validate patient_id format
        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Execute the golden PDM query with optional connection overrides
        logger.debug(f"Executing golden PDM queries for patient: {patient_id}")

        result_data = await get_golden_pdm(patient_id=patient_id, **db_params)

        # Filter out empty results if requested
        if not include_empty:
            result_data = {
                key: values
                for key, values in result_data.items()
                if values and len(values) > 0
            }

        # Check if any data was found
        if not result_data:
            logger.warning(f"No golden PDM data found for patient: {patient_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No golden PDM data found for patient ID: {patient_id}",
            )

        # Calculate metrics
        record_counts = {key: len(values) for key, values in result_data.items()}
        total_records = len(result_data)
        total_items = sum(len(values) for values in result_data.values())

        logger.info(
            f"Successfully retrieved {total_records} record types with {total_items} total items for patient: {patient_id}"
        )

        return GoldenPDMResponse(
            patient_id=patient_id,
            data=result_data,
            total_records=total_records,
            record_counts=record_counts,
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving golden PDM for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving golden PDM data: {str(e)}",
        )


@router.get(
    "/golden/{patient_id}/summary",
    response_model=GoldenPDMSummaryResponse,
    summary="Get Golden PDM Summary",
    description="Get a summary of available data types for a patient without retrieving the full data",
)
async def get_golden_pdm_summary(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> GoldenPDMSummaryResponse:
    """
    Get a summary of available golden PDM data for a patient.
    Returns counts and data types without the full content.
    """

    try:
        logger.info(f"Retrieving golden PDM summary for patient: {patient_id}")

        # Validate patient_id
        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Get full data
        result_data = await get_golden_pdm(patient_id=patient_id, **db_params)

        # Create summary
        record_counts = {key: len(values) for key, values in result_data.items()}
        summary = GoldenPDMSummaryResponse(
            patient_id=patient_id,
            data_types_available=list(result_data.keys()),
            record_counts=record_counts,
            total_data_types=len(result_data),
            total_records=sum(len(values) for values in result_data.values()),
            has_data=len(result_data) > 0,
        )

        logger.info(
            f"Generated summary for patient {patient_id}: {summary.total_data_types} data types, {summary.total_records} total records"
        )

        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving golden PDM summary for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving summary: {str(e)}",
        )


@router.get(
    "/golden/{patient_id}/type/{data_type}",
    response_model=GoldenPDMByTypeResponse,
    summary="Get Specific Data Type",
    description="Retrieve only a specific type of data for a patient (e.g., conditions, observations)",
)
async def get_golden_pdm_by_type(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    data_type: str = Path(..., description="The specific data type to retrieve"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Get only a specific data type from the golden PDM for a patient.

    Available data types:
    - patientStatement
    - condition
    - observation
    - documentReference
    - diagnosticReport
    - procedure
    - encounter
    - contactPerson
    - medicationEvent
    - practitioner
    - allergy
    - familyMemberHistory
    - composition
    - serviceRequest
    - careTeam
    - carePlan
    - organization
    - location
    - practitionerRole
    """

    try:
        logger.info(f"Retrieving {data_type} data for patient: {patient_id}")

        # Validate inputs
        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        if not data_type or len(data_type.strip()) == 0:
            raise HTTPException(status_code=400, detail="Data type cannot be empty")

        # Get full data
        result_data = await get_golden_pdm(patient_id=patient_id, **db_params)

        # Check if requested data type exists
        if data_type not in result_data:
            available_types = list(result_data.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Data type '{data_type}' not found. Available types: {available_types}",
            )

        response = {
            "patient_id": patient_id,
            "data_type": data_type,
            "data": result_data[data_type],
            "count": len(result_data[data_type]),
        }

        logger.info(
            f"Retrieved {len(result_data[data_type])} {data_type} records for patient {patient_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving {data_type} for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving {data_type}: {str(e)}",
        )


@router.get(
    "/golden/{patient_id}/types",
    response_model=AvailableDataTypesResponse,
    summary="Get Available Data Types",
    description="Get list of available data types for a patient without retrieving the actual data",
)
async def get_available_data_types(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Get list of available data types for a patient.
    """

    try:
        logger.info(f"Retrieving available data types for patient: {patient_id}")

        # Validate patient_id
        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Get data
        result_data = await get_golden_pdm(patient_id=patient_id, **db_params)

        # Filter to only non-empty data types
        available_types = [
            key for key, values in result_data.items() if values and len(values) > 0
        ]

        response = {
            "patient_id": patient_id,
            "available_data_types": available_types,
            "total_types": len(available_types),
            "all_possible_types": list(result_data.keys()),
        }

        logger.info(
            f"Found {len(available_types)} available data types for patient {patient_id}"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving data types for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving data types: {str(e)}",
        )


@router.get(
    "/",
    response_model=PDMServiceInfoResponse,
    summary="PDM Service Info",
    description="Get information about the PDM service",
)
async def pdm_service_info():
    """Get information about the PDM service"""
    return {
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
            "encounter",
            "contactPerson",
            "medicationEvent",
            "practitioner",
            "allergy",
            "familyMemberHistory",
            "composition",
            "serviceRequest",
            "careTeam",
            "carePlan",
            "organization",
            "location",
            "practitionerRole",
        ],
    }

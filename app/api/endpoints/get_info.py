from urllib import response
from fastapi import APIRouter, HTTPException, Depends, Path
from typing import Dict, Any


from app.utils import app_utils
from app.utils.app_utils import logger
from app.utils.auth_utils import require_read_medical_data
from app.models.info_schemas import (
    MedicationResponse,
    ConditionResponse,
    ProcedureResponse,
    ObservationResponse,
    AllergyResponse,
    EncounterResponse,
    ImmunizationResponse,
    ClinicalNoteResponse,
    ProviderResponse,
    CodeServiceInfoResponse,
    CodeErrorResponse,
)
from app.utils.template_utils import cypher_template_manager

# Configure router
router = APIRouter()


@router.get(
    "/medications/{patient_id}",
    summary="Get Patient Medications",
    response_model=MedicationResponse,
    description="Retrieve name and code for all medications from a patient",
    responses={
        200: {"description": "Successfully retrieved medication data"},
        404: {
            "description": "Patient not found or no medications available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_medications(
    patient_id: str = Path(
        ...,
        description="The unique identifier for the patient",
    ),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all medications associated with a patient.
    """

    try:
        logger.info(f"Retrieving medication data for patient: {patient_id}")

        # Validate patient_id format
        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get medication name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_medications.cypher", patient_id=patient_id
        )

        # Execute query
        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        # Process results
        medications = [
            {
                "startDate": record["startDate"],
                "endDate": record["endDate"],
                "medication": record["medication"],
                "medicationCode": record["medicationCode"],
                "codeSystem": record["codeSystem"],
                "medicationStatus": record["medicationStatus"],
                "route": record["route"],
                "dosage": record["dosage"],
                "associatedCondition": record["associatedCondition"],
                "associatedConditionSystem": record["associatedConditionSystem"],
                "associatedConditionCode": record["associatedConditionCode"],
                "associatedConditionStatus": record["associatedConditionStatus"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(medications)} medications for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "medications",
            "data": medications,
            "count": len(medications),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving medications for patient {patient_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving medications: {str(e)}",
        )


@router.get(
    "/conditions/{patient_id}",
    summary="Get Patient Conditions",
    response_model=ConditionResponse,
    description="Retrieve name and code for all conditions from a patient",
    responses={
        200: {"description": "Successfully retrieved condition data"},
        404: {
            "description": "Patient not found or no conditions available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_conditions(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all conditions associated with a patient.
    """

    try:
        logger.info(f"Retrieving condition data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get condition name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_conditions.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        conditions = [
            {
                "condition": record["condition"],
                "conditionCode": record["conditionCode"],
                "codeSystem": record["codeSystem"],
                "clinicalStatus": record["conditionStatus"],
                "onsetDate": record["onsetDate"],
                "abatementDate": record["abatementDate"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(conditions)} conditions for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "conditions",
            "data": conditions,
            "count": len(conditions),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving conditions for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving conditions: {str(e)}",
        )


@router.get(
    "/procedures/{patient_id}",
    summary="Get Patient Procedures",
    response_model=ProcedureResponse,
    description="Retrieve name and code for all procedures from a patient",
    responses={
        200: {"description": "Successfully retrieved procedure data"},
        404: {
            "description": "Patient not found or no procedures available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_procedures(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all procedures associated with a patient.
    """

    try:
        logger.info(f"Retrieving procedure data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get procedure name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_procedures.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        procedures = [
            {
                "startDate": record["startDate"],
                "procedure": record["procedure"],
                "procedureCode": record["procedureCode"],
                "codeSystem": record["codeSystem"],
                "procedureStatus": record["procedureStatus"],
                "associatedCondition": record["associatedCondition"],
                "associatedConditionSystem": record["associatedConditionSystem"],
                "associatedConditionCode": record["associatedConditionCode"],
                "associatedConditionStatus": record["associatedConditionStatus"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(procedures)} procedures for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "procedures",
            "data": procedures,
            "count": len(procedures),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving procedures for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving procedures: {str(e)}",
        )


@router.get(
    "/observations/{patient_id}",
    summary="Get Patient Observations",
    response_model=ObservationResponse,
    description="Retrieve name and code for all observations from a patient",
    responses={
        200: {"description": "Successfully retrieved observation data"},
        404: {
            "description": "Patient not found or no observations available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_observations(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all observations associated with a patient.
    """

    try:
        logger.info(f"Retrieving observation data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get observation name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_observations.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        observations = [
            {
                "startDate": record["startDate"],
                "endDate": record["endDate"],
                "diagnosticReport": record["diagnosticReport"],
                "observationType": record["observationType"],
                "observation": record["observation"],
                "observationCode": record["observationCode"],
                "codeSystem": record["codeSystem"],
                "valueText": record["valueText"],
                "valueQuantity": record["valueQuantity"],
                "category": record["category"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(observations)} observations for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "observations",
            "data": observations,
            "count": len(observations),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving observations for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving observations: {str(e)}",
        )


@router.get(
    "/allergies/{patient_id}",
    summary="Get Patient Allergies",
    response_model=AllergyResponse,
    description="Retrieve name and code for all allergies from a patient",
    responses={
        200: {"description": "Successfully retrieved allergy data"},
        404: {
            "description": "Patient not found or no allergies available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_allergies(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all allergies associated with a patient.
    """

    try:
        logger.info(f"Retrieving allergy data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get allergy name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_allergies.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        allergies = [
            {
                "allergyRecordedDate": record["allergyRecordedDate"],
                "allergy": record["allergy"],
                "allergyCode": record["allergyCode"],
                "codeSystem": record["codeSystem"],
                "allergyType": record["allergyType"],
                "reactionRecordedDate": record["reactionRecordedDate"],
                "reactionSeverity": record["reactionSeverity"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(allergies)} allergies for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "allergies",
            "data": allergies,
            "count": len(allergies),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving allergies for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving allergies: {str(e)}",
        )


@router.get(
    "/immunizations/{patient_id}",
    summary="Get Patient Immunizations",
    response_model=ImmunizationResponse,
    description="Retrieve name and code for all immunizations from a patient",
    responses={
        200: {"description": "Successfully retrieved immunization data"},
        404: {
            "description": "Patient not found or no immunizations available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_immunizations(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve name and code for all immunizations associated with a patient.
    """

    try:
        logger.info(f"Retrieving immunization data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get immunization name and code
        cypher_query = cypher_template_manager.render_template(
            "get_patient_immunizations.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        immunizations = [
            {
                "recordedDate": record["recordedDate"],
                "status": record["status"],
                "immunization": record["immunization"],
                "immunizationCode": record["immunizationCode"],
                "codeSystem": record["codeSystem"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(immunizations)} immunizations for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "immunizations",
            "data": immunizations,
            "count": len(immunizations),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving immunizations for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving immunizations: {str(e)}",
        )


@router.get(
    "/providers/{patient_id}",
    summary="Get Patient Providers",
    response_model=ProviderResponse,
    description="Retrieve information for all providers associated with a patient",
    responses={
        200: {"description": "Successfully retrieved provider data"},
        404: {
            "description": "Patient not found or no providers available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_providers(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve information for all providers associated with a patient.
    """

    try:
        logger.info(f"Retrieving provider data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get provider information
        cypher_query = cypher_template_manager.render_template(
            "get_patient_providers.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        providers = [
            {
                "providerType": record["providerType"],
                "name": record["name"],
                "telecom": record["telecom"],
                "address": record["address"],
                "city": record["city"],
                "state": record["state"],
                "postalCode": record["postalCode"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(providers)} providers for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "providers",
            "data": providers,
            "count": len(providers),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving providers for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving providers: {str(e)}",
        )


@router.get(
    "/clinical-notes/{patient_id}",
    summary="Get Patient Clinical Notes",
    response_model=ClinicalNoteResponse,
    description="Retrieve all clinical notes and documentation for a patient",
    responses={
        200: {"description": "Successfully retrieved clinical note data"},
        404: {
            "description": "Patient not found or no clinical notes available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_clinical_notes(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve all clinical notes and documentation for a patient.
    """

    try:
        logger.info(f"Retrieving clinical note data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get clinical notes
        cypher_query = cypher_template_manager.render_template(
            "get_patient_clinical_notes.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        clinical_notes = [
            {
                "noteType": record["noteType"],
                "content": record["content"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(clinical_notes)} clinical notes for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "clinical_notes",
            "data": clinical_notes,
            "count": len(clinical_notes),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving clinical notes for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving clinical notes: {str(e)}",
        )


@router.get(
    "/encounters/{patient_id}",
    summary="Get Patient Encounters",
    response_model=EncounterResponse,
    description="Retrieve all encounters and visits for a patient",
    responses={
        200: {"description": "Successfully retrieved encounter data"},
        404: {
            "description": "Patient not found or no encounters available",
            "model": CodeErrorResponse,
        },
        400: {"description": "Invalid patient ID format", "model": CodeErrorResponse},
        500: {"description": "Internal server error", "model": CodeErrorResponse},
    },
)
async def get_patient_encounters(
    patient_id: str = Path(..., description="The unique identifier for the patient"),
    db_params: Dict[str, Any] = Depends(app_utils.get_db_params),
    current_user: Dict = Depends(require_read_medical_data),
) -> Dict[str, Any]:
    """
    Retrieve all encounters and visits for a patient.
    """

    try:
        logger.info(f"Retrieving encounter data for patient: {patient_id}")

        if not patient_id or len(patient_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Patient ID cannot be empty")

        # Cypher query to get encounter information
        cypher_query = cypher_template_manager.render_template(
            "get_patient_encounters.cypher", patient_id=patient_id
        )

        result = await app_utils.execute_cypher_query(query=cypher_query, **db_params)

        encounters = [
            {
                "startDate": record["startDate"],
                "endDate": record["endDate"],
                "encounterClassification": record["encounterClassification"],
                "encounterType": record["encounterType"],
            }
            for record in result
        ]

        logger.info(
            f"Successfully retrieved {len(encounters)} encounters for patient: {patient_id}"
        )

        return {
            "patient_id": patient_id,
            "data_type": "encounters",
            "data": encounters,
            "count": len(encounters),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            f"Error retrieving encounters for patient {patient_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving encounters: {str(e)}",
        )


@router.get(
    "/",
    summary="Medical Information Service",
    response_model=CodeServiceInfoResponse,
    description="Get information about the Medical information service",
)
async def medical_information_service():
    """Get information about the Medical information service"""
    return {
        "service": "Medical Information Service",
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
            "health_check": "/code/health",
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

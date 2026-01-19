import orjson
from typing import Dict, Any
from app.utils import app_utils


async def get_golden_pdm(
    patient_id: str,
    uri: str = app_utils.neo.uri,
    username: str = app_utils.neo.username,
    password: str = app_utils.neo.password,
    database: str = app_utils.neo.database,
    params: Dict[str, Any] = {},
):
    """
    Function to query golden PDM from the graph
    @Args:
        patient_id: The ID of the patient to query
        uri: The URI of the Neo4j database
        username: The username to connect to the database
        password: The password to connect to the database
        database: The name of the database
        params: Additional parameters for the query
    """
    cypher_queries = [
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' RETURN collect(n.content) as patientStatement",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_CONDITION]->(c:Condition) RETURN collect(c.content) as condition",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_OBSERVATION]->(o:Observation) RETURN collect(o.content) as observation",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_DOCUMENT_REFERENCE]->(d:DocumentReference) RETURN collect(d.content) as documentReference",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_DIAGNOSTIC_REPORT]->(dr:DiagnosticReport) RETURN collect(dr.content) as diagnosticReport",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_PROCEDURE]->(p:Procedure) RETURN collect(p.content) as procedure",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_ENCOUNTER]->(e:Encounter) RETURN collect(e.content) as encounter",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_CONTACT]->(c:ContactPerson) RETURN collect(c.content) as contactPerson",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_MEDICATION_EVENT]->(me:MedicationEvent) RETURN collect(me.content) as medicationEvent",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_PRACTITIONER]->(p:Practitioner) RETURN collect(p.content) as practitioner",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_ALLERGY]->(a:Allergy) RETURN collect(a.content) as allergy",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_FAMILY_MEMBER_HISTORY]->(f:FamilyMemberHistory) RETURN collect(f.content) as familyMemberHistory",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_COMPOSITION]->(c:Composition) RETURN collect(c.content) as composition",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_SERVICE_REQUEST]->(sr:ServiceRequest) RETURN collect(sr.content) as serviceRequest",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_CARE_TEAM]->(ct:CareTeam) RETURN collect(ct.content) as careTeam",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:HAS_CARE_PLAN]->(cp:CarePlan) RETURN collect(cp.content) as carePlan",
        f"MATCH (n:Patient) WHERE n.id = '{patient_id}' OPTIONAL MATCH (n:Patient)-[:INTERACTS_WITH]->(o:Organization) RETURN collect(o.content) as organization",
        f"""
            MATCH (n:Patient) WHERE n.id = '{patient_id}'
            CALL (n) {{
                WITH n
                OPTIONAL MATCH (n)-[:INTERACTS_WITH]->(o:Organization)
                OPTIONAL MATCH (o)<-[:MANAGED_BY]-(l:Location)
                RETURN l.content as content
                UNION
                OPTIONAL MATCH (n)-[:HAS_ENCOUNTER]->(e:Encounter)
                OPTIONAL MATCH (e)-[:TAKES_PLACE]->(l:Location)
                RETURN l.content as content
            }}
            RETURN collect(DISTINCT content) as location
        """,
        f"""
            MATCH (n:Patient) WHERE n.id = '{patient_id}' 
            OPTIONAL MATCH (n:Patient)-[:HAS_PRACTITIONER]->(p:Practitioner)
            OPTIONAL MATCH (p)-[:HAS_ROLE]->(pr:PractitionerRole) 
            RETURN collect(pr.content) as practitionerRole
        """,
    ]

    # Split into batches and execute
    batch_size = 5
    query_batches = [
        cypher_queries[i : i + batch_size]
        for i in range(0, len(cypher_queries), batch_size)
    ]

    all_results = []
    for batch in query_batches:
        batch_results = await app_utils.execute_batch_async(batch)
        all_results.extend(batch_results)

    # Convert to dictionary format
    result_dict = {}
    for df in all_results:
        if df is not None and not df.empty:
            column_name = df.columns[0]
            column_values = df[column_name].dropna().iloc[0] if len(df) > 0 else []
            result_dict[column_name] = [orjson.loads(cv) for cv in column_values]

    return result_dict

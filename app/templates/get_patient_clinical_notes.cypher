MATCH path = (p:Patient)-[r1]->(e:Allergy|Condition|Observation|Procedure|DiagnosticReport|MedicationEvent)-[r2:HAS_NOTE]->(n:Note)
WHERE p.id = "{{ patient_id }}"
RETURN DISTINCT
    labels(e)[0] as noteType,
    n.text as content

MATCH path = (p:Patient)-[r1]->(immun:MedicationEvent)-[r2:USED]->(med:Medication)
WHERE p.id = "{{ patient_id }}"
AND toLower(immun.medicationEventType) = "immunization"
OPTIONAL MATCH (med)-[:ENCODED_AS]->(medcode:Code)
WITH  immun, med, medcode
RETURN
    COALESCE(immun.effectivePeriodStartDate, immun.effectiveDateTime) as recordedDate,
    immun.status as status,
    apoc.coll.toSet(
        [text in COALESCE(med.displayText, []) WHERE text IS NOT NULL | toLower(text)] + 
        [text in COALESCE([medcode.name], []) WHERE text IS NOT NULL | toLower(text)]
    ) as immunization,
    medcode.code as immunizationCode,
    medcode.system as codeSystem
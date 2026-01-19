MATCH path = (p:Patient)-[r1]-(m:MedicationEvent)-[r2:USED]->(q:Medication)
WHERE p.id = "{{ patient_id }}"
OPTIONAL MATCH path2 = (q)-[r3:ENCODED_AS]->(s:Code)
OPTIONAL MATCH (m)-[r6]->(dosage:MedicationDosage)
OPTIONAL MATCH (m)-[r4]-(c:Condition)-[r5]-(s1:Code)
WHERE toLower(s1.name) <> 'diagnosis'
WITH p,m,q,s,s1,c, dosage, apoc.convert.fromJsonMap(dosage.route) as route, apoc.convert.fromJsonMap(c.clinicalStatus) as value
RETURN
    m.effectivePeriodStartDate as startDate,
    m.effectivePeriodEndDate as endDate,
    m.status as medicationStatus,
    apoc.coll.toSet(
        [text in COALESCE(q.displayText, []) WHERE text IS NOT NULL | lower(text)] + 
        [text in COALESCE([s.name], []) WHERE text IS NOT NULL | lower(text)]
    ) as medication,
    s.code AS medicationCode,
    s.system AS codeSystem,
    route["coding"][0]["display"] as route,
    dosage.text as dosage,
    apoc.coll.toSet(
        [text in COALESCE(s1.displayText, []) WHERE text IS NOT NULL | lower(text)] + 
        [text in COALESCE([s1.name], []) WHERE text IS NOT NULL | lower(text)]
    ) as associatedCondition,
    s1.code as associatedConditionCode,
    s1.system as associatedConditionSystem,
    COALESCE(value.coding[0].display, value.coding[0].code) as associatedConditionStatus
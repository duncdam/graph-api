MATCH (p:Patient)-[r1:HAS_PROCEDURE]->(n:Procedure)
WHERE p.id = "{{ patient_id }}"
OPTIONAL MATCH (n)-[r2:ENCODED_AS]->(q:Code)
OPTIONAL MATCH (n)-[r3:ASSOCIATED_WITH]->(s:Condition)-[r4:ENCODED_AS]->(t:Code)
WITH p, n, q, t, s, apoc.convert.fromJsonMap(n.statusReason) as statusReason, apoc.convert.fromJsonMap(s.clinicalStatus) as value
RETURN DISTINCT
    n.occurrencePeriodStartDate as startDate, 
    apoc.coll.toSet(
        [text in COALESCE(n.displayText, []) WHERE text IS NOT NULL | toLower(text)] + 
        [text in COALESCE([q.name], []) WHERE text IS NOT NULL | toLower(text)]
    ) as procedure,
    q.code as procedureCode,
    q.system as codeSystem,
    statusReason["coding"][0]["code"] as procedureStatus,
    apoc.coll.toSet(
        [text in COALESCE(s.displayText, []) WHERE text IS NOT NULL | toLower(text)] + 
        [text in COALESCE([t.name], []) WHERE text IS NOT NULL | toLower(text)]
    ) as associatedCondition,
    t.system as associatedConditionSystem,
    t.code as associatedConditionCode,
    COALESCE(value.coding[0].display, value.coding[0].code) as associatedConditionStatus
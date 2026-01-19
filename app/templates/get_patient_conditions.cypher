MATCH (pa:Patient)-[r1:HAS_CONDITION]->(cond:Condition)
WHERE pa.id = "{{ patient_id }}" 
OPTIONAL MATCH (cond)-[r2]->(c:Code)
OPTIONAL MATCH (cond)-[r]->(enc:Encounter)
WITH pa, cond, c, apoc.convert.fromJsonMap(cond.clinicalStatus) as value ,enc
RETURN DISTINCT 
    apoc.coll.toSet(
        [text in COALESCE(cond.displayText, []) WHERE text IS NOT NULL and lower(text) <> 'diagnosis' | lower(text)] + 
        [text in COALESCE([c.name], []) WHERE text IS NOT NULL and lower(text) <> 'diagnosis' | lower(text)]
    ) as condition,
    c.code as conditionCode,
    c.system as codeSystem,
    COALESCE(value.coding[0].display, value.coding[0].code) as conditionStatus,
    COALESCE (toString(cond.onsetDateTime), COALESCE(enc.actualPeriodStartDate, cond.onsetPeriodStartDate)) as onsetDate,
    c.abatement_date as abatementDate
    